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


def test_direct_links_report_direct_citation_coverage():
    worksheet = score_report.build_worksheet(REPORT)
    assert worksheet["citation_coverage"]["status"] == "direct"
    assert worksheet["checks"]


NUMERIC_FOOTNOTE_REPORT = """# Findings

The verifier cut the measured cost by 4.5x in the evaluated workload28.

## Works cited

> 28. Verifying Agents in Rubric-Graded Environments — [paper](https://openreview.net/forum?id=ayA2tJNDET)
"""


def test_numbered_bibliography_links_are_resolved_back_to_inline_claims():
    worksheet = score_report.build_worksheet(NUMERIC_FOOTNOTE_REPORT)
    assert worksheet["citation_coverage"]["status"] == "resolvable"
    assert len(worksheet["checks"]) == 1
    assert worksheet["checks"][0]["url"] == "https://openreview.net/forum?id=ayA2tJNDET"
    assert "4.5x" in worksheet["checks"][0]["text"]


PARTIAL_NUMERIC_FOOTNOTE_REPORT = """# Findings

The attached brief supplied the framing1. The verifier cut measured cost by 4.5x28.

## Works cited

> 1. Attached brief without a retrievable URL
> 28. Verifying Agents — [paper](https://openreview.net/forum?id=ayA2tJNDET)
"""


def test_resolvable_numeric_citations_remain_scoreable_when_some_markers_are_opaque():
    worksheet = score_report.build_worksheet(PARTIAL_NUMERIC_FOOTNOTE_REPORT)
    assert worksheet["citation_coverage"]["status"] == "resolvable"
    assert worksheet["citation_coverage"]["unresolved_numeric_markers"] == 1
    assert len(worksheet["checks"]) == 1


OPAQUE_CITATION_REPORT = """# Findings

The benchmark retained all 13 facts. citeturn26view0

## Annotated bibliography

The provider export did not preserve retrievable URLs.
"""


def test_opaque_provider_markers_are_reported_instead_of_scoring_as_empty():
    worksheet = score_report.build_worksheet(OPAQUE_CITATION_REPORT)
    assert worksheet["citation_coverage"]["status"] == "opaque"
    assert worksheet["citation_coverage"]["opaque_markers"] == 1
    assert worksheet["checks"] == []


def test_report_without_citation_signals_is_distinct_from_opaque_export():
    worksheet = score_report.build_worksheet("# Findings\n\nNothing is cited here.\n")
    assert worksheet["citation_coverage"]["status"] == "absent"


def test_version_digits_without_a_bibliography_are_not_opaque_citations():
    worksheet = score_report.build_worksheet("# Findings\n\nModelX2 improved the result.\n")
    assert worksheet["citation_coverage"]["status"] == "absent"


def test_prose_reference_heading_does_not_start_a_bibliography():
    report = """# Findings

## Implementation references and examples

The measured result rose 12% [in the primary source](https://example.com/study).
"""
    worksheet = score_report.build_worksheet(report)
    assert worksheet["citation_coverage"]["status"] == "direct"
    assert len(worksheet["checks"]) == 1


def test_unattached_urls_are_not_misreported_as_no_citation_signals():
    report = """# Findings

The measured result rose substantially.

https://example.com/study
"""
    worksheet = score_report.build_worksheet(report)
    assert worksheet["citation_coverage"]["status"] == "opaque"
    assert worksheet["citation_coverage"]["citations"] == 1
    assert worksheet["checks"] == []


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


def build_checks(n_quant: int, n_plain: int) -> list[dict]:
    checks = []
    for i in range(n_quant):
        checks.append({"id": f"Q{i + 1}", "quantitative": True, "attribution": False})
    for i in range(n_plain):
        checks.append({"id": f"P{i + 1}", "quantitative": False, "attribution": False})
    return checks


def test_sample_prefers_quantitative_claims():
    sample = score_report.select_sample(build_checks(20, 20), size=10)
    quant = [cid for cid in sample if cid.startswith("Q")]
    assert len(quant) == 7  # QUANTITATIVE_SHARE of 10


def test_sample_backfills_when_quantitative_claims_are_scarce():
    sample = score_report.select_sample(build_checks(2, 20), size=10)
    assert len(sample) == 10
    assert {"Q1", "Q2"} <= set(sample)


def test_sample_is_capped_by_available_claims():
    assert len(score_report.select_sample(build_checks(2, 3), size=10)) == 5


def test_sample_is_deterministic():
    claims = build_checks(20, 20)
    assert score_report.select_sample(claims, 10) == score_report.select_sample(claims, 10)


# --- scoring --------------------------------------------------------------


def worksheet_with(verdicts: dict[str, str]) -> dict:
    return {
        "checks": [
            {"id": "Q1", "quantitative": True, "attribution": False},
            {"id": "Q2", "quantitative": True, "attribution": False},
            {"id": "P1", "quantitative": False, "attribution": False},
            {"id": "P2", "quantitative": False, "attribution": False},
        ],
        "sample": ["Q1", "Q2", "P1", "P2"],
        "verdicts": verdicts,
    }


