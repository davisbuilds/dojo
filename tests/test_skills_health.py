from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "skills_health.py"


def load_module():
    spec = importlib.util.spec_from_file_location("skills_health", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


REFERENCE_BODY = """# {title}

## When to use
Use when {title} applies.

## Boundaries
Not for unrelated tasks.

## Verification
Success criteria: the result is correct.
"""


def make_skill(skills_root: Path, name: str, triggers: list[str] | None = None):
    d = skills_root / name
    d.mkdir(parents=True)
    fm = [f"name: {name}", f"description: Reference for {name}. Use when {name} applies.", "skill-type: reference"]
    if triggers:
        fm.append("triggers:")
        fm += [f"  - {t}" for t in triggers]
    (d / "SKILL.md").write_text("---\n" + "\n".join(fm) + "\n---\n\n" + REFERENCE_BODY.format(title=name), encoding="utf-8")


def test_build_report_aggregates_contract_and_triggers(tmp_path: Path):
    module = load_module()
    skills_root = tmp_path / "skills"
    skills_root.mkdir()
    make_skill(skills_root, "alpha", triggers=["use alpha", "run alpha"])
    make_skill(skills_root, "bravo")  # no triggers

    report = module.build_report(skills_root)

    assert report["summary"]["total"] == 2
    assert report["summary"]["skills_declaring_triggers"] == 1
    assert report["summary"]["trigger_assertions"] == 2

    by_name = {s["skill"]: s for s in report["skills"]}
    assert by_name["alpha"]["triggers_declared"] == 2
    assert by_name["bravo"]["triggers_declared"] == 0
    # contract status is one of the known states
    assert by_name["alpha"]["contract_status"] in {"pass", "warn", "fail"}


def test_format_report_renders_summary(tmp_path: Path):
    module = load_module()
    skills_root = tmp_path / "skills"
    skills_root.mkdir()
    make_skill(skills_root, "alpha", triggers=["use alpha"])

    text = module.format_report(module.build_report(skills_root))
    assert "Skill Health Report" in text
    assert "catalog: 1 skills" in text
    assert "declare triggers" in text
