from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_spec_handoff_keeps_optional_routine_critique_checklist() -> None:
    skill = (REPO_ROOT / "skills/write-spec/SKILL.md").read_text(encoding="utf-8")
    wrapper = (
        REPO_ROOT / "skills/write-spec/commands/workflows/spec.md"
    ).read_text(encoding="utf-8")

    assert "Review the contract with a critique subagent" in skill
    assert "is the end-state falsifiable?" in skill
    assert "For routine contracts, critique remains optional" in skill
    assert "Review a routine contract with a critique subagent" in wrapper


def test_plan_handoff_keeps_optional_routine_critique_checklist() -> None:
    skill = (REPO_ROOT / "skills/write-plan/SKILL.md").read_text(encoding="utf-8")
    wrapper = (
        REPO_ROOT / "skills/write-plan/commands/workflows/plan.md"
    ).read_text(encoding="utf-8")

    assert "Review the plan with a critique subagent" in skill
    assert "is the chosen seam the thinnest" in skill
    assert "For routine plans, critique remains optional" in skill
    assert "Review a routine plan with a critique subagent" in wrapper
