from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "skills" / "research-architect" / "scripts" / "score_report.py"


def load_module():
    spec = importlib.util.spec_from_file_location("score_report", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


score_report = load_module()


REPORT = """# Frame check

Frame verified: the question compares unlike venues, checked against volume data.

## Findings

The market processed 292M trades in 2025, per [the underconfidence paper](https://arxiv.org/abs/2602.19520).
Retail participation is broadly flat year over year.
Polymarket resolution disputes rose 43% after the rule change (https://dune.com/queries/12345).
The 2024 review finds that longshot bias persists in thin books [source](https://ssrn.com/abstract=403).
Liquidity providers tend to cluster around round numbers.

## Summary

`key_findings` / `citations` / `confidence_gaps` / `next_queries`
"""


# --- citation extraction --------------------------------------------------


def test_extracts_markdown_link_citations():
    citations = score_report.extract_citations(REPORT)
    urls = [c["url"] for c in citations]
    assert "https://arxiv.org/abs/2602.19520" in urls
    assert "https://ssrn.com/abstract=403" in urls


def test_extracts_bare_url_citations():
    urls = [c["url"] for c in score_report.extract_citations(REPORT)]
    assert "https://dune.com/queries/12345" in urls


def test_citations_are_numbered_in_document_order():
    citations = score_report.extract_citations(REPORT)
    assert [c["id"] for c in citations] == [f"C{i}" for i in range(1, len(citations) + 1)]
    assert citations[0]["url"] == "https://arxiv.org/abs/2602.19520"


def test_markdown_link_url_is_not_double_counted_as_bare():
    urls = [c["url"] for c in score_report.extract_citations(REPORT)]
    assert urls.count("https://arxiv.org/abs/2602.19520") == 1


# --- claim extraction -----------------------------------------------------


def test_quantitative_claims_are_flagged():
    citations = score_report.extract_citations(REPORT)
    claims = score_report.extract_claims(REPORT, citations)
    quant = [c for c in claims if c["quantitative"]]
    assert any("292M" in c["text"] for c in quant)
    assert any("43%" in c["text"] for c in quant)


def test_attribution_claims_are_flagged():
    citations = score_report.extract_citations(REPORT)
    claims = score_report.extract_claims(REPORT, citations)
    assert any(c["attribution"] and "longshot bias" in c["text"] for c in claims)


def test_claims_carry_the_citations_in_their_sentence():
    citations = score_report.extract_citations(REPORT)
    claims = score_report.extract_claims(REPORT, citations)
    quant = next(c for c in claims if "292M" in c["text"])
    assert quant["citations"] == ["C1"]


def test_claim_text_stops_at_headings_and_paragraph_breaks():
    # A sentence-only splitter runs the heading, the frame check, and the first
    # finding together, because "# Frame check" has no terminal punctuation.
    citations = score_report.extract_citations(REPORT)
    claims = score_report.extract_claims(REPORT, citations)
    first = next(c for c in claims if "292M" in c["text"])
    assert first["text"].startswith("The market processed")
    assert "Frame check" not in first["text"]
    assert "Findings" not in first["text"]


def test_claim_line_number_points_at_the_claim():
    citations = score_report.extract_citations(REPORT)
    claims = score_report.extract_claims(REPORT, citations)
    first = next(c for c in claims if "292M" in c["text"])
    assert REPORT.splitlines()[first["line"] - 1].startswith("The market processed")


def test_uncited_prose_is_not_a_claim():
    citations = score_report.extract_citations(REPORT)
    claims = score_report.extract_claims(REPORT, citations)
    assert not any("round numbers" in c["text"] for c in claims)


# --- sampling -------------------------------------------------------------


def build_claims(n_quant: int, n_plain: int) -> list[dict]:
    claims = []
    for i in range(n_quant):
        claims.append({"id": f"Q{i + 1}", "quantitative": True, "attribution": False})
    for i in range(n_plain):
        claims.append({"id": f"P{i + 1}", "quantitative": False, "attribution": False})
    return claims


def test_sample_prefers_quantitative_claims():
    sample = score_report.select_sample(build_claims(20, 20), size=10)
    quant = [cid for cid in sample if cid.startswith("Q")]
    assert len(quant) == 7  # QUANTITATIVE_SHARE of 10


def test_sample_backfills_when_quantitative_claims_are_scarce():
    sample = score_report.select_sample(build_claims(2, 20), size=10)
    assert len(sample) == 10
    assert {"Q1", "Q2"} <= set(sample)


def test_sample_is_capped_by_available_claims():
    assert len(score_report.select_sample(build_claims(2, 3), size=10)) == 5


def test_sample_is_deterministic():
    claims = build_claims(20, 20)
    assert score_report.select_sample(claims, 10) == score_report.select_sample(claims, 10)


# --- scoring --------------------------------------------------------------


def worksheet_with(verdicts: dict[str, str]) -> dict:
    return {
        "claims": [
            {"id": "Q1", "quantitative": True, "attribution": False},
            {"id": "Q2", "quantitative": True, "attribution": False},
            {"id": "P1", "quantitative": False, "attribution": False},
            {"id": "P2", "quantitative": False, "attribution": False},
        ],
        "sample": ["Q1", "Q2", "P1", "P2"],
        "verdicts": verdicts,
    }


def test_hit_rate_counts_supported_over_judged():
    result = score_report.score_worksheet(
        worksheet_with({"Q1": "supported", "Q2": "unsupported",
                        "P1": "supported", "P2": "supported"})
    )
    assert result["hit_rate"] == 0.75
    assert result["judged"] == 4


def test_hit_rate_breaks_out_quantitative_claims():
    result = score_report.score_worksheet(
        worksheet_with({"Q1": "unsupported", "Q2": "unsupported",
                        "P1": "supported", "P2": "supported"})
    )
    assert result["quantitative"]["hit_rate"] == 0.0
    assert result["qualitative"]["hit_rate"] == 1.0


def test_partial_is_not_a_hit():
    result = score_report.score_worksheet(
        worksheet_with({"Q1": "partial", "Q2": "supported",
                        "P1": "supported", "P2": "supported"})
    )
    assert result["hit_rate"] == 0.75


def test_unreachable_is_excluded_from_the_denominator():
    result = score_report.score_worksheet(
        worksheet_with({"Q1": "unreachable", "Q2": "supported",
                        "P1": "supported", "P2": "supported"})
    )
    assert result["judged"] == 3
    assert result["hit_rate"] == 1.0
    assert result["unreachable"] == 1


def test_unjudged_sample_entries_are_reported_not_assumed():
    result = score_report.score_worksheet(worksheet_with({"Q1": "supported"}))
    assert result["unjudged"] == ["Q2", "P1", "P2"]
    assert result["complete"] is False


def test_invalid_verdict_is_rejected():
    try:
        score_report.score_worksheet(worksheet_with({"Q1": "looks fine"}))
    except ValueError as exc:
        assert "looks fine" in str(exc)
    else:
        raise AssertionError("expected ValueError on an unrecognized verdict")


# --- CLI ------------------------------------------------------------------


def test_cli_worksheet_emits_json(tmp_path):
    report = tmp_path / "report.md"
    report.write_text(REPORT, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "worksheet", str(report)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload["sample"]
    assert payload["verdicts"] == {}


def test_cli_score_reports_hit_rate(tmp_path):
    sheet = tmp_path / "sheet.json"
    sheet.write_text(json.dumps(worksheet_with(
        {"Q1": "supported", "Q2": "supported", "P1": "supported", "P2": "unsupported"}
    )), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "score", str(sheet)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0
    assert "75" in proc.stdout


def test_cli_missing_file_exits_two(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "worksheet", str(tmp_path / "nope.md")],
        capture_output=True, text=True,
    )
    assert proc.returncode == 2
