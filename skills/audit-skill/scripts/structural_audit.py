#!/usr/bin/env python3
"""Layer 1: Structural audit for agent skills."""

import os
import re
import sys
from pathlib import Path

import yaml

# Import validate_skill and _extract_frontmatter from quick_validate.py
_SKILL_CREATOR_DIR = str(
    Path(__file__).resolve().parent.parent.parent / "skill-creator" / "scripts"
)
if _SKILL_CREATOR_DIR not in sys.path:
    sys.path.insert(0, _SKILL_CREATOR_DIR)

from quick_validate import _extract_frontmatter, validate_skill  # noqa: E402

# Tool risk classification
TOOL_RISK = {
    # CRITICAL
    "Bash(*)": "CRITICAL",
    # HIGH
    "Bash(curl:*)": "HIGH",
    "Bash(wget:*)": "HIGH",
    "Bash(pip:*)": "HIGH",
    "Bash(pip3:*)": "HIGH",
    "Bash(npm:*)": "HIGH",
    "Write": "HIGH",
    # MEDIUM
    "Bash(git:*)": "MEDIUM",
    "Bash(python3:*)": "MEDIUM",
    "Bash(python:*)": "MEDIUM",
    # LOW
    "Read": "LOW",
    "Glob": "LOW",
    "Grep": "LOW",
    "WebFetch": "LOW",
    "WebSearch": "LOW",
}

SUSPICIOUS_EXTENSIONS = {".pyc", ".so", ".dll", ".exe", ".bin", ".pyd", ".whl"}
NETWORK_PATTERNS = [
    r"\bcurl\b",
    r"\bwget\b",
    r"\brequests\.",
    r"\bfetch\(",
    r"\bhttpx\.",
    r"\burllib\.",
    r"\bpip\s+install\b",
    r"\bnpm\s+install\b",
    r"\bpip3\s+install\b",
]


def check_frontmatter(skill_path: Path) -> list[dict]:
    """Validate skill via quick_validate and convert to findings."""
    valid, message = validate_skill(str(skill_path))
    if valid:
        return []
    return [
        {
            "id": "STRUCT-001",
            "severity": "HIGH",
            "layer": 1,
            "category": "frontmatter",
            "message": f"Frontmatter validation failed: {message}",
            "file": "SKILL.md",
            "line": None,
            "remediation": "Fix SKILL.md frontmatter per the skill spec.",
        }
    ]


