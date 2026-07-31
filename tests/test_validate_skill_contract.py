from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "skills" / "skill-evals" / "scripts" / "validate_skill_contract.py"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_skill_contract", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


def write_skill(
    root: Path,
    name: str,
    body: str,
    *,
    bundled: tuple[str, ...] = (),
    skill_type: str = "workflow",
) -> Path:
    """Create a minimal skill directory that satisfies every unrelated check."""
    skill_dir = root / name
    skill_dir.mkdir(parents=True)
    for d in bundled:
        (skill_dir / d).mkdir()
        (skill_dir / d / "placeholder.txt").write_text("x", encoding="utf-8")
    frontmatter = (
        "---\n"
        f"name: {name}\n"
        f'description: "Do a thing. Use when the user asks to do a thing."\n'
        f"skill-type: {skill_type}\n"
        "version: 1.0.0\n"
        "---\n\n"
    )
    (skill_dir / "SKILL.md").write_text(frontmatter + body, encoding="utf-8")
    return skill_dir


def always_valid(_path: str) -> tuple[bool, str]:
    return True, "ok"


def evaluate(skill_dir: Path, strict: bool = True) -> dict:
    return MODULE.evaluate_skill(skill_dir, always_valid, strict)


# --- resource_map_present -------------------------------------------------
#
# The check is deliberately loose: any recognized resource heading OR any
# resource path mention satisfies it. These tests pin the boundary that a
# *behavioral* "Rules" section must not stand in for documenting bundled
# resources, which is what makes `rules/` different from `references/` or
# `commands/` as a heading word.


def test_behavioral_rules_heading_does_not_satisfy_resource_map(tmp_path: Path) -> None:
    """A '## Rules' section is usually behavioral, not a resource map.

    Regression guard: a skill bundling scripts/ that documents neither the
    script nor any other resource must not pass merely because it happens to
    have a Rules section.
    """
    skill_dir = write_skill(
        tmp_path,
        "behavioral-rules",
        "# Thing\n\n## When To Use\n\n- always\n\n## Rules\n\n"
        "- Never guess.\n\n## Boundaries\n\n- not for x\n\n## Verification\n\n- it ran\n",
        bundled=("scripts",),
    )
    assert MODULE.resource_map_present((skill_dir / "SKILL.md").read_text(), skill_dir) is False


def test_rules_directory_is_recognized_when_documented(tmp_path: Path) -> None:
    """A skill that actually points at its bundled rules/ passes."""
    skill_dir = write_skill(
        tmp_path,
        "documented-rules",
        "# Thing\n\n## When To Use\n\n- always\n\n"
        "Constraints live in `rules/policy.yaml`.\n\n"
        "## Boundaries\n\n- not for x\n\n## Verification\n\n- it ran\n",
        bundled=("rules",),
    )
    assert MODULE.resource_map_present((skill_dir / "SKILL.md").read_text(), skill_dir) is True


def test_rules_directory_undocumented_fails(tmp_path: Path) -> None:
    skill_dir = write_skill(
        tmp_path,
        "undocumented-rules",
        "# Thing\n\n## When To Use\n\n- always\n\n## Boundaries\n\n- not for x\n\n"
        "## Verification\n\n- it ran\n",
        bundled=("rules",),
    )
    assert MODULE.resource_map_present((skill_dir / "SKILL.md").read_text(), skill_dir) is False


# --- context_budget -------------------------------------------------------
#
# The 251-500 tier is ADVISORY BY DESIGN and must stay a warning even under
# --strict. It flags inverted progressive disclosure, which is a judgment call
# about placement rather than a contract breach, and six existing skills sit in
# the band. Escalating it to a failure would turn CI red on work nobody has
# agreed to do. Only the >700 tier fails under strict.


def long_body(lines: int) -> str:
    filler = "\n".join(f"- point {i}" for i in range(lines))
    return (
        "# Thing\n\n## When To Use\n\n- always\n\n## Boundaries\n\n- not for x\n\n"
        "## Steps\n\n1. do it\n\n## Output\n\n- a thing\n\n"
        "See `references/detail.md`.\n\n## Verification\n\n- it ran\n\n" + filler + "\n"
    )


def test_midsize_skill_with_references_warns_but_never_fails_under_strict(tmp_path: Path) -> None:
    skill_dir = write_skill(tmp_path, "midsize", long_body(300), bundled=("references",))
    result = evaluate(skill_dir, strict=True)
    assert 250 < result["line_count"] <= 500
    assert result["checks"]["context_budget"]["status"] == "warn"
    assert "context_budget" not in result["required_failures"]
    assert "context_budget" in result["warnings"]


def test_midsize_skill_without_references_passes(tmp_path: Path) -> None:
    """Length alone is not the defect; having somewhere to put the detail is."""
    skill_dir = write_skill(tmp_path, "midsize-no-refs", long_body(300), bundled=("scripts",))
    result = evaluate(skill_dir, strict=True)
    assert 250 < result["line_count"] <= 500
    assert result["checks"]["context_budget"]["status"] == "pass"


def test_short_skill_passes_regardless_of_references(tmp_path: Path) -> None:
    skill_dir = write_skill(tmp_path, "short", long_body(20), bundled=("references",))
    result = evaluate(skill_dir, strict=True)
    assert result["line_count"] <= 250
    assert result["checks"]["context_budget"]["status"] == "pass"


@pytest.mark.parametrize("strict,expected", [(True, "fail"), (False, "warn")])
def test_very_long_skill_still_fails_under_strict(tmp_path: Path, strict: bool, expected: str) -> None:
    """The pre-existing >700 escalation is unchanged by the new tier."""
    skill_dir = write_skill(tmp_path, f"huge-{strict}", long_body(800), bundled=("references",))
    result = evaluate(skill_dir, strict=strict)
    assert result["line_count"] > 700
    assert result["checks"]["context_budget"]["status"] == expected
