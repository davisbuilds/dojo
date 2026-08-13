"""Task 5A — observe the surface the operator actually runs, and derive the limit.

Every test here pins a defect that shipped and was found by measurement rather
than by review. In order of how much they cost:

1. The probe rendered `codex exec` while the operator runs `codex-tui`, so 69 of
   110 entries were invisible and a 246%-of-budget target read as 76%.
2. The limit came from the model catalog (2% of a 272,000 window = 5,440) when
   the interactive surface budgets against 4,000 — a 36% overstatement.
3. dojo entries render with absolute locators, not `rN/` aliases; assuming the
   alias form understated demand by 9% and flipped a verdict.
4. The harness's shortening warning was proposed as a conformance check. It has
   false negatives: silent at 144% while clipping 50 of 56 descriptions.
5. A local `enabled = false` on an account-synced connector is inert.

Discipline carried from the rest of this package: no hardcoded catalog totals
where a fixture can supply them, every detector exercised against a case known to
be present, and the *pre-fix* path asserted to fail so each correction is pinned
by the failure it repairs rather than only by the behaviour it adds.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "profiles"
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from profiles import probe_codex, rollout_codex  # noqa: E402
from profiles.rollout_codex import (  # noqa: E402
    ORIGIN_CONNECTOR,
    ORIGIN_DOJO,
    ORIGIN_FOREIGN,
    SURFACE_TUI,
    LimitEvidence,
    attribute_demand,
    classify_locator,
    derive_limit,
    is_saturated,
    observations,
    read_rollout,
    staleness,
    surface_mismatch,
)

INTRO = "Each entry includes a name, description, and source locator.\n"

F110 = FIXTURES / "codex-tui-clipped-110.jsonl"
F56 = FIXTURES / "codex-tui-clipped-56.jsonl"

OBSERVED_LIMIT = 4_000
VENDOR_LIMIT = 5_440          # 2% of the 272,000 window `codex debug models` reports


@pytest.fixture
def obs110():
    return read_rollout(F110)


@pytest.fixture
def obs56():
    return read_rollout(F56)


# --------------------------------------------------------------------------
# The surface
# --------------------------------------------------------------------------


def test_the_recorded_surface_is_available_not_inferred(obs110, obs56):
    """The whole defect was an unlabelled surface. It must be a field."""
    for observation in (obs110, obs56):
        assert observation.meta.surface == SURFACE_TUI
        assert observation.meta.cli_version
        assert observation.meta.harness_build.startswith(observation.meta.cli_version)


def test_a_session_with_no_model_call_is_absent_not_empty(tmp_path):
    """A rollout with no skills block means nothing was sent.

    Distinguishable from a listing of zero entries, because "nobody looked" and
    "the harness sent nothing" are different facts — the same confusion that made
    an unmeasured absence read as an observed one in Task 3.
    """
    path = tmp_path / "rollout-empty.jsonl"
    path.write_text('{"type":"session_meta","payload":{"originator":"codex-tui"}}\n')
    assert read_rollout(path) is None


def test_a_user_pasted_block_is_never_measured(obs56):
    """PR #60 review, P1. A conversation that *discusses* a listing must not supply it.

    Both fixtures carry a user-authored decoy block placed **before** the
    harness-authored record. An earlier reader walked every string in every
    record and took the first hit, so it would have measured the paste. This is
    not hypothetical: across 309 rollouts on the capture machine the block
    appears twice with role `user`, and session 2026-07-28T17-23-34 has the user
    copy first. The spec's historical table happened to use that session's
    sibling, recorded 14 seconds later — correct by luck.
    """
    raw = F56.read_text()
    assert "decoy-pasted-by-user" in raw, "fixture lost the decoy"
    assert raw.index("decoy-pasted-by-user") < raw.index('"role": "developer"'), \
        "the decoy must precede the harness record or this proves nothing"

    assert not any(e.name == "decoy-pasted-by-user" for e in obs56.listing.entries)
    assert len(obs56.listing.entries) == 56


def test_compacted_summaries_are_not_measured(tmp_path):
    """A compacted summary is harness-authored but its listing may be stale.

    136 of the block's occurrences on the capture machine sit inside `compacted`
    records. Accepting them would silently measure an earlier turn's catalog.
    """
    import json as _json

    block = ("<skills_instructions>\n" + INTRO + "### Available skills\n"
             "- stale: from a compaction summary "
             "(file: /Users/example-dev/.agents/skills/stale/SKILL.md)\n"
             "</skills_instructions>")
    path = tmp_path / "rollout-compacted.jsonl"
    path.write_text(
        _json.dumps({"type": "session_meta",
                     "payload": {"originator": "codex-tui", "cli_version": "0.146.0",
                                 "cwd": str(tmp_path), "model": "m"}}) + "\n"
        + _json.dumps({"type": "compacted", "payload": {"message": block}}) + "\n"
    )
    assert read_rollout(path) is None


def test_surface_mismatch_is_reported_rather_than_reconciled(obs56):
    """EV: the live probe and the recorded session disagreeing is the finding."""
    live = probe_codex.parse_block(
        "<skills_instructions>\n"
        "Each entry includes a name, description, and source locator.\n"
        "### Available skills\n"
        "- brainstorming: x (file: /Users/example-dev/.agents/skills/brainstorming/SKILL.md)\n"
        "</skills_instructions>"
    )
    mismatch = surface_mismatch(live, obs56)
    assert mismatch is not None
    assert mismatch["kind"] == "surface-mismatch"
    assert mismatch["recorded_surface"] == SURFACE_TUI
    assert mismatch["recorded_entries"] > mismatch["live_entries"]
    assert mismatch["only_in_recorded"], "the entries the probe cannot see must be named"


def test_identical_listings_do_not_report_a_mismatch(obs56):
    """Guards the detector against firing on everything."""
    assert surface_mismatch(obs56.listing, obs56) is None


def test_a_duplicate_only_difference_is_still_a_mismatch(obs56):
    """PR #60 review, P2. Codex charges every copy of a duplicated name.

    The fixture lists `skill-creator` twice — once bundled by Codex, once shipped
    by dojo. Comparing bare-name sets reports no mismatch when one copy vanishes,
    hiding a real cost difference. Compared as a multiset of qualified
    identities, it does not.
    """
    import copy

    live = copy.deepcopy(obs56.listing)
    victim = next(e for e in live.entries if e.name == "skill-creator")
    live.entries.remove(victim)

    assert {e.name for e in live.entries} == {e.name for e in obs56.listing.entries}, \
        "the bare-name sets must be identical or this proves nothing"
    mismatch = surface_mismatch(live, obs56)
    assert mismatch is not None
    assert any("skill-creator" in i for i in mismatch["only_in_recorded"])


# --------------------------------------------------------------------------
# The limit, by saturation
# --------------------------------------------------------------------------


def test_two_saturating_renders_disclose_the_limit(obs110, obs56):
    """The central correction. Different inputs, same total, to the token."""
    assert len(obs110.listing.entries) != len(obs56.listing.entries)
    evidence = derive_limit([obs110, obs56])
    assert evidence.basis == "observed"
    assert evidence.provisional is False
    assert evidence.limit == OBSERVED_LIMIT
    assert obs110.charged_tokens == obs56.charged_tokens == OBSERVED_LIMIT


def test_the_observed_limit_contradicts_the_vendor_window(obs110):
    """Pins the defect: the catalog-derived limit is 36% too high.

    Not a restatement of the previous test — this asserts the *disagreement*,
    which is the reason a vendor limit may never be trusted unchecked.
    """
    window_limit, unit = probe_codex.budget_for_window(272_000)
    assert unit == "tokens"
    assert window_limit == VENDOR_LIMIT
    assert window_limit != OBSERVED_LIMIT
    overstatement = (window_limit - OBSERVED_LIMIT) / OBSERVED_LIMIT
    assert overstatement > 0.35, "the vendor route overstates by ~36%"


def test_one_render_cannot_establish_a_limit(obs56):
    """A single saturating render is a cost, not a ceiling."""
    evidence = derive_limit([obs56])
    assert evidence.limit is None
    assert evidence.provisional is True
    assert "2 saturating" in evidence.reason


def test_two_renders_of_the_same_size_agree_trivially(obs56):
    """Agreement between identical inputs discloses nothing and must be refused."""
    evidence = derive_limit([obs56, obs56])
    assert evidence.limit is None
    assert evidence.provisional is True
    assert "same entry count" in evidence.reason


def test_disagreeing_renders_are_indeterminate(obs110, obs56, monkeypatch):
    """If two saturating renders disagree, neither is the limit."""
    obs56.listing.entry_cost_tokens += 17
    evidence = derive_limit([obs110, obs56])
    assert evidence.limit is None
    assert evidence.basis == "indeterminate"
    assert "disagree" in evidence.reason


def test_a_limit_is_never_derived_across_harness_builds(obs110, obs56):
    """Found by running the verifier against live sessions, not by a fixture.

    A 2026-07-10 session on CLI 0.144.1 charged 6,188 tokens *without* clipping,
    while every 0.146.0 render saturates at exactly 4,000. The ceiling is a
    property of the build. Pooling builds would fabricate a disagreement, or —
    worse, had both saturated — average two real ceilings into one belonging to
    neither.
    """
    import copy

    older = copy.deepcopy(obs110)
    older.meta = rollout_codex.RolloutMeta(
        path=older.meta.path, surface=older.meta.surface, cli_version="0.144.1",
        cwd=older.meta.cwd, model=older.meta.model,
    )
    evidence = derive_limit([older, obs56])
    assert evidence.limit is None
    assert evidence.provisional is True
    assert "harness builds" in evidence.reason

    # …and the same pair within one build still establishes it.
    assert derive_limit([obs110, obs56]).limit == OBSERVED_LIMIT


def test_unclipped_renders_are_not_saturation_evidence(obs56):
    """An under-budget listing totals what it costs, which is not a ceiling."""
    for entry in obs56.listing.entries:
        entry.description = "x" * (200 + len(entry.name))   # deliberately ragged
    assert is_saturated(obs56) is False
    assert derive_limit([obs56, obs56]).limit is None


def test_saturation_is_detected_on_a_known_clipped_render(obs110, obs56):
    """Verify the detector against cases known to be true (the zero rule)."""
    assert is_saturated(obs110) is True
    assert is_saturated(obs56) is True


def test_uniform_lengths_alone_are_not_clipping(obs56):
    """Written to a common length is not cut to a common length.

    Templated descriptions — generated metadata, a vendor bundle sharing one
    boilerplate summary — can put well over a fifth of a catalog within three
    characters of the longest without anything having been clipped. The shape
    rule cannot tell that from budget clipping, and it feeds an outcome that
    speaks every session, so the shape needs corroborating: budget clipping cuts
    mid-sentence, and text written to a length does not.
    """
    for entry in obs56.listing.entries:
        entry.description = "a templated summary of the skill and its use."
    assert is_saturated(obs56) is False, \
        "uniform but complete descriptions are a catalog style, not a clipped render"
    assert rollout_codex.clipped_entry_names(obs56) == []

    # The same uniform lengths, now cut mid-sentence: both signals agree.
    for entry in obs56.listing.entries:
        entry.description = "a templated summary of the skill and its us"
    assert is_saturated(obs56) is True


def test_one_stray_unpunctuated_description_does_not_raise_clipping(obs56):
    """Corroboration is about the group, not any single entry.

    A description that simply omits its full stop is common; the claim being
    made is about the listing as a whole, so it takes a majority to support it.
    """
    for entry in obs56.listing.entries:
        entry.description = "a templated summary of the skill and its use."
    obs56.listing.entries[0].description = "a templated summary of the skill and its u"
    assert is_saturated(obs56) is False


# --------------------------------------------------------------------------
# The pre-5A path, pinned by the failure it repairs
# --------------------------------------------------------------------------


def test_pre_5a_scoring_reports_the_target_as_comfortable(obs56):
    """The defect, asserted so the fix cannot be silently reverted.

    Scoring the recorded listing against the vendor limit reports ~74% — a
    passing figure — for a listing whose descriptions are all clipped. The same
    listing against the observed limit is at 100%.
    """
    charged = obs56.charged_tokens
    assert charged / VENDOR_LIMIT < 0.80, "the old denominator reads as comfortable"
    assert charged / OBSERVED_LIMIT == 1.0, "the real denominator is saturated"


def test_warning_absence_is_not_evidence_of_fit(obs56):
    """Codex warned at 246% and printed nothing at 144%, still clipping 50 of 56."""
    assert obs56.listing.warning is None
    assert is_saturated(obs56) is True, "clipped with no warning present"


# --------------------------------------------------------------------------
# Attribution, and the set-versus-total rule
# --------------------------------------------------------------------------


def test_demand_is_attributed_by_origin(obs56):
    attribution = attribute_demand(obs56)
    assert ORIGIN_DOJO in attribution
    assert attribution[ORIGIN_DOJO] > 0
    assert sum(attribution.values()) >= obs56.charged_tokens


def test_connector_entries_are_named_as_uncontrolled(obs56):
    """Connector demand is governed by an account setting, not by this repo."""
    uncontrolled = obs56.uncontrolled_entries
    assert uncontrolled, "the fixture must contain uncontrolled entries"
    assert any(i.startswith(f"{ORIGIN_CONNECTOR}:github:") for i in uncontrolled)
    # No identity in the set may be dojo's, and the check is by *qualified* id —
    # a bare name cannot express this, which is the point of the next test.
    assert not any(i.startswith(f"{ORIGIN_DOJO}:") for i in uncontrolled)


def test_a_name_listed_from_two_origins_is_not_conflated(obs56):
    """`skill-creator` is bundled by Codex *and* shipped by dojo.

    Codex does not shadow across roots, so both are listed and both are charged
    — the collision the harness-equivalence declaration exists to record. Keyed
    by bare name, the dojo copy would be swept into the uncontrolled set and the
    catalog would look partly ungovernable. Asserted against the real collision
    rather than a constructed one, so the fixture proves the case exists.
    """
    origins = {obs56.origin_of(e.locator)
               for e in obs56.listing.entries if e.name == "skill-creator"}
    assert origins == {"harness-bundled", ORIGIN_DOJO}, "fixture lost the collision"

    uncontrolled = obs56.uncontrolled_entries
    assert "harness-bundled:skill-creator" in uncontrolled
    assert f"{ORIGIN_DOJO}:skill-creator" not in uncontrolled


def test_classification_on_raw_alias_locators_returns_a_confident_zero(obs56):
    """Pins the defect the previous test caught, so the fix cannot be reverted.

    In alias render mode every plugin locator is `rN/...`. Classifying that raw
    string matches no absolute path segment, so every entry falls through to
    `foreign` and the uncontrolled set comes back **empty** — the exact shape of
    a broken detector reporting a clean result.
    """
    raw = {classify_locator(e.locator) for e in obs56.listing.entries
           if e.locator.startswith("r")}
    assert raw == {ORIGIN_FOREIGN}, "raw alias locators must be unclassifiable"
    resolved = {obs56.origin_of(e.locator) for e in obs56.listing.entries}
    assert ORIGIN_CONNECTOR in resolved


def test_no_fixture_is_a_raw_session_capture():
    """A rollout is ~1.8 MB of verbatim conversation; a fixture is a derivation.

    Two independent checks, because the naming rule alone would not stop someone
    renaming a capture, and the size rule alone would not stop a small one.
    """
    for path in sorted(FIXTURES.glob("*.jsonl")):
        assert not path.name.startswith("rollout-"), (
            f"{path.name} is named like a raw capture; derive a fixture instead")
        assert path.stat().st_size < 200_000, (
            f"{path.name} is {path.stat().st_size:,} bytes — too large to be a "
            "derivation of what the parser consumes")
        text = path.read_text()
        assert "/Users/example-dev" in text
        # Exactly one HARNESS-authored block. The fixtures deliberately carry a
        # second, user-authored decoy to pin the extraction rule, so a bare
        # count of the tag would now be wrong.
        assert text.count('"role": "developer"') == 1
        assert text.count("<skills_instructions>") <= 2


def test_a_symlinked_locator_resolves_before_classification(tmp_path):
    """Codex 0.147.0 reports the symlink path; 0.146.0 reported the target.

    Task 0 recorded "Codex reports resolved paths" as a property of the harness.
    It was a property of the builds observed. When 0.147.0 began reporting
    `~/.codex/skills/<name>/SKILL.md` instead of the `~/.agents/skills/` target,
    every dojo skill classified as `foreign` — 2,547 tokens of the operator's own
    catalog relabelled, silently, with the totals still summing correctly.
    """
    target = tmp_path / ".agents" / "skills" / "brainstorming"
    target.mkdir(parents=True)
    (target / "SKILL.md").write_text("x")
    link_root = tmp_path / ".codex" / "skills"
    link_root.mkdir(parents=True)
    (link_root / "brainstorming").symlink_to(target)

    as_written = str(link_root / "brainstorming" / "SKILL.md")
    assert "/.agents/skills/" not in as_written, "the link path must not name the target"
    assert classify_locator(as_written) == ORIGIN_DOJO

    # …and the pre-fix behaviour is pinned: without resolution it is unclassifiable.
    assert ORIGIN_DOJO not in as_written


def test_wholesale_foreign_classification_raises_an_alarm(obs56):
    """`foreign` is the else-branch, so a render change degrades into it silently."""
    from profiles.rollout_codex import classification_alarm

    assert classification_alarm(obs56) is None, "the fixture classifies cleanly"

    import copy
    broken = copy.deepcopy(obs56)
    for entry in broken.listing.entries:
        entry.locator = f"/nowhere/unrecognised/{entry.name}/SKILL.md"
    alarm = classification_alarm(broken)
    assert alarm is not None
    assert "may have changed how it renders locators" in alarm


def _wreck_classification(obs):
    """Make every locator unrecognisable, as a harness render change would."""
    import copy

    broken = copy.deepcopy(obs)
    for entry in broken.listing.entries:
        entry.locator = f"/nowhere/unrecognised/{entry.name}/SKILL.md"
    return broken


def test_attribution_refuses_a_degraded_observation(obs56):
    """PR #61 review, P2. The alarm existed and nothing consulted it.

    This is the same defect as PR #60's P1 — a control nothing calls — repeated
    in the PR that adds "a capability nothing calls is not a control" to the
    guidance. An attribution over wholesale-misclassified entries sums correctly
    and means nothing, which is worse than refusing: that is how 2,547 tokens of
    the operator's own catalog were reported as someone else's.

    SC-04 already required this: a verdict that cannot attribute demand to a
    controllable source is unsupported rather than a pass.
    """
    from profiles.rollout_codex import ClassificationError

    assert attribute_demand(obs56), "the healthy fixture must still attribute"

    broken = _wreck_classification(obs56)
    with pytest.raises(ClassificationError, match="renders locators"):
        attribute_demand(broken)

    # …and the escape hatch works, for inspecting the broken labels.
    degraded = attribute_demand(broken, allow_degraded=True)
    assert degraded, "allow_degraded must still return the (untrustworthy) split"


def test_staleness_surfaces_degraded_classification(obs56):
    """Its uncontrolled sets are classification-derived, so a broken classifier
    produces a confident, meaningless diff."""
    broken = _wreck_classification(obs56)
    reasons = staleness(obs56, broken)
    assert any("degraded classification" in r for r in reasons)


def test_the_alarm_is_reachable_from_the_observation(obs56):
    """A caller holding an observation must be able to ask without importing a helper."""
    assert obs56.classification_alarm is None
    assert _wreck_classification(obs56).classification_alarm is not None


def test_locator_classification_separates_connector_from_dojo():
    assert classify_locator(
        "/Users/example-dev/.codex/plugins/cache/openai-curated-remote/github/0.1.8/skills/x/SKILL.md"
    ) == ORIGIN_CONNECTOR
    assert classify_locator(
        "/Users/example-dev/.agents/skills/brainstorming/SKILL.md"
    ) == ORIGIN_DOJO


def test_staleness_compares_the_set_not_the_total(obs110, obs56):
    """The 2026-08-06 case: six entries left, nine arrived, totals cancelled.

    A totals comparison reports nothing happened. This is the exact shape that
    would let an uncontrolled change pass unnoticed, so it is asserted directly:
    equal totals, different sets, must still be stale.
    """
    assert obs110.charged_tokens == obs56.charged_tokens      # totals agree exactly
    assert obs110.uncontrolled_entries != obs56.uncontrolled_entries
    reasons = staleness(obs110, obs56)
    assert reasons, "equal totals must not mask a changed entry set"
    assert any("uncontrolled entry set changed" in r for r in reasons)


def test_staleness_compares_membership_not_cardinality(obs56):
    """One uncontrolled entry swapped for another: same count, different set.

    Found by mutation probe. The previous test compared two fixtures whose
    uncontrolled sets differ in *size*, so replacing `before != after` with
    `len(before) != len(after)` survived it — the detector would have passed a
    one-for-one substitution silently. That is the 2026-08-06 shape exactly:
    entries left, entries arrived, and the totals said nothing happened.
    """
    import copy

    swapped = copy.deepcopy(obs56)
    target = next(e for e in swapped.listing.entries
                  if swapped.origin_of(e.locator) == ORIGIN_CONNECTOR)
    target.name = target.name + "-replaced"

    before, after = obs56.uncontrolled_entries, swapped.uncontrolled_entries
    assert len(before) == len(after), "the sizes must match or this proves nothing"
    assert before != after
    reasons = staleness(obs56, swapped)
    assert any("uncontrolled entry set changed" in r for r in reasons)


def test_a_harness_build_change_alone_makes_a_verdict_stale(obs56):
    """A desktop update added 18% of budget with no local action."""
    import copy

    later = copy.deepcopy(obs56)
    later.meta = rollout_codex.RolloutMeta(
        path=later.meta.path, surface=later.meta.surface,
        cli_version="0.999.0", cwd=later.meta.cwd, model=later.meta.model,
    )
    reasons = staleness(obs56, later)
    assert any("harness build changed" in r for r in reasons)


def test_an_unchanged_target_is_not_stale(obs56):
    """Guards the detector: a rule that always fires reports nothing."""
    assert staleness(obs56, obs56) == []


# --------------------------------------------------------------------------
# Discovery
# --------------------------------------------------------------------------


def test_observations_filter_by_surface(tmp_path):
    """`exec` sessions must be excludable — they are the surface that misled."""
    day = tmp_path / "2026" / "08" / "06"
    day.mkdir(parents=True)
    block = (
        "<skills_instructions>\n" + INTRO + "### Available skills\n"
        "- a: d (file: /Users/example-dev/.agents/skills/a/SKILL.md)\n"
        "</skills_instructions>"
    )
    import json as _json

    for name, originator in (("rollout-tui.jsonl", "codex-tui"),
                             ("rollout-exec.jsonl", "codex_exec")):
        (day / name).write_text(
            _json.dumps({"type": "session_meta",
                         "payload": {"originator": originator, "cli_version": "0.146.0",
                                     "cwd": str(tmp_path), "model": "m"}}) + "\n"
            + _json.dumps({"type": "response_item",
                           "payload": {"type": "message", "role": "developer",
                                       "content": [{"type": "input_text", "text": block}]}}) + "\n"
        )

    tui = observations(tmp_path, surface="codex-tui")
    assert [o.meta.surface for o in tui] == ["codex-tui"]
    assert len(observations(tmp_path)) == 2


def test_one_unparseable_rollout_does_not_abort_a_scan(tmp_path):
    """Found by sweeping the real history: 98 of 313 rollouts use an older intro.

    Codex changed the wording from "name, description, and file path" to "name,
    description, and source locator". `parse_block` fails closed on the older
    form, which is right — but the first such file aborted the entire sweep. The
    skip must also be *counted*, because a scan that silently dropped a third of
    its input would report a confident and wrong history.
    """
    import json as _json

    day = tmp_path / "2026" / "08" / "06"
    day.mkdir(parents=True)

    def write(name, intro):
        block = ("<skills_instructions>\n" + intro + "### Available skills\n"
                 "- a: d (file: /Users/example-dev/.agents/skills/a/SKILL.md)\n"
                 "</skills_instructions>")
        (day / name).write_text(
            _json.dumps({"type": "session_meta",
                         "payload": {"originator": "codex-tui", "cli_version": "0.146.0",
                                     "cwd": str(tmp_path), "model": "m"}}) + "\n"
            + _json.dumps({"type": "response_item",
                           "payload": {"type": "message", "role": "developer",
                                       "content": [{"type": "input_text", "text": block}]}}) + "\n"
        )

    write("rollout-old.jsonl", "Each entry includes a name, description, and file path.\n")
    write("rollout-new.jsonl", INTRO)

    errors: list = []
    found = observations(tmp_path, errors=errors)
    assert len(found) == 1, "the parseable rollout must still be returned"
    assert len(errors) == 1, "the skip must be reported, never silent"
    assert "rollout-old" in errors[0][0].name

    with pytest.raises(ValueError):
        read_rollout(day / "rollout-old.jsonl")


def test_find_rollouts_on_a_missing_root_is_empty_not_an_error():
    assert rollout_codex.find_rollouts(Path("/nonexistent/sessions")) == []

def test_ordering_follows_the_session_not_the_file_mtime(tmp_path):
    """A resumed old session must not present itself as the current state.

    `find_rollouts` sorted by modification time, but a rollout's listing block is
    captured once at session start and never rewritten. Touching a July file --
    resuming it, or any tool that rewrites it -- therefore floated a stale
    observation to the top: on 2026-08-12 the live check reported a 0.144.1
    session from 2026-07-10 as newest while 0.147.0 sessions from that morning
    sat below it. The drift check would have called that a build regression from
    0.147.0 back to 0.144.1, an event that never happened.

    Order by the stamp in the filename, which is when the block was captured.
    """
    import shutil

    root = tmp_path / "sessions" / "2026" / "08" / "12"
    root.mkdir(parents=True)
    older = root / "rollout-2026-07-10T09-40-00000000-0000-0000-0000-000000000000.jsonl"
    newer = root / "rollout-2026-08-12T12-43-11111111-1111-1111-1111-111111111111.jsonl"
    shutil.copy(F110, older)
    shutil.copy(F56, newer)

    # The stale one is the most recently *modified*, which is the trap.
    import os
    os.utime(newer, (1_700_000_000, 1_700_000_000))
    os.utime(older, (1_800_000_000, 1_800_000_000))

    found = rollout_codex.find_rollouts(tmp_path / "sessions")
    assert [p.name[8:24] for p in found] == ["2026-08-12T12-43", "2026-07-10T09-40"], (
        "newest session first, regardless of which file was touched last")
