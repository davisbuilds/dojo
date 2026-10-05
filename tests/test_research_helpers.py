"""The structured helpers expose triage limits, including when used standalone."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1] / "skills" / "deep-research"


@pytest.mark.parametrize("script,args", [
    ("depth_router.py", []),
    ("evidence_filter.py", []),
    ("run_pipeline.py", []),
    ("run_pipeline.py", ["--depth-only"]),
])
def test_helper_cli_preserves_input_and_reports_advisory_scope(tmp_path, script, args):
    source = tmp_path / "findings.json"
    original = (ROOT / "assets" / "sample-input.json").read_bytes()
    source.write_bytes(original)
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script), "--input", str(source), *args],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert source.read_bytes() == original
    # The limit travels with the JSON; consumers need not have read SKILL.md.
    assert payload["assessment_scope"] == "heuristic_triage"
    assert payload["sources_verified"] is False
    if script == "run_pipeline.py":
        assert payload["meta"]["filter_stage_executed"] == (not args)
        if args:
            assert payload["research_packet"] is None
        else:
            assert payload["research_packet"]["stats"]["input_findings"] > 0
            assert payload["research_packet"]["sources_verified"] is False
