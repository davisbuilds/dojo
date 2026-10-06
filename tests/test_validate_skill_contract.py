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
    return MODULE.evaluate_skill(skill_dir, always_valid, strict, authoring_hints=True)


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


# These checks exercise the difference between packaging failures and authoring
# hints. Content quality is deliberately not inferred from these assertions.


@pytest.mark.parametrize("strict", [False, True])
def test_freeform_guidance_is_not_a_contract_failure(tmp_path: Path, strict: bool) -> None:
    skill = write_skill(tmp_path, "freeform", "# Choose a source\n\nRead the supplied source and return its supported answer.\n")
    result = evaluate(skill, strict)
    assert result["status"] == "warn"
    assert result["required_failures"] == []
    assert result["checks"]["execution_anchor_present"]["required"] is False


@pytest.mark.parametrize("strict", [False, True])
def test_very_long_skill_warns_without_blocking(tmp_path: Path, strict: bool) -> None:
    skill = write_skill(tmp_path, "long-skill", "A relevant instruction.\n" * 800)
    result = evaluate(skill, strict)
    assert result["checks"]["context_budget"]["status"] == "warn"
    assert result["checks"]["context_budget"]["required"] is False
    assert not result["required_failures"]


@pytest.mark.parametrize("bundled", [(), ("references",)])
def test_reference_directory_does_not_change_length_diagnostic(tmp_path: Path, bundled) -> None:
    skill = write_skill(tmp_path, "medium-skill", "A relevant instruction.\n" * 300, bundled=bundled)
    result = evaluate(skill)
    assert result["checks"]["context_budget"]["status"] == "pass"
    assert result["line_count"] == len((skill / "SKILL.md").read_text().splitlines())


def test_natural_description_does_not_require_magic_trigger_words(tmp_path: Path) -> None:
    skill = write_skill(tmp_path, "natural", "# Main\n\nExplain the user's supplied data.\n")
    p = skill / "SKILL.md"
    p.write_text(p.read_text().replace("Do a thing. Use when the user asks to do a thing.", "Interpret supplied time-series data and explain anomalies."))
    result = evaluate(skill)
    assert result["checks"]["description_trigger_ready"]["status"] == "warn"
    assert not result["required_failures"]


@pytest.mark.parametrize("strict", [False, True])
def test_invalid_packaging_still_blocks(tmp_path: Path, strict: bool) -> None:
    skill = write_skill(tmp_path, "invalid", "# Main\n")
    result = MODULE.evaluate_skill(skill, lambda _: (False, "Invalid SemVer"), strict)
    assert result["status"] == "fail"
    assert "frontmatter_valid" in result["required_failures"]


@pytest.mark.parametrize("change,check", [
    ("name", "name_matches_directory"),
    ("skill-type", "skill_type_declared"),
])
def test_strict_enforces_catalog_identity(tmp_path: Path, change: str, check: str) -> None:
    skill = write_skill(tmp_path, "catalog-entry", "# Main\n")
    p = skill / "SKILL.md"
    s = p.read_text()
    s = s.replace("name: catalog-entry", "name: another-entry") if change == "name" else s.replace("skill-type: workflow\n", "")
    p.write_text(s)
    assert check in evaluate(skill, True)["required_failures"]
    assert check not in evaluate(skill, False)["required_failures"]


def test_report_uses_current_date_and_qualifies_evidence() -> None:
    from datetime import datetime, timezone
    report = MODULE.render_markdown([], True)
    assert datetime.now(timezone.utc).date().isoformat() in report
    assert "not behavioral evidence" in report


@pytest.mark.parametrize("edit,expected_exit", [
    (None, 0),
    (("version: 1.0.0", "version: not-semver"), 1),
    (("skill-type: workflow", "skill-type: [workflow]"), 1),
    (("name: cli-entry", "name: another-name"), 1),
])
def test_cli_uses_real_metadata_gate(tmp_path: Path, edit, expected_exit: int) -> None:
    import json
    import subprocess
    import sys

    skill = write_skill(tmp_path, "cli-entry", "# Decide\n\nReturn a supported answer.\n")
    p = skill / "SKILL.md"
    if edit:
        p.write_text(p.read_text().replace(*edit))
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--skills-root", str(tmp_path), "--strict", "--json"],
        capture_output=True, text=True,
    )
    assert result.returncode == expected_exit, result.stderr
    payload = json.loads(result.stdout)
    assert payload["summary"]["total"] == 1
    assert payload["summary"]["fail"] == expected_exit


def test_normal_cli_omits_style_hints_but_can_request_them(tmp_path: Path) -> None:
    import json
    import subprocess
    import sys

    write_skill(tmp_path, "freeform-cli", "# Work\n\nAnswer from the supplied source.\n")
    args = [sys.executable, str(SCRIPT_PATH), "--skills-root", str(tmp_path), "--strict", "--json"]
    default = subprocess.run(args, capture_output=True, text=True)
    assert default.returncode == 0
    assert json.loads(default.stdout)["summary"]["warn"] == 0
    hints = subprocess.run(args + ["--authoring-hints"], capture_output=True, text=True)
    assert hints.returncode == 0
    assert json.loads(hints.stdout)["summary"]["warn"] == 1


@pytest.mark.parametrize("hints", [False, True])
def test_saved_report_records_whether_hints_ran(tmp_path: Path, hints: bool) -> None:
    import json
    import subprocess
    import sys

    write_skill(
        tmp_path, "reportable", "# Guidance\n\n## Scope\nUse the input.\n\n"
        "## Boundaries\nRespect scope.\n\n## Verification\nCheck the result.\n",
        skill_type="reference",
    )
    report_path = tmp_path / "report.md"
    args = [sys.executable, str(SCRIPT_PATH), "--skills-root", str(tmp_path),
            "--strict", "--json", "--markdown", str(report_path)]
    if hints:
        args.append("--authoring-hints")
    result = subprocess.run(args, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["summary"]["pass"] == 1
    expected = "enabled" if hints else "disabled (not evaluated)"
    assert f"Authoring hints: {expected}" in report_path.read_text()
