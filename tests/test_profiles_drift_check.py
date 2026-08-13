"""Machine-side drift check — the four changes CI structurally cannot see.

Each test below corresponds to something that actually happened during this
program and that no CI run could have noticed: the ceiling moving, a desktop
update adding entries, connectors refilling recovered headroom, and clipping
starting. The detector is exercised against each, and against a baseline it
should call clean, because a monitor that fires on everything is as useless as
one that fires on nothing.

The load-bearing property is that it **fails closed**. A monitor reporting "no
drift" when it observed nothing is worse than no monitor, so every
cannot-evaluate path is asserted explicitly rather than assumed.
"""

from __future__ import annotations

import dataclasses
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "profiles"
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from profiles import rollout_codex as rc  # noqa: E402
from profiles.drift_check import (  # noqa: E402
    EXIT_CANNOT_EVALUATE,
    EXIT_CLEAN,
    EXIT_DRIFT,
    EXIT_SATURATED,
    Baseline,
    compare,
    run,
)

F110 = FIXTURES / "codex-tui-clipped-110.jsonl"
F56 = FIXTURES / "codex-tui-clipped-56.jsonl"
# A listing that fits, so "clean" can be asserted without a clipped sample
# standing in for a healthy one — and so the saturation checks below have a
# control that proves they are not simply firing on everything.
FOK45 = FIXTURES / "codex-tui-healthy-45.jsonl"


def _only(store: dict) -> dict:
    """The single baseline in a one-entry store, as a mutable dict."""
    assert len(store) == 1, f"expected one baseline, got {list(store)}"
    return next(iter(store.values()))


def _stamp(*, days_ago: int) -> str:
    """A baseline `observed_at` that many days in the past."""
    when = datetime.now() - timedelta(days=days_ago)
    return when.strftime("%Y-%m-%dT%H-%M")


@pytest.fixture
def base110():
    return Baseline.from_observation(rc.read_rollout(F110))


@pytest.fixture
def base56():
    return Baseline.from_observation(rc.read_rollout(F56))


# --------------------------------------------------------------------------
# It reports nothing when nothing changed
# --------------------------------------------------------------------------


def test_an_unchanged_observation_is_clean(base56):
    """Guards against a detector that fires on everything."""
    assert compare(base56, base56) == []


# --------------------------------------------------------------------------
# The four changes CI cannot see
# --------------------------------------------------------------------------


def test_a_moved_ceiling_is_reported(base56):
    """0.145.0 took the ceiling from 5,440 to 4,000; 0.147.0 raised it again."""
    moved = dataclasses.replace(base56, ceiling=5440, charged_tokens=5440)
    findings = compare(moved, base56)
    assert any("ceiling moved: 5440 -> 4000" in f for f in findings)


def test_a_ceiling_becoming_underivable_is_reported(base56):
    """0.147.0: nothing saturates, so no render discloses the limit.

    Reported rather than treated as clean — "we can no longer measure it" is a
    finding, and it is the shape a silent regression would also take.
    """
    fits = dataclasses.replace(base56, ceiling=None, saturated=False, charged_tokens=4843)
    findings = compare(base56, fits)
    assert any("no longer derivable" in f for f in findings)
    assert any("clipping has stopped" in f for f in findings)


def test_clipping_starting_is_reported(base56):
    """The failure that ran silently for fifteen days."""
    healthy = dataclasses.replace(base56, saturated=False, ceiling=None)
    findings = compare(healthy, base56)
    assert any("now saturated" in f for f in findings)
    assert any("no warning" in f for f in findings), (
        "the report must say the harness may stay silent; that is why nobody noticed")


def test_an_app_update_adding_entries_is_reported(base56):
    """A Codex desktop update added a whole plugin marketplace worth 723 tokens."""
    grown = dataclasses.replace(
        base56,
        entry_ids=sorted(base56.entry_ids + ["plugin:documents", "plugin:pdf"]),
        uncontrolled_ids=sorted(base56.uncontrolled_ids + ["plugin:documents", "plugin:pdf"]),
    )
    findings = compare(base56, grown)
    assert any("+2" in f and "documents" in f for f in findings)
    assert any("uncontrolled entries changed" in f for f in findings)


