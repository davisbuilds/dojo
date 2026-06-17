#!/bin/sh
""":"
if command -v python >/dev/null 2>&1; then
    exec python "$0" "$@"
fi
exec python3 "$0" "$@"
":"""
"""Deterministic AI-slop prose linter for authored Markdown.

Flags well-known LLM-slop tells (filler openers, cliché metaphors, hype verbs)
in skill prose and core docs. High-precision by design — it is a CI gate, so
every pattern is one that is almost never legitimate in technical writing.

Complements the `design-critique` skill, which catches *visual* slop; this
catches *prose* slop.

Usage:
    slop_scan.py             # scan the default set; exit 1 on any hit
    slop_scan.py PATH ...    # scan specific files instead
    slop_scan.py --list      # print the patterns and exit
"""

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# (label, pattern) — patterns are matched case-insensitively. Keep these
# high-precision: a hit should almost always be slop, never a false positive.
PATTERNS: list[tuple[str, str]] = [
    ("filler-opener", r"it'?s important to note"),
    ("filler-opener", r"it is worth noting"),
    ("filler-opener", r"needless to say"),
    ("filler-opener", r"at the end of the day,"),
    ("filler-opener", r"in conclusion,"),
    ("hype-temporal", r"in today'?s (fast-paced|digital|modern|ever-changing) \w+"),
    ("hype-temporal", r"ever-(evolving|changing) (world|landscape|realm)"),
    ("cliche-metaphor", r"\b(rich )?tapestry\b"),
    ("cliche-metaphor", r"embark on (a|this|your) journey"),
    ("cliche-metaphor", r"navigating the (complex|ever-changing|intricate)? ?(world|landscape|realm)"),
    ("cliche-metaphor", r"the realm of"),
    ("cliche-metaphor", r"a testament to"),
    ("hype-verb", r"(unleash|unlock|harness) the power of"),
    ("hype-verb", r"\belevate your\b"),
    ("hype-verb", r"\bsupercharge\b"),
    ("hype-verb", r"\bgame[- ]changer\b"),
    ("hype-verb", r"\bdelve into\b"),
    ("hype-filler", r"plays a (crucial|pivotal|vital|key) role"),
    ("hype-filler", r"look no further"),
    ("hype-filler", r"when it comes to the world of"),
]

COMPILED = [(label, re.compile(pat, re.IGNORECASE)) for label, pat in PATTERNS]

DEFAULT_GLOBS = [
    "skills/*/SKILL.md",
    "rules/*.md",
    "README.md",
    "docs/system/*.md",
]


def scan_text(text: str) -> list[tuple[int, str, str]]:
    findings = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for label, rx in COMPILED:
            m = rx.search(line)
            if m:
                findings.append((lineno, label, m.group(0)))
    return findings


def default_files() -> list[Path]:
    files: list[Path] = []
    for pattern in DEFAULT_GLOBS:
        files.extend(sorted(REPO_ROOT.glob(pattern)))
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="*", help="Files to scan (default: skill prose + core docs)")
    parser.add_argument("--list", action="store_true", help="Print patterns and exit")
    parser.add_argument("--warn-only", action="store_true", help="Report hits but exit 0")
    args = parser.parse_args()

    if args.list:
        for label, pat in PATTERNS:
            print(f"{label:16} {pat}")
        return 0

    files = [Path(p) for p in args.paths] if args.paths else default_files()

    total = 0
    for path in files:
        if not path.exists():
            continue
        for lineno, label, match in scan_text(path.read_text(encoding="utf-8")):
            try:
                shown = path.relative_to(REPO_ROOT)
            except ValueError:
                shown = path
            print(f"{shown}:{lineno}: [{label}] {match!r}")
            total += 1

    if total:
        print(f"\n{total} slop hit(s) found.", file=sys.stderr)
        return 0 if args.warn_only else 1
    print("No slop detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
