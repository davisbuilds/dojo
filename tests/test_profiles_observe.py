"""Task 4 — effective-catalog observation.

The strongest test here is `test_computed_demand_agrees_with_the_probes_own_figure`.
Every other test checks a rule in isolation; that one checks the whole cost model
against a number the harness produced itself, and it is what caught a frontmatter
parser that silently returned two characters where the real description was four
hundred.
"""

from __future__ import annotations

import collections
import hashlib
import json
import shutil
import sys
from dataclasses import replace
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "profiles"
POLICIES = REPO_ROOT / "profiles" / "policies"
SKILLS = REPO_ROOT / "skills"
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from profiles import probe_claude, probe_codex  # noqa: E402
from profiles.budget import assess, load_policy  # noqa: E402
from profiles.observe import (  # noqa: E402
    PLUGIN_CACHE,
    observe_claude,
    observe_codex,
    source_descriptions,
)


@pytest.fixture
def codex_policy():
    return load_policy(POLICIES / "codex.yaml")


@pytest.fixture
def claude_1m():
    return load_policy(POLICIES / "claude-code-1m.yaml")


def codex_listing(name="codex-prompt-input-dojo-2026-08-02.json", cwd=REPO_ROOT):
    payload = json.loads((FIXTURES / name).read_text())
    listing = probe_codex.parse_block(probe_codex.extract_block(payload))
    return probe_codex.classify(listing, SKILLS, None, cwd)


# --------------------------------------------------------------------------
# The probe decides membership
# --------------------------------------------------------------------------


def test_the_filesystem_never_adds_an_entry_the_probe_did_not_list(codex_policy, tmp_path):
    """The rule this program has broken six times.

    A skill present on disk but absent from the listing contributes nothing —
    no entry, no cost. `microsoft-foundry` (installed, disabled) and
    `review-agent` (bundled, unlisted) are both live instances.
    """
    fake_root = tmp_path / "skills"
    shutil.copytree(SKILLS, fake_root)
    invented = fake_root / "not-in-any-listing"
    invented.mkdir()
    (invented / "SKILL.md").write_text(
        "---\nname: not-in-any-listing\ndescription: Should never be observed.\n---\n"
    )

    observation = observe_codex(codex_listing(), codex_policy, fake_root)
    assert "not-in-any-listing" not in {e.name for e in observation.entries}

    result = assess(observation.as_budget_entries(), codex_policy, root_lines=observation.root_lines, surface="codex-tui")
    baseline = observe_codex(codex_listing(), codex_policy, SKILLS)
    assert result.demand == assess(
        baseline.as_budget_entries(), codex_policy, root_lines=baseline.root_lines,
        surface="codex-tui",
    ).demand


def test_an_unclassified_listing_is_refused(codex_policy):
    """Failing closed: unknown origins would collapse into one bucket silently."""
    payload = json.loads((FIXTURES / "codex-prompt-input-dojo-2026-08-02.json").read_text())
    unclassified = probe_codex.parse_block(probe_codex.extract_block(payload))
    with pytest.raises(ValueError, match="unclassified"):
        observe_codex(unclassified, codex_policy, SKILLS)


# --------------------------------------------------------------------------
# Cost
# --------------------------------------------------------------------------


def test_computed_demand_agrees_with_the_probes_own_figure(codex_policy):
    """An end-to-end check of the cost model against the harness's own number.

    The probe reports what Codex charged for the listing it rendered. Demand is
    computed independently from source frontmatter. On a target with no
    degradation the two must agree closely — and when they did not, the cause
    was real: the frontmatter parser was regex-based and returned one or two
    characters for the five skills using a folded YAML scalar, four of which are
    overlay members. The gap was 190 tokens and pointed straight at it.
    """
    listing = codex_listing()
    observation = observe_codex(listing, codex_policy, SKILLS)
    result = assess(observation.as_budget_entries(), codex_policy, root_lines=observation.root_lines, surface="codex-tui")

    assert result.degradations == (), "fixture is degraded; the comparison would not hold"
    drift = abs(result.demand - listing.charged_tokens)
    assert drift <= listing.charged_tokens * 0.01, (
        f"computed {result.demand} against probe-charged {listing.charged_tokens}"
    )


