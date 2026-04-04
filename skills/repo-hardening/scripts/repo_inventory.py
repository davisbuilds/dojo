#!/usr/bin/env python3
"""Deterministic repo inventory for supply-chain and workflow hardening."""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".next",
    ".repo-hardening",
    ".turbo",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "venv",
}

TEXT_SUFFIXES = {
    "",
    ".cjs",
    ".conf",
    ".css",
    ".env",
    ".js",
    ".json",
    ".jsonc",
    ".jsx",
    ".mjs",
    ".md",
    ".mts",
    ".py",
    ".rb",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}

RISK_PATTERNS = {
    "curl_pipe_shell": re.compile(r"curl\b[^\n|]*\|\s*(?:sh|bash)\b"),
    "remote_latest": re.compile(r"releases/latest|@[Ll]atest\b"),
    "raw_github": re.compile(r"raw\.githubusercontent\.com|github\.com/.*/raw/"),
    "npm_install_global": re.compile(r"\bnpm\s+install\s+-g\b"),
    "npm_install": re.compile(r"\bnpm\s+install\b"),
    "pip_install_requirements": re.compile(r"\bpip\s+install\s+-r\b"),
    "uv_sync_unfrozen": re.compile(r"\buv\s+sync\b(?![^\n]*--frozen)"),
}

MUTABLE_REF_RE = re.compile(r"@(main|master|beta|release/|v\d+)\b")
SHA_REF_RE = re.compile(r"@[0-9a-f]{40}$")
WRITE_SCOPE_RE = re.compile(r"^\s*[A-Za-z-]+:\s+write\s*$", re.MULTILINE)
RUNS_ON_LATEST_RE = re.compile(r"runs-on:\s+.*latest")


@dataclass
class Hit:
    path: str
    line: int
    text: str


def iter_files(root: Path) -> Iterable[Path]:
    for current_root, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".cache")]
        current = Path(current_root)
        for name in files:
            path = current / name
            if path.stat().st_size > 1_000_000:
                continue
            suffix = path.suffix.lower()
            if suffix not in TEXT_SUFFIXES and path.name not in {
                "Dockerfile",
                ".gitlab-ci.yml",
                "package.json",
                "requirements.txt",
                "requirements.lock",
                "uv.lock",
                "pnpm-lock.yaml",
                "package-lock.json",
                "bun.lock",
                "bun.lockb",
            }:
                continue
            yield path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def scan_pattern_hits(root: Path) -> dict[str, list[dict[str, object]]]:
    results: dict[str, list[dict[str, object]]] = defaultdict(list)
    for path in iter_files(root):
        text = read_text(path)
        lines = text.splitlines()
        rel = relative(path, root)
        is_markdown = path.suffix.lower() == ".md"
        for idx, line in enumerate(lines, start=1):
            for label, pattern in RISK_PATTERNS.items():
                if is_markdown and label in {
                    "npm_install_global",
                    "npm_install",
                    "pip_install_requirements",
                    "uv_sync_unfrozen",
                }:
                    continue
                if pattern.search(line):
                    results[label].append(asdict(Hit(rel, idx, line.strip())))
    return dict(results)


def scan_packages_of_interest(root: Path, packages: list[str]) -> dict[str, list[dict[str, object]]]:
    if not packages:
        return {}
    results: dict[str, list[dict[str, object]]] = {pkg: [] for pkg in packages}
    package_patterns = {
        pkg: re.compile(rf"(?<![A-Za-z0-9_-]){re.escape(pkg)}(?![A-Za-z0-9_-])", re.IGNORECASE)
        for pkg in packages
    }
    for path in iter_files(root):
        rel = relative(path, root)
        text = read_text(path)
        for idx, line in enumerate(text.splitlines(), start=1):
            for pkg, pattern in package_patterns.items():
                if pattern.search(line):
                    results[pkg].append(asdict(Hit(rel, idx, line.strip())))
    return {pkg: hits for pkg, hits in results.items() if hits}


def find_files(root: Path, names: tuple[str, ...]) -> list[str]:
    found: list[str] = []
    for path in iter_files(root):
        if path.name in names:
            found.append(relative(path, root))
    return sorted(set(found))


