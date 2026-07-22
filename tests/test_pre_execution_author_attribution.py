from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_authoring_surfaces_include_agent_attribution_placeholder() -> None:
    relative_paths = [
        "skills/brainstorming/SKILL.md",
        "skills/write-spec/SKILL.md",
        "skills/write-spec/assets/spec-template.md",
        "skills/write-plan/SKILL.md",
        "skills/write-plan/assets/plan-template.md",
    ]

    for relative_path in relative_paths:
        text = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        assert "author: <agent>" in text, relative_path
