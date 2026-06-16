from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "skills" / "skill-evals" / "scripts" / "run_trigger_evals.py"


def load_module():
    spec = importlib.util.spec_from_file_location("run_trigger_evals", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_skill(skills_root: Path, name: str, description: str, triggers: list[str]) -> None:
    skill_dir = skills_root / name
    skill_dir.mkdir(parents=True)
    trig_block = "".join(f"  - {t}\n" for t in triggers)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\ntriggers:\n{trig_block}---\n\n# {name}\n",
        encoding="utf-8",
    )


def test_declared_triggers_self_route(tmp_path: Path) -> None:
    module = load_module()
    skills_root = tmp_path / "skills"
    skills_root.mkdir()
    write_skill(
        skills_root,
        "diagnose",
        "Use when debugging hard bugs and performance regressions.",
        ["diagnose this", "diagnose this bug"],
    )
    write_skill(
        skills_root,
        "handoff",
        "Use when creating a session summary for context handoff.",
        ["create a handoff", "write a handoff summary"],
    )

    skills = module.build_skill_index(skills_root, None)
    result = module.evaluate_declared_triggers(skills)

    assert result["summary"]["failed"] == 0
    assert result["summary"]["skills_with_triggers"] == 2
    assert all(a["routes"] and a["collision_with"] is None for a in result["assertions"])


def test_declared_trigger_collision_is_flagged(tmp_path: Path) -> None:
    module = load_module()
    skills_root = tmp_path / "skills"
    skills_root.mkdir()
    # Two skills claiming an identical trigger phrase -> guaranteed collision.
    write_skill(
        skills_root,
        "review-swarm",
        "Use when running a parallel multi-agent review of a diff.",
        ["review this diff"],
    )
    write_skill(
        skills_root,
        "local-review",
        "Use when reviewing local workspace changes without posting to GitHub.",
        ["review this diff"],
    )

    skills = module.build_skill_index(skills_root, None)
    result = module.evaluate_declared_triggers(skills)

    assert result["summary"]["failed"] >= 1
    flagged = [a for a in result["assertions"] if a["collision_with"] is not None]
    assert flagged, "expected at least one collision to be flagged"
