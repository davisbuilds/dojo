#!/usr/bin/env python3
"""Machine-side drift check: notice when the ground moves.

CI validates the repository. It cannot observe an effective catalog — no harness
binary, no session rollouts, no global roots — so the failures that actually hurt
this program are invisible from there. Over eight days the Codex listing ceiling
moved three times (5,440 → 4,000 → ≥4,843), a desktop update added 723 tokens of
plugins, account connectors refilled recovered headroom overnight, and 0.147.0
reversed how locators are rendered. CI ran on every pull request throughout and
could not have noticed one of them.

Each was found by a person happening to look. This is that look, automated.

It compares the newest observed session against a recorded baseline and reports
what changed. It **never mutates anything** — not the baseline (without
`--update`), not installed skills, not configuration. Its only output is a
report and an exit code.

Design rules carried from the rest of this package:

- **Fail closed.** No rollout, an unparseable one, or degraded classification is
  reported as *cannot evaluate* (exit 1), never as clean. A monitor that reports
  "no drift" when it observed nothing is worse than no monitor.
- **Compare sets, not sums.** On 2026-08-06 two uncontrolled changes cancelled to
  11 tokens with the entry count unchanged; a totals check would have reported
  that nothing happened.
- **A ceiling belongs to one build.** Samples are never pooled across builds, and
  a build change is itself reportable drift.

Exit: 0 no drift, 1 cannot evaluate, 2 drift detected, 3 blind too long
(with --max-blind-days: the check has not managed to evaluate in that many
days, so it is reporting healthy while watching nothing).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from profiles import rollout_codex as rc  # noqa: E402

# Machine-local by default and deliberately outside the repository: a baseline
# records absolute paths and installed membership for one machine, and this
# repository is public (R30).
DEFAULT_BASELINE = Path.home() / ".agents" / ".dojo-profile-baseline.json"

EXIT_CLEAN = 0
EXIT_CANNOT_EVALUATE = 1
EXIT_DRIFT = 2
# Persistent blindness is its own outcome, not drift. Reporting it as drift
# would mislabel what moved — nothing moved; the instrument stopped working.
EXIT_BLIND = 3


@dataclass
class Baseline:
    """What the last accepted observation looked like."""

    harness_build: str
    surface: str
    observed_at: str
    entry_ids: list[str] = field(default_factory=list)
    uncontrolled_ids: list[str] = field(default_factory=list)
    charged_tokens: int = 0
    saturated: bool = False
    ceiling: int | None = None

    @classmethod
    def from_observation(cls, obs: rc.RolloutObservation) -> "Baseline":
        return cls(
            harness_build=obs.meta.harness_build,
            surface=obs.meta.surface,
            observed_at=obs.meta.path.name[8:24],
            entry_ids=sorted(rc.qualified_identities(obs.listing).elements()),
            uncontrolled_ids=sorted(obs.uncontrolled_entries),
            charged_tokens=obs.charged_tokens,
            saturated=rc.is_saturated(obs),
            ceiling=obs.charged_tokens if rc.is_saturated(obs) else None,
        )


def _days_blind(baseline: Baseline | None) -> int | None:
    """Days since the last successful observation; None if there never was one.

    None and a large number mean the same thing operationally — nobody is
    watching this machine — but they are distinguished because the remedies
    differ: one machine needs a session run on it, the other needs the check
    moved off it.
    """
    if baseline is None:
        return None
    try:
        when = datetime.strptime(baseline.observed_at[:16], "%Y-%m-%dT%H-%M")
    except (ValueError, TypeError):
        return None
    return (datetime.now() - when).days


def load_baseline(path: Path) -> Baseline | None:
    if not path.exists():
        return None
    return Baseline(**json.loads(path.read_text()))


def _ceiling_explains(previous: Baseline, current: Baseline, demand_delta: int) -> bool:
    """Would reporting the demand move just restate the ceiling line?

    Saturation pins charged demand *to* the limit, so when both samples clip and
    the ceiling moved by the same amount, the two lines describe one event. A
    weekly report that says the same thing in two voices stops being read.
    """
    return (previous.saturated and current.saturated
            and previous.ceiling is not None and current.ceiling is not None
            and current.ceiling - previous.ceiling == demand_delta)


def compare(previous: Baseline, current: Baseline) -> list[str]:
    """Every difference worth a human's attention, most consequential first."""
    findings: list[str] = []

    if previous.harness_build != current.harness_build:
        # Separate the two, because they invalidate different things and a
        # monitor a human reads should not call a model switch a build change.
        prev_cli, _, prev_model = previous.harness_build.partition("/")
        cur_cli, _, cur_model = current.harness_build.partition("/")
        if prev_cli != cur_cli:
            findings.append(
                f"harness build changed: {prev_cli} -> {cur_cli}. The listing ceiling, "
                "locator form, and render mode are all build-scoped; re-derive rather "
                "than carrying the previous figures forward.")
        if prev_model != cur_model:
            findings.append(
                f"model changed: {prev_model} -> {cur_model}. The ceiling has been "
                "observed to follow the context window on some builds (2% of it) and "
                "to ignore the model entirely on others, so a model switch may or may "
                "not move it — which is why it is reported rather than assumed.")

    if previous.ceiling != current.ceiling:
        if current.ceiling is None:
            findings.append(
                f"ceiling no longer derivable (was {previous.ceiling}): nothing saturates, "
                "so the listing now fits with room. The limit is only known to be "
                f">= {current.charged_tokens}.")
        elif previous.ceiling is None:
            findings.append(
                f"ceiling became derivable at {current.ceiling}: something is clipping "
                "again, which is what discloses the limit.")
        else:
            findings.append(
                f"ceiling moved: {previous.ceiling} -> {current.ceiling}")

    if current.saturated and not previous.saturated:
        findings.append(
            "the listing is now saturated — descriptions are being clipped, mid-word "
            "and unmarked. The harness may emit no warning; it is silent well below "
            "the point where clipping begins.")
    elif previous.saturated and not current.saturated:
        findings.append("the listing no longer saturates; clipping has stopped.")

    # Multiset subtraction, not set subtraction. Codex does not shadow across
    # roots — it lists and charges every copy of a duplicated name — so losing
    # one of two copies is a real change that leaves the two *sets* identical.
    before, after = Counter(previous.entry_ids), Counter(current.entry_ids)
    gone = sorted((before - after).elements())
    arrived = sorted((after - before).elements())
    if gone or arrived:
        findings.append(
            f"listed entries changed: -{len(gone)} +{len(arrived)}"
            + (f" | removed: {', '.join(gone[:6])}" if gone else "")
            + (f" | added: {', '.join(arrived[:6])}" if arrived else ""))

    # Membership answers *what* is listed; only the total answers *how much the
    # same listing now costs*. A vendor rewriting one description moves no
    # identity and is invisible to every comparison above.
    demand_delta = current.charged_tokens - previous.charged_tokens
    if demand_delta and not _ceiling_explains(previous, current, demand_delta):
        # Only attribute a cause when the evidence supports one. If membership
        # moved, that line already explains this; claiming a vendor content
        # rewrite on top of it would be a cause the observation does not show.
        cause = (" with membership unchanged — entry content is rendered by the "
                 "vendor and can change under a stable identity, so this is "
                 "headroom moving with nothing done locally"
                 if not (gone or arrived) else
                 "; see the entry-set change above")
        findings.append(
            f"charged demand moved: {previous.charged_tokens} -> "
            f"{current.charged_tokens} ({demand_delta:+d}){cause}.")

    ub, ua = set(previous.uncontrolled_ids), set(current.uncontrolled_ids)
    if ub != ua:
        # Reported separately even when the entry-set line already covers it:
        # this is demand the operator cannot govern from the repository, and it
        # moves without any local action.
        findings.append(
            f"uncontrolled entries changed: -{len(ub - ua)} +{len(ua - ub)}. "
            "These are vendor and account-synced entries; a local disable of an "
            "account-synced connector is inert.")

    return findings


