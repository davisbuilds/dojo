#!/usr/bin/env python3
"""Check an assembled research prompt for common drafting defects.

Detects empty prompts, unfilled {{slots}}, leftover HTML comments or trailing
harness tags, and potentially unsourced statistics in labeled background blocks.
These are text heuristics, not a research-quality score. A pass says nothing
about question quality, evidence sufficiency, or the truth of seeded claims.
Literal examples can resemble draft debris; inspect a flagged match in context.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SLOT_RE = re.compile(r"\{\{([^}]*)\}\}", re.DOTALL)
HARNESS_TRAILER_RE = re.compile(
    r"(?P<trailer></(?:content|tool_call|tool_result|write|file)>)\s*\Z",
    re.IGNORECASE,
)

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
    checks = [{
        "name": "nonempty_prompt",
        "status": "pass" if text.strip() else "fail",
        "detail": "prompt has content" if text.strip() else "prompt is empty",
    }]

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

    floating = unsourced_magnitudes(text)
    checks.append({
        "name": "seeded_statistics",
        "status": "warn" if floating else "pass",
        "detail": "seeded magnitudes with no retrievable source: "
        f"{', '.join(floating)} — identify each source (name + arXiv/DOI/SSRN/URL) "
        "or drop the number"
        if floating else "no unsourced seeded magnitudes",
    })

    statuses = {c["status"] for c in checks}
    overall = "fail" if "fail" in statuses else "warn" if "warn" in statuses else "pass"
    return {
        "executor": executor,
        "scope": "prompt_hygiene",
        "checks": checks,
        "status": overall,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("file", help="Assembled prompt markdown file")
    parser.add_argument("--executor", choices=["web", "terminal"], default="terminal",
                        help="Executor label only; both use the same hygiene checks (default: terminal)")
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
        print(f"\noverall: {result['status']} (prompt hygiene only)")

    if result["status"] == "fail":
        return 1
    if result["status"] == "warn" and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
