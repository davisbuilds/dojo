#!/bin/sh
""":"
if command -v python >/dev/null 2>&1; then
    exec python "$0" "$@"
fi
exec python3 "$0" "$@"
":"""
"""Generate per-skill harness adapters from SKILL.md frontmatter.

Two artifact kinds, all derived from the canonical `skills/<name>/SKILL.md`:

1. Selected project skills from config/project-skills.json, exposed as
   per-skill links in .agents/skills and .claude/skills. The full source catalog
   remains readable without being promoted into every session.

2. A colocated Codex interface sidecar per skill:
       skills/<name>/agents/openai.yaml

Generated sidecars start with an AUTO-GENERATED marker. Hand-authored sidecars
(no marker — e.g. curated ones with icons) are never overwritten and are only
checked for existence. Generation is deterministic and idempotent.

Usage:
    gen_harness_adapters.py           # write symlinks + missing/stale sidecars
    gen_harness_adapters.py --check   # exit non-zero on drift; write nothing
"""

import argparse
import json
import os
import sys
from pathlib import Path

import yaml

# Project selection is owned here; workspace deployment tools can reference this
# declaration directly. It is independent of the measurement-only profiles/ data.
SELECTION_PATH = "config/project-skills.json"
SYMLINK_TARGET = "../skills"  # exact legacy root link we may safely retire
MARKER = "# AUTO-GENERATED from SKILL.md frontmatter — do not edit"

# Claude Code reads slash commands from .claude/commands/. Selected skills'
# commands/<rel>.md is linked to .claude/commands/<rel>.md, preserving nested
# layout (workflows/brainstorm.md -> /workflows:brainstorm). Local-only and
# gitignored, like the per-skill links in .claude/skills.
COMMANDS_LINK_DIR = ".claude/commands"


