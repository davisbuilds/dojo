"""Task 0 — the listing probes every later profiles task depends on.

These tests read captured fixtures, never the live harnesses, so they are
hermetic and reproducible. The live probes are exercised by the verification
commands in the plan, not here.

Two disciplines are enforced throughout and are the reason several assertions
look indirect:

* **No hardcoded totals.** Entry counts move whenever anyone authors or retires
  a skill. Assertions are non-degeneracy floors or relations between probe
  outputs, so authoring a skill can never silently falsify a test.
* **Every detector is proven against a case known to be present** before any
  absence is trusted. A count of zero is a claim about the instrument.
"""

from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "profiles"
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from profiles import probe_claude, probe_codex  # noqa: E402

CODEX_HOME = Path.home() / ".codex"
DOJO_SKILLS = REPO_ROOT / "skills"

# The truncating fixture was captured from a scratch directory holding only
# `.agents/skills -> <canonical catalog>`, which is the topology that made a dojo
# session cost 177% before PR #54. Tests needing that cwd rebuild it under
# `tmp_path` rather than referencing the original capture directory, which does
# not exist on any other machine.
ROOT_ALIAS_RE = re.compile(r"^- `(?P<alias>\w+)` = `(?P<path>.*)`$")


def rebuild_capture_cwd(listing: probe_codex.Listing, tmp_path: Path) -> Path:
    """Recreate the project-scope topology the fixture was captured under.

    The link is allowed to dangle: its *target path* is what classification
    compares against, and that path belongs to the machine that produced the
    capture. Requiring it to exist here would make the test pass only on that
    machine — which is exactly how it was first written, and it failed the moment
    the capture directory was moved.
    """
    canonical = None
    for line in listing.root_lines:
        match = ROOT_ALIAS_RE.match(line)
        if match and match.group("path").endswith("/skills") and "/.codex/" not in match.group("path"):
            canonical = match.group("path")
    assert canonical, "fixture roots table names no canonical catalog root"
    cwd = tmp_path / "capture"
    (cwd / ".agents").mkdir(parents=True)
    (cwd / ".agents" / "skills").symlink_to(canonical)
    return cwd


def load_codex(name: str) -> probe_codex.Listing:
    payload = json.loads((FIXTURES / name).read_text())
    return probe_codex.parse_block(probe_codex.extract_block(payload))


@pytest.fixture
def dojo() -> probe_codex.Listing:
    return load_codex("codex-prompt-input-dojo-2026-08-02.json")


@pytest.fixture
def viral() -> probe_codex.Listing:
    return load_codex("codex-prompt-input-viral-2026-08-02.json")


@pytest.fixture
def truncating() -> probe_codex.Listing:
    return load_codex("codex-prompt-input-truncating-2026-08-02.json")


@pytest.fixture
def claude_debug() -> probe_claude.DebugResult:
    return probe_claude.parse_debug((FIXTURES / "claude-debug-dojo-2026-08-02.txt").read_text())


@pytest.fixture
def claude_request() -> probe_claude.RequestResult:
    body = json.loads((FIXTURES / "claude-request-dojo-2026-08-02.json").read_text())
    return probe_claude.parse_request(body)


# --------------------------------------------------------------------------
# Codex: the parser
# --------------------------------------------------------------------------


def test_recovers_namespaced_plugin_entries(dojo):
    """The zero rule, applied to the error that produced one.

    Plugin skills render as ``namespace:name``. A parser splitting on the first
    colon drops them and reports zero plugin entries in every session — which is
    exactly what happened when this table was first produced. Asserting only a
    nonzero count would pass for a parser that found them by luck, so the names
    must actually contain a colon.
    """
    namespaced = [e for e in dojo.entries if e.is_namespaced]
    assert namespaced, "no namespaced entries recovered; the anchor rule regressed"
    assert all(":" in e.name for e in namespaced)


def test_roots_table_is_not_parsed_as_entries(truncating):
    """The roots table lives in the same block and starts with '- '.

    An earlier parser counted it as a fake entry. Every parsed entry must carry
    a locator; root lines carry an alias assignment instead.
    """
    assert truncating.root_lines, "alias fixture has no roots table to confuse us with"
    assert all(e.locator for e in truncating.entries)
    assert not any(e.name.startswith("`r") for e in truncating.entries)


