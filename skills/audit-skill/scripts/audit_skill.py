#!/usr/bin/env python3
"""Main orchestrator for skill security audits.

Usage: audit_skill.py <skill-directory> [--quick] [--json] [--layer 1|2|3]
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Add parent scripts dir so layer modules can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent))

from instruction_audit import run_instruction_audit  # noqa: E402
from score import compute_trust_score, format_score_json, format_score_markdown  # noqa: E402
from structural_audit import run_structural_audit  # noqa: E402

# Repo root (two levels up from scripts/)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SECURE_CODE_DIR = REPO_ROOT / "skills" / "secure-code"
AUDIT_RULES = Path(__file__).resolve().parent.parent / "rules" / "skill-scripts.yaml"

# --- Layer 3: Code Audit ---

SECRET_PATTERNS = [
    (r"""(?:api_key|apikey|api_secret|secret_key|auth_token|access_token|private_key)\s*[=:]\s*['"][A-Za-z0-9_\-/.+]{16,}['"]""", "hardcoded-secret"),
    (r"""['"]sk-[A-Za-z0-9]{20,}['"]""", "openai-key"),
    (r"""['"]ghp_[A-Za-z0-9]{36}['"]""", "github-token"),
    (r"""['"]AKIA[A-Z0-9]{16}['"]""", "aws-access-key"),
]

DANGEROUS_PATTERNS = [
    (r"""\beval\s*\(""", "eval-call"),
    (r"""\bexec\s*\(""", "exec-call"),
    (r"""\brm\s+-rf\b""", "rm-rf"),
    (r"""\bcurl\b.*\|\s*bash""", "curl-pipe-bash"),
    (r"""\bwget\b.*\|\s*bash""", "wget-pipe-bash"),
    (r"""\bchmod\s+777\b""", "chmod-777"),
    (r"""\bos\.system\s*\(""", "os-system"),
    (r"""shell\s*=\s*True""", "shell-true"),
]


def run_code_audit_regex(skill_path: Path) -> list[dict]:
    """Regex-based code checks (always available, no external deps)."""
    scripts_dir = skill_path / "scripts"
    if not scripts_dir.exists():
        return []

    findings = []
    for fpath in scripts_dir.rglob("*"):
        if not fpath.is_file() or fpath.suffix not in (".py", ".sh", ".bash", ".js", ".ts"):
            continue
        if any(part == "__pycache__" for part in fpath.parts):
            continue
        try:
            content = fpath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        rel = str(fpath.relative_to(skill_path))
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            for pattern, category in SECRET_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(
                        {
                            "id": "CODE-010",
                            "severity": "CRITICAL",
                            "layer": 3,
                            "category": f"secret-{category}",
                            "message": f"Potential hardcoded secret ({category}): {line.strip()[:80]}",
                            "file": rel,
                            "line": i,
                            "remediation": "Use environment variables or a secrets manager.",
                        }
                    )
                    break

            for pattern, category in DANGEROUS_PATTERNS:
                if re.search(pattern, line):
                    findings.append(
                        {
                            "id": "CODE-020",
                            "severity": "HIGH",
                            "layer": 3,
                            "category": f"dangerous-{category}",
                            "message": f"Dangerous pattern ({category}): {line.strip()[:80]}",
                            "file": rel,
                            "line": i,
                            "remediation": "Avoid dynamic execution and dangerous shell patterns.",
                        }
                    )
                    break

    return findings