def run(baseline_path: Path, *, cwd: str | None = None, update: bool = False,
        as_json: bool = False, max_blind_days: int | None = None) -> int:
    errors: list[tuple[Path, str]] = []
    observations = rc.observations(
        cwd=cwd, surface=rc.SURFACE_TUI, errors=errors, limit=1)

    if not observations:
        detail = f"; {len(errors)} rollouts were unparseable" if errors else ""
        findings = [f"no parseable {rc.SURFACE_TUI} session found{detail}"]

        # Being unable to evaluate is normal for a machine used interactively
        # only now and then, and treating a quiet week as red trains the
        # operator to ignore the job. Being unable to evaluate *for months*, or
        # never having managed it at all, is the opposite: it is the monitor
        # reporting healthy while watching nothing, which is precisely the
        # failure this module was written to prevent.
        blind_days = _days_blind(load_baseline(baseline_path))
        if max_blind_days is not None and (
                blind_days is None or blind_days > max_blind_days):
            findings.append(
                (f"this machine has never been successfully observed"
                 if blind_days is None else
                 f"last successful observation was {blind_days}d ago")
                + f", past the {max_blind_days}d threshold. Nothing here is "
                  "being watched: run an interactive session on this machine, "
                  "or stop scheduling the check on it.")
            _emit(as_json, "blind", findings, None)
            return EXIT_BLIND

        if blind_days is not None:
            findings.append(f"last successful observation was {blind_days}d ago"
                            + (f" (threshold {max_blind_days}d)"
                               if max_blind_days is not None else ""))
        _emit(as_json, "cannot-evaluate", findings, None)
        return EXIT_CANNOT_EVALUATE

    current_obs = observations[0]
    alarm = current_obs.classification_alarm
    if alarm:
        _emit(as_json, "cannot-evaluate", [f"classification degraded: {alarm}"], None)
        return EXIT_CANNOT_EVALUATE

    current = Baseline.from_observation(current_obs)
    previous = load_baseline(baseline_path)

    if previous is None:
        if update:
            _write(baseline_path, current)
            _emit(as_json, "baseline-recorded", [], current)
            return EXIT_CLEAN
        _emit(as_json, "cannot-evaluate",
              [f"no baseline at {baseline_path}; run with --update to record one"], current)
        return EXIT_CANNOT_EVALUATE

    findings = compare(previous, current)
    if update:
        _write(baseline_path, current)
    _emit(as_json, "drift" if findings else "clean", findings, current)
    return EXIT_DRIFT if findings else EXIT_CLEAN