def parse_frontmatter(skill_md: Path) -> dict:
    import re

    text = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n?", text, re.DOTALL)
    if not match:
        return {}
    try:
        parsed = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def yq(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def display_name(name: str) -> str:
    return " ".join(part.capitalize() for part in name.split("-"))


SHORT_DESC_MAX = 64  # openai.yaml contract: short_description is 25-64 chars
SHORT_DESC_MIN = 25


def short_description(description: str, dn: str) -> str:
    """Derive a 25-64 char blurb per the openai.yaml contract."""
    first = description.strip().split(". ")[0].strip().rstrip(".")
    text = first if len(first) >= SHORT_DESC_MIN else description.strip().rstrip(".")

    if len(text) > SHORT_DESC_MAX:
        cut = text[:SHORT_DESC_MAX]
        if " " in cut:
            cut = cut[: cut.rfind(" ")]
        text = cut.rstrip(" ,.;:—-")

    if len(text) < SHORT_DESC_MIN:
        text = f"{dn} — {text}".strip(" —")[:SHORT_DESC_MAX]
    return text


def render_sidecar(name: str, frontmatter: dict) -> str:
    desc = frontmatter.get("description", "")
    if not isinstance(desc, str):
        desc = ""
    dn = display_name(name)
    return (
        f"{MARKER}\n"
        "interface:\n"
        f"  display_name: {yq(dn)}\n"
        f"  short_description: {yq(short_description(desc, dn))}\n"
        f"  default_prompt: {yq(f'Use ${name} for this task.')}\n"
    )


def is_generated(path: Path) -> bool:
    return path.exists() and path.read_text(encoding="utf-8").startswith(MARKER)


def load_selection(repo_root: Path, skills_root: Path) -> dict:
    selection = json.loads((repo_root / SELECTION_PATH).read_text())
    if not isinstance(selection, dict):
        raise ValueError("selection must be an object")
    if selection.get("roots") != [".agents/skills", ".claude/skills"]:
        raise ValueError("project roots must be .agents/skills and .claude/skills")
    names = selection.get("linked")
    if not isinstance(names, list) or any(
        not isinstance(name, str) or not name or Path(name).name != name
        or name.startswith(".") or not (skills_root / name / "SKILL.md").is_file()
        for name in names
    ) or len(names) != len(set(names)):
        raise ValueError("linked must contain unique canonical skill names")
    if selection.get("retired_roots", []) != [".agent/skills", ".codex/skills"]:
        raise ValueError("retired_roots must name .agent/skills and .codex/skills")
    return selection


def ensure_selected_skills(root: Path, skills_root: Path, names: list[str], write: bool) -> tuple[list[str], list[str]]:
    drift, errors = [], []
    if root.is_symlink():
        if os.readlink(root) != SYMLINK_TARGET:
            return [], [f"{root} is a foreign symlink; leaving it alone"]
        if not write:
            return [f"{root} is a retired whole-catalog link"], []
        root.unlink()
    elif root.exists() and not root.is_dir():
        return [], [f"{root} is a real file; leaving it alone"]
    if write:
        root.mkdir(parents=True, exist_ok=True)
    if root.is_dir():
        for entry in root.iterdir():
            if entry.name in names:
                continue
            if entry.is_symlink() and _symlink_target_abs(entry).parent == skills_root:
                if write:
                    entry.unlink()
                else:
                    drift.append(f"{entry} is no longer selected")
            else:
                errors.append(f"{entry} is unexpected local content; leaving it alone")
    for name in names:
        link, source = root / name, skills_root / name
        target = os.path.relpath(source, root)
        if link.is_symlink() and os.readlink(link) == target:
            continue
        if link.exists() or link.is_symlink():
            if not link.is_symlink() or _symlink_target_abs(link).parent != skills_root:
                errors.append(f"{link} is not a managed skill link; leaving it alone")
                continue
            if write:
                link.unlink()
        if write:
            link.symlink_to(target)
        else:
            drift.append(f"{link} missing or wrong target")
    return drift, errors


def retire_legacy_symlink(link: Path, write: bool) -> tuple[bool, str | None]:
    """Remove a link this generator used to create and no longer owns.

    Returns (drift, error). Deliberately narrow: only a symlink whose target is
    exactly ``SYMLINK_TARGET`` is ours to retire. A real directory may hold a
    developer's own skills, and a foreign symlink may point somewhere
    deliberate -- both are reported rather than touched, because the cost of
    deleting either is far higher than the cost of one more listing.
    """
    if not link.exists() and not link.is_symlink():
        return False, None

    if not link.is_symlink():
        if not link.is_dir():
            return False, f"{link} is a real file; leaving it alone."
        if any(link.iterdir()):
            return False, (
                f"{link} is a non-empty real directory; refusing to delete it. "
                f"It may hold your own skills. Move it aside before retiring this root."
            )
        # An empty real dir contributes no skills, so it is harmless -- but it is
        # also what an interrupted migration leaves behind. Clear it when writing.
        if write:
            link.rmdir()
        return False, None
    if os.readlink(link) != SYMLINK_TARGET:
        return False, (
            f"{link} is a foreign symlink -> {os.readlink(link)}; leaving it alone. "
            f"Remove it by hand if it was meant to be the retired catalog link."
        )

    if not write:
        return True, None  # drift, reported by --check
    link.unlink()
    return False, None


def plan_command_links(skills_root: Path, commands_root: Path, selected: list[str]) -> tuple[dict[Path, Path], list[str]]:
    """Map each desired .claude/commands link to its source command file.

    Returns (desired, collisions). A collision is two skills whose command files
    resolve to the same link path; both are dropped from ``desired`` and reported.
    """
    desired: dict[Path, Path] = {}
    seen: dict[Path, Path] = {}
    collisions: list[str] = []
    for cmd in sorted(skills_root.glob("*/commands/**/*.md")):
        parts = cmd.relative_to(skills_root).parts  # (skill, "commands", *rel)
        if len(parts) < 3 or parts[1] != "commands" or parts[0] not in selected:
            continue
        link = commands_root.joinpath(*parts[2:])
        if link in seen:
            collisions.append(
                f"{link.relative_to(commands_root)}: "
                f"{seen[link].relative_to(skills_root)} and {cmd.relative_to(skills_root)}"
            )
            desired.pop(link, None)
            continue
        seen[link] = cmd
        desired[link] = cmd
    return desired, collisions


def _symlink_target_abs(link: Path) -> Path:
    """Resolve a symlink's target without requiring it to exist (dangling-safe)."""
    raw = os.readlink(link)
    if os.path.isabs(raw):
        return Path(os.path.normpath(raw))
    return Path(os.path.normpath(link.parent / raw))


def _is_managed_command_link(link: Path, skills_root: Path) -> bool:
    """True if ``link`` is a symlink pointing into skills/*/commands/ (ours to manage)."""
    if not link.is_symlink():
        return False
    try:
        rel = _symlink_target_abs(link).relative_to(skills_root)
    except ValueError:
        return False
    return len(rel.parts) >= 2 and rel.parts[1] == "commands"


def managed_command_links(commands_root: Path, skills_root: Path) -> list[Path]:
    """Existing symlinks under commands_root that point into skills/*/commands/.

    Only these are ours to prune; a user's hand-authored command file or a foreign
    symlink is left untouched. Dangling links (source removed) still count as ours.
    """
    found: list[Path] = []
    if not commands_root.is_dir():
        return found
    for path in sorted(commands_root.rglob("*")):
        if _is_managed_command_link(path, skills_root):
            found.append(path)
    return found


def ensure_command_symlink(
    link: Path, source: Path, skills_root: Path, write: bool
) -> tuple[bool, str | None]:
    """Ensure ``link`` is a relative symlink to ``source``. Never clobber a real file
    or a foreign symlink; only a managed link (into skills/*/commands/) is replaceable."""
    rel_target = os.path.relpath(source, link.parent)
    if link.is_symlink():
        if os.readlink(link) == rel_target:
            return True, None
        if not _is_managed_command_link(link, skills_root):
            return False, f"{link} is a foreign symlink; move it aside"
        if not write:
            return False, None
        link.unlink()  # wrong/broken managed symlink: safe to replace
    elif link.exists():
        return False, f"{link} exists and is not a managed symlink; move it aside"
    if not write:
        return False, None
    link.parent.mkdir(parents=True, exist_ok=True)
    os.symlink(rel_target, link)
    return True, None


def _prune_empty_dirs(start: Path, stop: Path) -> None:
    """Remove now-empty directories from ``start`` up to (not including) ``stop``."""
    current = start
    while current != stop and stop in current.parents:
        try:
            current.rmdir()
        except OSError:
            break
        current = current.parent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skills-root", default="skills", help="Path to skills directory (default: skills)")
    parser.add_argument("--repo-root", default=None, help="Repo root (default: parent of this script)")
    parser.add_argument("--check", action="store_true", help="Report drift without writing; exit 1 on drift")
    parser.add_argument(
        "--skip-symlinks",
        action="store_true",
        help="Only handle Codex sidecars (the committed artifacts); ignore the local-only harness symlinks",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[1]
    skills_root = Path(args.skills_root)
    if not skills_root.is_absolute():
        skills_root = (repo_root / skills_root).resolve()

    if not skills_root.is_dir():
        print(f"Skills root not found: {skills_root}", file=sys.stderr)
        return 1

    write = not args.check
    drift: list[str] = []
    errors: list[str] = []
    wrote: list[str] = []

    # Validate selection even in CI sidecar-only mode.
    try:
        selection = load_selection(repo_root, skills_root)
    except (OSError, ValueError, TypeError) as exc:
        print(f"Invalid project skill selection: {exc}", file=sys.stderr)
        return 1

    if not args.skip_symlinks:
        for root_rel in selection["roots"]:
            missing, refused = ensure_selected_skills(
                repo_root / root_rel, skills_root, selection["linked"], write)
            drift.extend(missing)
            errors.extend(refused)
        for root_rel in selection["retired_roots"]:
            stale, error = retire_legacy_symlink(repo_root / root_rel, write)
            if error:
                errors.append(error)
            elif stale:
                drift.append(f"{root_rel} is a retired catalog link and should be removed")

    # 2. Codex sidecars
    for skill_md in sorted(skills_root.glob("*/SKILL.md")):
        name = skill_md.parent.name
        fm = parse_frontmatter(skill_md)
        sidecar = skill_md.parent / "agents" / "openai.yaml"

        if sidecar.exists() and not is_generated(sidecar):
            continue  # hand-authored: leave alone

        rendered = render_sidecar(name, fm)
        current = sidecar.read_text(encoding="utf-8") if sidecar.exists() else None
        if current == rendered:
            continue
        if args.check:
            drift.append(f"{name}: openai.yaml missing or stale")
        else:
            sidecar.parent.mkdir(parents=True, exist_ok=True)
            sidecar.write_text(rendered, encoding="utf-8")
            wrote.append(name)

    # 3. Command wrappers -> .claude/commands (local-only, like the skills symlink)
    if not args.skip_symlinks:
        commands_root = repo_root / COMMANDS_LINK_DIR
        desired, collisions = plan_command_links(skills_root, commands_root, selection["linked"])
        for c in collisions:
            errors.append(f"command collision (rename one to disambiguate): {c}")
        for link, source in sorted(desired.items()):
            ok, error = ensure_command_symlink(link, source, skills_root, write)
            if error:
                errors.append(error)
            elif not ok:
                drift.append(f"{COMMANDS_LINK_DIR}/{link.relative_to(commands_root)} missing or wrong target")
        for link in managed_command_links(commands_root, skills_root):
            if link not in desired:
                if write:
                    link.unlink()
                    _prune_empty_dirs(link.parent, commands_root)
                else:
                    drift.append(f"{COMMANDS_LINK_DIR}/{link.relative_to(commands_root)} is stale")

    if errors:
        print("Harness adapter errors (resolve, then re-run):", file=sys.stderr)
        for item in errors:
            print(f"  - {item}", file=sys.stderr)
        return 1

    if args.check:
        if drift:
            print("Harness adapter drift (run scripts/gen_harness_adapters.py):", file=sys.stderr)
            for item in drift:
                print(f"  - {item}", file=sys.stderr)
            return 1
        print("Harness adapters are up to date.")
        return 0

    print(f"Symlinks ensured for {', '.join(selection['roots'])}; sidecars written: {len(wrote)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
