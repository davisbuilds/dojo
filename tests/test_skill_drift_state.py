"""Tests for the SessionStart skill-drift debounce logic.

The notice must fire exactly once per distinct drift situation: when new drift
appears or the drifted set changes, but never while the same set persists (that
is the "annoying" behavior the hook is designed to avoid) and never when clean.
"""

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "hooks" / "skill_drift_state.py"


def load_module():
    spec = importlib.util.spec_from_file_location("skill_drift_state", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


mod = load_module()


def test_clean_stays_silent():
    assert mod.should_emit([], []) is False
    # Clean now, even if something was reported before (drift just resolved).
    assert mod.should_emit([], ["verify-before-complete"]) is False


def test_new_drift_emits():
    assert mod.should_emit(["verify-before-complete"], []) is True


def test_unchanged_drift_is_silent():
    # Same set as last session: already seen, do not nag.
    assert mod.should_emit(["a", "b"], ["a", "b"]) is False


def test_changed_set_emits():
    # Partial sync left a smaller set.
    assert mod.should_emit(["a"], ["a", "b"]) is True
    # A new skill started drifting.
    assert mod.should_emit(["a", "b"], ["a"]) is True


def test_notice_names_skills_and_sync_command():
    notice = mod.format_notice(["diagnose", "skill-creator"])
    assert "diagnose" in notice
    assert "skill-creator" in notice
    assert "sync.py" in notice


def test_state_roundtrip(tmp_path):
    state = tmp_path / "drift-state.json"
    assert mod.load_prior(state) == []  # absent -> empty
    mod.save_current(state, ["b", "a"], "2026-07-17T00:00:00Z")
    # Persisted sorted so comparison is order-independent.
    assert mod.load_prior(state) == ["a", "b"]


def test_load_prior_tolerates_corrupt_state(tmp_path):
    state = tmp_path / "drift-state.json"
    state.write_text("{not json", encoding="utf-8")
    assert mod.load_prior(state) == []


def test_extract_drifted_selects_only_content_drift():
    report = {
        "issues": [
            {"code": "CONTENT_DRIFT", "skill": "diagnose"},
            {"code": "INVALID_SKILL_DIR", "skill": "codex-primary-runtime"},
            {"code": "CONTENT_DRIFT", "skill": "api-design"},
        ]
    }
    assert mod.extract_drifted(report) == ["api-design", "diagnose"]


def test_run_debounces_across_sessions(tmp_path):
    state = tmp_path / "drift-state.json"
    drift = {"issues": [{"code": "CONTENT_DRIFT", "skill": "diagnose"}]}
    clean = {"issues": [{"code": "INVALID_SKILL_DIR", "skill": "codex-primary-runtime"}]}

    # First sighting of drift speaks.
    first = mod.run(drift, state, "t1")
    assert "diagnose" in first
    # Same drift next session: silent.
    assert mod.run(drift, state, "t2") == ""
    # Drift resolved: silent, and baseline cleared.
    assert mod.run(clean, state, "t3") == ""
    assert mod.load_prior(state) == []
    # Drift returns after being clean: speaks again.
    assert "diagnose" in mod.run(drift, state, "t4")
