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


def test_specific_pubmed_rule_takes_precedence_over_generic_gov_namespace():
    assessment = evidence_filter.credibility_assessment(
        "academic", "pubmed.ncbi.nlm.nih.gov"
    )

    assert assessment["score"] == 0.86
    assert assessment["registry_id"] == "pubmed-index"
    assert assessment["document_class"] == "bibliographic_record"
    assert assessment["source_type_consistency"] == "compatible"


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


def test_owned_provider_root_covers_documentation_subdomains():
    expected = {
        "code.claude.com": "claude-provider",
        "developers.openai.com": "openai-provider",
        "docs.cursor.com": "cursor-harness",
        "geminicli.com": "gemini-cli-harness",
        "docs.github.com": "github-docs",
        "learn.microsoft.com": "microsoft-learn",
        "docs.devin.ai": "devin-harness",
        "docs.windsurf.com": "windsurf-harness",
        "modelcontextprotocol.io": "model-context-protocol",
        "docs.langchain.com": "langchain-docs",
        "developers.llamaindex.ai": "llamaindex-docs",
    }

    for host, registry_id in expected.items():
        assessment = evidence_filter.credibility_assessment("official", host)
        assert assessment["registry_id"] == registry_id
        assert assessment["priority_source"] is True


def test_owned_provider_root_does_not_match_lookalike_domain():
    assessment = evidence_filter.credibility_assessment(
        "official", "code.claude.com.example.com"
    )

    assert assessment["score"] == 0.5
    assert assessment["registry_id"] is None
    assert assessment["priority_source"] is False


def test_unrelated_registered_hosts_do_not_become_priority_sources():
    assert (
        evidence_filter.credibility_assessment("primary", "github.com")[
            "priority_source"
        ]
        is False
    )
    assert (
        evidence_filter.credibility_assessment("academic", "nejm.org")[
            "priority_source"
        ]
        is False
    )
    assert (
        evidence_filter.credibility_assessment("academic", "arxiv.org")[
            "priority_source"
        ]
        is False
    )


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
        assert isinstance(rule.get("include_subdomains", False), bool)
        assert isinstance(rule.get("priority_source", False), bool)


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


def test_cli_retains_relevant_verified_provider_source_below_default_threshold(
    tmp_path,
):
    payload = {
        "research_brief": (
            "Claude Code skill listing context budget project scope user scope "
            "discovery shadow install harness metadata truncation"
        ),
        "depth": "quick",
        "now": "2026-07-27",
        "findings": [
            {
                "title": "Claude documentation",
                "url": "https://code.claude.com/docs/en/skills",
                "summary": "Reference for configuration.",
                "source_type": "official",
                "published_at": "2020-01-01",
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
    packet = json.loads(proc.stdout)
    assert packet["stats"]["retained_findings"] == 1
    assert packet["key_findings"][0]["score"] < 0.55
    assert (
        packet["key_findings"][0]["retention_reason"]
        == "verified_priority_source_below_threshold"
    )
    assert any(
        "verified priority source retained below the score threshold" in gap
        for gap in packet["confidence_gaps"]
    )


# --- on-chain and code hosts ----------------------------------------------


def test_block_explorer_outranks_an_unknown_domain():
    assessment = evidence_filter.credibility_assessment("primary", "etherscan.io")

    assert assessment["registry_id"] == "etherscan-explorer"
    assert assessment["authority"] == "onchain_explorer"
    assert assessment["score"] > 0.8


def test_community_query_platform_ranks_below_raw_chain_data():
    # Dune queries are user-authored SQL: the underlying data is authoritative,
    # the aggregation is not.
    dune = evidence_filter.credibility_assessment("primary", "dune.com")
    etherscan = evidence_filter.credibility_assessment("primary", "etherscan.io")

    assert dune["registry_id"] == "dune-analytics"
    assert dune["ceiling"] < etherscan["ceiling"]


def test_raw_source_file_outranks_the_repository_page():
    # A file's bytes are what they are; a repo page is mostly README prose.
    raw = evidence_filter.credibility_assessment("primary", "raw.githubusercontent.com")
    repo = evidence_filter.credibility_assessment("primary", "github.com")

    assert raw["ceiling"] > repo["ceiling"]
    assert repo["registry_id"] == "github-repository"


def test_code_host_stays_below_peer_reviewed_ceiling():
    repo = evidence_filter.credibility_assessment("primary", "github.com")
    journal = evidence_filter.credibility_assessment("academic", "nejm.org")

    assert repo["ceiling"] < journal["ceiling"]


def test_registry_rules_are_wellformed():
    required = {"id", "host", "authority", "document_class", "base_score",
                "ceiling", "compatible_source_types", "rationale"}
    ids = set()
    for rule in evidence_filter.load_credibility_registry():
        assert required <= set(rule), f"{rule.get('id')} missing {required - set(rule)}"
        assert rule["id"] not in ids, f"duplicate registry id: {rule['id']}"
        ids.add(rule["id"])
        assert 0.0 <= rule["base_score"] <= rule["ceiling"] <= 1.0, rule["id"]