def _write(path: Path, baseline: Baseline) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(baseline), indent=2, sort_keys=True) + "\n")


def _emit(as_json: bool, state: str, findings: list[str], current: Baseline | None) -> None:
    if as_json:
        payload = {"state": state, "findings": findings,
                   "observed": asdict(current) if current else None}
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    if current:
        ceiling = current.ceiling if current.ceiling is not None else f">={current.charged_tokens}"
        print(f"{current.surface} {current.harness_build} @ {current.observed_at}: "
              f"{len(current.entry_ids)} entries, {current.charged_tokens} charged, "
              f"ceiling {ceiling}, saturated={current.saturated}")
    print(f"state: {state}")
    for finding in findings:
        print(f"  - {finding}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--cwd", default=None,
                        help="only consider sessions from this working directory")
    parser.add_argument("--update", action="store_true",
                        help="record the current observation as the new baseline")
    parser.add_argument("--json", dest="as_json", action="store_true")
    parser.add_argument("--max-blind-days", type=int, default=None,
                        help="escalate to exit 3 when the check has been unable "
                             "to evaluate for longer than this")
    args = parser.parse_args(argv)
    return run(args.baseline, cwd=args.cwd, update=args.update,
           as_json=args.as_json, max_blind_days=args.max_blind_days)


if __name__ == "__main__":
    raise SystemExit(main())
