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


def test_an_unchanged_observation_is_clean(base56):
    """Guards against a detector that fires on everything."""
    assert compare(base56, base56) == []


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
    # WHY: a second copy of an identity already listed, not a new one, or set
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


def test_health_mode_accepts_only_uncontrolled_membership_drift_as_notice(
        tmp_path, capsys, monkeypatch):
    """Connector packaging can change without making the workstation unhealthy.

    The strict default must still report drift. Health-mode may downgrade only
    the same-build, non-saturating transition whose entire membership delta is
    outside local control, while retaining the exact finding in its report.
    """
    import profiles.drift_check as dc

    obs = rc.read_rollout(FOK45)
    current = Baseline.from_observation(obs)
    removed = "connector:github:yeet"
    previous = dataclasses.replace(
        current,
        entry_ids=sorted(current.entry_ids + [removed]),
        uncontrolled_ids=sorted(current.uncontrolled_ids + [removed]),
        charged_tokens=current.charged_tokens + 100,
    )
    path = tmp_path / "baseline.json"
    path.write_text(json.dumps({obs.meta.cwd: dataclasses.asdict(previous)}))
    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [obs])

    assert dc.run(path) == EXIT_DRIFT, "the drift check stays strict by default"
    capsys.readouterr()

    assert dc.run(path, update=True, uncontrolled_as_notice=True) == EXIT_CLEAN
    out = capsys.readouterr().out
    assert "state: notice" in out
    assert removed in out, "notice mode must retain the exact vendor delta"
    assert Baseline(**json.loads(path.read_text())[obs.meta.cwd]) == current, \
        "notice mode must accept the observed state just like ordinary update"


def test_health_mode_does_not_hide_controlled_or_build_drift(
        tmp_path, capsys, monkeypatch):
    """A notice path that swallows local or build drift is worse than the noise."""
    import profiles.drift_check as dc

    obs = rc.read_rollout(FOK45)
    current = Baseline.from_observation(obs)
    path = tmp_path / "baseline.json"
    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [obs])

    controlled = "dojo-managed:write-plan-shadow"
    previous = dataclasses.replace(
        current, entry_ids=sorted(current.entry_ids + [controlled]))
    path.write_text(json.dumps({obs.meta.cwd: dataclasses.asdict(previous)}))
    assert dc.run(path, uncontrolled_as_notice=True) == EXIT_DRIFT
    assert controlled in capsys.readouterr().out

    connector = "connector:github:yeet"
    previous = dataclasses.replace(
        current,
        harness_build="0.146.0/gpt-5.6-terra",
        entry_ids=sorted(current.entry_ids + [connector]),
        uncontrolled_ids=sorted(current.uncontrolled_ids + [connector]),
    )
    path.write_text(json.dumps({obs.meta.cwd: dataclasses.asdict(previous)}))
    assert dc.run(path, uncontrolled_as_notice=True) == EXIT_DRIFT
    assert "harness build changed" in capsys.readouterr().out


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


def test_a_fresh_healthy_observation_never_reports_blind(tmp_path, monkeypatch):
    import profiles.drift_check as dc
    from datetime import timezone

    observation = rc.read_rollout(FOK45)
    observation.meta = dataclasses.replace(
        observation.meta, observed_at=datetime.now(timezone.utc).isoformat())
    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [observation])
    path = tmp_path / "baseline.json"
    assert dc.run(path, update=True, max_blind_days=1) == EXIT_CLEAN


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

    dc.run(path, update=True)
    capsys.readouterr()

    assert dc.run(path, max_blind_days=30) == dc.EXIT_BLIND, \
        "a stale sample that compares clean must not report clean"
    assert "70d" in capsys.readouterr().out


def test_blindness_outranks_uncontrolled_notice_and_prevents_update(
        tmp_path, capsys, monkeypatch):
    """Vendor churn cannot make an old observation current or healthy."""
    import profiles.drift_check as dc

    obs = rc.read_rollout(FOK45)
    current = Baseline.from_observation(obs)
    connector = "connector:github:yeet"
    previous = dataclasses.replace(
        current,
        entry_ids=sorted(current.entry_ids + [connector]),
        uncontrolled_ids=sorted(current.uncontrolled_ids + [connector]),
    )
    path = tmp_path / "baseline.json"
    path.write_text(json.dumps({obs.meta.cwd: dataclasses.asdict(previous)}))
    before = path.read_text()
    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [obs])
    monkeypatch.setattr(dc, "_observation_age_days", lambda o: 70)

    assert dc.run(
        path,
        update=True,
        max_blind_days=30,
        uncontrolled_as_notice=True,
    ) == dc.EXIT_BLIND
    out = capsys.readouterr().out
    assert "state: blind" in out
    assert "70d" in out
    assert path.read_text() == before, "a stale sample must not be accepted by --update"


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

    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [in_dojo])
    monkeypatch.setattr(dc, "_observation_cwd", lambda o: "/Users/x/Dev/dojo")
    assert dc.run(path, update=True) != EXIT_DRIFT, \
        "a different project's catalog is not drift"
    capsys.readouterr()

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

    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [rc.read_rollout(F110)])
    assert dc.run(path) == EXIT_SATURATED
    assert path.read_bytes() == before, "a run without --update must not rewrite the baseline"


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