def test_render_mode_is_read_from_the_intro(dojo, truncating):
    """render.rs picks alias mode only when absolute mode omits or truncates.

    The mode is therefore a free degradation signal: absolute mode is proof that
    nothing was dropped or clipped.
    """
    assert dojo.render_mode == "absolute"
    assert truncating.render_mode == "alias"


def test_alias_locators_expand_to_absolute_paths(truncating, tmp_path):
    """Classification must not depend on render mode."""
    cwd = rebuild_capture_cwd(truncating, tmp_path)
    listing = probe_codex.classify(truncating, DOJO_SKILLS, CODEX_HOME, cwd)
    assert any(not e.locator.startswith("/") for e in listing.entries), "fixture is not alias-rendered"
    origins = {e.origin for e in listing.entries}
    assert "plugin" in origins, "alias locators failed to expand; plugin cache went undetected"


# --------------------------------------------------------------------------
# Codex: cost, which is where the arithmetic has to be exact
# --------------------------------------------------------------------------


def test_only_skill_lines_are_charged(dojo):
    """The intro prose and headers are not charged by render.rs.

    Measuring the whole block overstates cost. This pins the gap as real and
    positive rather than asserting a particular size.
    """
    whole_block_tokens = probe_codex.approx_tokens("x" * dojo.block_chars)
    assert dojo.entry_cost_tokens < whole_block_tokens


def test_alias_table_cost_is_a_body_difference_not_a_line_sum(truncating):
    """``aliased_metadata_overhead_cost`` rounds each whole body once.

    Summing per-line costs gives a different number — 65 against 24 on this
    fixture — and using it makes the budget appear 41 tokens smaller than it is,
    which is enough to misreport a listing that exactly fits as over budget.
    """
    line_sum = sum(probe_codex.line_cost_tokens(r) for r in truncating.root_lines)
    assert truncating.root_table_cost_tokens != line_sum
    assert truncating.root_table_cost_tokens == probe_codex.alias_table_cost_tokens(truncating.root_lines)


def test_vendor_parity_a_truncating_listing_exactly_fills_its_budget(truncating):
    """The strongest available check that this port matches render.rs.

    When Codex truncates, ``render_lines_with_description_budget`` spends the
    description budget down to the last token. So for a capture that truncated,
    entry cost must equal the limit minus the alias table cost **exactly** — not
    approximately. An off-by-one anywhere in the byte counting, the newline, or
    the ceiling division breaks this.
    """
    limit, unit = probe_codex.budget_for_window(272_000)
    assert (limit, unit) == (5_440, "tokens")
    assert truncating.entry_cost_tokens == limit - truncating.root_table_cost_tokens


def test_truncation_is_observable_and_unmarked(truncating):
    """Budget-driven truncation adds no suffix; the 1,024-char cap adds '...'.

    Two different mechanisms in render.rs. This fixture exercises the first: a
    description clipped mid-word with no marker of any kind, which is why a
    truncated listing is indistinguishable from short descriptions.
    """
    clipped = [
        e for e in truncating.entries
        if e.description and not e.description.rstrip().endswith((".", "!", "?", probe_codex.TRUNCATED_SKILL_DESCRIPTION_SUFFIX))
    ]
    assert clipped, "no mid-sentence descriptions; fixture may no longer truncate"
    assert not any(e.description.endswith("…") for e in clipped), "Codex does not use an ellipsis marker"


def test_budget_uses_the_full_window_not_the_effective_one():
    """5,440, not 5,168. session/mod.rs passes ``context_window`` unmodified."""
    assert probe_codex.budget_for_window(272_000)[0] == 5_440
    assert probe_codex.budget_for_window(int(272_000 * 0.95))[0] != 5_440


def test_unknown_window_falls_back_to_characters_not_a_guessed_token_count():
    """Either/or, never a combination."""
    assert probe_codex.budget_for_window(None) == (8_000, "characters")
    assert probe_codex.budget_for_window(0) == (8_000, "characters")


# --------------------------------------------------------------------------
# Codex: origin and scope classification
# --------------------------------------------------------------------------


def test_every_origin_is_proven_against_a_known_present_case(dojo):
    """Non-degeneracy floors, never totals (SC-04, SC-05)."""
    listing = probe_codex.classify(dojo, DOJO_SKILLS, CODEX_HOME, REPO_ROOT)
    origins = collections.Counter(e.origin for e in listing.entries)
    for origin in ("dojo-managed", "harness-bundled", "plugin", "foreign"):
        assert origins[origin] >= 1, f"no {origin} entry observed; detector unproven"
    assert origins["unknown"] == 0


