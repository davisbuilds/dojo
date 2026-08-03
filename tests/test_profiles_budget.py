"""Task 3 — per-harness budget policies, and the degradation detector.

The load-bearing test in this file is `test_cost_never_derives_from_rendered_output`.
Everything else checks arithmetic; that one checks the thing that makes the
arithmetic worth doing. A harness that elides to fit always appears to fit, so a
model calibrated on captured output would certify the exact failure this
contract exists to catch.
"""

from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
POLICIES = REPO_ROOT / "profiles" / "policies"
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "profiles"
CATALOG_PATH = REPO_ROOT / "skills.json"
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from profiles import definitions, probe_claude, probe_codex  # noqa: E402
from profiles.budget import (  # noqa: E402
    BASIS,
    CEILING_BASIS_POINTS,
    Degradation,
    Verdict,
    assess,
    demand,
    detect_degradation,
    load_policy,
)
from profiles.resolve import resolve  # noqa: E402


@pytest.fixture
def codex_policy():
    return load_policy(POLICIES / "codex.yaml")


@pytest.fixture
def claude_1m():
    return load_policy(POLICIES / "claude-code-1m.yaml")


@pytest.fixture
def claude_200k():
    return load_policy(POLICIES / "claude-code-200k.yaml")


@pytest.fixture
def catalog():
    return definitions.load_catalog(CATALOG_PATH)


def source_entries(names, catalog) -> list[dict]:
    """Entries carrying untruncated frontmatter — the only valid cost input."""
    return [
        {"name": n, "source_description": catalog[n]["description"], "locator": f"/r/{n}/SKILL.md"}
        for n in names
    ]


# --------------------------------------------------------------------------
# The rule the whole task exists for
# --------------------------------------------------------------------------


def test_cost_never_derives_from_rendered_output(claude_200k):
    """SC-04. The elision hazard, on the live capture that demonstrates it.

    In this fixture 52 of 75 descriptions were removed outright, so the rendered
    block sits near the budget while true demand is nearly three times it. Cost
    computed from the rendering would report roughly 100%; cost computed from
    source reports the truth. A model calibrated on captured output fails here,
    which is the point.
    """
    body = json.loads((FIXTURES / "claude-request-dojo-2026-08-02.json").read_text())
    rendered = probe_claude.parse_request(body)
    debug = probe_claude.parse_debug((FIXTURES / "claude-debug-dojo-2026-08-02.txt").read_text())

    rendered_cost = demand(
        [{"name": e.name, "source_description": e.description or ""} for e in rendered.entries],
        claude_200k,
    )
    assert rendered_cost <= claude_200k.limit * 1.1, "fixture no longer 'appears to fit'"
    assert debug.demand_chars > 2 * claude_200k.limit
    assert debug.demand_chars > 2 * rendered_cost


def test_all_five_degradation_shapes_are_detected(codex_policy, claude_200k):
    """Five shapes across two harnesses; two of them are invisible in the output."""
    long_source = "x" * (probe_codex.MAX_DEFAULT_CONTEXT_SKILL_DESCRIPTION_CHARS + 50)

    codex_cases = [
        # (a) clipped mid-word, no marker at all
        ([{"name": "a", "source_description": "full sentence here", "listed_description": "full sen"}],
         Degradation.CODEX_CLIPPED),
        # (b) 1,024-char pre-cap, which DOES mark with "..."
        ([{"name": "b", "source_description": long_source,
           "listed_description": long_source[:1021] + "..."}],
         Degradation.CODEX_PRECAP),
    ]
    for entries, expected in codex_cases:
        assert expected in detect_degradation(entries, codex_policy)

    # (c) omission, both detection routes
    assert Degradation.CODEX_OMITTED in detect_degradation(
        [{"name": "a", "source_description": "s", "listed_description": "s"}],
        codex_policy, warning="Exceeded skills context budget. All skill descriptions were removed",
    )
    assert Degradation.CODEX_OMITTED in detect_degradation(
        [{"name": "a", "source_description": "s", "listed_description": "s"}],
        codex_policy, candidate_count=5,
    )

    # (d) and (e), Claude Code
    assert Degradation.CLAUDE_ELLIPSIS_TRUNCATED in detect_degradation(
        [{"name": "d", "source_description": "long", "listed_description": "lon…"}], claude_200k
    )
    assert Degradation.CLAUDE_DESCRIPTION_REMOVED in detect_degradation(
        [{"name": "e", "source_description": "gone", "listed_description": None}], claude_200k
    )