def test_a_one_for_one_uncontrolled_swap_is_reported(base56):
    """The 2026-08-06 case: entries left, entries arrived, totals cancelled to 11
    tokens with the count unchanged. A totals check reports nothing happened."""
    swapped_ids = sorted(set(base56.uncontrolled_ids) - {base56.uncontrolled_ids[0]}
                         | {"connector:something-new"})
    swapped = dataclasses.replace(
        base56, uncontrolled_ids=swapped_ids,
        entry_ids=sorted(set(base56.entry_ids) - {base56.uncontrolled_ids[0]}
                         | {"connector:something-new"}),
    )
    assert len(swapped.uncontrolled_ids) == len(base56.uncontrolled_ids), \
        "the sizes must match or this proves nothing"
    findings = compare(base56, swapped)
    assert any("uncontrolled entries changed" in f for f in findings)


def test_losing_one_copy_of_a_duplicated_identity_is_reported(base56):
    """Codex does not shadow across roots, so it charges each copy separately.

    `skill-creator` was listed twice pre-cut — bundled by Codex and shipped by
    dojo — and each copy was charged. `Baseline` stores `Counter.elements()` for
    exactly this reason, so the comparison has to subtract as a multiset: with
    sets, dropping one of two copies leaves both sides equal and the freed
    tokens are reported as coming from nowhere.
    """
    # A *second copy of an identity already listed* — not a new one, or set
    # subtraction would catch it and this would prove nothing.
    twin = base56.entry_ids[0]
    doubled = dataclasses.replace(base56, entry_ids=sorted(base56.entry_ids + [twin]))
    assert set(doubled.entry_ids) == set(base56.entry_ids), \
        "the two must be set-identical or this tests the wrong thing"

    findings = compare(doubled, base56)
    assert any("listed entries changed" in f for f in findings), findings
    assert any(twin in f for f in findings), (
        "the surviving copy must not mask the one that disappeared")


def test_charged_demand_moving_without_a_membership_change_is_reported(base56):
    """A vendor rewriting one description costs headroom and moves no identity.

    Membership answers *what* is listed; it cannot answer *how much* the same
    listing now costs. An entry whose description grows is invisible to every
    set comparison in this function, which is the shape of the 723-token desktop
    update — only that one changed membership too, and so was caught by luck
    rather than by design.
    """
    fits = dataclasses.replace(base56, saturated=False, ceiling=None)
    grown = dataclasses.replace(fits, charged_tokens=fits.charged_tokens + 400)
    findings = compare(fits, grown)
    assert set(grown.entry_ids) == set(fits.entry_ids), "membership must be held equal"
    assert any("charged demand" in f for f in findings), findings
    assert any("+400" in f for f in findings), "the report must name the size of the move"


def test_a_pinned_saturated_total_is_not_reported_twice(base56):
    """When both samples clip, the total *is* the ceiling.

    Saturation pins charged demand to the limit, so a moved ceiling and a moved
    total are one event described twice. A monitor a human reads weekly must not
    say the same thing in two voices, or the voices stop being read.
    """
    moved = dataclasses.replace(base56, ceiling=5440, charged_tokens=5440)
    findings = compare(moved, base56)
    assert any("ceiling moved" in f for f in findings)
    assert not any("charged demand" in f for f in findings), findings


def test_a_harness_build_change_is_reported(base56):
    build = dataclasses.replace(base56, harness_build="0.147.0/gpt-5.6-luna")
    findings = compare(base56, build)
    assert any("harness build changed" in f for f in findings)
    assert any("build-scoped" in f for f in findings), (
        "the report must say why a build change invalidates the previous figures")


def test_entry_set_changes_are_compared_as_sets_not_counts(base56):
    """One entry swapped for another: same count, different membership.

    Found by mutation probe, twice in this package now. The earlier version of
    this test compared two different fixtures and asserted only that *something*
    was reported — which other findings satisfied, so replacing the set
    comparison with a length comparison survived. Everything but the entry set
    is held identical here so the assertion can only be satisfied by the line it
    names.
    """
    swapped = dataclasses.replace(
        base56,
        entry_ids=sorted(set(base56.entry_ids) - {base56.entry_ids[0]} | {"dojo-managed:renamed"}),
    )
    assert len(swapped.entry_ids) == len(base56.entry_ids), \
        "the counts must match or this proves nothing"
    findings = compare(base56, swapped)
    assert any("listed entries changed" in f for f in findings), findings
    assert any("renamed" in f for f in findings), "the report must name what arrived"


# --------------------------------------------------------------------------
# Fails closed
# --------------------------------------------------------------------------