def run_code_audit_semgrep(skill_path: Path) -> list[dict]:
    """Run semgrep via secure-code scripts if available."""
    scripts_dir = skill_path / "scripts"
    if not scripts_dir.exists():
        return []

    scan_sh = SECURE_CODE_DIR / "scripts" / "scan.sh"
    if not scan_sh.exists() or not shutil.which("semgrep"):
        return []

    findings = []

    # Run with custom skill-audit rules
    if AUDIT_RULES.exists():
        try:
            result = subprocess.run(
                ["bash", str(scan_sh), str(scripts_dir), "--config", str(AUDIT_RULES)],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.stdout.strip():
                data = json.loads(result.stdout)
                for r in data.get("results", []):
                    severity_map = {"ERROR": "HIGH", "WARNING": "MEDIUM", "INFO": "LOW"}
                    sev = severity_map.get(r.get("extra", {}).get("severity", ""), "MEDIUM")
                    fpath = r.get("path", "")
                    try:
                        rel = str(Path(fpath).relative_to(skill_path))
                    except ValueError:
                        rel = fpath
                    findings.append(
                        {
                            "id": "CODE-030",
                            "severity": sev,
                            "layer": 3,
                            "category": f"semgrep-{r.get('check_id', 'unknown')}",
                            "message": r.get("extra", {}).get("message", r.get("check_id", "")),
                            "file": rel,
                            "line": r.get("start", {}).get("line"),
                            "remediation": r.get("extra", {}).get("fix", "See semgrep rule for details."),
                        }
                    )
        except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
            pass

    # Run trifecta audit
    trifecta_py = SECURE_CODE_DIR / "scripts" / "trifecta_audit.py"
    if trifecta_py.exists():
        try:
            result = subprocess.run(
                ["python3", str(trifecta_py), str(scripts_dir)],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.stdout.strip():
                data = json.loads(result.stdout)
                for r in data.get("results", []):
                    if r.get("trifecta_detected"):
                        try:
                            rel = str(Path(r["file"]).relative_to(skill_path))
                        except ValueError:
                            rel = r["file"]
                        findings.append(
                            {
                                "id": "CODE-040",
                                "severity": "CRITICAL",
                                "layer": 3,
                                "category": "trifecta",
                                "message": f"Lethal trifecta detected in {rel}: "
                                f"all three legs present ({', '.join(r.get('detected_legs', []))}).",
                                "file": rel,
                                "line": None,
                                "remediation": "Separate private data access, untrusted input, "
                                "and external communication into distinct modules.",
                            }
                        )
        except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
            pass

    return findings


def run_code_audit(skill_path: Path) -> list[dict]:
    """Run full Layer 3 audit: regex checks + semgrep (if available)."""
    findings = run_code_audit_regex(skill_path)
    findings.extend(run_code_audit_semgrep(skill_path))
    return findings


# --- Orchestrator ---


def run_audit(skill_path: str, quick: bool = False, layers: list[int] | None = None) -> dict:
    """Run the full skill audit and return structured results."""
    path = Path(skill_path).resolve()
    if not path.is_dir():
        return {"error": f"Not a directory: {skill_path}"}

    has_scripts = (path / "scripts").exists()
    all_findings = []
    run_layers = layers or [1, 2, 3]

    if 1 in run_layers:
        all_findings.extend(run_structural_audit(str(path)))

    if 2 in run_layers:
        all_findings.extend(run_instruction_audit(str(path)))

    if 3 in run_layers and not quick:
        all_findings.extend(run_code_audit(path))

    score = compute_trust_score(all_findings, has_scripts=has_scripts)

    return {
        "skill": str(path),
        "score": score,
        "findings": all_findings,
    }


def format_markdown(result: dict) -> str:
    """Format full audit result as markdown."""
    if "error" in result:
        return f"**Error**: {result['error']}"

    lines = [f"# Skill Audit: {Path(result['skill']).name}", ""]
    lines.append(format_score_markdown(result["score"]))
    lines.append("")

    findings = result["findings"]
    if not findings:
        lines.append("No findings. Clean audit.")
        return "\n".join(lines)

    # Group by severity
    by_severity = {}
    for f in findings:
        by_severity.setdefault(f["severity"], []).append(f)

    for sev in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFORMATIONAL"):
        group = by_severity.get(sev, [])
        if not group:
            continue
        lines.append(f"## {sev} ({len(group)})")
        lines.append("")
        for f in group:
            loc = f["file"]
            if f.get("line"):
                loc += f":{f['line']}"
            lines.append(f"- **[{f['id']}]** {f['message']}")
            lines.append(f"  - File: `{loc}` | Category: {f['category']}")
            lines.append(f"  - Fix: {f['remediation']}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Audit an agent skill for security issues.")
    parser.add_argument("skill_directory", help="Path to the skill directory to audit")
    parser.add_argument("--quick", action="store_true", help="Skip Layer 3 code audit (semgrep)")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output JSON instead of markdown")
    parser.add_argument("--layer", type=int, choices=[1, 2, 3], help="Run only a specific layer")
    args = parser.parse_args()

    layers = [args.layer] if args.layer else None
    result = run_audit(args.skill_directory, quick=args.quick, layers=layers)

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_markdown(result))

    if "error" in result:
        sys.exit(2)
    sys.exit(0 if result["score"]["passed"] else 1)


if __name__ == "__main__":
    main()