def test_description_removal_is_caught_by_absence_not_prefix(claude_200k):
    """The most severe shape has no listed text to compare a prefix against.

    A detector built only on "listed is a prefix of source" scores this as clean,
    which is how the worst case would go unreported.
    """
    entries = [{"name": "x", "source_description": "a real description", "listed_description": None}]
    assert Degradation.CLAUDE_DESCRIPTION_REMOVED in detect_degradation(entries, claude_200k)


def test_exempt_entries_do_not_register_removal(claude_200k):
    """Bundled and explicitly-invoked skills are exempt from stripping."""
    entries = [{"name": "doctor", "source_description": "d", "listed_description": None, "exempt": True}]
    assert detect_degradation(entries, claude_200k) == ()


def test_degradation_makes_a_target_nonconformant_regardless_of_cost(claude_1m):
    """A listing that fits *after* the harness elided it does not fit."""
    entries = [{"name": "x", "source_description": "tiny", "listed_description": None}]
    result = assess(entries, claude_1m)
    assert result.demand < result.limit * 0.01
    assert result.verdict is Verdict.NONCONFORMANT
    assert Degradation.CLAUDE_DESCRIPTION_REMOVED in result.degradations


# --------------------------------------------------------------------------
# Arithmetic, per policy's own unit
# --------------------------------------------------------------------------


def test_the_two_harnesses_use_genuinely_different_units(codex_policy, claude_1m):
    assert (codex_policy.unit, claude_1m.unit) == ("tokens", "characters")
    entries = [{"name": "n", "source_description": "d" * 400, "locator": "/r/n/SKILL.md"}]
    assert demand(entries, claude_1m) > 3 * demand(entries, codex_policy)


def test_claude_arithmetic_is_characters_end_to_end(claude_1m, claude_200k):
    """`context_tokens * 4 * fraction`, with no token conversion anywhere."""
    assert claude_200k.limit == probe_claude.budget_chars(200_000)
    assert claude_1m.limit == probe_claude.budget_chars(1_000_000)
    assert claude_1m.limit == 5 * claude_200k.limit


def test_codex_arithmetic_reproduces_the_vendor_constants(codex_policy):
    assert probe_codex.budget_for_window(codex_policy.context_window) == (codex_policy.limit, "tokens")
    assert codex_policy.limit == 5_440, "the full window, not the 95%-effective one"


@pytest.mark.parametrize("bps, deployable", [(8_900, True), (9_000, True), (9_100, False)])
@pytest.mark.parametrize("unit", ["tokens", "characters"])
def test_boundary_is_exact_integer_arithmetic(codex_policy, bps, deployable, unit):
    """EV-NEG-02, per unit, landing on the basis point exactly.

    The limit is chosen as 10,000 so each demand lands on its basis point with
    no rounding at all. A first attempt derived demand from the real limits and
    landed on 8,898 instead of 8,900 — double integer flooring — which would
    have tested a neighbourhood of the boundary rather than the boundary.
    The basis point is asserted before the verdict for exactly that reason.
    """
    policy = replace(codex_policy, limit=10_000, unit=unit)
    result = assess([{"name": "x", "source_description": "y", "locator": "/r/x"}], policy)
    result.demand = bps
    assert result.basis_points == bps
    assert (result.demand * BASIS <= policy.limit * CEILING_BASIS_POINTS) is deployable


def test_the_ceiling_is_ninety_percent_not_a_hundred(codex_policy):
    """A target can be inside the budget and still non-deployable.

    The 10% reserve is the contract's guardrail for estimator variance and
    harness-added metadata; `viral` sits at 95% on Codex today, under the budget
    and over the ceiling.
    """
    policy = replace(codex_policy, limit=10_000)
    result = assess([{"name": "x", "source_description": "y", "locator": "/r/x"}], policy)
    result.demand = 9_500
    assert result.demand < policy.limit
    assert result.demand * BASIS > policy.limit * CEILING_BASIS_POINTS