def test_source_descriptions_survive_folded_yaml():
    """Parsed as YAML, never by regex.

    `description: >-` continues across lines; a `^description:(.*)$` match takes
    the first line only and returns a couple of characters. Both `engineering`
    anchors use folded scalars, so the overlay's cost was understated by roughly
    1,200 characters until this was fixed.
    """
    descriptions = source_descriptions(SKILLS)
    folded = [
        p.name for p in sorted(SKILLS.iterdir())
        if (p / "SKILL.md").exists()
        and any(line.startswith("description: >") or line.startswith("description: |")
                for line in (p / "SKILL.md").read_text().split("---")[1].splitlines())
    ]
    assert folded, "catalog no longer contains a folded description; this test is inert"
    for name in folded:
        assert len(descriptions[name]) > 50, f"{name} parsed as {descriptions[name]!r}"

    for name, text in descriptions.items():
        real = yaml.safe_load((SKILLS / name / "SKILL.md").read_text().split("---")[1])["description"]
        assert text == real.strip()


def test_entries_without_a_readable_source_are_still_charged(codex_policy):
    """SC-04 counts foreign, bundled, and plugin entries; they occupy the budget.

    Costing them at zero understated a live target by 20%, in the direction that
    makes an over-budget catalog look safe. Their cost basis is recorded as
    observation-derived so evidence can say it is a floor.
    """
    observation = observe_codex(codex_listing(), codex_policy, SKILLS)
    basis = observation.cost_basis_counts
    assert basis["observed"] >= 1 and basis["source"] >= 1

    entries = observation.as_budget_entries()
    unreadable = [e for e in entries if e["cost_basis"] == "observed"]
    assert unreadable, "no observation-derived entries; this test is inert"
    assert all(e["source_description"] for e in unreadable), "charged as if they had no description"


# --------------------------------------------------------------------------
# Origin, scope, and shadowing
# --------------------------------------------------------------------------


def test_every_origin_is_present_as_a_non_degeneracy_floor(codex_policy):
    observation = observe_codex(codex_listing(), codex_policy, SKILLS)
    origins = collections.Counter(e.origin for e in observation.entries)
    for origin in ("dojo-managed", "harness-bundled", "plugin", "foreign"):
        assert origins[origin] >= 1, f"no {origin} entry; detector unproven"


def test_codex_plugins_are_classified_by_the_codex_cache_not_the_claude_one(codex_policy):
    """The standardizer's needle is Claude-only and would report zero here.

    Classification happens once, in `probe_codex.classify`, from the capture's
    own inferred home. This module deliberately does not re-classify: a mutation
    swapping the needle here passed all 14 tests, which proved the line was dead
    rather than defensive.
    """
    observation = observe_codex(codex_listing(), codex_policy, SKILLS)
    plugins = [e for e in observation.entries if e.origin == "plugin"]
    assert plugins
    assert all(PLUGIN_CACHE["codex"] in e.locator for e in plugins)
    assert not any(PLUGIN_CACHE["claude-code"] in e.locator for e in plugins)


def test_observation_does_not_reclassify_what_the_probe_already_labelled(codex_policy):
    """Pins the removal: origins must pass through untouched.

    If this module ever re-derives an origin, the two classifiers can disagree
    and the evidence will report whichever ran last.
    """
    listing = codex_listing()
    before = {(e.name, e.locator): e.origin for e in listing.entries}
    observation = observe_codex(listing, codex_policy, SKILLS)
    after = collections.Counter(e.origin for e in observation.entries)
    assert after == collections.Counter(before.values())


def test_shadowing_follows_the_policy_in_both_directions(codex_policy, tmp_path):
    """SC-04: counted "according to actual harness behavior", which differs.

    Flipping only `shadows_by_name` must flip the outcome. A model that always
    collapses is wrong for Codex; one that never collapses is wrong for Claude
    Code. Hard-coding either passes half the fixtures and fails silently on the
    other harness.
    """
    listing = codex_listing("codex-prompt-input-truncating-2026-08-02.json", cwd=tmp_path)
    assert listing.entries

    not_shadowing = observe_codex(listing, codex_policy, SKILLS)
    duplicated = not_shadowing.duplicated_names
    assert duplicated, "fixture no longer exercises duplication"
    assert any(e.duplicate_of for e in not_shadowing.entries)

    shadowing = observe_codex(listing, replace(codex_policy, shadows_by_name=True), SKILLS)
    assert not any(e.duplicate_of for e in shadowing.entries)


def test_project_scope_is_read_per_harness(codex_policy, claude_1m):
    assert codex_policy.project_scope_root == ".agents/skills"
    assert claude_1m.project_scope_root == ".claude/skills"


