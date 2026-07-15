#!/usr/bin/env python3
"""Bump a skill's SemVer version and prepend a CHANGELOG heading.

Updates the top-level `version` field in a skill's SKILL.md frontmatter and
prepends a matching `## <version> - <date>` heading to its CHANGELOG.md
(created if absent), so the release-version check in check_skill_versions.py
passes without hand-editing two files.

Examples:
    python3 skills/skill-evals/scripts/bump_skill_version.py skills/api-design patch
    python3 skills/skill-evals/scripts/bump_skill_version.py skills/api-design minor -m "Add pagination guidance."
    python3 skills/skill-evals/scripts/bump_skill_version.py skills/api-design --set 2.0.0
"""

from __future__ import annotations

import argparse
import datetime as _dt
import importlib.util
import re
import sys
from pathlib import Path

# Reuse the canonical SemVer parser + regexes from the version checker so bump
# arithmetic and heading detection stay identical to what CI enforces.
_CHECK_PATH = Path(__file__).with_name("check_skill_versions.py")
_spec = importlib.util.spec_from_file_location("check_skill_versions", _CHECK_PATH)
_check = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
# Register before exec so the module's dataclasses (under `from __future__ import
# annotations`) can resolve their own field types via sys.modules.
sys.modules[_spec.name] = _check
_spec.loader.exec_module(_check)

SemVer = _check.SemVer
FRONTMATTER_RE = _check.FRONTMATTER_RE
CHANGELOG_HEADING_RE = _check.CHANGELOG_HEADING_RE

_VERSION_LINE_RE = re.compile(r"^(version:[ \t]*)(\S.*?)[ \t]*$", re.MULTILINE)


class BumpError(Exception):
    """Raised on any user-facing bump failure (missing file, non-increasing version)."""


def bump_version(current: str, part: str) -> str:
    """Return `current` with `part` (major|minor|patch) incremented, prerelease dropped."""
    sv = SemVer.parse(current)  # raises ValueError on invalid input
    if part == "major":
        return f"{sv.major + 1}.0.0"
    if part == "minor":
        return f"{sv.major}.{sv.minor + 1}.0"
    if part == "patch":
        return f"{sv.major}.{sv.minor}.{sv.patch + 1}"
    raise ValueError(f"unknown bump part: {part!r} (expected major, minor, or patch)")


def _read_current_version(skill_md: Path) -> str:
    text = skill_md.read_text(encoding="utf-8")
    fm = FRONTMATTER_RE.match(text)
    if not fm:
        raise BumpError(f"{skill_md} has no YAML frontmatter")
    match = _VERSION_LINE_RE.search(fm.group(1))
    if not match:
        raise BumpError(f"{skill_md} frontmatter has no `version` field")
    return match.group(2)


def _replace_version_line(skill_md: Path, new_version: str) -> None:
    """Rewrite only the frontmatter `version:` line, leaving everything else byte-identical."""
    text = skill_md.read_text(encoding="utf-8")
    fm = FRONTMATTER_RE.match(text)
    assert fm is not None  # _read_current_version already validated
    fm_body = fm.group(1)
    new_fm_body, count = _VERSION_LINE_RE.subn(rf"\g<1>{new_version}", fm_body, count=1)
    if count != 1:
        raise BumpError(f"{skill_md} frontmatter has no `version` field")
    skill_md.write_text(text[: fm.start(1)] + new_fm_body + text[fm.end(1) :], encoding="utf-8")


def _changelog_block(version: str, date: str, entry: str | None) -> str:
    bullet = entry.strip() if entry and entry.strip() else f"Release {version}."
    return f"## {version} - {date}\n\n- {bullet}\n"


def _prepend_changelog(changelog: Path, version: str, date: str, entry: str | None) -> None:
    existing = changelog.read_text(encoding="utf-8") if changelog.exists() else ""
    if CHANGELOG_HEADING_RE.pattern and re.search(
        CHANGELOG_HEADING_RE.pattern.format(version=re.escape(version)), existing, re.MULTILINE
    ):
        raise BumpError(f"{changelog} already has a heading for {version}")
    block = _changelog_block(version, date, entry)
    changelog.write_text(block + ("\n" + existing if existing.strip() else ""), encoding="utf-8")


def apply_bump(
    skill_dir: Path,
    part: str | None = None,
    set_version: str | None = None,
    entry: str | None = None,
    date: str | None = None,
    dry_run: bool = False,
) -> tuple[str, str]:
    """Bump one skill. Returns (old_version, new_version). Writes unless dry_run."""
    if (part is None) == (set_version is None):
        raise ValueError("provide exactly one of `part` or `set_version`")

    skill_md = Path(skill_dir) / "SKILL.md"
    if not skill_md.is_file():
        raise BumpError(f"no SKILL.md found in {skill_dir}")

    old_version = _read_current_version(skill_md)
    old_sv = SemVer.parse(old_version)

    if set_version is not None:
        try:
            new_sv = SemVer.parse(set_version)
        except ValueError as exc:
            raise BumpError(str(exc)) from exc
        if not old_sv < new_sv:
            raise BumpError(f"--set {set_version} is not greater than current {old_version}")
        new_version = set_version
    else:
        new_version = bump_version(old_version, part)

    if date is None:
        date = _dt.date.today().isoformat()

    if not dry_run:
        _prepend_changelog(Path(skill_dir) / "CHANGELOG.md", new_version, date, entry)
        _replace_version_line(skill_md, new_version)

    return old_version, new_version


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("skill", help="Path to the skill directory (contains SKILL.md)")
    parser.add_argument(
        "part",
        nargs="?",
        choices=["major", "minor", "patch"],
        help="Which SemVer part to bump (omit when using --set)",
    )
    parser.add_argument("--set", dest="set_version", help="Set an explicit version instead of bumping")
    parser.add_argument("-m", "--message", dest="entry", help="Changelog bullet text for the new entry")
    parser.add_argument("--date", help="Override the changelog date (default: today, ISO 8601)")
    parser.add_argument("--dry-run", action="store_true", help="Print the change without writing")
    args = parser.parse_args(argv)

    if (args.part is None) == (args.set_version is None):
        parser.error("provide exactly one of a bump part (major|minor|patch) or --set VERSION")

    try:
        old, new = apply_bump(
            Path(args.skill),
            part=args.part,
            set_version=args.set_version,
            entry=args.entry,
            date=args.date,
            dry_run=args.dry_run,
        )
    except (BumpError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    prefix = "would bump" if args.dry_run else "bumped"
    print(f"{prefix} {args.skill}: {old} -> {new}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