def worksheet_with_applicability(
    verdicts: dict[str, str], applicability: dict[str, str]
) -> dict:
    worksheet = worksheet_with(verdicts)
    worksheet["applicability"] = applicability
    worksheet["citation_coverage"] = {"status": "direct"}
    return worksheet


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


def test_unreachable_check_is_excluded_from_applicability_rate():
    result = score_report.score_worksheet(
        worksheet_with_applicability(
            {"Q1": "unreachable", "Q2": "supported"},
            {"Q1": "fit", "Q2": "mismatch"},
        )
    )
    assert result["applicability"]["assessed"] == 1
    assert result["applicability"]["fit_rate"] == 0.0


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


def test_supported_but_domain_mismatched_citation_is_not_usable():
    result = score_report.score_worksheet(
        worksheet_with_applicability(
            {"Q1": "supported"},
            {"Q1": "mismatch"},
        )
    )
    assert result["hit_rate"] == 1.0
    assert result["applicability"]["fit_rate"] == 0.0
    assert result["applicability"]["mismatch"] == 1
    assert result["usable"]["usable_rate"] == 0.0


def test_supported_and_domain_fit_citation_is_usable():
    result = score_report.score_worksheet(
        worksheet_with_applicability(
            {"Q1": "supported"},
            {"Q1": "fit"},
        )
    )
    assert result["hit_rate"] == 1.0
    assert result["applicability"]["fit_rate"] == 1.0
    assert result["usable"]["usable_rate"] == 1.0


def test_new_worksheet_requires_applicability_for_each_reachable_check():
    result = score_report.score_worksheet(
        worksheet_with_applicability({"Q1": "supported"}, {})
    )
    assert result["complete"] is False
    assert result["applicability_unjudged"] == ["Q1", "Q2", "P1", "P2"]


def test_old_worksheet_without_applicability_remains_scoreable():
    result = score_report.score_worksheet(
        worksheet_with({"Q1": "supported", "Q2": "supported",
                        "P1": "supported", "P2": "supported"})
    )
    assert result["complete"] is True
    assert result["applicability"] is None


def test_invalid_applicability_verdict_is_rejected():
    try:
        score_report.score_worksheet(
            worksheet_with_applicability({"Q1": "supported"}, {"Q1": "close enough"})
        )
    except ValueError as exc:
        assert "close enough" in str(exc)
    else:
        raise AssertionError("expected ValueError on an unrecognized applicability verdict")


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
    assert payload["applicability"] == {}


def test_cli_worksheet_flags_opaque_citation_exports(tmp_path):
    report = tmp_path / "report.md"
    report.write_text(OPAQUE_CITATION_REPORT, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "worksheet", str(report)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 1
    payload = json.loads(proc.stdout)
    assert payload["citation_coverage"]["status"] == "opaque"


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


# --- per-citation checks --------------------------------------------------


MULTI_CITE = (
    "## Findings\n\n"
    "Two datasets put disputes at 43% "
    "([Dune](https://dune.com/queries/1), [Etherscan](https://etherscan.io/tx/0xabc)).\n"
)


def test_a_claim_with_two_citations_yields_two_checks():
    worksheet = score_report.build_worksheet(MULTI_CITE)
    assert len(worksheet["claims"]) == 1
    assert len(worksheet["checks"]) == 2
    assert {c["citation"] for c in worksheet["checks"]} == {"C1", "C2"}
    assert {c["claim"] for c in worksheet["checks"]} == {"Q1"}


def test_check_carries_the_url_the_verifier_must_fetch():
    checks = score_report.build_worksheet(MULTI_CITE)["checks"]
    assert {c["url"] for c in checks} == {
        "https://dune.com/queries/1", "https://etherscan.io/tx/0xabc"
    }


def test_check_inherits_the_claim_kind_for_weighting():
    checks = score_report.build_worksheet(MULTI_CITE)["checks"]
    assert all(c["quantitative"] for c in checks)


def test_one_bad_citation_is_not_hidden_by_a_good_one():
    # The whole point: C1 supporting the claim must not mask C2 refuting it.
    worksheet = score_report.build_worksheet(MULTI_CITE)
    ids = [c["id"] for c in worksheet["checks"]]
    worksheet["verdicts"] = {ids[0]: "supported", ids[1]: "unsupported"}
    result = score_report.score_worksheet(worksheet)
    assert result["judged"] == 2
    assert result["hit_rate"] == 0.5


def test_uncited_claims_contribute_no_checks():
    worksheet = score_report.build_worksheet("## F\n\nNothing is cited here.\n")
    assert worksheet["checks"] == []
    assert worksheet["sample"] == []


# --- CLI input validation -------------------------------------------------


def test_cli_rejects_a_zero_sample_size(tmp_path):
    report = tmp_path / "report.md"
    report.write_text(REPORT, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "worksheet", str(report), "--size", "0"],
        capture_output=True, text=True,
    )
    assert proc.returncode == 2
    assert "ZeroDivisionError" not in proc.stderr
    assert "positive" in proc.stderr.lower()


def test_spread_of_zero_is_empty_not_a_crash():
    assert score_report.spread([{"id": "a"}, {"id": "b"}], 0) == []