def test_one_name_carries_two_distinct_origins(dojo):
    """Codex does not shadow across roots, so duplication is real and charged.

    ``skill-creator`` exists both as a dojo skill and as a Codex ``.system``
    entry, and both are listed. This is the live case motivating the spec's
    harness-equivalence declaration.
    """
    listing = probe_codex.classify(dojo, DOJO_SKILLS, CODEX_HOME, REPO_ROOT)
    by_name = collections.defaultdict(set)
    for entry in listing.entries:
        by_name[entry.name].add(entry.origin)
    multi = {n: o for n, o in by_name.items() if len(o) > 1}
    assert multi, "no name with two origins; the duplication case regressed"


def test_project_scope_is_detected_through_a_symlinked_root(truncating, tmp_path):
    """Codex reports the symlink's *target*, not the link.

    Every dojo checkout exposes its catalog as `.agents/skills -> ../skills`, so
    an unresolved comparison against the cwd finds project scope nowhere and
    returns a confident zero. The truncating fixture was captured from exactly
    that topology.
    """
    cwd = rebuild_capture_cwd(truncating, tmp_path)
    listing = probe_codex.classify(truncating, DOJO_SKILLS, CODEX_HOME, cwd)
    scopes = collections.Counter(e.scope for e in listing.entries)
    assert scopes["project"] >= 1, "project scope undetected through a symlinked root"
    assert scopes["user"] >= 1


def test_a_session_without_a_project_root_has_no_project_entries(dojo):
    """The negative case, with the positive one above as its control."""
    listing = probe_codex.classify(dojo, DOJO_SKILLS, CODEX_HOME, REPO_ROOT)
    assert all(e.scope == "user" for e in listing.entries)


def test_duplication_is_visible_and_charged_twice(truncating):
    """A collapsing model would understate demand (SC-04)."""
    names = collections.Counter(e.name for e in truncating.entries)
    duplicated = {n: c for n, c in names.items() if c > 1}
    assert len(duplicated) > 1, "fixture no longer exercises cross-root duplication"
    deduped = sum(
        next(e.cost_tokens for e in truncating.entries if e.name == name)
        for name in names
    )
    assert truncating.entry_cost_tokens > deduped


# --------------------------------------------------------------------------
# Claude Code
# --------------------------------------------------------------------------


def test_sent_and_loaded_are_different_numbers(claude_debug):
    """Using ``loaded`` restates the filesystem error in a new costume.

    Claude Code deduplicates by name across scopes, so a dojo session loads far
    more skills than it sends. The listing count is ``sent``.
    """
    assert claude_debug.loaded is not None and claude_debug.sent is not None
    assert claude_debug.sent < claude_debug.loaded


def test_demand_comes_from_the_debug_verdict(claude_debug):
    assert claude_debug.over_budget is True
    assert claude_debug.demand_chars > claude_debug.budget_chars
    assert claude_debug.ratio > 2


def test_budget_is_characters_end_to_end_with_no_token_conversion():
    """``context_tokens × 4 × fraction``, compared characters to characters."""
    assert probe_claude.budget_chars(200_000) == 8_000
    assert probe_claude.budget_chars(1_000_000) == 40_000
    # The same repository is conformant on one model and not the other, which is
    # why the model belongs to policy identity.
    assert probe_claude.budget_chars(1_000_000) > probe_claude.budget_chars(200_000)


def test_the_listing_is_found_by_its_opening_sentence_not_its_section(claude_request):
    """Both the real listing and dojo's own catalog live in ``messages``.

    dojo's SessionStart hook injects ``## Available Skills`` into the same
    section. The fixture deliberately retains both, so a parser that keyed on the
    section rather than the sentence would parse the wrong one and measure dojo
    injecting a catalog instead of the harness listing it.
    """
    body = json.loads((FIXTURES / "claude-request-dojo-2026-08-02.json").read_text())
    assert probe_claude.DECOY_OPENING in json.dumps(body), "fixture lost its decoy"
    assert probe_claude.LISTING_OPENING in json.dumps(body)
    names = {e.name for e in claude_request.entries}
    assert "## Available Skills" not in names
    assert len(names) > 10


def test_description_removal_is_detected_by_absence(claude_request):
    """Claude Code's severe degradation shape.

    Over budget, lower-priority skills render as a bare ``- name`` with no
    description at all. A 'listed is a prefix of source' check cannot catch this
    — there is no listed description to compare against — so it must be detected
    by absence. This fixture carries the shape live.
    """
    assert claude_request.description_removed >= 1
    bare = [e for e in claude_request.entries if e.shape == "description_removed"]
    assert all(e.description is None for e in bare)
    assert any(e.shape == "full" for e in claude_request.entries), "everything stripped; no contrast"


