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
    fm = [
        f"name: {name}",
        f"description: Reference for {name}. Use when {name} applies.",
        "version: 1.0.0",
        "skill-type: reference",
    ]
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


# Frozen output of the static (no-runtime) format_report for a fixed report.
# The phase-2 runtime section must be strictly additive: a report without a
# `runtime_source` in its summary renders byte-identically to this baseline.
_STATIC_GOLDEN = """Skill Health Report
  catalog: 2 skills
  contract: pass=1 warn=1 fail=0
  triggers: 1/2 skills declare triggers; assertions=2 passed=1 failed=1

Needs attention:
  warn  alpha                            contract=warn  warn:line-count  trigger-issues:bravo"""

_STATIC_REPORT = {
    "summary": {
        "total": 2, "contract_pass": 1, "contract_warn": 1, "contract_fail": 0,
        "skills_declaring_triggers": 1, "trigger_assertions": 2,
        "trigger_passed": 1, "trigger_failed": 1,
    },
    "skills": [
        {"skill": "alpha", "skill_type": "workflow", "contract_status": "warn",
         "warnings": ["line-count"], "required_failures": [], "line_count": 10,
         "triggers_declared": 2, "triggers_failed": ["bravo"]},
        {"skill": "bravo", "skill_type": "workflow", "contract_status": "pass",
         "warnings": [], "required_failures": [], "line_count": 8,
         "triggers_declared": 0, "triggers_failed": []},
    ],
}


def test_default_run_is_byte_identical():
    module = load_module()
    assert module.format_report(_STATIC_REPORT) == _STATIC_GOLDEN
    # A report carrying no runtime_source must produce no runtime section.
    assert "Runtime health" not in module.format_report(_STATIC_REPORT)
