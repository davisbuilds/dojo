#!/usr/bin/env python3
"""Bump a skill's SemVer version and add a CHANGELOG heading.

Updates the top-level `version` field in a skill's SKILL.md frontmatter and
adds a matching `## <version> - <date>` heading to its CHANGELOG.md (created if
absent), placing it below an optional H1 title, so the release-version check in
check_skill_versions.py
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

# Rewrites only the scalar, preserving optional quotes and any inline comment.
_VERSION_LINE_RE = re.compile(
    r"""^(?P<pre>version:[ \t]*)(?P<q>["']?)(?P<val>[^"'#\n]*?)(?P=q)(?P<post>[ \t]*(?:\#.*)?)$""",
    re.MULTILINE,
)


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
    # Parse via YAML (matching check_skill_versions.py) so quoted scalars and
    # inline comments resolve to the same value CI reads.
    version = _check.current_skill_version(skill_md)
    if version is None:
        raise BumpError(f"{skill_md} frontmatter has no string `version` field")
    return version


def _replace_version_line(skill_md: Path, new_version: str) -> None:
    """Rewrite only the frontmatter `version:` scalar, preserving quotes, any inline
    comment, and every other byte of the file."""
    text = skill_md.read_text(encoding="utf-8")
    fm = FRONTMATTER_RE.match(text)
    if not fm:
        raise BumpError(f"{skill_md} has no YAML frontmatter")
    fm_body = fm.group(1)

    def _sub(m: re.Match[str]) -> str:
        return f"{m.group('pre')}{m.group('q')}{new_version}{m.group('q')}{m.group('post')}"

    new_fm_body, count = _VERSION_LINE_RE.subn(_sub, fm_body, count=1)
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
    title, separator, entries = existing.partition("\n")
    if title.startswith("# "):
        prefix = title + separator
        entries = entries.lstrip("\n")
        changelog.write_text(prefix + "\n" + block + ("\n" + entries if entries else ""), encoding="utf-8")
        return
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


def _load_manifest_generator(repo_root: Path):
    """Import the repo's manifest generator, or None if this checkout lacks it."""
    gen_path = repo_root / "scripts" / "generate_skills_manifest.py"
    if not gen_path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("generate_skills_manifest", gen_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def regenerate_manifest(skill_dir: Path) -> Path | None:
    """Rebuild skills.json (and cascade the catalog) for `skill_dir`'s checkout.

    This script writes SKILL.md directly, so the post-tool-use manifest-regen
    hook never fires; regenerating here closes the "forgot to regen -> CI --check
    fails" gap. Returns the manifest path when it regenerates, or None when the
    skill is not inside a dojo checkout with the generator present (e.g. a global
    install), so a bump there degrades to a printed reminder rather than failing.
    """
    skill_dir = Path(skill_dir).resolve()
    if skill_dir.parent.name != "skills":
        return None
    repo_root = skill_dir.parent.parent
    generator = _load_manifest_generator(repo_root)
    if generator is None:
        return None
    manifest_path = repo_root / "skills.json"
    catalog_path = repo_root / "docs" / "catalog" / "index.html"
    # This is a recognized dojo checkout (skills/ parent + generator present), so
    # always pass the catalog path: the generator creates it when missing, which
    # is exactly what CI's `gen_catalog.py --check` step expects. Guarding on
    # existence would skip a deleted/omitted catalog and still fail that check.
    generator.generate_manifest(
        str(repo_root / "skills"),
        str(manifest_path),
        catalog_path=str(catalog_path),
    )
    return manifest_path


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
    parser.add_argument(
        "--no-regen",
        action="store_true",
        help="Skip regenerating skills.json/catalog (e.g. batch bumps that regenerate once at the end)",
    )
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
    if args.dry_run:
        return 0
    if args.no_regen:
        print("next: run scripts/generate_skills_manifest.py once when the batch is done")
        return 0
    manifest_path = regenerate_manifest(Path(args.skill))
    if manifest_path is None:
        print(
            "note: not inside a dojo checkout with the manifest generator; "
            "run scripts/generate_skills_manifest.py where skills.json lives"
        )
    else:
        print(f"regenerated {manifest_path} and the catalog")
    return 0


if __name__ == "__main__":
    sys.exit(main())
