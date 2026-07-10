"""Tests for the opt-in runtime health module (phase-2 skill feedback loop)."""

import json
from pathlib import Path
from unittest import mock

import pytest

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import skill_health_runtime as shr  # noqa: E402

FIXTURE = REPO_ROOT / "tests" / "fixtures" / "sample-skill-health.json"


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


# --- Task 3: ranking + render -------------------------------------------------

def _enriched(*names):
    report = _report(*names)
    shr.enrich_report(report, _fixture_rows(), source="fixture")
    return report


def test_never_fired_sorts_first():
    report = _enriched("write-spec", "brainstorming", "find-skills", "write-plan")
    order = [e["skill"] for e in shr.rank_runtime_skills(report)]
    # never-fired first, then rarely-fired band, then rest by invocations asc.
    assert order[0] == "find-skills"
    assert order.index("brainstorming") < order.index("write-plan")
    assert order.index("write-plan") < order.index("write-spec")


def test_misfire_does_not_affect_rank():
    report = _enriched("write-spec", "write-plan", "brainstorming", "find-skills")
    before = [e["skill"] for e in shr.rank_runtime_skills(report)]
    # Perturb misfire fields only; ranking must not move.
    for e in report["skills"]:
        e["misfires"] = 999 if e.get("misfires") is not None else e.get("misfires")
        e["misfire_rate"] = 0.99 if e.get("misfire_rate") is not None else e.get("misfire_rate")
    after = [e["skill"] for e in shr.rank_runtime_skills(report)]
    assert before == after


def test_render_marks_misfire_experimental_and_never_fired():
    report = _enriched("find-skills", "write-plan", "write-spec")
    lines = shr.render_runtime_section(report)
    text = "\n".join(lines)
    assert "Runtime health" in text
    assert "find-skills" in text and "never" in text.lower()
    # write-plan has misfire data -> experimental label with N/M denominator.
    assert "2/10" in text and "experimental" in text


def test_unknown_skill_renders_no_data_and_sorts_last():
    report = _enriched("write-spec", "audit-skill", "find-skills")
    order = [e["skill"] for e in shr.rank_runtime_skills(report)]
    assert order[-1] == "audit-skill"  # no runtime data -> last
    assert "no data" in "\n".join(shr.render_runtime_section(report))


# --- Task 3: CLI main() wiring (subprocess) -----------------------------------

import subprocess  # noqa: E402

SKILLS_HEALTH = REPO_ROOT / "scripts" / "skills_health.py"


def test_json_includes_runtime_fields():
    proc = subprocess.run(
        [sys.executable, str(SKILLS_HEALTH), "--json", "--health-json", str(FIXTURE)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["summary"]["runtime_source"].endswith("sample-skill-health.json")
    by_name = {s["skill"]: s for s in payload["skills"]}
    assert by_name["write-spec"]["invocations"] == 125
    assert by_name["find-skills"]["never_fired"] is True


def test_runtime_load_failure_exits_nonzero_no_report():
    proc = subprocess.run(
        [sys.executable, str(SKILLS_HEALTH), "--health-json", "/no/such/health.json"],
        capture_output=True, text=True,
    )
    assert proc.returncode == 1
    assert proc.stdout.strip() == ""  # no partial report
    assert "health" in proc.stderr.lower()


# --- Task 4: findings ---------------------------------------------------------

def test_findings_emits_backlog_block_for_never_fired():
    report = _enriched("find-skills", "write-spec", "brainstorming")
    block = shr.render_findings(report)
    assert "#### find-skills" in block
    assert "Status: noted" in block
    assert "**What**" in block
    assert "**Why it matters**" in block
    assert "**Sketch**" in block
    # Skills that fired must not be proposed for retirement.
    assert "#### write-spec" not in block
    # Static caveat about the queried range is present.
    assert "range" in block.lower()


def test_findings_none_when_all_fired():
    report = _enriched("write-spec", "brainstorming")
    block = shr.render_findings(report)
    assert "####" not in block  # no never-fired skills -> no findings blocks


def test_findings_writes_no_file():
    backlog = REPO_ROOT / "docs" / "project" / "BACKLOG.md"
    before = backlog.read_bytes()
    proc = subprocess.run(
        [sys.executable, str(SKILLS_HEALTH), "--findings", "--health-json", str(FIXTURE)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert "####" in proc.stdout  # findings printed to stdout
    assert backlog.read_bytes() == before  # nothing auto-written