def test_no_session_is_cannot_evaluate_not_clean(tmp_path, capsys):
    """A monitor reporting 'no drift' when it observed nothing is worse than none."""
    empty = tmp_path / "sessions"
    empty.mkdir()
    import profiles.drift_check as dc

    original = rc.default_sessions_root
    rc.default_sessions_root = lambda: empty  # type: ignore[assignment]
    try:
        code = dc.run(tmp_path / "baseline.json")
    finally:
        rc.default_sessions_root = original  # type: ignore[assignment]
    assert code == EXIT_CANNOT_EVALUATE
    assert "no parseable" in capsys.readouterr().out


# --------------------------------------------------------------------------
# Blind for too long is a finding, not a quiet pass
# --------------------------------------------------------------------------


def test_never_having_evaluated_is_escalated_not_tolerated(tmp_path, capsys, monkeypatch):
    """The mini's real state on 2026-08-12, reported green every week.

    Its newest interactive session was nine weeks old and unparseable, so the
    check could never evaluate — and the health wrapper treated cannot-evaluate
    as a pass. A machine that has *never* been observed is not a machine between
    sessions; it is a machine nobody is watching, and saying so is the whole
    point of the monitor.
    """
    import profiles.drift_check as dc

    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [])
    code = dc.run(tmp_path / "absent.json", max_blind_days=30)
    assert code == dc.EXIT_BLIND, "never-evaluated must escalate, not pass"
    assert "never" in capsys.readouterr().out.lower()


def test_a_machine_merely_between_sessions_is_not_escalated(tmp_path, capsys, monkeypatch):
    """The exemption that was right for the wrong reason.

    Interactive work happens on the mini only when monitors are connected, so a
    quiet week is normal and must not go red — that trains the operator to
    ignore the job. Only *persistent* blindness escalates.
    """
    import profiles.drift_check as dc

    path = tmp_path / "baseline.json"
    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [rc.read_rollout(F56)])
    dc.run(path, update=True)
    store = json.loads(path.read_text())
    _only(store)["observed_at"] = _stamp(days_ago=3)
    path.write_text(json.dumps(store))
    capsys.readouterr()

    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [])
    assert dc.run(path, max_blind_days=30) == EXIT_CANNOT_EVALUATE
    assert "3d" in capsys.readouterr().out


def test_blindness_past_the_threshold_escalates_and_dates_itself(
        tmp_path, capsys, monkeypatch):
    import profiles.drift_check as dc

    path = tmp_path / "baseline.json"
    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [rc.read_rollout(F56)])
    dc.run(path, update=True)
    store = json.loads(path.read_text())
    _only(store)["observed_at"] = _stamp(days_ago=64)
    path.write_text(json.dumps(store))
    capsys.readouterr()

    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [])
    assert dc.run(path, max_blind_days=30) == dc.EXIT_BLIND
    out = capsys.readouterr().out
    assert "64d" in out, "the report must say how long it has been blind"


def test_blindness_is_opt_in_so_ad_hoc_runs_are_unaffected(tmp_path, monkeypatch):
    """Without a threshold the exit codes are exactly what they were."""
    import profiles.drift_check as dc

    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [])
    assert dc.run(tmp_path / "absent.json") == EXIT_CANNOT_EVALUATE


def test_a_machine_that_can_be_read_never_reports_blind(tmp_path, monkeypatch):
    """Blindness is about the instrument, never about what the instrument saw.

    A threshold that also fired on a healthy observation would make the check
    unusable on the daily driver, which is the machine it most needs to watch.
    """
    import profiles.drift_check as dc

    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [rc.read_rollout(FOK45)])
    path = tmp_path / "baseline.json"
    assert dc.run(path, update=True, max_blind_days=1) == EXIT_CLEAN
    assert dc.run(path, max_blind_days=1) == EXIT_CLEAN


def test_a_stale_but_readable_session_still_counts_as_blind(tmp_path, capsys, monkeypatch):
    """The hole in the first version of the threshold.

    It was reached only when *no* observation parsed. But nothing gives
    `observations()` a freshness cutoff, so a machine that stops being used
    interactively keeps returning the same historical rollout forever: it
    matches the baseline, compares clean, and the monitor reports healthy
    indefinitely while receiving nothing new. Being able to read a two-month-old
    session is not the same as watching a machine.
    """
    import profiles.drift_check as dc

    obs = rc.read_rollout(F56)
    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [obs])
    monkeypatch.setattr(dc, "_observation_age_days", lambda o: 70)
    path = tmp_path / "baseline.json"

    dc.run(path, update=True)          # seed from the same stale sample
    capsys.readouterr()

    assert dc.run(path, max_blind_days=30) == dc.EXIT_BLIND, \
        "a stale sample that compares clean must not report clean"
    assert "70d" in capsys.readouterr().out