def _sessions_dir(tmp_path, originator: str, name: str = "sessions"):
    """A sessions root holding the healthy fixture re-labelled with `originator`."""
    text = FOK45.read_text().replace('"originator": "codex-tui"',
                                     f'"originator": "{originator}"')
    day = tmp_path / name / "2026" / "08" / "06"
    day.mkdir(parents=True)
    (day / "rollout-2026-08-06T00-00-00-00000000-0000-0000-0000-000000000045.jsonl"
     ).write_text(text)
    return tmp_path / name


def test_partial_resumed_turn_cannot_update_either_directory_baseline(
        tmp_path, monkeypatch, capsys):
    import profiles.drift_check as dc
    from profiles.probe_codex import render_available_skills_body

    root = _sessions_dir(tmp_path, "codex-tui")
    monkeypatch.setattr(rc, "default_sessions_root", lambda: root)
    baseline = tmp_path / "baseline.json"
    assert dc.main(["--baseline", str(baseline), "--update", "--json"]) == EXIT_CLEAN
    capsys.readouterr()
    before = baseline.read_bytes()
    initial_cwd = next(iter(json.loads(before)))
    new_cwd = str(tmp_path / "another-project")
    body = render_available_skills_body([], [
        "- new-skill: A synthetic skill. (file: /Users/example/.agents/skills/new/SKILL.md)",
    ])
    record = {
        "type": "response_item", "timestamp": "2026-11-03T13:00:00Z",
        "payload": {"type": "message", "role": "developer", "content": [
            {"type": "input_text", "text": f"<skills_instructions>\n## Host skills\n{body}</skills_instructions>"},
        ]},
    }
    rollout = next(root.rglob("*.jsonl"))
    with rollout.open("a") as stream:
        stream.write(json.dumps(record) + "\n")

    for cwd in (initial_cwd, new_cwd):
        assert dc.main(["--baseline", str(baseline), "--cwd", cwd,
                        "--update", "--json"]) == EXIT_CANNOT_EVALUATE
        assert json.loads(capsys.readouterr().out)["observed"] is None
        assert baseline.read_bytes() == before

    with rollout.open("a") as stream:
        stream.write(json.dumps({
            "type": "turn_context", "timestamp": "2026-11-03T13:00:00Z",
            "payload": {"cwd": new_cwd, "model": "example-model"},
        }) + "\n")
    assert dc.main(["--baseline", str(baseline), "--cwd", new_cwd,
                    "--update", "--json"]) == EXIT_CLEAN
    assert json.loads(capsys.readouterr().out)["observed"]["entry_ids"] == ["dojo-managed:new-skill"]
    stored = json.loads(baseline.read_text())
    assert stored[initial_cwd] == json.loads(before)[initial_cwd]
    assert new_cwd in stored


def test_the_default_still_reads_only_the_tui(tmp_path, capsys, monkeypatch):
    """Opt-in, not a changed default: with no --surface a desktop-only machine is
    still unobserved, exactly as before."""
    import profiles.drift_check as dc

    root = _sessions_dir(tmp_path, "Codex Desktop")
    monkeypatch.setattr(rc, "default_sessions_root", lambda: root)
    assert dc.run(tmp_path / "baseline.json", update=True) == EXIT_CANNOT_EVALUATE
    assert "no parseable codex-tui session" in capsys.readouterr().out


@pytest.mark.parametrize("originator,surfaces", [
    ("Codex Desktop", ("Codex Desktop",)),
    ("Codex Desktop", ("codex-tui", "Codex Desktop")),
    ("codex-tui", ("codex-tui", "Codex Desktop")),
])
def test_a_selected_surface_is_observed(tmp_path, capsys, monkeypatch, originator, surfaces):
    import profiles.drift_check as dc

    root = _sessions_dir(tmp_path, originator)
    monkeypatch.setattr(rc, "default_sessions_root", lambda: root)
    assert dc.run(tmp_path / "baseline.json", update=True,
                  surfaces=surfaces) == EXIT_CLEAN
    assert "state: baseline-recorded" in capsys.readouterr().out