def test_an_empty_catalog_is_unsupported_not_deployable(codex_policy):
    """A trivial catalog must not satisfy the check (spec Evaluation)."""
    result = assess([], codex_policy)
    assert result.verdict is Verdict.UNSUPPORTED
    assert "no entries" in result.reason


# --------------------------------------------------------------------------
# SC-03 fit proofs, one per declared pair
# --------------------------------------------------------------------------


def _fit_entries(catalog):
    """`core` + one non-empty overlay + three foreign entries."""
    defs = definitions.load_definitions(REPO_ROOT / "profiles", catalog)
    members = resolve(("core", "research"), defs, catalog).members
    entries = source_entries(members, catalog)
    entries += [
        {"name": f"foreign-{i}", "source_description": "A foreign skill installed by someone else. " * 3,
         "locator": f"/foreign/{i}/SKILL.md"}
        for i in range(3)
    ]
    return entries


def test_fit_proof_codex_gpt56(codex_policy, catalog):
    result = assess(_fit_entries(catalog), codex_policy)
    assert result.verdict is Verdict.DEPLOYABLE, result.reason


def test_fit_proof_claude_1m(claude_1m, catalog):
    result = assess(_fit_entries(catalog), claude_1m)
    assert result.verdict is Verdict.DEPLOYABLE, result.reason


def test_reports_undeclared_pair_without_gating(claude_200k, catalog):
    """Spec revision 11: declared, scored, reported — never gating.

    The 200k pair's limit is exactly as authoritative as the 1M pair's; what
    differs is that nobody runs it. It must produce a real verdict, so a session
    landing there is told, and `gating` must be false, so a suite does not fail
    for a path in nobody's use.
    """
    result = assess(_fit_entries(catalog), claude_200k)
    assert result.verdict in (Verdict.DEPLOYABLE, Verdict.NONCONFORMANT)
    assert result.gating is False
    assert result.basis_points > 0


def test_the_declared_pairs_are_exactly_those_marked_deployable():
    """Promotion must be a visible edit, not a side effect of model choice."""
    policies = {p.stem: load_policy(p) for p in POLICIES.glob("*.yaml")}
    assert {n for n, p in policies.items() if p.deployable} == {"codex", "claude-code-1m"}
    assert policies["claude-code-200k"].deployable is False


def test_policy_identity_includes_the_model(claude_1m, claude_200k):
    """SC-04: the budget moves with the window, so the model is policy.

    Same harness, same version, same estimator — different model, and therefore
    a different policy identity feeding realization identity.
    """
    assert claude_1m.harness == claude_200k.harness
    assert claude_1m.harness_version == claude_200k.harness_version
    assert claude_1m.model != claude_200k.model
    assert claude_1m.identity != claude_200k.identity


def test_a_policy_missing_a_required_field_is_refused(tmp_path):
    """Fail closed: a policy that cannot be checked authorizes nothing."""
    import yaml
    good = yaml.safe_load((POLICIES / "codex.yaml").read_text())
    del good["limit"]
    path = tmp_path / "broken.yaml"
    path.write_text(yaml.safe_dump(good))
    with pytest.raises(ValueError, match="missing limit"):
        load_policy(path)


def test_an_unobserved_entry_is_not_an_observed_absence(claude_1m, catalog):
    """The defect the SC-03 fit proof caught.

    `listed_description` present-and-None means the harness rendered a bare name.
    The key being *missing* means nobody rendered anything — a hypothetical
    composition scored before any target exists. Conflating them made the fit
    proof report every member as description-removed, i.e. the detector
    inventing a degradation from the absence of a measurement, which is the
    inverse of the rule this package is built around.
    """
    hypothetical = [{"name": "x", "source_description": "never rendered"}]
    assert detect_degradation(hypothetical, claude_1m) == ()
    assert assess(hypothetical, claude_1m).verdict is Verdict.DEPLOYABLE

    observed_absent = [{"name": "x", "source_description": "never rendered", "listed_description": None}]
    assert Degradation.CLAUDE_DESCRIPTION_REMOVED in detect_degradation(observed_absent, claude_1m)