def test_the_elision_hazard_is_quantified_on_one_capture(claude_debug, claude_request):
    """The whole justification for computing cost from source.

    A harness that elides to fit produces output that always fits. On this
    capture the rendered block sits within a few percent of the budget while
    true demand is nearly three times it. A verifier calibrated on rendered
    output would report roughly 100% and certify the failure it exists to catch.
    """
    rendered_ratio = claude_request.rendered_chars / claude_debug.budget_chars
    demand_ratio = claude_debug.demand_chars / claude_debug.budget_chars
    assert rendered_ratio < 1.05, "rendered block no longer 'appears to fit'"
    assert demand_ratio > 2
    assert demand_ratio > rendered_ratio * 2


# --------------------------------------------------------------------------
# Staleness
# --------------------------------------------------------------------------


def test_a_perturbed_fingerprint_marks_dependent_evidence_stale():
    """EV-LEG-03: a harness or model change invalidates prior evidence."""
    recorded = {"harness": "codex", "version": "codex-cli 0.145.0", "model": "gpt-5.6-terra", "context_window": 272_000}
    assert probe_codex.is_stale(recorded, dict(recorded)) == []
    assert probe_codex.is_stale(recorded, {**recorded, "version": "codex-cli 0.146.0"}) == ["version"]
    assert probe_codex.is_stale(recorded, {**recorded, "context_window": 200_000}) == ["context_window"]
    # The model alone is enough, because the budget is a function of its window.
    assert "model" in probe_codex.is_stale(recorded, {**recorded, "model": "gpt-5.4"})


def test_claude_fingerprint_records_the_model():
    """Claude Code's budget moves with the context window, so the model is policy."""
    assert probe_claude.fingerprint("haiku")["model"] == "haiku"
    assert probe_claude.fingerprint("opus")["model"] == "opus"


@pytest.fixture
def claude_debug_under_budget() -> probe_claude.DebugResult:
    """A 1M-window capture of the same repository: no warning line at all."""
    return probe_claude.parse_debug(
        (FIXTURES / "claude-debug-dojo-1m-under-budget-2026-08-02.txt").read_text()
    )


def test_sent_is_read_without_help_from_the_over_budget_warning(claude_debug_under_budget):
    """Isolates the ``sent`` path, which the over-budget capture cannot.

    A mutation setting ``sent := loaded`` passed every test until this fixture
    existed: on an over-budget capture the warning line also carries a skill
    count, and letting it overwrite ``sent`` masked the error. Here there is no
    warning, so ``sent`` has only one possible source.
    """
    result = claude_debug_under_budget
    assert result.over_budget is False
    assert result.demand_chars is None
    assert result.warned_skills is None
    assert result.loaded is not None and result.sent is not None
    assert result.sent < result.loaded


def test_the_same_repository_is_conformant_on_one_model_and_not_another(
    claude_debug, claude_debug_under_budget
):
    """Why the model belongs to policy identity (SC-04).

    Identical catalog, identical machine, same day — over budget on a 200k
    window and silent on a 1M one. A fits-proof against one model says nothing
    about the other, which is what SC-03 now requires.
    """
    assert claude_debug.over_budget is True
    assert claude_debug_under_budget.over_budget is False
    assert claude_debug.sent == claude_debug_under_budget.sent


def test_the_two_skill_counts_are_cross_checked_not_reconciled(claude_debug):
    """A disagreement would be a harness change, and must surface as one."""
    assert claude_debug.warned_skills == claude_debug.sent
    assert claude_debug.counts_disagree is False


def test_fingerprints_degrade_rather_than_crash_without_the_harness(monkeypatch):
    """CI has neither binary, and only fixture-driven tests run there.

    An unknown version is a legitimate fingerprint state: ``is_stale`` compares
    field by field, so evidence produced against it can never be mistaken for
    fresh. Raising instead would make the whole module unimportable in CI.
    """
    monkeypatch.setenv("PATH", "")
    result = probe_claude.fingerprint("haiku")
    assert result["model"] == "haiku"
    assert result["version"] is None
    assert probe_codex.is_stale({"version": "codex-cli 0.145.0"}, {"version": None}) == ["version"]