def test_degraded_classification_can_also_be_blind(tmp_path, capsys, monkeypatch):
    """The other bypass: the alarm returned before the threshold was consulted.

    A classifier broken by a render change yields cannot-evaluate on every run,
    which the scheduled wrapper treats as a pass — the same silent-forever
    failure, reached by a different door.
    """
    import copy

    import profiles.drift_check as dc

    broken = copy.deepcopy(rc.read_rollout(F56))
    for entry in broken.listing.entries:
        entry.locator = f"/nowhere/{entry.name}/SKILL.md"
    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [broken])

    assert dc.run(tmp_path / "b.json", max_blind_days=30) == dc.EXIT_BLIND
    out = capsys.readouterr().out
    assert "classification degraded" in out, "it must still say what broke"


def test_real_drift_outranks_staleness(tmp_path, capsys, monkeypatch):
    """Staleness must not mask a change the operator has never seen.

    A stale sample that *differs* from the baseline is the more actionable
    finding, so it is reported as drift; blindness is what a stale sample means
    when there is otherwise nothing to say.
    """
    import profiles.drift_check as dc

    monkeypatch.setattr(dc, "_observation_age_days", lambda o: 70)
    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [rc.read_rollout(F56)])
    path = tmp_path / "baseline.json"
    dc.run(path, update=True)
    capsys.readouterr()

    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [rc.read_rollout(F110)])
    assert dc.run(path, max_blind_days=30) == EXIT_DRIFT
    assert "listed entries changed" in capsys.readouterr().out


# --------------------------------------------------------------------------
# Samples are not pooled across working directories
# --------------------------------------------------------------------------


def test_two_working_dirs_do_not_report_each_other_as_drift(tmp_path, capsys, monkeypatch):
    """Measured on this machine: at build 0.144.1, `Dev` listed 55 entries and
    `Dev/dojo` listed 112 — the repository's own project-scoped catalog on top of
    the global one. With a single machine-wide baseline the hook accepts whichever
    project it saw last and reports ~57 entries added, then the reverse on the next
    switch. That is not noise to tune down; it fires on every project switch.

    Same rule the module already applies to builds: compare like with like.
    """
    import profiles.drift_check as dc

    in_dev = rc.read_rollout(FOK45)
    in_dojo = rc.read_rollout(F110)
    path = tmp_path / "baseline.json"

    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [in_dev])
    monkeypatch.setattr(dc, "_observation_cwd", lambda o: "/Users/x/Dev")
    assert dc.run(path, update=True) == EXIT_CLEAN
    capsys.readouterr()

    # Switch project: a different cwd with a legitimately different catalog.
    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [in_dojo])
    monkeypatch.setattr(dc, "_observation_cwd", lambda o: "/Users/x/Dev/dojo")
    assert dc.run(path, update=True) != EXIT_DRIFT, \
        "a different project's catalog is not drift"
    capsys.readouterr()

    # ...and coming back must not report the reverse change either.
    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [in_dev])
    monkeypatch.setattr(dc, "_observation_cwd", lambda o: "/Users/x/Dev")
    assert dc.run(path) == EXIT_CLEAN, "returning to a known project must be clean"


def test_each_working_dir_keeps_its_own_baseline(tmp_path, monkeypatch):
    """Accepting one project's listing must not overwrite another's."""
    import profiles.drift_check as dc

    path = tmp_path / "baseline.json"
    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [rc.read_rollout(F56)])
    monkeypatch.setattr(dc, "_observation_cwd", lambda o: "/Users/x/Dev")
    dc.run(path, update=True)

    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [rc.read_rollout(F110)])
    monkeypatch.setattr(dc, "_observation_cwd", lambda o: "/Users/x/Dev/dojo")
    dc.run(path, update=True)

    store = json.loads(path.read_text())
    assert set(store) == {"/Users/x/Dev", "/Users/x/Dev/dojo"}, store
    assert len(store["/Users/x/Dev"]["entry_ids"]) == 56
    assert len(store["/Users/x/Dev/dojo"]["entry_ids"]) == 110