def test_the_third_root_has_no_live_consumer(codex_policy, tmp_path):
    """`.agent/skills` is read by neither harness, so it yields no project scope."""
    (tmp_path / ".agent").mkdir()
    (tmp_path / ".agent" / "skills").symlink_to(SKILLS)
    observation = observe_codex(codex_listing(cwd=tmp_path), codex_policy, SKILLS)
    assert all(e.scope != "project" for e in observation.entries)


# --------------------------------------------------------------------------
# Claude Code, and the authority boundary
# --------------------------------------------------------------------------


def test_claude_listing_count_is_sent_not_loaded(claude_1m):
    """94 loaded, 75 sent. Using `loaded` restates the filesystem error."""
    body = json.loads((FIXTURES / "claude-request-dojo-2026-08-02.json").read_text())
    result = probe_claude.classify(probe_claude.parse_request(body), SKILLS,
                                   REPO_ROOT / ".claude" / "skills")
    debug = probe_claude.parse_debug((FIXTURES / "claude-debug-dojo-2026-08-02.txt").read_text())

    observation = observe_claude(result, debug, claude_1m, SKILLS)
    assert len(observation.entries) == debug.sent
    assert debug.loaded > debug.sent
    assert observation.unsupported == []


def test_a_sent_count_mismatch_is_reported_not_reconciled(claude_1m):
    """A parser that drops entries must surface it, not quietly agree with itself."""
    body = json.loads((FIXTURES / "claude-request-dojo-2026-08-02.json").read_text())
    result = probe_claude.classify(probe_claude.parse_request(body), SKILLS, None)
    debug = probe_claude.parse_debug((FIXTURES / "claude-debug-dojo-2026-08-02.txt").read_text())
    debug.sent = 999

    observation = observe_claude(result, debug, claude_1m, SKILLS)
    assert any("999" in u for u in observation.unsupported)


def test_a_policy_for_the_wrong_harness_is_refused(claude_1m):
    with pytest.raises(ValueError, match="expected a codex policy"):
        observe_codex(codex_listing(), claude_1m, SKILLS)


def test_no_observation_path_writes(codex_policy, tmp_path):
    """SC-12 and the spec's Verifier authority: read-only, by construction."""
    tree = tmp_path / "skills"
    shutil.copytree(SKILLS, tree)

    def digest(root: Path) -> str:
        h = hashlib.sha256()
        for path in sorted(root.rglob("*")):
            h.update(str(path.relative_to(root)).encode())
            if path.is_file():
                h.update(path.read_bytes())
        return h.hexdigest()

    before = digest(tree)
    observation = observe_codex(codex_listing(), codex_policy, tree)
    assess(observation.as_budget_entries(), codex_policy, root_lines=observation.root_lines, surface="codex-tui")
    assert digest(tree) == before


def test_only_managed_entries_take_a_canonical_description(codex_policy):
    """PR #59 review, P2. A shared name is not a shared skill.

    Codex's bundled `skill-creator` sits beside dojo's in this fixture and their
    descriptions differ. Attaching dojo's text to the bundled entry scored the
    wrong content *and* fabricated a truncation signal — listed then differs
    from "source" for a reason that has nothing to do with elision.

    The fix was made before this test existed, and a mutation reverting it passed
    all 34 tests, which is why the test is here.
    """
    observation = observe_codex(codex_listing(), codex_policy, SKILLS)
    duplicated = [e for e in observation.entries if e.name == "skill-creator"]
    assert len(duplicated) == 2, "fixture no longer carries the same name twice"

    managed = next(e for e in duplicated if e.origin == "dojo-managed")
    bundled = next(e for e in duplicated if e.origin == "harness-bundled")

    assert managed.source_description, "the managed copy must carry canonical text"
    assert bundled.source_description is None, "a bundled entry took dojo's description"
    assert bundled.listed_description != managed.source_description, (
        "fixture no longer distinguishes the two texts; this test would be inert"
    )


def test_a_non_managed_entry_never_produces_a_false_truncation_signal(codex_policy):
    """The consequence of the bug above, asserted at the detector.

    With dojo's description attached, the bundled entry's listed text differs
    from its "source" and the degradation detector reads that as clipping.
    """
    from profiles.budget import detect_degradation

    observation = observe_codex(codex_listing(), codex_policy, SKILLS)
    assert detect_degradation(observation.as_budget_entries(), codex_policy) == ()
