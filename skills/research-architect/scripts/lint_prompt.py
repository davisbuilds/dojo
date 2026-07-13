#!/usr/bin/env python3
"""Deterministic stage-4 lint for assembled research prompts.

Checks the structural invariants the research-architect skeleton requires:
instruction budget per executor, no unfilled {{slots}}, no leftover drafting
comments, and the presence of the required blocks (do-not list, degradation
order, rubric, summary block, self-report).

Instruction counting is a documented approximation: each occurrence of an
imperative marker (must / never / always / do not / don't) and each bullet that
starts with a common imperative verb counts as one instruction. Judgment checks
(requirements checkable from report text, do-nots being topic-specific) stay
with the drafting session.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

BUDGETS = {"web": 40, "terminal": 60}
WARN_FRACTION = 0.9

INSTRUCTION_RE = re.compile(r"\b(?:must|never|always|do not|don't)\b", re.IGNORECASE)
BULLET_RE = re.compile(r"^\s*(?:[-*+] |\d+[.)]\s+)([A-Za-z][A-Za-z'-]*)\b", re.MULTILINE)
SLOT_RE = re.compile(r"\{\{([^}]*)\}\}", re.DOTALL)
HARNESS_TRAILER_RE = re.compile(
    r"(?P<trailer></(?:content|tool_call|tool_result|write|file)>)\s*\Z",
    re.IGNORECASE,
)
SUMMARY_TOKENS = ("key_findings", "citations", "confidence_gaps", "next_queries")

# Deliberately curated rather than pretending to parse English grammar. These
# are common instruction-leading verbs in assembled research prompts.
IMPERATIVE_VERBS = {
    "actively", "add", "align", "apply", "ask", "attack", "avoid", "check",
    "cite", "classify", "clone", "close", "compare", "confirm", "cover",
    "demand", "deliver", "describe", "distinguish", "document", "end",
    "explain", "fetch", "flag", "focus", "follow", "grade", "identify",
    "include", "inspect", "label", "lead", "list", "mark", "name", "note",
    "prefer", "present", "prioritize", "provide", "record", "report",
    "retain", "say", "score", "search", "separate", "show", "state", "strip",
    "summarize", "tag", "test", "treat", "use", "verify", "write",
}

REQUIRED_BLOCKS = [
    ("do_not_list", re.compile(r"do not \(|do-not list", re.IGNORECASE),
     "A7 do-not list ('Do NOT (known failure modes...)')"),
    ("degradation_order", re.compile(r"degradation order", re.IGNORECASE),
     "A8 degradation order"),
    ("rubric_present", re.compile(r"acceptance criteria|rubric", re.IGNORECASE),
     "A9 shipped rubric / acceptance criteria"),
    ("self_report", re.compile(r"self-report", re.IGNORECASE),
     "A10 self-report"),
]


def count_instructions(text: str) -> int:
    marker_count = len(INSTRUCTION_RE.findall(text))
    bullet_count = 0
    for match in BULLET_RE.finditer(text):
        line_end = text.find("\n", match.start())
        line = text[match.start():line_end if line_end >= 0 else len(text)]
        if INSTRUCTION_RE.search(line):
            continue
        if match.group(1).lower() in IMPERATIVE_VERBS:
            bullet_count += 1
    return marker_count + bullet_count


def evaluate(text: str, executor: str) -> dict:
    checks = []

    slots = [match.split()[0] if (match := m.group(1).strip()) else "(unnamed)"
             for m in SLOT_RE.finditer(text)]
    checks.append({
        "name": "unfilled_slots",
        "status": "fail" if slots else "pass",
        "detail": f"unfilled slots: {', '.join(slots)}" if slots else "no unfilled slots",
    })

    has_comments = "<!--" in text
    checks.append({
        "name": "drafting_comments",
        "status": "fail" if has_comments else "pass",
        "detail": "HTML drafting comments remain — delete before shipping"
        if has_comments else "no drafting comments",
    })

    harness_trailer = HARNESS_TRAILER_RE.search(text)
    checks.append({
        "name": "harness_debris",
        "status": "fail" if harness_trailer else "pass",
        "detail": f"trailing harness debris: {harness_trailer.group('trailer')}"
        if harness_trailer else "no trailing harness debris",
    })

    budget = BUDGETS[executor]
    count = count_instructions(text)
    if count > budget:
        status = "fail"
    elif count >= WARN_FRACTION * budget:
        status = "warn"
    else:
        status = "pass"
    checks.append({
        "name": "instruction_budget",
        "status": status,
        "detail": f"{count} instructions vs budget {budget} ({executor})",
    })

    for name, pattern, label in REQUIRED_BLOCKS:
        present = bool(pattern.search(text))
        checks.append({
            "name": name,
            "status": "pass" if present else "fail",
            "detail": f"{label} {'present' if present else 'missing'}",
        })

    missing_tokens = [t for t in SUMMARY_TOKENS if t not in text]
    checks.append({
        "name": "summary_block",
        "status": "fail" if missing_tokens else "pass",
        "detail": f"summary block missing tokens: {', '.join(missing_tokens)}"
        if missing_tokens else "summary block tokens present",
    })

    statuses = {c["status"] for c in checks}
    overall = "fail" if "fail" in statuses else "warn" if "warn" in statuses else "pass"
    return {
        "executor": executor,
        "instruction_count": count,
        "budget": budget,
        "checks": checks,
        "status": overall,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("file", help="Assembled prompt markdown file")
    parser.add_argument("--executor", choices=sorted(BUDGETS), default="terminal",
                        help="Budget profile (default: terminal)")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--strict", action="store_true",
                        help="Treat warnings as failures")
    args = parser.parse_args(argv)

    path = Path(args.file)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot read {path}: {exc}", file=sys.stderr)
        return 2

    result = evaluate(text, executor=args.executor)
    result["file"] = str(path)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for c in result["checks"]:
            print(f"[{c['status'].upper():4}] {c['name']} — {c['detail']}")
        print(f"\noverall: {result['status']} "
              f"({result['instruction_count']}/{result['budget']} instructions)")

    if result["status"] == "fail":
        return 1
    if result["status"] == "warn" and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
