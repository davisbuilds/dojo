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
    Baseline,
    compare,
    run,
)

F110 = FIXTURES / "codex-tui-clipped-110.jsonl"
F56 = FIXTURES / "codex-tui-clipped-56.jsonl"


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


def test_a_missing_baseline_refuses_rather_than_passing(tmp_path, capsys, monkeypatch):
    """First run must not report clean; it has nothing to compare against."""
    import profiles.drift_check as dc

    monkeypatch.setattr(dc.rc, "observations",
                        lambda **kw: [rc.read_rollout(F56)])
    code = dc.run(tmp_path / "absent.json")
    assert code == EXIT_CANNOT_EVALUATE
    assert "no baseline" in capsys.readouterr().out


def test_update_records_a_baseline_then_reports_clean(tmp_path, capsys, monkeypatch):
    import profiles.drift_check as dc

    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [rc.read_rollout(F56)])
    path = tmp_path / "baseline.json"

    assert dc.run(path, update=True) == EXIT_CLEAN
    assert path.exists()
    capsys.readouterr()

    assert dc.run(path) == EXIT_CLEAN, "an unchanged machine must report clean"
    assert "state: clean" in capsys.readouterr().out


def test_drift_exits_two_and_names_what_moved(tmp_path, capsys, monkeypatch):
    import profiles.drift_check as dc

    monkeypatch.setattr(dc.rc, "observations", lambda **kw: [rc.read_rollout(F56)])
    path = tmp_path / "baseline.json"
    dc.run(path, update=True)
    capsys.readouterr()

    stale = Baseline(**json.loads(path.read_text()))
    path.write_text(json.dumps(dataclasses.asdict(
        dataclasses.replace(stale, harness_build="0.140.0/old", ceiling=5440)), indent=2))

    assert dc.run(path) == EXIT_DRIFT
    out = capsys.readouterr().out
    assert "harness build changed" in out and "ceiling moved" in out


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
    assert dc.run(path) == EXIT_DRIFT
    assert path.read_bytes() == before, "a run without --update must not rewrite the baseline"


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
