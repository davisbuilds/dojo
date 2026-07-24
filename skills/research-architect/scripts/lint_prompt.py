#!/usr/bin/env python3
"""Deterministic stage-4 lint for assembled research prompts.

Checks the structural invariants the research-architect skeleton requires:
instruction budget per executor, no unfilled {{slots}}, no leftover drafting
comments, the presence of the required blocks (do-not list, degradation order,
rubric, summary block, self-report), and no unsourced statistics seeded into the
background material.

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

# A seeded statistic with no retrievable source is an attractor for fabricated
# corroboration: the executor "confirms" it by inventing a citation that matches
# the number. Scoped to the seed/background region, because numbers the report
# is asked to *produce* are not seeds.
SEED_BLOCK_START_RE = re.compile(r"^\s*\**\s*(?:seed sources|background)", re.IGNORECASE)
SEED_BLOCK_END_RE = re.compile(r"^\s*(?:\*\*|#)")
SEED_ENTRY_SPLIT_RE = re.compile(r"\n(?=\s*[-*+] )")
MAGNITUDE_RE = re.compile(
    r"""\b\d{1,3}(?:,\d{3})+\b            # 1,234,567
      | \b\d+(?:\.\d+)?\s*%               # 43%
      | \b\d+(?:\.\d+)?\s*(?:[KMB]\b|thousand|million|billion|trillion)
      | \b\d{3,}(?:\.\d+)?\b              # bare 3+ digit magnitude
    """,
    re.VERBOSE | re.IGNORECASE,
)
IDENTIFIER_RE = re.compile(
    r"https?://|arxiv|doi[:\s/]|ssrn|pubmed|nber|isbn|github\.com|\b\w+/\w+\.(?:md|py|ts|go)\b",
    re.IGNORECASE,
)

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


def seed_block(text: str) -> str:
    """Return the seed-sources / background region, or '' when absent."""
    lines = text.splitlines()
    collected: list[str] = []
    inside = False
    for line in lines:
        if inside:
            if SEED_BLOCK_END_RE.match(line) and not SEED_BLOCK_START_RE.match(line):
                inside = False
                continue
            collected.append(line)
        elif SEED_BLOCK_START_RE.match(line):
            inside = True
            collected.append(line)
    return "\n".join(collected)


def unsourced_magnitudes(text: str) -> list[str]:
    """Magnitudes seeded without a retrievable identifier, in document order."""
    found: list[str] = []
    for entry in SEED_ENTRY_SPLIT_RE.split(seed_block(text)):
        if IDENTIFIER_RE.search(entry):
            continue
        for match in MAGNITUDE_RE.finditer(entry):
            magnitude = match.group(0).strip()
            if magnitude not in found:
                found.append(magnitude)
    return found


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

    floating = unsourced_magnitudes(text)
    checks.append({
        "name": "seeded_statistics",
        "status": "warn" if floating else "pass",
        "detail": "seeded magnitudes with no retrievable source: "
        f"{', '.join(floating)} — identify each source (name + arXiv/DOI/SSRN/URL) "
        "or drop the number"
        if floating else "no unsourced seeded magnitudes",
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
