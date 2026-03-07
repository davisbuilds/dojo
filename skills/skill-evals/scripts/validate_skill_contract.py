#!/bin/sh
""":"
if command -v python >/dev/null 2>&1; then
    exec python "$0" "$@"
fi
exec python3 "$0" "$@"
":"""
"""Validate SKILL.md files against SKILL Contract v1."""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class CheckResult:
    status: str  # pass|warn|fail
    required: bool
    message: str


def parse_frontmatter(text: str) -> dict[str, Any] | None:
    match = re.match(r"^---\n(.*?)\n---\n?", text, re.DOTALL)
    if not match:
        return None
    try:
        parsed = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None
    return parsed if isinstance(parsed, dict) else None


def has_heading(text: str, patterns: list[str]) -> bool:
    regex = r"^##+\s+(?:" + "|".join(patterns) + r")\b"
    return re.search(regex, text, re.IGNORECASE | re.MULTILINE) is not None


def has_numbered_steps(text: str) -> bool:
    return re.search(r"^\s*1\.\s+", text, re.MULTILINE) is not None


def description_trigger_ready(description: str) -> bool:
    return re.search(
        r"\b(use when|use this when|use this skill when|use for|should be used when|when the user|triggers on|on-demand via|use when asked|when asked to)\b",
        description,
        re.IGNORECASE,
    ) is not None


def resource_map_present(text: str, skill_dir: Path) -> bool:
    bundled = [d for d in ("scripts", "references", "assets", "commands") if (skill_dir / d).exists()]
    if not bundled:
        return True

    has_resource_heading = has_heading(
        text,
        [
            r"references",
            r"resources",
            r"scripts",
            r"commands",
            r"examples",
            r"template",
            r"reference files",
            r"full compiled document",
        ],
    )
    has_path_mentions = re.search(r"\b(scripts/|references/|assets/|commands/)\b", text) is not None
    return has_resource_heading or has_path_mentions


def evaluate_skill(skill_dir: Path, validate_skill_fn, strict: bool) -> dict[str, Any]:
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    lines = text.count("\n") + 1

    valid, validate_msg = validate_skill_fn(str(skill_dir))
    fm = parse_frontmatter(text)
    description = ""
    if fm and isinstance(fm.get("description"), str):
        description = fm["description"].strip()

    checks: dict[str, CheckResult] = {}

    checks["frontmatter_valid"] = CheckResult(
        status="pass" if valid else "fail",
        required=True,
        message=validate_msg,
    )

    checks["description_trigger_ready"] = CheckResult(
        status="pass" if description and description_trigger_ready(description) else "fail",
        required=True,
        message="Description includes trigger-ready language"
        if description and description_trigger_ready(description)
        else "Description should include trigger language (for example: 'use when', 'triggers on')",
    )

    execution_anchor = has_heading(
        text,
        [
            r"workflow",
            r"core workflow",
            r"default workflow",
            r"process",
            r"core process",
            r"7-step process",
            r"usage",
            r"basic usage",
            r"how to use",
            r"quick start",
            r"commands",
            r"application process",
            r"design thinking",
        ],
    ) or has_numbered_steps(text)

    checks["execution_anchor_present"] = CheckResult(
        status="pass" if execution_anchor else "fail",
        required=True,
        message="Execution anchor present"
        if execution_anchor
        else "Add workflow/process/commands section or numbered execution steps",
    )

    scope_anchor = has_heading(
        text,
        [
            r"when to use",
            r"when to apply",
            r"when to use this skill",
            r"start behavior",
            r"prerequisites?",
            r"scope",
        ],
    )
    checks["scope_anchor_present"] = CheckResult(
        status="pass" if scope_anchor else ("fail" if strict else "warn"),
        required=strict,
        message="Scope anchor present" if scope_anchor else "Add a scope section (When to use / Prerequisites)",
    )

    boundaries_anchor = has_heading(
        text,
        [
            r"boundaries",
            r"when not to use",
            r"not for",
            r"constraints",
            r"anti-patterns",
            r"safety rules",
            r"rules",
            r"what does not qualify",
        ],
    ) or re.search(r"\b(skip this skill|do not use|not for)\b", text, re.IGNORECASE) is not None
    checks["boundaries_anchor_present"] = CheckResult(
        status="pass" if boundaries_anchor else ("fail" if strict else "warn"),
        required=strict,
        message="Boundaries anchor present"
        if boundaries_anchor
        else "Add boundaries/non-goals section (Not for / Constraints)",
    )

    output_anchor = has_heading(
        text,
        [r"output contract", r"output requirements", r"output", r"deliverables", r"summary"],
    )
    checks["output_anchor_present"] = CheckResult(
        status="pass" if output_anchor else ("fail" if strict else "warn"),
        required=strict,
        message="Output anchor present" if output_anchor else "Add output expectations section",
    )

    verification_anchor = has_heading(
        text,
        [
            r"verification",
            r"quality rules",
            r"success criteria",
            r"severity handling",
            r"verification gate",
            r"validation",
        ],
    )
    checks["verification_anchor_present"] = CheckResult(
        status="pass" if verification_anchor else ("fail" if strict else "warn"),
        required=strict,
        message="Verification anchor present"
        if verification_anchor
        else "Add verification/quality criteria section",
    )

    resource_anchor = resource_map_present(text, skill_dir)
    checks["resource_map_present"] = CheckResult(
        status="pass" if resource_anchor else ("fail" if strict else "warn"),
        required=strict,
        message="Resource map present"
        if resource_anchor
        else "Skill bundles resources but SKILL.md does not clearly reference them",
    )

    if lines <= 500:
        context_status = "pass"
        context_msg = f"SKILL.md is within context budget ({lines} lines)"
    elif lines <= 700:
        context_status = "warn"
        context_msg = f"SKILL.md is long ({lines} lines); consider splitting references"
    else:
        context_status = "warn" if not strict else "fail"
        context_msg = f"SKILL.md is very long ({lines} lines); should be decomposed"

    checks["context_budget"] = CheckResult(
        status=context_status,
        required=strict,
        message=context_msg,
    )

    required_failures = [name for name, result in checks.items() if result.required and result.status == "fail"]
    warns = [name for name, result in checks.items() if result.status == "warn"]
    optional_failures = [
        name
        for name, result in checks.items()
        if (not result.required) and result.status == "fail"
    ]

    if required_failures:
        overall = "fail"
    elif warns or optional_failures:
        overall = "warn"
    else:
        overall = "pass"

    return {
        "skill": skill_dir.name,
        "path": str(skill_md),
        "status": overall,
        "line_count": lines,
        "required_failures": required_failures,
        "warnings": warns,
        "optional_failures": optional_failures,
        "checks": {
            name: {
                "status": result.status,
                "required": result.required,
                "message": result.message,
            }
            for name, result in checks.items()
        },
    }


