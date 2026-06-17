from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "behavioral_evals.py"


def load_module():
    spec = importlib.util.spec_from_file_location("behavioral_evals", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


CATALOG = [
    {"name": "diagnose", "description": "Debug hard bugs.", "triggers": ["debug this", "diagnose this"]},
    {"name": "handoff", "description": "Summarize a session.", "triggers": ["create a handoff"]},
]


def test_build_cases_from_triggers():
    module = load_module()
    cases = module.build_cases(CATALOG)
    assert {(c["skill"], c["trigger"]) for c in cases} == {
        ("diagnose", "debug this"),
        ("diagnose", "diagnose this"),
        ("handoff", "create a handoff"),
    }


def test_build_prompt_lists_skills_and_request():
    module = load_module()
    prompt = module.build_prompt(CATALOG, "debug this")
    assert "diagnose: Debug hard bugs." in prompt
    assert 'User request: "debug this"' in prompt
    assert "ONLY the single best skill name" in prompt


def test_parse_response_is_tolerant():
    module = load_module()
    names = ["diagnose", "handoff"]
    assert module.parse_response("diagnose", names) == "diagnose"
    assert module.parse_response("The best skill is `handoff`.", names) == "handoff"
    assert module.parse_response("none of these apply", names) is None


def test_run_evals_with_injected_runner():
    module = load_module()

    # Perfect router: echoes the owning skill for each known trigger.
    trigger_to_skill = {"debug this": "diagnose", "diagnose this": "diagnose", "create a handoff": "handoff"}

    def good_runner(prompt: str) -> str:
        for trig, skill in trigger_to_skill.items():
            if f'"{trig}"' in prompt:
                return skill
        return "unknown"

    report = module.run_evals(CATALOG, good_runner)
    assert report["summary"]["cases"] == 3
    assert report["summary"]["failed"] == 0

    # Always-wrong router
    report2 = module.run_evals(CATALOG, lambda p: "handoff")
    assert report2["summary"]["failed"] == 2  # the two diagnose cases misroute


def test_gated_off_by_default(tmp_path: Path, monkeypatch):
    module = load_module()
    monkeypatch.delenv("DOJO_BEHAVIORAL_EVALS", raising=False)
    monkeypatch.setattr("sys.argv", ["behavioral"])

    called = {"runner": False}
    monkeypatch.setattr(module, "default_runner", lambda p: called.__setitem__("runner", True) or "x")

    assert module.main() == 0  # opt-in notice, clean exit
    assert called["runner"] is False  # never invoked the agent
