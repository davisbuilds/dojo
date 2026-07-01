#!/usr/bin/env python3
"""Check per-skill SemVer bumps against a git base."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from functools import total_ordering
from pathlib import Path
from typing import Iterable

import yaml

SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)
CHANGELOG_HEADING_RE = re.compile(r"^##+\s+(?:\[)?{version}(?:\])?(?:\s|$)", re.MULTILINE)

IGNORED_EXACT = {
    "CHANGELOG.md",
    "agents/openai.yaml",
}
IGNORED_PARTS = {"__pycache__", ".pytest_cache"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}


@total_ordering
@dataclass(frozen=True)
class SemVer:
    major: int
    minor: int
    patch: int
    prerelease: tuple[str, ...]
    raw: str

    @classmethod
    def parse(cls, value: str) -> "SemVer":
        match = SEMVER_RE.match(value)
        if not match:
            raise ValueError(f"invalid SemVer: {value}")
        prerelease = tuple((match.group(4) or "").split(".")) if match.group(4) else ()
        return cls(
            major=int(match.group(1)),
            minor=int(match.group(2)),
            patch=int(match.group(3)),
            prerelease=prerelease,
            raw=value,
        )

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, SemVer):
            return NotImplemented
        core = (self.major, self.minor, self.patch)
        other_core = (other.major, other.minor, other.patch)
        if core != other_core:
            return core < other_core
        return _compare_prerelease(self.prerelease, other.prerelease) < 0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SemVer):
            return NotImplemented
        return (
            self.major,
            self.minor,
            self.patch,
            self.prerelease,
        ) == (
            other.major,
            other.minor,
            other.patch,
            other.prerelease,
        )


def _compare_prerelease(left: tuple[str, ...], right: tuple[str, ...]) -> int:
    if not left and not right:
        return 0
    if not left:
        return 1
    if not right:
        return -1
    for a, b in zip(left, right):
        if a == b:
            continue
        a_numeric = a.isdigit()
        b_numeric = b.isdigit()
        if a_numeric and b_numeric:
            return -1 if int(a) < int(b) else 1
        if a_numeric:
            return -1
        if b_numeric:
            return 1
        return -1 if a < b else 1
    if len(left) == len(right):
        return 0
    return -1 if len(left) < len(right) else 1


def run_git(repo_root: Path, args: list[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def git_lines(repo_root: Path, args: list[str]) -> set[str]:
    result = run_git(repo_root, args)
    if result.returncode != 0:
        return set()
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def base_ref_exists(repo_root: Path, base: str) -> bool:
    return run_git(repo_root, ["rev-parse", "--verify", f"{base}^{{commit}}"]).returncode == 0


def changed_files(repo_root: Path, base: str, include_untracked: bool) -> set[str]:
    files: set[str] = set()
    files |= git_lines(repo_root, ["diff", "--name-only", f"{base}...HEAD"])
    if not files:
        files |= git_lines(repo_root, ["diff", "--name-only", f"{base}..HEAD"])
    files |= git_lines(repo_root, ["diff", "--name-only"])
    files |= git_lines(repo_root, ["diff", "--cached", "--name-only"])
    if include_untracked:
        files |= git_lines(repo_root, ["ls-files", "--others", "--exclude-standard"])
    return files


def skill_name_for_path(path: str) -> str | None:
    parts = Path(path).parts
    if len(parts) < 3 or parts[0] != "skills":
        return None
    skill_name = parts[1]
    if skill_name.startswith("_"):
        return None
    return skill_name


def is_release_relevant(path: str) -> bool:
    parts = Path(path).parts
    if len(parts) < 3 or parts[0] != "skills":
        return False
    rel = "/".join(parts[2:])
    if rel in IGNORED_EXACT:
        return False
    if any(part in IGNORED_PARTS for part in parts):
        return False
    return not any(path.endswith(suffix) for suffix in IGNORED_SUFFIXES)


def parse_frontmatter(text: str) -> dict[str, object] | None:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None
    try:
        parsed = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None
    return parsed if isinstance(parsed, dict) else None


def current_skill_version(skill_md: Path) -> str | None:
    if not skill_md.exists():
        return None
    fm = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    version = fm.get("version") if fm else None
    return version.strip() if isinstance(version, str) else None


def base_skill_version(repo_root: Path, base: str, skill_name: str) -> str | None:
    result = run_git(repo_root, ["show", f"{base}:skills/{skill_name}/SKILL.md"])
    if result.returncode != 0:
        return None
    fm = parse_frontmatter(result.stdout)
    version = fm.get("version") if fm else None
    return version.strip() if isinstance(version, str) else None


def changelog_has_version(changelog: Path, version: str) -> bool:
    if not changelog.exists():
        return False
    pattern = CHANGELOG_HEADING_RE.pattern.format(version=re.escape(version))
    return re.search(pattern, changelog.read_text(encoding="utf-8"), re.MULTILINE) is not None


def changed_skill_map(paths: Iterable[str]) -> dict[str, list[str]]:
    changed: dict[str, list[str]] = {}
    for path in sorted(paths):
        if not is_release_relevant(path):
            continue
        skill_name = skill_name_for_path(path)
        if not skill_name:
            continue
        changed.setdefault(skill_name, []).append(path)
    return changed


def check_versions(repo_root: Path, skills_root: Path, base: str, include_untracked: bool) -> list[str]:
    errors: list[str] = []
    if not base_ref_exists(repo_root, base):
        return [f"git base ref is not resolvable: {base}"]

    changed = changed_skill_map(changed_files(repo_root, base, include_untracked))

    for skill_name, paths in sorted(changed.items()):
        skill_dir = skills_root / skill_name
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        current_raw = current_skill_version(skill_md)
        if current_raw is None:
            errors.append(f"{skill_name}: missing current version")
            continue
        try:
            current = SemVer.parse(current_raw)
        except ValueError:
            errors.append(f"{skill_name}: current version is not valid SemVer: {current_raw}")
            continue

        base_raw = base_skill_version(repo_root, base, skill_name)
        if base_raw is None:
            continue
        try:
            base_version = SemVer.parse(base_raw)
        except ValueError:
            continue

        if current <= base_version:
            changed_list = ", ".join(paths)
            errors.append(
                f"{skill_name}: release-relevant files changed but version did not increase "
                f"({base_raw} -> {current_raw}); changed: {changed_list}"
            )
            continue

        if not changelog_has_version(skill_dir / "CHANGELOG.md", current_raw):
            errors.append(f"{skill_name}: missing CHANGELOG.md entry for {current_raw}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="origin/main", help="Git base ref to compare against")
    parser.add_argument("--skills-root", default="skills", help="Path to skills root")
    parser.add_argument(
        "--no-untracked",
        action="store_true",
        help="Ignore untracked files when collecting changed paths",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[3]
    skills_root = Path(args.skills_root)
    if not skills_root.is_absolute():
        skills_root = (repo_root / skills_root).resolve()

    errors = check_versions(
        repo_root=repo_root,
        skills_root=skills_root,
        base=args.base,
        include_untracked=not args.no_untracked,
    )
    if errors:
        print("Skill version check failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print("Skill version check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