def scan_package_managers(root: Path) -> dict[str, object]:
    package_jsons = find_files(root, ("package.json",))
    package_manager_fields: list[dict[str, str]] = []
    publish_scripts: list[dict[str, str]] = []
    for rel in package_jsons:
        path = root / rel
        try:
            data = json.loads(read_text(path))
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            package_manager = data.get("packageManager")
            if isinstance(package_manager, str):
                package_manager_fields.append({"path": rel, "value": package_manager})
            scripts = data.get("scripts")
            if isinstance(scripts, dict):
                for name in ("prepublishOnly", "publish", "postinstall", "prepare"):
                    value = scripts.get(name)
                    if isinstance(value, str):
                        publish_scripts.append({"path": rel, "script": name, "value": value})
    return {
        "package_json_files": package_jsons,
        "package_manager_fields": package_manager_fields,
        "publish_and_install_scripts": publish_scripts,
        "lockfiles": {
            "pnpm": find_files(root, ("pnpm-lock.yaml",)),
            "npm": find_files(root, ("package-lock.json",)),
            "bun": find_files(root, ("bun.lock", "bun.lockb")),
            "uv": find_files(root, ("uv.lock",)),
            "python_hash": find_files(root, ("requirements.lock",)),
            "poetry": find_files(root, ("poetry.lock",)),
        },
        "python_manifests": sorted(
            set(find_files(root, ("pyproject.toml",)) + find_files(root, ("requirements.txt",)))
        ),
    }


def scan_github_workflows(root: Path) -> dict[str, object]:
    workflow_dir = root / ".github" / "workflows"
    files = []
    if workflow_dir.exists():
        files = sorted(
            [relative(path, root) for path in workflow_dir.iterdir() if path.suffix in {".yml", ".yaml"}]
        )
    missing_permissions: list[str] = []
    mutable_refs: list[dict[str, object]] = []
    sha_pinned_count = 0
    latest_runners: list[dict[str, object]] = []
    write_scoped_workflows: list[str] = []
    bot_workflows: list[str] = []

    for rel in files:
        path = root / rel
        text = read_text(path)
        if not re.search(r"(?m)^permissions:\s*$", text):
            missing_permissions.append(rel)
        if WRITE_SCOPE_RE.search(text):
            write_scoped_workflows.append(rel)
        if any(token in text for token in ("issue_comment:", "pull_request_review_comment:", "@claude", "gemini", "codex")):
            bot_workflows.append(rel)
        for idx, line in enumerate(text.splitlines(), start=1):
            if RUNS_ON_LATEST_RE.search(line):
                latest_runners.append(asdict(Hit(rel, idx, line.strip())))
            match = re.search(r"^\s*uses:\s*([^\s#]+)", line)
            if not match:
                continue
            ref = match.group(1)
            if SHA_REF_RE.search(ref):
                sha_pinned_count += 1
            elif MUTABLE_REF_RE.search(ref):
                mutable_refs.append({"path": rel, "line": idx, "ref": ref})

    return {
        "files": files,
        "missing_top_level_permissions": missing_permissions,
        "mutable_refs": mutable_refs,
        "sha_pinned_uses_count": sha_pinned_count,
        "latest_runners": latest_runners,
        "write_scoped_workflows": sorted(set(write_scoped_workflows)),
        "bot_workflows": sorted(set(bot_workflows)),
    }


