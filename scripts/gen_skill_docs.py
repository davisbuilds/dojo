#!/bin/sh
""":"
if command -v python >/dev/null 2>&1; then
    exec python "$0" "$@"
fi
exec python3 "$0" "$@"
":"""
"""Opt-in shared-fragment composition for SKILL.md files.

A skill opts in by placing an include directive in its SKILL.md body:

    <!-- INCLUDE: fragment-name -->

On generation, the directive plus any previously generated block (through the
matching closing marker) is replaced with:

    <!-- INCLUDE: fragment-name -->
    <!-- AUTO-GENERATED from skills/_fragments/fragment-name.md — do not edit -->
    <fragment body>
    <!-- /INCLUDE: fragment-name -->

Generation is deterministic and idempotent: running it twice produces no diff.
Skills with no INCLUDE directive are left byte-for-byte unchanged.

Usage:
    gen_skill_docs.py            # expand all opted-in skills, writing changes
    gen_skill_docs.py --check    # exit non-zero if any opted-in skill is stale
"""

import argparse
import re
import sys
from pathlib import Path

FRAGMENTS_DIRNAME = "_fragments"

# Matches an INCLUDE directive and, optionally, the generated block it owns
# (up to the matching closing marker with the same fragment name).
INCLUDE_RE = re.compile(
    r"<!-- INCLUDE: (?P<name>[a-z0-9][a-z0-9-]*) -->"
    r"(?:.*?<!-- /INCLUDE: (?P=name) -->)?",
    re.DOTALL,
)


def load_fragment(fragments_dir: Path, name: str) -> str:
    path = fragments_dir / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"fragment not found: {path}")
    return path.read_text(encoding="utf-8").strip("\n")


def expand(text: str, fragments_dir: Path) -> str:
    def repl(match: re.Match) -> str:
        name = match.group("name")
        body = load_fragment(fragments_dir, name)
        return (
            f"<!-- INCLUDE: {name} -->\n"
            f"<!-- AUTO-GENERATED from skills/{FRAGMENTS_DIRNAME}/{name}.md — do not edit -->\n"
            f"{body}\n"
            f"<!-- /INCLUDE: {name} -->"
        )

    return INCLUDE_RE.sub(repl, text)


def has_directive(text: str) -> bool:
    return INCLUDE_RE.search(text) is not None


def iter_skill_mds(skills_root: Path):
    for skill_md in sorted(skills_root.glob("*/SKILL.md")):
        yield skill_md


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skills-root", default="skills", help="Path to skills directory (default: skills)")
    parser.add_argument("--check", action="store_true", help="Report drift without writing; exit 1 if stale")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    skills_root = Path(args.skills_root)
    if not skills_root.is_absolute():
        skills_root = (repo_root / skills_root).resolve()
    fragments_dir = skills_root / FRAGMENTS_DIRNAME

    if not skills_root.is_dir():
        print(f"Skills root not found: {skills_root}", file=sys.stderr)
        return 1

    stale: list[str] = []
    written: list[str] = []

    for skill_md in iter_skill_mds(skills_root):
        original = skill_md.read_text(encoding="utf-8")
        if not has_directive(original):
            continue  # not opted in: never touch
        try:
            expanded = expand(original, fragments_dir)
        except FileNotFoundError as exc:
            print(f"ERROR: {skill_md.parent.name}: {exc}", file=sys.stderr)
            return 1

        if expanded == original:
            continue
        if args.check:
            stale.append(skill_md.parent.name)
        else:
            skill_md.write_text(expanded, encoding="utf-8")
            written.append(skill_md.parent.name)

    if args.check:
        if stale:
            print("Stale composed SKILL.md (run scripts/gen_skill_docs.py):", file=sys.stderr)
            for name in stale:
                print(f"  - {name}", file=sys.stderr)
            return 1
        print("All opted-in skills are up to date.")
        return 0

    if written:
        print(f"Regenerated {len(written)} skill(s): {', '.join(written)}")
    else:
        print("No changes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