def test_a_missing_baseline_refuses_rather_than_passing(tmp_path, capsys, monkeypatch):
    """First run must not report clean; it has nothing to compare against."""
    import profiles.drift_check as dc

    monkeypatch.setattr(dc.rc, "observations",
                        lambda **kw: [rc.read_rollout(FOK45)])
    code = dc.run(tmp_path / "absent.json")
    assert code == EXIT_CANNOT_EVALUATE
    assert "no baseline" in capsys.readouterr().out


def test_a_missing_baseline_does_not_hide_saturation(tmp_path, capsys, monkeypatch):
    """Whether the listing clips is knowable without any baseline at all.

    Falling back to cannot-evaluate here would be the same silence by a
    different door: the scheduled wrapper treats exit 1 as a pass, so a machine
    that had never recorded a baseline could clip indefinitely without a word.
    """
    import profiles.drift_check as dc

    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [rc.read_rollout(F56)])
    assert dc.run(tmp_path / "absent.json") == EXIT_SATURATED
    out = capsys.readouterr().out
    assert "no baseline" in out, "it must still say the comparison could not run"
    assert "clipped" in out


def test_update_records_a_baseline_then_reports_clean(tmp_path, capsys, monkeypatch):
    import profiles.drift_check as dc

    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [rc.read_rollout(FOK45)])
    path = tmp_path / "baseline.json"

    assert dc.run(path, update=True) == EXIT_CLEAN
    assert path.exists()
    capsys.readouterr()

    assert dc.run(path) == EXIT_CLEAN, "an unchanged machine must report clean"
    assert "state: clean" in capsys.readouterr().out


def test_drift_exits_two_and_names_what_moved(tmp_path, capsys, monkeypatch):
    import profiles.drift_check as dc

    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [rc.read_rollout(FOK45)])
    path = tmp_path / "baseline.json"
    dc.run(path, update=True)
    capsys.readouterr()

    store = json.loads(path.read_text())
    key = next(iter(store))
    store[key] = dataclasses.asdict(dataclasses.replace(
        Baseline(**store[key]), harness_build="0.140.0/old",
        saturated=True, ceiling=5440))
    path.write_text(json.dumps(store, indent=2))

    assert dc.run(path) == EXIT_DRIFT
    out = capsys.readouterr().out
    assert "harness build changed" in out and "no longer derivable" in out


def test_degraded_classification_is_cannot_evaluate(tmp_path, capsys, monkeypatch):
    """A broken classifier yields a confident, meaningless diff."""
    import copy

    import profiles.drift_check as dc

    broken = copy.deepcopy(rc.read_rollout(F56))
    for entry in broken.listing.entries:
        entry.locator = f"/nowhere/{entry.name}/SKILL.md"
    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [broken])

    assert dc.run(tmp_path / "b.json") == EXIT_CANNOT_EVALUATE
    assert "classification degraded" in capsys.readouterr().out


def test_the_check_never_writes_without_update(tmp_path, monkeypatch):
    """It is a monitor. Its only outputs are a report and an exit code."""
    import profiles.drift_check as dc

    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [rc.read_rollout(F56)])
    path = tmp_path / "baseline.json"
    dc.run(path, update=True)
    before = path.read_bytes()

    # Both fixtures clip, so the run reports the standing state rather than the
    # change; either way it found something, which is what makes the write
    # assertion meaningful.
    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [rc.read_rollout(F110)])
    assert dc.run(path) == EXIT_SATURATED
    assert path.read_bytes() == before, "a run without --update must not rewrite the baseline"


# --------------------------------------------------------------------------
# Saturation is a standing state, not a change
# --------------------------------------------------------------------------


def test_a_clipping_listing_is_never_reported_as_clean(tmp_path, capsys, monkeypatch):
    """The gap this exit code closes, taken from the machine that had it.

    On 2026-08-13 the mini was saturated at its 4,000-token ceiling with 24 of
    48 descriptions cut mid-word, and this check printed `state: clean` with
    exit 0 — correctly, under the old contract: it compares against a baseline,
    and nothing had moved. But the program exists to notice clipping, and in the
    one case where clipping was real it said everything was fine.

    Drift asks "did it move?". This asks "is it broken?", which a comparison
    against a baseline recorded while already broken can never answer.
    """
    import profiles.drift_check as dc

    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [rc.read_rollout(F56)])
    path = tmp_path / "baseline.json"
    dc.run(path, update=True)
    capsys.readouterr()

    assert dc.run(path) == EXIT_SATURATED, \
        "an unchanged but clipping listing must not report clean"
    out = capsys.readouterr().out
    assert "state: saturated" in out
    assert "4000" in out, "the report must name the ceiling being hit"


