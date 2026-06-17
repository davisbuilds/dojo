#!/bin/sh
""":"
if command -v python >/dev/null 2>&1; then
    exec python "$0" "$@"
fi
exec python3 "$0" "$@"
":"""
"""Generate per-skill harness adapters from SKILL.md frontmatter.

Two artifact kinds, all derived from the canonical `skills/<name>/SKILL.md`:

1. Dir-level relative symlinks so SKILL.md-native harnesses discover every skill:
       .claude/skills  -> ../skills
       .agents/skills  -> ../skills
       .agent/skills   -> ../skills

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
import os
import sys
from pathlib import Path

import yaml

HARNESS_DIRS = (".claude", ".agents", ".agent")
SYMLINK_TARGET = "../skills"
MARKER = "# AUTO-GENERATED from SKILL.md frontmatter — do not edit"


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


def symlink_ok(link: Path) -> bool:
    return link.is_symlink() and os.readlink(link) == SYMLINK_TARGET


def ensure_symlink(link: Path, write: bool) -> tuple[bool, str | None]:
    """Ensure ``link`` is a relative symlink to ``../skills``.

    Returns (ok, error). Never recursively deletes a real (non-symlink)
    directory: a populated local harness dir may hold untracked skills or
    config, so refuse and ask the developer to move it instead.
    """
    if symlink_ok(link):
        return True, None
    if not write:
        return False, None  # drift, reported by --check

    if link.is_symlink():
        link.unlink()  # wrong/broken symlink: safe to replace
    elif link.exists():
        if link.is_dir():
            if any(link.iterdir()):
                return False, (
                    f"{link} is a non-empty real directory; refusing to delete it. "
                    f"Move or remove it, then re-run to create the symlink."
                )
            link.rmdir()  # empty real dir: safe to replace
        else:
            return False, f"{link} is a real file; refusing to replace it."

    link.parent.mkdir(parents=True, exist_ok=True)
    os.symlink(SYMLINK_TARGET, link)
    return True, None


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

    # 1. Dir-level symlinks (local-only; gitignored)
    if not args.skip_symlinks:
        for harness in HARNESS_DIRS:
            link = repo_root / harness / "skills"
            ok, error = ensure_symlink(link, write)
            if error:
                errors.append(error)
            elif not ok:
                drift.append(f"{harness}/skills should be a symlink -> {SYMLINK_TARGET}")

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

    print(f"Symlinks ensured for {', '.join(HARNESS_DIRS)}; sidecars written: {len(wrote)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