def test_a_surface_that_was_not_selected_is_not_observed(tmp_path, capsys, monkeypatch):
    import profiles.drift_check as dc

    root = _sessions_dir(tmp_path, "codex-tui")
    monkeypatch.setattr(rc, "default_sessions_root", lambda: root)
    assert dc.run(tmp_path / "baseline.json", update=True,
                  surfaces=("Codex Desktop",)) == EXIT_CANNOT_EVALUATE


def test_exec_cannot_be_selected(tmp_path, capsys):
    """The control: `codex exec` renders a different listing, so reading it as the
    machine's listing would report 69 phantom removals. Refused, not merely unused."""
    import profiles.drift_check as dc

    with pytest.raises(SystemExit) as exc:
        dc.main(["--baseline", str(tmp_path / "b.json"), "--surface", "codex_exec"])
    assert exc.value.code == 2
    assert "codex_exec" in capsys.readouterr().err
    with pytest.raises(ValueError):
        dc.run(tmp_path / "b.json", surfaces=("codex_exec",))


def test_the_missing_session_message_names_the_selected_surfaces(tmp_path, capsys, monkeypatch):
    import profiles.drift_check as dc

    empty = tmp_path / "sessions"
    empty.mkdir()
    monkeypatch.setattr(rc, "default_sessions_root", lambda: empty)
    dc.run(tmp_path / "baseline.json")
    assert "no parseable codex-tui session" in capsys.readouterr().out
    dc.run(tmp_path / "baseline.json", surfaces=("codex-tui", "Codex Desktop"))
    out = capsys.readouterr().out
    assert "codex-tui or Codex Desktop" in out


def test_surface_flag_is_repeatable_on_the_command_line(tmp_path, capsys, monkeypatch):
    import profiles.drift_check as dc

    root = _sessions_dir(tmp_path, "Codex Desktop")
    monkeypatch.setattr(rc, "default_sessions_root", lambda: root)
    code = dc.main(["--baseline", str(tmp_path / "b.json"), "--update",
                    "--surface", "codex-tui", "--surface", "Codex Desktop"])
    assert code == EXIT_CLEAN
    assert "Codex Desktop" in capsys.readouterr().out


def test_the_newest_session_wins_across_selected_surfaces(tmp_path):
    """A machine used from both surfaces is watched through whichever ran last."""
    root = _sessions_dir(tmp_path, "codex-tui")
    newer = root / "2026" / "08" / "07"
    newer.mkdir(parents=True)
    (newer / "rollout-2026-08-07T00-00-00-00000000-0000-0000-0000-000000000046.jsonl"
     ).write_text(FOK45.read_text().replace('"originator": "codex-tui"',
                                            '"originator": "Codex Desktop"'))
    found = rc.observations(root, surface=rc.INTERACTIVE_SURFACES, limit=1)
    assert [o.meta.surface for o in found] == ["Codex Desktop"]


def test_a_surface_change_alone_does_not_defeat_notice_mode():
    """Flipping between TUI and desktop sessions of one build is not controlled
    drift: only membership outside local control moved."""
    import profiles.drift_check as dc

    healthy = Baseline.from_observation(rc.read_rollout(FOK45))
    swapped = "connector:github:yeet"
    previous = dataclasses.replace(
        healthy, surface="codex-tui",
        entry_ids=sorted(healthy.entry_ids + [swapped]),
        uncontrolled_ids=sorted(healthy.uncontrolled_ids + [swapped]))
    current = dataclasses.replace(healthy, surface="Codex Desktop")
    assert dc._only_uncontrolled_membership_changed(previous, current)
    assert not dc._only_uncontrolled_membership_changed(
        previous, dataclasses.replace(healthy, surface="codex_exec"))


def test_observation_timestamp_overrides_old_startup_filename(tmp_path, monkeypatch, capsys):
    import profiles.drift_check as dc
    from datetime import timezone

    obs = rc.read_rollout(FOK45)
    recorded = datetime.now(timezone.utc).isoformat()
    obs.meta = dataclasses.replace(obs.meta, observed_at=recorded)
    monkeypatch.setattr(rc, 'observations', lambda **kw: [obs])
    baseline = tmp_path / 'baseline.json'
    assert dc.run(baseline, update=True, max_blind_days=14) == EXIT_CLEAN
    capsys.readouterr()
    assert _only(json.loads(baseline.read_text()))['observed_at'] == recorded
    assert dc.run(baseline, max_blind_days=14) == EXIT_CLEAN


def test_baseline_age_accepts_aware_iso_timestamp():
    import profiles.drift_check as dc
    from datetime import timezone

    baseline = Baseline.from_observation(rc.read_rollout(FOK45))
    baseline.observed_at = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    assert dc._days_blind(baseline) == 2


