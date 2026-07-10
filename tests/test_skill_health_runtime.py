"""Tests for the opt-in runtime health module (phase-2 skill feedback loop)."""

import json
from pathlib import Path
from unittest import mock

import pytest

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import skill_health_runtime as shr  # noqa: E402

FIXTURE = REPO_ROOT / "skills" / "skill-evals" / "assets" / "sample-skill-health.json"


# --- Task 1: load_health_rows -------------------------------------------------

def test_load_health_rows_from_file():
    rows = shr.load_health_rows(url=None, path=str(FIXTURE))
    assert isinstance(rows, list)
    by_name = {r["name"]: r for r in rows}
    assert by_name["find-skills"]["neverFired"] is True
    assert by_name["write-spec"]["invocations"] == 125


def test_load_health_rows_url_error_raises():
    with mock.patch.object(shr.urllib.request, "urlopen", side_effect=OSError("refused")):
        with pytest.raises(RuntimeError):
            shr.load_health_rows(url="http://127.0.0.1:3141/api/v2/analytics/skills/health", path=None)


def test_load_health_rows_malformed_shape_raises(tmp_path):
    bad = tmp_path / "bad.json"
    # `data` present but items are not the expected shape.
    bad.write_text(json.dumps({"data": [{"nope": 1}]}), encoding="utf-8")
    with pytest.raises(RuntimeError):
        shr.load_health_rows(url=None, path=str(bad))


def test_load_health_rows_missing_data_raises(tmp_path):
    bad = tmp_path / "nodata.json"
    bad.write_text(json.dumps({"coverage": {}}), encoding="utf-8")
    with pytest.raises(RuntimeError):
        shr.load_health_rows(url=None, path=str(bad))


# --- Task 2: enrich_report ----------------------------------------------------

def _report(*skill_names):
    """A minimal build_report-shaped dict with the given dojo skills."""
    return {
        "summary": {"total": len(skill_names)},
        "skills": [{"skill": n, "contract_status": "pass"} for n in skill_names],
    }


def _fixture_rows():
    return shr.load_health_rows(url=None, path=str(FIXTURE))


def test_enrich_attaches_runtime_fields_to_dojo_skills():
    # find-skills (never-fired), write-spec (heavy), plus a dojo skill absent
    # from the health data (audit-skill).
    report = _report("find-skills", "write-spec", "audit-skill")
    shr.enrich_report(report, _fixture_rows(), source="fixture")
    by_name = {s["skill"]: s for s in report["skills"]}

    assert by_name["find-skills"]["never_fired"] is True
    assert by_name["find-skills"]["invocations"] == 0
    assert by_name["write-spec"]["invocations"] == 125
    assert by_name["write-spec"]["never_fired"] is False
    assert by_name["write-spec"]["misfire_eligible"] == 120


def test_enrich_ignores_non_dojo_rows():
    report = _report("find-skills", "write-spec")
    shr.enrich_report(report, _fixture_rows(), source="fixture")
    names = {s["skill"] for s in report["skills"]}
    # The fixture's non-dojo row must not be added to the report.
    assert "some-external-plugin" not in names


def test_enrich_marks_unmatched_dojo_skill_unknown():
    report = _report("audit-skill")  # no health row for this skill
    shr.enrich_report(report, _fixture_rows(), source="fixture")
    entry = report["skills"][0]
    assert entry["invocations"] == 0
    assert entry["never_fired"] is None  # unknown, distinct from explicit False


def test_enrich_adds_summary_rollups():
    report = _report("find-skills", "write-spec", "brainstorming", "audit-skill")
    shr.enrich_report(report, _fixture_rows(), source="http://example/health")
    s = report["summary"]
    assert s["runtime_source"] == "http://example/health"
    assert s["never_fired"] == 1  # only find-skills
    assert s["invoked"] == 2  # write-spec + brainstorming
