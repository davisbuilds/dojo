#!/usr/bin/env python3
"""Shared helpers for the skill-standardizer scripts."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
from typing import Any

AGENTS_HOME_ENV = "AGENTS_HOME"
CODEX_HOME_ENV = "CODEX_HOME"
CLAUDE_HOME_ENV = "CLAUDE_HOME"

IGNORE_NAMES = {".DS_Store", "__pycache__", ".git"}


@dataclass
class RootSpec:
    path: Path
    kind: str
    label: str
    exists: bool


@dataclass
class SkillEntry:
    name: str
    path: Path
    resolved_path: Path
    is_symlink: bool
    link_target: str | None
    dir_hash: str


@dataclass
class RootInventory:
    root: RootSpec
    skills: dict[str, SkillEntry]
    invalid_entries: list[str]


@dataclass
class Context:
    canonical_root: Path | None
    roots: list[RootSpec]


def _expand(path: str | Path) -> Path:
    return Path(path).expanduser().resolve()


def _normalize_skills_root(path: str | Path) -> Path:
    candidate = _expand(path)
    if (candidate / "skills").is_dir():
        return (candidate / "skills").resolve()
    return candidate


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def discover_repo_root(start: Path) -> Path | None:
    current = start.resolve()
    for probe in [current, *current.parents]:
        has_skills = (probe / "skills").is_dir()
        has_marker = (probe / "AGENTS.md").is_file() or (probe / "skills.json").is_file()
        if has_skills and has_marker:
            return probe
    return None


def global_roots() -> dict[str, Path]:
    agents_home = Path(os.environ.get(AGENTS_HOME_ENV, "~/.agents")).expanduser()
    codex_home = Path(os.environ.get(CODEX_HOME_ENV, "~/.codex")).expanduser()
    claude_home = Path(os.environ.get(CLAUDE_HOME_ENV, "~/.claude")).expanduser()
    return {
        "global-agents": (agents_home / "skills").resolve(),
        "global-codex": (codex_home / "skills").resolve(),
        "global-claude": (claude_home / "skills").resolve(),
    }


def is_plugin_cache_path(path: Path) -> bool:
    needle = "/.claude/plugins/cache"
    return needle in str(path)


def _classify_root(path: Path, canonical_root: Path | None, globals_map: dict[str, Path]) -> tuple[str, str]:
    if canonical_root and path == canonical_root:
        return "canonical", "canonical"
    for kind, root in globals_map.items():
        if path == root:
            return kind, kind
    if is_plugin_cache_path(path):
        return "plugin-cache", "plugin-cache"
    return "local", "local"


def _unique_paths(paths: list[Path]) -> list[Path]:
    seen: set[Path] = set()
    ordered: list[Path] = []
    for path in paths:
        if path in seen:
            continue
        seen.add(path)
        ordered.append(path)
    return ordered


def resolve_context(
    canonical_root_arg: str | None,
    root_args: list[str] | None,
    include_plugin_caches: bool,
) -> Context:
    cwd = Path.cwd().resolve()
    repo_root = discover_repo_root(cwd)

    canonical_root: Path | None = None
    if canonical_root_arg:
        canonical_root = _normalize_skills_root(canonical_root_arg)
    elif repo_root:
        canonical_root = (repo_root / "skills").resolve()

    globals_map = global_roots()
    roots: list[Path] = []
    if canonical_root:
        roots.append(canonical_root)
    roots.extend(globals_map.values())

    cwd_skills = (cwd / "skills").resolve()
    if cwd_skills.is_dir() and cwd_skills not in roots:
        roots.append(cwd_skills)

    for root_arg in root_args or []:
        roots.append(_normalize_skills_root(root_arg))

    specs: list[RootSpec] = []
    for path in _unique_paths(roots):
        kind, label = _classify_root(path, canonical_root, globals_map)
        if kind == "plugin-cache" and not include_plugin_caches:
            continue
        exists = path.exists() and path.is_dir()
        specs.append(RootSpec(path=path, kind=kind, label=label, exists=exists))

    return Context(canonical_root=canonical_root, roots=specs)


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def hash_directory(path: Path) -> str:
    digest = hashlib.sha256()
    root = path.resolve()

    for current, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        dirnames[:] = [
            name
            for name in sorted(dirnames)
            if name not in IGNORE_NAMES and not name.startswith(".")
        ]
        for name in sorted(filenames):
            if name in IGNORE_NAMES or name.endswith(".pyc"):
                continue
            file_path = current_path / name
            rel_path = file_path.relative_to(root).as_posix()
            if file_path.is_symlink():
                target = os.readlink(file_path)
                digest.update(f"L:{rel_path}:{target}\n".encode("utf-8"))
                continue
            digest.update(f"F:{rel_path}:".encode("utf-8"))
            digest.update(_hash_file(file_path).encode("utf-8"))
            digest.update(b"\n")
    return digest.hexdigest()


def scan_root(root: RootSpec) -> RootInventory:
    skills: dict[str, SkillEntry] = {}
    invalid_entries: list[str] = []

    if not root.exists:
        return RootInventory(root=root, skills=skills, invalid_entries=invalid_entries)

    for child in sorted(root.path.iterdir(), key=lambda p: p.name):
        if child.name.startswith("."):
            continue
        if child.name in IGNORE_NAMES:
            continue
        if not child.is_dir() and not child.is_symlink():
            continue

        skill_md = child / "SKILL.md"
        if not skill_md.is_file():
            invalid_entries.append(child.name)
            continue

        link_target = os.readlink(child) if child.is_symlink() else None
        resolved_path = child.resolve()
        if not resolved_path.is_dir():
            invalid_entries.append(child.name)
            continue
        skills[child.name] = SkillEntry(
            name=child.name,
            path=child,
            resolved_path=resolved_path,
            is_symlink=child.is_symlink(),
            link_target=link_target,
            dir_hash=hash_directory(resolved_path),
        )

    return RootInventory(root=root, skills=skills, invalid_entries=invalid_entries)


def _preferred_global_kinds() -> list[str]:
    return ["global-agents", "global-codex", "global-claude"]


def preferred_global_for_skill(skill: str, inventories: list[RootInventory]) -> tuple[RootSpec, SkillEntry] | None:
    by_kind = {inv.root.kind: inv for inv in inventories}
    for kind in _preferred_global_kinds():
        inv = by_kind.get(kind)
        if not inv:
            continue
        entry = inv.skills.get(skill)
        if entry:
            return inv.root, entry
    return None


def _to_jsonable_issue(issue: dict[str, Any]) -> dict[str, Any]:
    out = dict(issue)
    for key in ["source", "dest", "root", "canonical", "global_root", "local_root"]:
        if key in out and isinstance(out[key], Path):
            out[key] = str(out[key])
    return out


def build_audit_report(
    context: Context,
    local_policy: str,
    keep_local_skills: set[str] | None,
    enforce_mirror: bool,
) -> dict[str, Any]:
    keep_local_skills = keep_local_skills or set()

    inventories = [scan_root(root) for root in context.roots]
    by_path = {inv.root.path: inv for inv in inventories}
    canonical_inventory = by_path.get(context.canonical_root) if context.canonical_root else None

    issues: list[dict[str, Any]] = []
    actions: list[dict[str, Any]] = []

    def add_issue(**kwargs: Any) -> None:
        issues.append(kwargs)

    def add_action(**kwargs: Any) -> None:
        actions.append(kwargs)

    for inv in inventories:
        for name in inv.invalid_entries:
            add_issue(
                severity="warning",
                code="INVALID_SKILL_DIR",
                skill=name,
                root=inv.root.path,
                message="Directory does not contain a valid SKILL.md",
            )

    all_skill_names: set[str] = set()
    for inv in inventories:
        all_skill_names.update(inv.skills.keys())

    for skill in sorted(all_skill_names):
        entries = [(inv.root, inv.skills[skill]) for inv in inventories if skill in inv.skills]

        if canonical_inventory and skill in canonical_inventory.skills:
            canonical_entry = canonical_inventory.skills[skill]
            for root, entry in entries:
                if root.kind == "canonical":
                    continue

                if (
                    root.kind == "local"
                    and local_policy == "prefer-global-link"
                    and skill not in keep_local_skills
                    and preferred_global_for_skill(skill, inventories)
                ):
                    continue

                if entry.dir_hash != canonical_entry.dir_hash:
                    add_issue(
                        severity="warning",
                        code="CONTENT_DRIFT",
                        skill=skill,
                        root=root.path,
                        canonical=canonical_entry.path,
                        message="Skill content differs from canonical copy",
                    )
                    add_action(
                        action="sync_copy",
                        skill=skill,
                        source=canonical_entry.path,
                        dest=root.path / skill,
                        reason="Align with canonical copy",
                    )

            if enforce_mirror:
                for inv in inventories:
                    if not inv.root.kind.startswith("global-"):
                        continue
                    if skill in inv.skills:
                        continue
                    add_issue(
                        severity="info",
                        code="MISSING_GLOBAL_MIRROR",
                        skill=skill,
                        root=inv.root.path,
                        canonical=canonical_entry.path,
                        message="Canonical skill missing in global mirror",
                    )
                    add_action(
                        action="create_copy",
                        skill=skill,
                        source=canonical_entry.path,
                        dest=inv.root.path / skill,
                        reason="Create missing global mirror from canonical",
                    )

        # Detect cross-global drift even when canonical is absent.
        global_entries = [
            (root, entry)
            for root, entry in entries
            if root.kind.startswith("global-")
        ]
        if len(global_entries) > 1:
            preferred = preferred_global_for_skill(skill, inventories)
            if preferred:
                _, preferred_entry = preferred
                for root, entry in global_entries:
                    if entry.path == preferred_entry.path:
                        continue
                    if entry.dir_hash == preferred_entry.dir_hash:
                        continue
                    add_issue(
                        severity="warning",
                        code="GLOBAL_DRIFT",
                        skill=skill,
                        root=root.path,
                        global_root=preferred_entry.path,
                        message="Global copies differ from preferred global source",
                    )
                    if not (canonical_inventory and skill in canonical_inventory.skills):
                        add_action(
                            action="sync_copy",
                            skill=skill,
                            source=preferred_entry.path,
                            dest=root.path / skill,
                            reason="Align global copy with preferred global source",
                        )

        if local_policy == "prefer-global-link":
            preferred = preferred_global_for_skill(skill, inventories)
            if preferred is None:
                continue
            _, global_entry = preferred
            global_target = global_entry.path.resolve()

            for root, entry in entries:
                if root.kind != "local":
                    continue
                if skill in keep_local_skills:
                    continue

                already_linked = entry.is_symlink and entry.path.resolve() == global_target
                if already_linked:
                    continue

                code = "LOCAL_DUPLICATE_GLOBAL"
                message = "Local copy duplicates a global skill and should link to global"
                severity = "warning"
                if entry.dir_hash == global_entry.dir_hash:
                    code = "LOCAL_DUPLICATE_GLOBAL_IDENTICAL"
                    message = "Local copy matches global; symlink recommended"
                    severity = "info"

                add_issue(
                    severity=severity,
                    code=code,
                    skill=skill,
                    local_root=root.path,
                    global_root=global_entry.path,
                    message=message,
                )
                add_action(
                    action="relink_to_global",
                    skill=skill,
                    source=global_entry.path,
                    dest=root.path / skill,
                    reason="Prefer global link for local duplicate",
                )

    deduped_actions: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, str]] = set()
    for action in actions:
        key = (action["action"], str(action["dest"]))
        if key in seen_keys:
            continue
        seen_keys.add(key)
        deduped_actions.append(action)

    report = {
        "generated_at": utc_now_iso(),
        "cwd": str(Path.cwd()),
        "canonical_root": str(context.canonical_root) if context.canonical_root else None,
        "roots": [
            {
                "path": str(inv.root.path),
                "kind": inv.root.kind,
                "label": inv.root.label,
                "exists": inv.root.exists,
                "skill_count": len(inv.skills),
                "invalid_entries": list(inv.invalid_entries),
            }
            for inv in inventories
        ],
        "local_policy": local_policy,
        "keep_local_skills": sorted(keep_local_skills),
        "enforce_mirror": enforce_mirror,
        "issues": [_to_jsonable_issue(issue) for issue in issues],
        "actions": [_to_jsonable_issue(action) for action in deduped_actions],
    }
    return report


def summarize_report(report: dict[str, Any]) -> str:
    lines: list[str] = []
    canonical = report.get("canonical_root")
    lines.append(f"Canonical root: {canonical or 'none'}")
    lines.append("Roots:")
    for root in report["roots"]:
        suffix = " (missing)" if not root["exists"] else ""
        lines.append(
            f"- {root['kind']}: {root['path']} | skills={root['skill_count']}{suffix}"
        )

    issue_count = len(report["issues"])
    action_count = len(report["actions"])
    lines.append(f"Issues: {issue_count}")
    lines.append(f"Planned actions: {action_count}")

    if issue_count:
        lines.append("Issue summary:")
        for issue in report["issues"][:20]:
            skill = issue.get("skill", "<unknown>")
            code = issue.get("code", "ISSUE")
            msg = issue.get("message", "")
            lines.append(f"- [{code}] {skill}: {msg}")
        if issue_count > 20:
            lines.append(f"- ... ({issue_count - 20} more)")

    return "\n".join(lines)


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    output = _expand(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _backup_destination(dest: Path, backup_root: Path, stamp: str) -> Path | None:
    if not dest.exists() and not dest.is_symlink():
        return None

    digest = hashlib.sha1(str(dest).encode("utf-8")).hexdigest()[:10]
    backup_dir = backup_root / stamp
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{dest.name}-{digest}"

    if backup_path.exists() or backup_path.is_symlink():
        counter = 1
        while True:
            candidate = backup_dir / f"{dest.name}-{digest}-{counter}"
            if not candidate.exists() and not candidate.is_symlink():
                backup_path = candidate
                break
            counter += 1

    shutil.move(str(dest), str(backup_path))
    return backup_path


def _replace_with_copy(source: Path, dest: Path) -> None:
    src = source.resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dest, symlinks=True)


def _replace_with_symlink(source: Path, dest: Path) -> None:
    target = source.resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.symlink_to(target, target_is_directory=True)


def apply_actions(
    report: dict[str, Any],
    apply: bool,
    backup_root: str,
) -> dict[str, Any]:
    actions = report.get("actions", [])
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_base = _expand(backup_root)

    result = {
        "mode": "apply" if apply else "dry-run",
        "planned": actions,
        "applied": [],
        "backups": [],
        "errors": [],
        "backup_root": str(backup_base),
    }

    if not apply:
        return result

    for action in actions:
        action_type = action["action"]
        source = _expand(action["source"])
        dest = _expand(action["dest"])

        try:
            backup = _backup_destination(dest, backup_base, stamp)
            if backup:
                result["backups"].append({"dest": str(dest), "backup": str(backup)})

            if action_type in {"sync_copy", "create_copy"}:
                _replace_with_copy(source, dest)
            elif action_type == "relink_to_global":
                _replace_with_symlink(source, dest)
            else:
                raise ValueError(f"Unsupported action type: {action_type}")

            result["applied"].append(action)
        except Exception as exc:  # noqa: BLE001
            result["errors"].append(
                {
                    "action": action,
                    "error": str(exc),
                }
            )

    return result


def print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2))


def root_describe(context: Context) -> dict[str, Any]:
    inventories = [scan_root(root) for root in context.roots]
    return {
        "generated_at": utc_now_iso(),
        "cwd": str(Path.cwd()),
        "canonical_root": str(context.canonical_root) if context.canonical_root else None,
        "roots": [
            {
                **asdict(inv.root),
                "path": str(inv.root.path),
                "skills": sorted(inv.skills.keys()),
                "skill_count": len(inv.skills),
                "invalid_entries": inv.invalid_entries,
            }
            for inv in inventories
        ],
    }