def render_markdown(results: list[dict[str, Any]], strict: bool) -> str:
    total = len(results)
    passes = sum(1 for r in results if r["status"] == "pass")
    warns = sum(1 for r in results if r["status"] == "warn")
    fails = sum(1 for r in results if r["status"] == "fail")

    out: list[str] = []
    out.append("# SKILL Contract Application Report")
    out.append("")
    out.append(f"Date: 2026-03-07")
    out.append(f"Mode: {'strict' if strict else 'default'}")
    out.append("")
    out.append("## Summary")
    out.append("")
    out.append(f"- Total skills: {total}")
    out.append(f"- Pass: {passes}")
    out.append(f"- Warn: {warns}")
    out.append(f"- Fail: {fails}")
    out.append("")
    out.append("## Per-Skill Status")
    out.append("")
    out.append("| Skill | Status | Required Failures | Warnings | Lines |")
    out.append("|---|---|---:|---:|---:|")
    for row in sorted(results, key=lambda item: (item["status"], item["skill"])):
        out.append(
            f"| {row['skill']} | {row['status']} | {len(row['required_failures'])} | {len(row['warnings'])} | {row['line_count']} |"
        )

    issues = [r for r in results if r["status"] != "pass"]
    if issues:
        out.append("")
        out.append("## Required Fixes")
        out.append("")
        for row in sorted(issues, key=lambda item: (item["status"], item["skill"])):
            if not row["required_failures"]:
                continue
            out.append(f"### {row['skill']}")
            for key in row["required_failures"]:
                out.append(f"- `{key}`: {row['checks'][key]['message']}")
            out.append("")

        out.append("## Recommended Improvements")
        out.append("")
        for row in sorted(issues, key=lambda item: item["skill"]):
            if not row["warnings"]:
                continue
            out.append(f"### {row['skill']}")
            for key in row["warnings"]:
                out.append(f"- `{key}`: {row['checks'][key]['message']}")
            out.append("")

    return "\n".join(out).rstrip() + "\n"


def collect_skills(skills_root: Path, selected: set[str] | None) -> list[Path]:
    skills = [path.parent for path in sorted(skills_root.glob("*/SKILL.md"))]
    if selected:
        return [skill for skill in skills if skill.name in selected]
    return skills


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate SKILL.md files against SKILL Contract v1")
    parser.add_argument(
        "--skills-root",
        default="skills",
        help="Path to skills root directory (default: skills)",
    )
    parser.add_argument(
        "--skills",
        help="Comma-separated subset of skills to evaluate",
    )
    parser.add_argument("--strict", action="store_true", help="Treat recommended checks as required")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    parser.add_argument("--markdown", help="Write markdown report to this path")
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[3]

    quick_validate_path = repo_root / "skills" / "skill-creator" / "scripts"
    sys.path.insert(0, str(quick_validate_path))
    try:
        from quick_validate import validate_skill  # type: ignore
    except Exception as exc:  # pragma: no cover
        print(f"Failed to import validate_skill: {exc}", file=sys.stderr)
        return 1

    skills_root = Path(args.skills_root)
    if not skills_root.is_absolute():
        skills_root = (repo_root / skills_root).resolve()

    if not skills_root.is_dir():
        print(f"Skills root not found: {skills_root}", file=sys.stderr)
        return 1

    selected = None
    if args.skills:
        selected = {name.strip() for name in args.skills.split(",") if name.strip()}

    skill_dirs = collect_skills(skills_root, selected)
    if not skill_dirs:
        print("No skills selected.", file=sys.stderr)
        return 1

    results = [evaluate_skill(skill_dir, validate_skill, args.strict) for skill_dir in skill_dirs]

    summary = {
        "total": len(results),
        "pass": sum(1 for item in results if item["status"] == "pass"),
        "warn": sum(1 for item in results if item["status"] == "warn"),
        "fail": sum(1 for item in results if item["status"] == "fail"),
        "strict": args.strict,
    }

    payload = {
        "summary": summary,
        "skills": results,
    }

    if args.markdown:
        report = render_markdown(results, args.strict)
        output_path = Path(args.markdown)
        if not output_path.is_absolute():
            output_path = (repo_root / output_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(
            "Summary: "
            f"total={summary['total']} pass={summary['pass']} warn={summary['warn']} fail={summary['fail']}"
        )
        for item in results:
            print(
                f"{item['status'].upper():4} {item['skill']} "
                f"(required_failures={len(item['required_failures'])}, warnings={len(item['warnings'])})"
            )

    return 1 if summary["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
