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
