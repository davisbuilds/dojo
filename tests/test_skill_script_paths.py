"""A skill's runnable commands must work in the repository that *uses* the skill.

Skills are installed into a global root and loaded from whatever repository the
session is in, so the working directory at the moment a command runs is the
user's project — never dojo. A command written `skills/<name>/scripts/x.sh` is
resolved against that project and is simply not there.

This was live in fourteen skills, including the two whose whole point is a
verification step: `write-plan` and `write-spec` told the agent to run
`skills/write-plan/scripts/validate_plan.py docs/plans/<file>.md`, so every plan
written outside dojo had its validator fail or be improvised around. It looked
fine from inside dojo, which is the one place it works, and it survived in
`habits-ai` for a different reason — that repository happened to keep a
same-named local skills directory carrying the scripts, so the wrong path
resolved by accident.

The spec's "use relative paths from the skill root" rule (`spec/agent-skills-spec.md`)
covers *file references* in prose — a link to `references/REFERENCE.md`. It does
not settle a **shell command**, where the anchor has to be explicit because the
shell's cwd is the user's repository. dojo already had the working form in
`gemini-imagen` and `screenshot`: `<skill-dir>/scripts/...`, which tells the
agent to substitute the directory it loaded the skill from.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "skills"

# A command line invoking a script by a *repository*-relative skills path.
REPO_RELATIVE = re.compile(r"(?<![\w/<-])skills/[a-z0-9-]+/scripts/[\w./-]+")

# Genuine dojo-repository tooling: these document how to run dojo's own gates
# from a dojo checkout, where the repo-relative path is the correct one. They are
# named individually rather than pattern-matched, so adding one is a decision.
REPO_TOOLING = {
    "skill-evals",      # CI gate over dojo's own catalog (`--skills-root skills`)
}


def _command_lines(text: str) -> list[tuple[int, str]]:
    """Lines inside fenced code blocks — where a path is executed, not described.

    Prose may legitimately name a repository path ("see skills/foo/scripts/bar");
    only a line the agent is meant to run has to resolve at runtime.
    """
    lines, inside, out = text.splitlines(), False, []
    for number, line in enumerate(lines, 1):
        if line.lstrip().startswith("```"):
            inside = not inside
            continue
        if inside:
            out.append((number, line))
    return out


def _skill_files() -> list[Path]:
    """SKILL.md plus the bundled prose that also carries runnable commands.

    Command wrappers are canonical runbooks per this repo's own working
    conventions — a harness that does not expose command files still has an
    agent reading them — so a broken path there is broken in the same way.
    """
    return sorted(
        [*SKILLS_ROOT.glob("*/SKILL.md"),
         *SKILLS_ROOT.glob("*/commands/**/*.md"),
         *SKILLS_ROOT.glob("*/references/*.md")],
        key=str)


def test_there_are_skills_to_check():
    """The zero rule: a sweep that finds nothing to look at proves nothing."""
    assert len(_skill_files()) > 20, "skill discovery is broken, not the catalog"
    assert any(p.name != "SKILL.md" for p in _skill_files()), \
        "bundled command wrappers are not being scanned"


@pytest.mark.parametrize("skill_file", _skill_files(), ids=lambda p: str(p.relative_to(SKILLS_ROOT)))
def test_runnable_commands_do_not_assume_a_dojo_checkout(skill_file: Path):
    offenders = [
        (number, line.strip())
        for number, line in _command_lines(skill_file.read_text(encoding="utf-8"))
        if REPO_RELATIVE.search(line)
    ]
    owner = skill_file.relative_to(SKILLS_ROOT).parts[0]
    if owner in REPO_TOOLING:
        return
    assert not offenders, (
        f"{skill_file.relative_to(SKILLS_ROOT)}: command(s) resolve only inside a dojo checkout.\n"
        + "\n".join(f"  line {n}: {t}" for n, t in offenders)
        + "\nUse <skill-dir>/scripts/... so the command anchors to wherever the "
          "skill was loaded from, rather than to the repository the session "
          "happens to be in."
    )