def build_findings(inventory: dict[str, object]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    pm = inventory["package_managers"]
    gha = inventory["github_actions"]
    risky = inventory["risky_patterns"]

    if pm["package_json_files"] and not pm["package_manager_fields"]:
        findings.append(
            {
                "severity": "medium",
                "title": "Node repo lacks pinned packageManager metadata",
                "detail": "One or more package.json files exist but none declare a packageManager field.",
            }
        )

    lockfile_count = sum(len(v) for v in pm["lockfiles"].values())
    if (pm["package_json_files"] or pm["python_manifests"]) and lockfile_count == 0:
        findings.append(
            {
                "severity": "high",
                "title": "Repo has package manifests but no committed lockfiles",
                "detail": "Fresh dependency resolution remains part of the normal install path.",
            }
        )

    if not gha["files"]:
        findings.append(
            {
                "severity": "medium",
                "title": "No GitHub Actions workflow found",
                "detail": "There is no CI enforcement for frozen installs, lint, build, or test.",
            }
        )
    if gha["mutable_refs"]:
        findings.append(
            {
                "severity": "high",
                "title": "Mutable GitHub Action refs are present",
                "detail": f"{len(gha['mutable_refs'])} mutable uses refs were found across workflow files.",
            }
        )
    if gha["missing_top_level_permissions"]:
        findings.append(
            {
                "severity": "high",
                "title": "Some workflows lack explicit top-level permissions",
                "detail": f"{len(gha['missing_top_level_permissions'])} workflow files are missing a top-level permissions block.",
            }
        )
    if gha["bot_workflows"]:
        findings.append(
            {
                "severity": "medium",
                "title": "Bot or comment-triggered workflows exist",
                "detail": f"{len(gha['bot_workflows'])} workflows appear to be bot-triggered and deserve extra permission review.",
            }
        )

    if risky.get("curl_pipe_shell"):
        findings.append(
            {
                "severity": "high",
                "title": "Install-script bootstrap path detected",
                "detail": f"{len(risky['curl_pipe_shell'])} curl-pipe-shell style hits were found.",
            }
        )
    if risky.get("remote_latest"):
        findings.append(
            {
                "severity": "medium",
                "title": "Mutable latest-style remote downloads detected",
                "detail": f"{len(risky['remote_latest'])} latest-style remote references were found.",
            }
        )
    if risky.get("npm_install") or risky.get("pip_install_requirements") or risky.get("uv_sync_unfrozen"):
        total = len(risky.get("npm_install", [])) + len(risky.get("pip_install_requirements", [])) + len(
            risky.get("uv_sync_unfrozen", [])
        )
        findings.append(
            {
                "severity": "medium",
                "title": "Fresh install or unlock-friendly commands detected",
                "detail": f"{total} install-command hits were found that may bypass a frozen install path.",
            }
        )

    if not findings:
        findings.append(
            {
                "severity": "low",
                "title": "No obvious baseline gaps detected by deterministic scan",
                "detail": "Manual review may still find policy or product-specific issues.",
            }
        )

    severity_order = {"high": 0, "medium": 1, "low": 2}
    return sorted(findings, key=lambda item: severity_order[item["severity"]])


def build_plan(inventory: dict[str, object]) -> tuple[list[str], list[str], list[str]]:
    gha = inventory["github_actions"]
    pm = inventory["package_managers"]
    risky = inventory["risky_patterns"]

    immediate: list[str] = []
    next_items: list[str] = []
    verification: list[str] = []

    if not gha["files"]:
        immediate.append("Add a minimum CI workflow with frozen installs and the repo's native lint/build/test commands.")
    if gha["mutable_refs"]:
        immediate.append("Pin mutable GitHub Action refs to commit SHAs.")
    if gha["missing_top_level_permissions"]:
        immediate.append("Add explicit top-level permissions blocks to every workflow.")
    if pm["package_json_files"] and not pm["package_manager_fields"]:
        immediate.append("Add a packageManager field to package.json so local and CI installs use the same pnpm version.")
    if risky.get("curl_pipe_shell"):
        immediate.append("Replace curl-pipe-shell bootstrap paths with pinned artifacts or fail-closed behavior.")
    if risky.get("npm_install") or risky.get("pip_install_requirements") or risky.get("uv_sync_unfrozen"):
        immediate.append("Convert CI and release installs to frozen or hash-verified forms.")

    if gha["bot_workflows"]:
        next_items.append("Review bot workflow write scopes and remove install-capable commands unless explicitly justified.")
    if gha["latest_runners"]:
        next_items.append("Review latest runner labels and pin them where compatibility risk is low.")
    if risky.get("remote_latest") or risky.get("raw_github"):
        next_items.append("Replace latest and raw remote artifact fetches in build or release paths with versioned, verified retrieval.")
    if not next_items:
        next_items.append("Keep the artifact packet current whenever workflow, package-manager, or release-path behavior changes.")

    verification.extend(
        [
            "Rerun the target repo's native lint, build, and test commands after any hardening change.",
            "Re-run the inventory script so inventory.json, audit.md, and hardening-plan.md match the post-change state.",
            "If workflow files changed, confirm there are no mutable uses refs and no missing top-level permissions blocks.",
        ]
    )

    return immediate or ["No immediate deterministic baseline gap was found."], next_items, verification


def format_bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def format_findings(findings: list[dict[str, str]]) -> str:
    blocks = []
    for finding in findings:
        blocks.append(
            f"### {finding['severity'].upper()}: {finding['title']}\n\n- {finding['detail']}"
        )
    return "\n\n".join(blocks)


def format_evidence(inventory: dict[str, object]) -> str:
    bullets: list[str] = []
    gha = inventory["github_actions"]
    pm = inventory["package_managers"]
    risky = inventory["risky_patterns"]
    bullets.append(f"GitHub workflow files: {len(gha['files'])}")
    bullets.append(f"Mutable workflow refs: {len(gha['mutable_refs'])}")
    bullets.append(f"Workflows missing top-level permissions: {len(gha['missing_top_level_permissions'])}")
    bullets.append(f"SHA-pinned workflow uses refs: {gha['sha_pinned_uses_count']}")
    bullets.append(
        f"Lockfiles present: {sum(len(v) for v in pm['lockfiles'].values())} total across pnpm/npm/bun/uv/python-hash/poetry"
    )
    for label, hits in sorted(risky.items()):
        bullets.append(f"{label}: {len(hits)} hit(s)")
    if inventory["packages_of_interest"]:
        for pkg, hits in sorted(inventory["packages_of_interest"].items()):
            bullets.append(f"package search {pkg}: {len(hits)} hit(s)")
    return format_bullets(bullets)


def load_template(script_path: Path, name: str, fallback: str) -> str:
    candidate = script_path.parent.parent / "assets" / "templates" / name
    if candidate.exists():
        return read_text(candidate)
    return fallback


def write_reports(root: Path, out_dir: Path, inventory: dict[str, object]) -> None:
    generated_at = inventory["generated_at"]
    repo_name = inventory["repo_name"]
    findings = build_findings(inventory)
    immediate, next_items, verification = build_plan(inventory)
    summary_bullets = format_bullets(
        [
            f"Repo path: {inventory['repo_path']}",
            f"GitHub workflow files: {len(inventory['github_actions']['files'])}",
            f"Mutable workflow refs: {len(inventory['github_actions']['mutable_refs'])}",
            f"Missing top-level permissions: {len(inventory['github_actions']['missing_top_level_permissions'])}",
            f"Lockfiles present: {sum(len(v) for v in inventory['package_managers']['lockfiles'].values())}",
        ]
    )
    audit_template = load_template(
        Path(__file__),
        "audit.md.tpl",
        "# Repo Hardening Audit\n\n## Snapshot\n\n{summary_bullets}\n\n## Findings\n\n{findings}\n",
    )
    plan_template = load_template(
        Path(__file__),
        "hardening-plan.md.tpl",
        "# Repo Hardening Plan\n\n## Immediate\n\n{immediate}\n",
    )
    audit_body = audit_template.format(
        generated_at=generated_at,
        repo_name=repo_name,
        summary_bullets=summary_bullets,
        findings=format_findings(findings),
        evidence=format_evidence(inventory),
    )
    plan_body = plan_template.format(
        generated_at=generated_at,
        repo_name=repo_name,
        immediate=format_bullets(immediate),
        next_items=format_bullets(next_items),
        verification=format_bullets(verification),
    )
    (out_dir / "audit.md").write_text(audit_body, encoding="utf-8")
    (out_dir / "hardening-plan.md").write_text(plan_body, encoding="utf-8")
    (out_dir / "inventory.json").write_text(json.dumps(inventory, indent=2, sort_keys=True), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo_path", nargs="?", default=".", help="Target repo path")
    parser.add_argument("--out-dir", default=".repo-hardening", help="Output directory inside the target repo")
    parser.add_argument("--package", action="append", default=[], help="Package name to search for")
    args = parser.parse_args()

    root = Path(args.repo_path).resolve()
    out_dir = root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    inventory = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "repo_name": root.name,
        "repo_path": str(root),
        "package_managers": scan_package_managers(root),
        "github_actions": scan_github_workflows(root),
        "gitlab_ci_files": sorted(
            [relative(path, root) for path in root.glob(".gitlab-ci.yml")]
            + [relative(path, root) for path in (root / "pipelines").glob("*.yml") if (root / "pipelines").exists()]
        ),
        "risky_patterns": scan_pattern_hits(root),
        "packages_of_interest": scan_packages_of_interest(root, args.package),
    }
    write_reports(root, out_dir, inventory)

    print(
        json.dumps(
            {
                "repo": root.name,
                "output_dir": str(out_dir),
                "files": [
                    str(out_dir / "inventory.json"),
                    str(out_dir / "audit.md"),
                    str(out_dir / "hardening-plan.md"),
                ],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