def allowed_tools_blast_radius(skill_path: Path) -> list[dict]:
    """Analyze allowed-tools for dangerous permissions."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return []

    content = skill_md.read_text(encoding="utf-8")
    match = _extract_frontmatter(content)
    if not match:
        return []

    try:
        fm = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return []

    if not isinstance(fm, dict):
        return []

    tools = fm.get("allowed-tools")
    if tools is None:
        return [
            {
                "id": "STRUCT-010",
                "severity": "INFORMATIONAL",
                "layer": 1,
                "category": "allowed-tools",
                "message": "No allowed-tools field in frontmatter. "
                "Skill relies on command wrappers or defaults.",
                "file": "SKILL.md",
                "line": None,
                "remediation": "Consider adding an explicit allowed-tools list.",
            }
        ]

    if not isinstance(tools, list):
        tools = [tools]

    findings = []
    for tool in tools:
        tool_str = str(tool).strip()
        # Check exact matches first, then prefix matches
        severity = None
        for pattern, risk in TOOL_RISK.items():
            if tool_str == pattern or (
                pattern.endswith("*)") and tool_str.startswith(pattern[:-2])
            ):
                severity = risk
                break
        # Check for generic Bash(*) — unrestricted shell
        if severity is None and re.match(r"^Bash\(\*\)$", tool_str):
            severity = "CRITICAL"
        # Check for Bash with dangerous commands
        if severity is None and tool_str.startswith("Bash("):
            inner = tool_str[5:].rstrip(")")
            for dangerous in ("curl", "wget", "pip", "pip3", "npm"):
                if inner.startswith(dangerous):
                    severity = "HIGH"
                    break
            if severity is None:
                severity = "MEDIUM"

        if severity and severity in ("CRITICAL", "HIGH"):
            findings.append(
                {
                    "id": "STRUCT-011",
                    "severity": severity,
                    "layer": 1,
                    "category": "allowed-tools",
                    "message": f"Tool '{tool_str}' grants {severity.lower()}-risk access.",
                    "file": "SKILL.md",
                    "line": None,
                    "remediation": f"Narrow the tool scope or document why '{tool_str}' is needed.",
                }
            )
    return findings


def file_inventory(skill_path: Path) -> list[dict]:
    """Flag suspicious files, excessive file count, or large total size."""
    findings = []
    total_size = 0
    file_count = 0

    for root, dirs, files in os.walk(skill_path):
        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
        for fname in files:
            fpath = Path(root) / fname
            rel = fpath.relative_to(skill_path)
            file_count += 1
            try:
                total_size += fpath.stat().st_size
            except OSError:
                pass

            ext = fpath.suffix.lower()
            if ext in SUSPICIOUS_EXTENSIONS:
                findings.append(
                    {
                        "id": "STRUCT-020",
                        "severity": "HIGH",
                        "layer": 1,
                        "category": "suspicious-file",
                        "message": f"Binary/compiled file detected: {rel}",
                        "file": str(rel),
                        "line": None,
                        "remediation": "Remove compiled/binary files. Skills should contain source only.",
                    }
                )

            if fname.startswith(".") and fname not in (".gitkeep", ".gitignore"):
                findings.append(
                    {
                        "id": "STRUCT-021",
                        "severity": "MEDIUM",
                        "layer": 1,
                        "category": "hidden-file",
                        "message": f"Hidden file detected: {rel}",
                        "file": str(rel),
                        "line": None,
                        "remediation": "Remove hidden files unless they serve a documented purpose.",
                    }
                )

    if file_count > 50:
        findings.append(
            {
                "id": "STRUCT-022",
                "severity": "MEDIUM",
                "layer": 1,
                "category": "excessive-files",
                "message": f"Skill contains {file_count} files (threshold: 50).",
                "file": ".",
                "line": None,
                "remediation": "Reduce file count. Skills should be focused and minimal.",
            }
        )

    if total_size > 1_000_000:
        findings.append(
            {
                "id": "STRUCT-023",
                "severity": "MEDIUM",
                "layer": 1,
                "category": "excessive-size",
                "message": f"Skill total size is {total_size / 1_000_000:.1f}MB (threshold: 1MB).",
                "file": ".",
                "line": None,
                "remediation": "Reduce total size. Move large assets to external references.",
            }
        )

    return findings


def network_inference(skill_path: Path) -> list[dict]:
    """Detect network access in scripts not declared in compatibility."""
    scripts_dir = skill_path / "scripts"
    if not scripts_dir.exists():
        return []

    # Check if compatibility mentions network
    skill_md = skill_path / "SKILL.md"
    compatibility_mentions_network = False
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")
        match = _extract_frontmatter(content)
        if match:
            try:
                fm = yaml.safe_load(match.group(1))
                compat = (fm or {}).get("compatibility", "")
                if isinstance(compat, str) and re.search(
                    r"(network|internet|online|http|api|fetch|download)", compat, re.I
                ):
                    compatibility_mentions_network = True
            except yaml.YAMLError:
                pass

    findings = []
    compiled = [re.compile(p, re.IGNORECASE) for p in NETWORK_PATTERNS]

    for fpath in scripts_dir.rglob("*"):
        if not fpath.is_file():
            continue
        try:
            text = fpath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        for i, line in enumerate(text.split("\n"), 1):
            for pat in compiled:
                if pat.search(line):
                    severity = "HIGH" if not compatibility_mentions_network else "LOW"
                    rel = fpath.relative_to(skill_path)
                    findings.append(
                        {
                            "id": "STRUCT-030",
                            "severity": severity,
                            "layer": 1,
                            "category": "undeclared-network",
                            "message": f"Network access pattern in {rel}:{i} — "
                            + (
                                "not declared in compatibility field."
                                if not compatibility_mentions_network
                                else "declared in compatibility."
                            ),
                            "file": str(rel),
                            "line": i,
                            "remediation": "Add network requirement to compatibility field, "
                            "or remove network access.",
                        }
                    )
                    break  # One finding per line

    return findings


def size_check(skill_path: Path) -> list[dict]:
    """Flag oversized markdown files."""
    findings = []

    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        lines = skill_md.read_text(encoding="utf-8").count("\n")
        if lines > 1000:
            findings.append(
                {
                    "id": "STRUCT-040",
                    "severity": "HIGH",
                    "layer": 1,
                    "category": "oversized-file",
                    "message": f"SKILL.md has {lines} lines (threshold: 1000).",
                    "file": "SKILL.md",
                    "line": None,
                    "remediation": "Move content to references/ to reduce SKILL.md size.",
                }
            )
        elif lines > 500:
            findings.append(
                {
                    "id": "STRUCT-040",
                    "severity": "MEDIUM",
                    "layer": 1,
                    "category": "oversized-file",
                    "message": f"SKILL.md has {lines} lines (threshold: 500).",
                    "file": "SKILL.md",
                    "line": None,
                    "remediation": "Consider moving some content to references/.",
                }
            )

    refs_dir = skill_path / "references"
    if refs_dir.exists():
        for fpath in refs_dir.rglob("*.md"):
            lines = fpath.read_text(encoding="utf-8").count("\n")
            if lines > 2000:
                rel = fpath.relative_to(skill_path)
                findings.append(
                    {
                        "id": "STRUCT-041",
                        "severity": "MEDIUM",
                        "layer": 1,
                        "category": "oversized-file",
                        "message": f"{rel} has {lines} lines (threshold: 2000).",
                        "file": str(rel),
                        "line": None,
                        "remediation": "Split large reference files into smaller focused documents.",
                    }
                )

    return findings


def run_structural_audit(skill_path: str) -> list[dict]:
    """Run all structural checks and return findings."""
    path = Path(skill_path)
    findings = []
    findings.extend(check_frontmatter(path))
    findings.extend(allowed_tools_blast_radius(path))
    findings.extend(file_inventory(path))
    findings.extend(network_inference(path))
    findings.extend(size_check(path))
    return findings


if __name__ == "__main__":
    import json

    if len(sys.argv) != 2:
        print("Usage: structural_audit.py <skill-directory>", file=sys.stderr)
        sys.exit(1)
    results = run_structural_audit(sys.argv[1])
    json.dump(results, sys.stdout, indent=2)
    print()
