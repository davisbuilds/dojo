from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "skills" / "deep-research" / "scripts" / "evidence_filter.py"


def load_module():
    spec = importlib.util.spec_from_file_location("evidence_filter", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


evidence_filter = load_module()


def test_known_preprint_repository_uses_domain_policy_not_official_label():
    assessment = evidence_filter.credibility_assessment("official", "arxiv.org")

    assert assessment["score"] == 0.82
    assert assessment["registry_id"] == "arxiv-preprints"
    assert assessment["source_type_consistency"] == "mismatch"


def test_compatible_source_type_only_breaks_ties_within_domain_ceiling():
    assessment = evidence_filter.credibility_assessment("academic", "arxiv.org")

    assert assessment["score"] == 0.84
    assert assessment["score"] <= assessment["ceiling"]
    assert assessment["source_type_consistency"] == "compatible"


def test_controlled_government_namespace_has_high_domain_credibility():
    assessment = evidence_filter.credibility_assessment("government", "data.cdc.gov")

    assert assessment["score"] == 0.92
    assert assessment["registry_id"] == "us-government"


def test_approved_university_research_host_gets_specific_institutional_prior():
    assessment = evidence_filter.credibility_assessment("academic", "hai.stanford.edu")

    assert assessment["score"] == 0.8
    assert assessment["registry_id"] == "stanford-hai"


def test_unlisted_university_subdomain_is_not_blanket_upgraded():
    assessment = evidence_filter.credibility_assessment(
        "official", "studentblog.stanford.edu"
    )

    assert assessment["score"] == 0.5
    assert assessment["registry_id"] is None


def test_lookalike_domain_does_not_match_registry_hostname():
    assessment = evidence_filter.credibility_assessment(
        "academic", "arxiv.org.example.com"
    )

    assert assessment["score"] == 0.5
    assert assessment["registry_id"] is None


def test_common_www_alias_and_url_noise_still_match_exact_registry_host():
    assessment = evidence_filter.credibility_assessment(
        "academic", "HTTPS://user:pass@WWW.ARXIV.ORG.:443/path"
    )

    assert assessment["registry_id"] == "arxiv-preprints"
    assert assessment["score"] == 0.84


def test_unknown_domain_cannot_self_declare_official_credibility():
    assessment = evidence_filter.credibility_assessment("official", "example.com")

    assert assessment["score"] == 0.5
    assert assessment["registry_id"] is None


def test_low_grade_self_declaration_can_lower_unknown_domain_prior():
    assessment = evidence_filter.credibility_assessment("social", "example.com")

    assert assessment["score"] == 0.25
    assert assessment["source_type_consistency"] == "unverified"


def test_url_hostname_overrides_caller_supplied_domain():
    finding = evidence_filter.normalize_finding(
        {
            "title": "Untrusted",
            "url": "https://example.com/report",
            "summary": "A claim",
            "source_type": "official",
            "domain": "arxiv.org",
        }
    )

    assert finding.domain == "example.com"


def test_registry_rules_have_unique_ids_and_required_explanations():
    rules = evidence_filter.load_credibility_registry()

    assert len({rule["id"] for rule in rules}) == len(rules)
    for rule in rules:
        assert rule["host"]
        assert rule["authority"]
        assert rule["document_class"]
        assert 0 <= rule["base_score"] <= rule["ceiling"] <= 1
        assert rule["rationale"]


def test_cli_emits_explainable_credibility_fields(tmp_path):
    payload = {
        "research_brief": "preprint evidence",
        "depth": "quick",
        "min_score": 0,
        "findings": [
            {
                "title": "Preprint evidence",
                "url": "https://arxiv.org/abs/1234.5678",
                "summary": "Preprint evidence relevant to the brief.",
                "source_type": "academic",
                "published_at": "2026-07-01",
            }
        ],
    }
    input_path = tmp_path / "input.json"
    input_path.write_text(json.dumps(payload))

    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--input", str(input_path)],
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0
    finding = json.loads(proc.stdout)["key_findings"][0]
    assert finding["credibility_registry_id"] == "arxiv-preprints"
    assert finding["credibility_authority"] == "academic_repository"
    assert finding["credibility_document_class"] == "preprint"
    assert finding["source_type_consistency"] == "compatible"
    assert "not necessarily peer reviewed" in finding["credibility_reason"]
