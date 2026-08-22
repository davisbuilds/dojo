"""A skill's runnable commands must work in the repository that *uses* the skill.

Skills are installed into a global root and loaded from whatever repository the
session is in, so the working directory at the moment a command runs is the
user's project — never dojo. A command written `skills/<name>/scripts/x.sh` is
resolved against that project and is simply not there.

This was live in fourteen skills, including the two whose whole point is a
verification step: `write-plan` and `write-spec` told the agent to run
`skills/write-plan/scripts/validate_plan.py docs/plans/<file>.md`, so every plan
written outside dojo had its validator fail or be improvised around. It looked
fine from inside dojo, which is the one place it works, and it survived in one
consumer repository for a different reason — that repository happened to keep
a same-named local skills directory carrying the scripts, so the wrong path
resolved by accident.

The spec's "use relative paths from the skill root" rule (`spec/agent-skills-spec.md`)
covers *file references* in prose — a link to `references/REFERENCE.md`. It does
not settle a **shell command**, where the anchor has to be explicit because the
shell's cwd is the user's repository. dojo already had the working form in
`gemini-imagen` and `screenshot`: `<skill-dir>/scripts/...`, which tells the
agent to substitute the directory it loaded the skill from.

The failing path is not always the executable: `bash <skill-dir>/scripts/scan.sh
--config skills/secure-code/rules/` anchors the script but not the operand, so
Semgrep is still handed a path that does not exist outside dojo. Any
`skills/<name>/...` operand on a runnable line fails the same way, whatever
subdirectory it names — so this guard matches the whole prefix, not just
`scripts/`. And a runnable command is not always fenced: an inline
`` `python3 skills/foo/scripts/x.py` `` runs just as literally, so inline code
spans that look like commands are scanned too — while an inline *mention* of a
path (`see skills/foo/references/bar.md`), which carries no executor, is left to
the file-reference rule above.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "skills"

# Any repository-relative skills subpath — scripts/, rules/, assets/, whatever —
# because all of them resolve against the caller's cwd, not dojo. The lookbehind
# keeps an *absolute* anchor from matching: `$CODEX_HOME/skills/foo/...` and
# `.claude/skills/foo/...` are preceded by `/` and are already correct.
REPO_RELATIVE = re.compile(r"(?<![\w/<.-])skills/[a-z0-9-]+/[\w./-]+")

# Fenced blocks tagged as a shell: every line is a command (so a `\`-continued
# operand on its own line is still covered). An untagged fence may be a directory
# tree or sample data, so those lines qualify only if they carry an executor,
# the same bar inline spans must clear.
SHELL_FENCES = {"bash", "sh", "shell", "zsh", "console", "shell-session"}

# An executor at a command position: line start, or right after a pipe/`;`/`&&`
# /`$(`. Anchoring it here is what separates `python3 skills/foo/...` (a command)
# from a bare mention of `skills/foo/scripts/run.sh` (whose `.sh` would otherwise
# read as the `sh` executor).
_EXECUTOR = re.compile(r"(?:^|[|;&]\s*|\$\(\s*)(?:bash|sh|zsh|python3?|node|printf|\./)\b")
_INLINE_CODE = re.compile(r"`([^`]+)`")

# dojo's own skill-authoring and validation gates. A command that runs one of
# these is meant to run from a dojo checkout — that is the workflow — so a
# repo-relative path to `skill-evals`/`skill-creator` is correct wherever it is
# cited. The exemption keys on the tool being invoked, not the file citing it:
# `loop-design` telling an author to run `skill-evals` is the same correct case
# as `skill-evals` documenting itself.
REPO_TOOLING = {
    "skill-evals",      # strict contract gate over dojo's own catalog
    "skill-creator",    # scaffolds/validates a new skill, from a dojo checkout
}


def _command_lines(text: str) -> list[tuple[int, str]]:
    """(line number, text) for every place a command is actually run.

    Three sources: every line of a shell-tagged fence; a line of any other fence
    that carries an executor; and an inline code span that carries an executor.
    Prose that merely names a path resolves to none of these.
    """
    out: list[tuple[int, str]] = []
    inside = shell = False
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.lstrip()
        if stripped.startswith("```"):
            if inside:
                inside = shell = False
            else:
                inside = True
                shell = stripped[3:].strip().lower() in SHELL_FENCES
            continue
        if inside:
            if shell or _EXECUTOR.search(line):
                out.append((number, line))
            continue
        for span in _INLINE_CODE.findall(line):
            if _EXECUTOR.search(span):
                out.append((number, span))
    return out


def _offenders(text: str) -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []
    for number, line in _command_lines(text):
        for match in REPO_RELATIVE.finditer(line):
            if match.group(0).split("/")[1] in REPO_TOOLING:
                continue
            found.append((number, match.group(0)))
    return found


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
    offenders = _offenders(skill_file.read_text(encoding="utf-8"))
    assert not offenders, (
        f"{skill_file.relative_to(SKILLS_ROOT)}: command(s) resolve only inside a dojo checkout.\n"
        + "\n".join(f"  line {n}: {path}" for n, path in offenders)
        + "\nUse <skill-dir>/... so the command anchors to wherever the skill was "
          "loaded from, rather than to the repository the session happens to be in."
    )
