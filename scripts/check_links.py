#!/usr/bin/env python3
"""Fail on references that point at things which no longer exist.

Deleting a skill or a reference file is easy; finding everything that pointed at
it is not. Two cleanups on 2026-07-31 each left stale pointers behind — a
retirement left sibling sections naming deleted skills across sixteen files, and
a reference cut left three separate indexes listing files that were gone. Both
were caught by hand. This makes it mechanical.

Three checks, all conservative — they only fire on references with an
unambiguous target:

1. Relative markdown links (`[text](./references/foo.md)`) resolve on disk.
2. `skills/<name>/` paths name a skill that exists.
3. Skill names in a `## Sibling skills` section name a skill that exists.

Usage:  python3 scripts/check_links.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "skills"

# Docs that describe current state. Dated artifacts (plans, specs, designs,
# research, replay results) are deliberately excluded: they record what was true
# when written, and rewriting them to match today would destroy the record.
LIVING_DOCS = [
    REPO_ROOT / "README.md",
    REPO_ROOT / "docs" / "system",
    REPO_ROOT / "docs" / "project",
]

MD_LINK = re.compile(r"\[[^\]]*\]\((?!https?://|mailto:|#)([^)\s]+)\)")
SKILL_PATH = re.compile(r"(?<!/)\bskills/([a-z0-9][a-z0-9-]*)/")
# Sibling entries are list heads: "- `name` — description". Matching only that
# position keeps model names and inline mentions out of the check.
SIBLING_ENTRY = re.compile(r"^\s*[-*]\s+`([a-z0-9][a-z0-9-]{2,})`", re.M)
SIBLING_HEADING = re.compile(r"^#{1,4}\s+Sibling skills\s*$", re.M)
FENCE = re.compile(r"^```.*?^```", re.M | re.S)

# Documentation placeholders that stand in for "whatever skill you are working
# on". Kept explicit and small rather than loosening the path check, which would
# stop catching the real thing.
PLACEHOLDERS = {"my-skill", "your-skill", "example-skill", "skill-name", "some-skill"}

# docs/archive/ is gitignored: completed plans and superseded analyses are kept
# locally, not published. Living docs legitimately cite them for the local
# reader, so those links resolve on the author's machine and nowhere else.
# Checking them would fail every CI run for a reason that is not a defect.
LOCAL_ONLY_PREFIXES = ("docs/archive/",)


def strip_fences(text: str) -> str:
    """Drop fenced code blocks.

    They routinely illustrate hypothetical skills with placeholder filenames --
    skill-creator shows a PDF skill linking to FORMS.md and REFERENCE.md that
    were never meant to exist -- so checking inside them produces noise only.
    """
    return FENCE.sub("", text)


def known_skills(skills_root: Path) -> set[str]:
    return {p.parent.name for p in skills_root.glob("*/SKILL.md")}


def markdown_files(skills_root: Path, living_docs: list[Path]) -> list[Path]:
    files: list[Path] = sorted(skills_root.glob("**/*.md"))
    # A skill's own evals/replay-results-*.md is a dated record, like the docs above.
    files = [f for f in files if not f.name.startswith("replay-results-")]
    for target in living_docs:
        if target.is_dir():
            files.extend(sorted(target.glob("**/*.md")))
        elif target.is_file():
            files.append(target)
    return files


def sibling_section(text: str) -> str:
    """Return the text of the Sibling skills section, or '' if absent."""
    m = SIBLING_HEADING.search(text)
    if not m:
        return ""
    rest = text[m.end() :]
    nxt = re.search(r"^#{1,4}\s+\S", rest, re.M)
    return rest[: nxt.start()] if nxt else rest


def check(skills_root: Path = SKILLS_ROOT, living_docs: list[Path] | None = None) -> list[str]:
    living = LIVING_DOCS if living_docs is None else living_docs
    skills = known_skills(skills_root)
    problems: list[str] = []

    for path in markdown_files(skills_root, living):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        rel = path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path
        # assets/ holds templates whose links are placeholders by design.
        if "assets" in path.parts:
            continue
        text = strip_fences(text)

        for link in MD_LINK.findall(text):
            target = (path.parent / link.split("#", 1)[0]).resolve()
            try:
                as_rel = target.relative_to(REPO_ROOT).as_posix()
            except ValueError:
                as_rel = ""
            if as_rel.startswith(LOCAL_ONLY_PREFIXES):
                continue
            if not target.exists():
                problems.append(f"{rel}: broken link -> {link}")

        for name in set(SKILL_PATH.findall(text)):
            if name not in skills and name not in PLACEHOLDERS:
                problems.append(f"{rel}: references skills/{name}/ which does not exist")

        for name in set(SIBLING_ENTRY.findall(sibling_section(text))):
            if name not in skills:
                problems.append(f"{rel}: sibling section names `{name}`, which is not a skill")

    return sorted(set(problems))


def main() -> int:
    problems = check()
    if problems:
        print(f"Link check failed ({len(problems)} problems):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"Link check passed ({len(known_skills(SKILLS_ROOT))} skills).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