def test_recording_a_first_baseline_does_not_launder_saturation(
        tmp_path, capsys, monkeypatch):
    """`--update` accepts an observation; it must not bless it.

    This is the exact shape the mini reported: `state: baseline-recorded`,
    exit 0, on a listing that was clipping as it was recorded. Accepting a
    sample settles what to compare against next time and says nothing about
    whether the sample is healthy.
    """
    import profiles.drift_check as dc

    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [rc.read_rollout(F56)])
    path = tmp_path / "baseline.json"

    assert dc.run(path, update=True) == EXIT_SATURATED
    assert path.exists(), "it must still record the baseline it refuses to call clean"
    assert "clipped" in capsys.readouterr().out


def test_saturation_outranks_drift_and_still_names_what_moved(
        tmp_path, capsys, monkeypatch):
    """Both can hold. The exit code names the standing state, the report names both.

    Drift is debounced by `--update` and saturation is not, so letting drift win
    would report the transition once and then fall back to reporting the
    degraded state — which is the silence this code exists to prevent.
    """
    import profiles.drift_check as dc

    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [rc.read_rollout(F56)])
    path = tmp_path / "baseline.json"
    dc.run(path, update=True)
    capsys.readouterr()

    store = json.loads(path.read_text())
    key = next(iter(store))
    store[key] = dataclasses.asdict(dataclasses.replace(
        Baseline(**store[key]), harness_build="0.140.0/old"))
    path.write_text(json.dumps(store, indent=2))

    assert dc.run(path) == EXIT_SATURATED
    out = capsys.readouterr().out
    assert "harness build changed" in out, \
        "the drift finding must survive being outranked"


def test_a_listing_that_fits_is_clean(tmp_path, capsys, monkeypatch):
    """The control. A detector that cannot pass a healthy sample is not a detector."""
    import profiles.drift_check as dc

    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [rc.read_rollout(FOK45)])
    path = tmp_path / "baseline.json"

    assert dc.run(path, update=True) == EXIT_CLEAN
    capsys.readouterr()
    assert dc.run(path) == EXIT_CLEAN
    assert "state: clean" in capsys.readouterr().out


def test_blindness_outranks_saturation(tmp_path, capsys, monkeypatch):
    """A degraded state you are no longer observing is a broken instrument first.

    Reporting "you are clipping" from a sample two months stale would assert a
    present-tense fact the check has no current evidence for.
    """
    import profiles.drift_check as dc

    obs = rc.read_rollout(F56)
    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [obs])
    monkeypatch.setattr(dc, "_observation_age_days", lambda o: 70)
    path = tmp_path / "baseline.json"
    dc.run(path, update=True)
    capsys.readouterr()

    assert dc.run(path, max_blind_days=30) == dc.EXIT_BLIND
    assert "70d" in capsys.readouterr().out


def test_saturation_clearing_returns_to_clean(tmp_path, capsys, monkeypatch):
    """It must be able to go green again, or it is a permanent alarm.

    A raised ceiling or a trimmed catalog is the outcome this code is asking
    for, and the run after that has to say so.
    """
    import profiles.drift_check as dc

    path = tmp_path / "baseline.json"
    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [rc.read_rollout(F56)])
    monkeypatch.setattr(dc, "_observation_cwd", lambda o: "/Users/x/Dev")
    assert dc.run(path, update=True) == EXIT_SATURATED
    capsys.readouterr()

    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [rc.read_rollout(FOK45)])
    assert dc.run(path, update=True) == EXIT_DRIFT, \
        "the listing changing shape is still drift; it is just no longer clipping"
    capsys.readouterr()
    assert dc.run(path) == EXIT_CLEAN


def test_a_model_switch_is_not_called_a_build_change(base56):
    """A monitor a human reads must not mislabel what moved.

    The ceiling followed the context window on 0.144.1 (7,440 for a
    372k-window model) and ignored the model entirely on 0.146.0, so a model
    switch is reportable — but it is not a build change and must not read as one.
    """
    build, _, model = base56.harness_build.partition("/")
    other_model = dataclasses.replace(base56, harness_build=f"{build}/gpt-other")
    findings = compare(base56, other_model)
    assert any("model changed" in f for f in findings)
    assert not any("harness build changed" in f for f in findings)

    other_build = dataclasses.replace(base56, harness_build=f"9.9.9/{model}")
    findings = compare(base56, other_build)
    assert any("harness build changed" in f for f in findings)
    assert not any("model changed" in f for f in findings)
