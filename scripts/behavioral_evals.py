#!/bin/sh
""":"
if command -v python >/dev/null 2>&1; then
    exec python "$0" "$@"
fi
exec python3 "$0" "$@"
":"""
"""Opt-in behavioral trigger evals: does a REAL agent route a trigger correctly?

The deterministic lexical evals (`run_trigger_evals.py --from-triggers`) check
that a declared trigger *scores* highest for its skill. This goes one step
further and asks an actual local agent which skill it would pick for each
trigger phrase, then checks that choice against the declared owner.

This is **opt-in and never runs in CI**: it requires `DOJO_BEHAVIORAL_EVALS=1`
and a local agent command (non-deterministic, may cost tokens). The agent is
invoked via `DOJO_BEHAVIORAL_AGENT` (default: `claude -p`), receiving the prompt
on stdin and printing its answer to stdout.

Usage:
    DOJO_BEHAVIORAL_EVALS=1 behavioral_evals.py          # run against declared triggers
    DOJO_BEHAVIORAL_EVALS=1 behavioral_evals.py --json
"""

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


def parse_frontmatter(skill_md: Path) -> dict:
    text = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n?", text, re.DOTALL)
    if not match:
        return {}
    try:
        parsed = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def build_catalog(skills_root: Path) -> list[dict]:
    catalog = []
    for skill_md in sorted(skills_root.glob("*/SKILL.md")):
        fm = parse_frontmatter(skill_md)
        name = fm.get("name") or skill_md.parent.name
        desc = fm.get("description", "")
        triggers = fm.get("triggers", []) if isinstance(fm.get("triggers"), list) else []
        catalog.append({"name": name, "description": desc, "triggers": triggers})
    return catalog


def build_cases(catalog: list[dict]) -> list[dict]:
    cases = []
    for skill in catalog:
        for trigger in skill["triggers"]:
            if isinstance(trigger, str) and trigger.strip():
                cases.append({"skill": skill["name"], "trigger": trigger.strip()})
    return cases


def build_prompt(catalog: list[dict], request: str) -> str:
    lines = [
        "You are routing a user request to exactly one skill.",
        "Available skills (name: description):",
    ]
    for skill in catalog:
        lines.append(f"- {skill['name']}: {skill['description']}")
    lines += [
        "",
        f'User request: "{request}"',
        "",
        "Reply with ONLY the single best skill name, nothing else.",
    ]
    return "\n".join(lines)


def parse_response(text: str, valid_names: list[str]) -> str | None:
    """Extract the chosen skill name from a model reply, tolerant of extra prose."""
    lowered = text.lower()
    # Prefer the longest matching name to avoid substring collisions.
    matches = [n for n in valid_names if re.search(rf"\b{re.escape(n.lower())}\b", lowered)]
    if not matches:
        return None
    return max(matches, key=len)


def default_runner(prompt: str) -> str:
    cmd = shlex.split(os.environ.get("DOJO_BEHAVIORAL_AGENT", "claude -p"))
    proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"agent command failed ({' '.join(cmd)}): {proc.stderr.strip()}")
    return proc.stdout.strip()


def run_evals(catalog: list[dict], runner) -> dict:
    valid = [s["name"] for s in catalog]
    cases = build_cases(catalog)
    results = []
    for case in cases:
        reply = runner(build_prompt(catalog, case["trigger"]))
        chosen = parse_response(reply, valid)
        results.append(
            {
                "skill": case["skill"],
                "trigger": case["trigger"],
                "chosen": chosen,
                "passed": chosen == case["skill"],
            }
        )
    passed = sum(1 for r in results if r["passed"])
    return {
        "summary": {"cases": len(results), "passed": passed, "failed": len(results) - passed},
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skills-root", default="skills", help="Path to skills directory (default: skills)")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args()

    if os.environ.get("DOJO_BEHAVIORAL_EVALS") != "1":
        print(
            "Behavioral evals are opt-in. Set DOJO_BEHAVIORAL_EVALS=1 to run "
            "(uses a local agent; never runs in CI).",
            file=sys.stderr,
        )
        return 0

    skills_root = Path(args.skills_root)
    if not skills_root.is_absolute():
        skills_root = (REPO_ROOT / skills_root).resolve()

    catalog = build_catalog(skills_root)
    cases = build_cases(catalog)
    if not cases:
        if args.json:
            print(json.dumps({"summary": {"cases": 0, "passed": 0, "failed": 0}, "results": []}, indent=2))
        else:
            print("No skills declare `triggers:` — nothing to evaluate.")
        return 0

    try:
        report = run_evals(catalog, default_runner)
    except (RuntimeError, FileNotFoundError) as exc:
        print(f"Behavioral evals could not run: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        s = report["summary"]
        print(f"Behavioral evals: {s['passed']}/{s['cases']} routed correctly ({s['failed']} failed)")
        for r in report["results"]:
            if not r["passed"]:
                print(f"  MISROUTE  {r['trigger']!r}: expected {r['skill']}, agent chose {r['chosen']}")
    return 1 if report["summary"]["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