def test_baseline_age_respects_timezone_offset():
    import profiles.drift_check as dc
    from datetime import timezone

    baseline = Baseline.from_observation(rc.read_rollout(FOK45))
    zone = timezone(timedelta(hours=12))
    baseline.observed_at = (datetime.now(zone) - timedelta(hours=25)).isoformat()
    assert dc._days_blind(baseline) == 1


@pytest.mark.parametrize('error_age', [None, -1])
def test_unreadable_latest_catalog_preserves_baseline(tmp_path, monkeypatch, capsys, error_age):
    import profiles.drift_check as dc
    from datetime import timezone

    obs = rc.read_rollout(FOK45)
    observed = datetime.now(timezone.utc) - timedelta(days=1)
    obs.meta = dataclasses.replace(obs.meta, observed_at=observed.isoformat())
    failure_meta = dataclasses.replace(
        obs.meta, observed_at=None if error_age is None else
        (observed - timedelta(days=error_age)).isoformat())
    failure = ValueError('unsupported catalog update')
    failure.meta = failure_meta

    def collect(**kwargs):
        kwargs.get('evidence_errors', []).append(failure)
        return [obs]

    monkeypatch.setattr(rc, 'observations', collect)
    baseline = tmp_path / 'baseline.json'
    before = json.dumps({obs.meta.cwd: dataclasses.asdict(Baseline.from_observation(obs))}) + '\n'
    baseline.write_text(before)
    assert dc.run(baseline, update=True) == EXIT_CANNOT_EVALUATE
    assert baseline.read_text() == before
    assert 'unsupported catalog update' in capsys.readouterr().out


def test_older_unreadable_catalog_does_not_hide_newer_valid_observation(tmp_path, monkeypatch):
    import profiles.drift_check as dc
    from datetime import timezone

    obs = rc.read_rollout(FOK45)
    now = datetime.now(timezone.utc)
    obs.meta = dataclasses.replace(obs.meta, observed_at=now.isoformat())
    failure_meta = dataclasses.replace(obs.meta, observed_at=(now - timedelta(days=2)).isoformat())
    failure = ValueError('old unsupported render')
    failure.meta = failure_meta

    def collect(**kwargs):
        kwargs.get('evidence_errors', []).append(failure)
        return [obs]

    monkeypatch.setattr(rc, 'observations', collect)
    assert dc.run(tmp_path / 'baseline.json', update=True) == EXIT_CLEAN


def test_reconstructed_clipped_catalog_does_not_invent_ceiling():
    obs = rc.read_rollout(F56)
    obs.meta = dataclasses.replace(obs.meta, catalog_kind="delta")
    baseline = Baseline.from_observation(obs)
    assert baseline.saturated is True
    assert baseline.ceiling is None


def test_unsupported_only_catalog_reports_reason(tmp_path, monkeypatch, capsys):
    import profiles.drift_check as dc

    def collect(**kwargs):
        kwargs.get('evidence_errors', []).append(ValueError('zstd decoder is unavailable'))
        return []

    monkeypatch.setattr(rc, 'observations', collect)
    baseline = tmp_path / 'baseline.json'
    assert dc.run(baseline, update=True) == EXIT_CANNOT_EVALUATE
    assert not baseline.exists()
    assert 'zstd decoder is unavailable' in capsys.readouterr().out


def test_legacy_baseline_timestamp_keeps_local_wall_time():
    import profiles.drift_check as dc

    local = datetime.now().replace(second=0, microsecond=0)
    stamp = local.strftime('%Y-%m-%dT%H-%M')
    assert dc._timestamp(stamp) == local.astimezone()


def test_unmeasurable_observation_age_cannot_seed_fresh_baseline(tmp_path, monkeypatch, capsys):
    import profiles.drift_check as dc

    obs = rc.read_rollout(FOK45)
    obs.meta = dataclasses.replace(obs.meta, observed_at="not-a-timestamp")
    monkeypatch.setattr(rc, 'observations', lambda **kw: [obs])
    baseline = tmp_path / 'baseline.json'
    assert dc.run(baseline, update=True, max_blind_days=14) == dc.EXIT_BLIND
    assert not baseline.exists()
    assert 'observation timestamp' in capsys.readouterr().out


def test_unattributed_build_does_not_get_a_build_specific_ceiling(capsys):
    import profiles.drift_check as dc

    observation = rc.read_rollout(F56)
    observation.meta = dataclasses.replace(observation.meta, cli_version='unknown')
    baseline = Baseline.from_observation(observation)
    assert baseline.ceiling is None
    dc._emit(False, 'saturated', [], baseline)
    assert 'ceiling unmeasured' in capsys.readouterr().out
