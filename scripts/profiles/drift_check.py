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

Exit: 0 no drift (or an opted-in uncontrolled-membership notice),
1 cannot evaluate, 2 drift detected, 3 blind too long
(with --max-blind-days: the check has not managed to evaluate in that many
days, so it is reporting healthy while watching nothing), 4 saturated (the
listing is clipping right now, whether or not anything changed).

Precedence among those, and why it is not arbitrary: 3 outranks 4 because a
present-tense claim needs present-tense evidence; 4 outranks 2 because drift is
accepted into the baseline by --update and saturation is not; 2 outranks a stale
3 because "A differs from B" stays true however old A and B are.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from profiles import rollout_codex as rc  # noqa: E402

# WHY: outside the repository, because a baseline records absolute paths and
# installed membership for one machine, and this repository is public.
DEFAULT_BASELINE = Path.home() / ".agents" / ".dojo-profile-baseline.json"

_SURFACE_ORDER = (rc.SURFACE_TUI, rc.SURFACE_DESKTOP)


def _surfaces_label(surfaces) -> str:
    """"codex-tui or Codex Desktop", in the order a reader expects them."""
    return " or ".join(sorted(surfaces, key=_SURFACE_ORDER.index))


def _surface_class(surface: str) -> str:
    """Interactive Codex surfaces compare as one; any other stays itself.

    A machine used from both would otherwise read as a surface change whenever
    the newest session switched, which is not a change to anything governed.
    """
    return "interactive" if surface in rc.INTERACTIVE_SURFACES else surface

EXIT_CLEAN = 0
EXIT_CANNOT_EVALUATE = 1
EXIT_DRIFT = 2
EXIT_BLIND = 3
# WHY: neither blindness nor saturation is drift. A clipping listing stays
# degraded until someone acts, while `--update` accepts drift, so reporting
# saturation as drift announces it once and then debounces it into silence.
EXIT_SATURATED = 4


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
    catalog_kind: str = "full"

    @classmethod
    def from_observation(cls, obs: rc.RolloutObservation) -> "Baseline":
        return cls(
            harness_build=obs.meta.harness_build,
            surface=obs.meta.surface,
            observed_at=_observation_stamp(obs),
            entry_ids=sorted(rc.qualified_identities(obs.listing).elements()),
            uncontrolled_ids=sorted(obs.uncontrolled_entries),
            charged_tokens=obs.charged_tokens,
            saturated=rc.is_saturated(obs),
            ceiling=(obs.charged_tokens if rc.is_saturated(obs)
                     and obs.meta.catalog_kind == "full"
                     and obs.meta.cli_version != "unknown" else None),
            catalog_kind=obs.meta.catalog_kind,
        )


def _observation_cwd(obs: rc.RolloutObservation) -> str:
    """The working directory a session ran in — the key a baseline is filed under."""
    return str(obs.meta.cwd)


def _observation_stamp(obs: rc.RolloutObservation) -> str:
    return obs.meta.observed_at or obs.meta.path.name[8:24]


def _timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = (datetime.strptime(value, "%Y-%m-%dT%H-%M")
                  if re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}-\d{2}", value)
                  else datetime.fromisoformat(value.replace("Z", "+00:00")))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else parsed.astimezone()


def _age_days(value: str | None) -> int | None:
    when = _timestamp(value)
    return (datetime.now(timezone.utc) - when).days if when is not None else None


def _observation_age_days(obs: rc.RolloutObservation) -> int | None:
    return _age_days(_observation_stamp(obs))


def _days_blind(baseline: Baseline | None) -> int | None:
    return _age_days(baseline.observed_at) if baseline is not None else None


def load_store(path: Path) -> dict[str, Baseline]:
    """Baselines keyed by working directory.

    Keyed rather than single because a listing is not a property of the machine
    alone. Measured here at build 0.144.1: `~/Dev` listed 55 entries while
    `~/Dev/dojo` listed 112, the repository's own project-scoped catalog on top
    of the global one. One shared baseline would accept whichever project was
    seen last and report the difference as drift on the next switch, then report
    the reverse after that.

    This is the rule the module already applies to builds, extended to the other
    axis a sample belongs to: never pool observations that were never comparable.
    """
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}
    if not isinstance(raw, dict):
        return {}
    # WHY: a pre-keying baseline cannot be filed under a cwd it never recorded, so
    # it is dropped rather than guessed at: one re-seeding cycle is cheap, a
    # baseline attributed to the wrong project is not.
    if "harness_build" in raw:
        return {}
    return {cwd: Baseline(**data) for cwd, data in raw.items()}


def load_baseline(path: Path, cwd: str | None = None) -> Baseline | None:
    store = load_store(path)
    if cwd is not None:
        return store.get(cwd)
    return next(iter(store.values())) if len(store) == 1 else None


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
        prev_cli, _, prev_model = previous.harness_build.partition("/")
        cur_cli, _, cur_model = current.harness_build.partition("/")
        if prev_cli != cur_cli:
            if "unknown" in (prev_cli, cur_cli):
                findings.append(f"harness build provenance changed: {prev_cli} -> {cur_cli}; "
                                "a resumed catalog does not establish its process build.")
            else:
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

    if previous.catalog_kind != current.catalog_kind:
        findings.append(f"catalog evidence changed: {previous.catalog_kind} -> "
                        f"{current.catalog_kind}; reconstructed token cost is an estimate, "
                        "not a measured render ceiling.")

    if previous.ceiling != current.ceiling:
        if current.catalog_kind != "full":
            findings.append("ceiling is not derivable from a reconstructed catalog.")
        elif current.ceiling is None and current.saturated:
            findings.append("clipping is visible but its render build is unverified; "
                            "the previous build-specific ceiling cannot be retained.")
        elif current.ceiling is None:
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

    # WHY: multiset subtraction, not set subtraction. Codex lists and charges every
    # copy of a duplicated name, so losing one of two copies leaves the sets equal.
    before, after = Counter(previous.entry_ids), Counter(current.entry_ids)
    gone = sorted((before - after).elements())
    arrived = sorted((after - before).elements())
    if gone or arrived:
        findings.append(
            f"listed entries changed: -{len(gone)} +{len(arrived)}"
            + (f" | removed: {', '.join(gone[:6])}" if gone else "")
            + (f" | added: {', '.join(arrived[:6])}" if arrived else ""))

    # WHY: membership answers what is listed; only the total shows a vendor
    # rewriting a description, which moves no identity.
    demand_delta = current.charged_tokens - previous.charged_tokens
    if demand_delta and not _ceiling_explains(previous, current, demand_delta):
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
        findings.append(
            f"uncontrolled entries changed: -{len(ub - ua)} +{len(ua - ub)}. "
            "These are vendor and account-synced entries; a local disable of an "
            "account-synced connector is inert.")

    return findings


def _only_uncontrolled_membership_changed(previous: Baseline,
                                          current: Baseline) -> bool:
    """Whether the transition is packaging churn outside local control.

    Health monitors may treat this one transition as a notice. The normal drift
    command stays strict, and any build, surface, ceiling, saturation, or
    controlled-membership change remains drift. Charged demand may accompany
    the uncontrolled membership delta; the observation cannot attribute it
    more narrowly.
    """
    if (previous.harness_build != current.harness_build
            or _surface_class(previous.surface) != _surface_class(current.surface)
            or previous.ceiling != current.ceiling
            or previous.catalog_kind != current.catalog_kind
            or previous.saturated != current.saturated
            or previous.saturated or current.saturated):
        return False

    before = Counter(previous.entry_ids)
    after = Counter(current.entry_ids)
    removed = list((before - after).elements())
    added = list((after - before).elements())
    if not removed and not added:
        return False

    uncontrolled = set(previous.uncontrolled_ids) | set(current.uncontrolled_ids)
    if any(entry_id not in uncontrolled for entry_id in removed + added):
        return False

    controlled_before = Counter(
        entry_id for entry_id in previous.entry_ids if entry_id not in uncontrolled)
    controlled_after = Counter(
        entry_id for entry_id in current.entry_ids if entry_id not in uncontrolled)
    return controlled_before == controlled_after


def _saturation_findings(obs: rc.RolloutObservation, current: Baseline) -> list[str]:
    """The standing condition, stated with the number that makes it concrete."""
    if not current.saturated:
        return []
    clipped = rc.clipped_entry_names(obs)
    bound = (f"at its {current.ceiling}-token ceiling" if current.ceiling is not None
             else "with an unmeasured ceiling")
    return [
        f"the listing is saturated {bound}: "
        f"{len(clipped)} of {len(obs.listing.entries)} descriptions are cut at "
        "the clip length, mid-word and unmarked, so skill selection is running "
        "on truncated text. This is a standing condition rather than a change — "
        "it is reported on every run until the catalog fits or the ceiling rises."
        + (f" Clipped include: {', '.join(clipped[:5])}." if clipped else "")
    ]


def run(baseline_path: Path, *, cwd: str | None = None, update: bool = False,
        as_json: bool = False, max_blind_days: int | None = None,
        uncontrolled_as_notice: bool = False,
        surfaces: tuple[str, ...] = (rc.SURFACE_TUI,)) -> int:
    # WHY: `codex exec` does not load account-synced connectors, so a baseline taken
    # from it would report phantom removals; refuse it rather than trust callers.
    unsupported = sorted(set(surfaces) - rc.INTERACTIVE_SURFACES)
    if unsupported or not surfaces:
        raise ValueError(
            f"unsupported surface {unsupported or surfaces!r}; "
            f"choose from {sorted(rc.INTERACTIVE_SURFACES)}")
    surfaces = tuple(dict.fromkeys(surfaces))
    label = _surfaces_label(surfaces)
    errors: list[tuple[Path, str]] = []
    evidence_errors: list[rc.RolloutReadError] = []
    observations = rc.observations(
        cwd=cwd, surface=surfaces, errors=errors, evidence_errors=evidence_errors, limit=1)

    # WHY: every path that cannot establish a fresh, well-classified observation
    # runs through this one gate. Guarding only the no-rollout branch let a degraded
    # classifier and an idle machine re-reading an old rollout compare clean forever.
    def blind_or(state: str, findings: list[str], code: int) -> int:
        blind_days = _days_blind(load_baseline(baseline_path, cwd))
        if max_blind_days is not None and (
                blind_days is None or blind_days > max_blind_days):
            findings = findings + [
                ("this machine has never been successfully observed"
                 if blind_days is None else
                 f"last successful observation was {blind_days}d ago")
                + f", past the {max_blind_days}d threshold. Nothing here is "
                  "being watched: run an interactive session on this machine, "
                  "or stop scheduling the check on it."]
            _emit(as_json, "blind", findings, None)
            return EXIT_BLIND
        if blind_days is not None:
            findings = findings + [
                f"last successful observation was {blind_days}d ago"
                + (f" (threshold {max_blind_days}d)" if max_blind_days is not None else "")]
        _emit(as_json, state, findings, None)
        return code

    if not observations:
        detail = f"; {len(errors)} rollouts were unparseable" if errors else ""
        return blind_or("cannot-evaluate",
                        [f"no parseable {label} session found{detail}"]
                        + [str(error) for error in evidence_errors],
                        EXIT_CANNOT_EVALUATE)

    current_obs = observations[0]
    observed_at = _timestamp(_observation_stamp(current_obs))
    blocking = [error for error in evidence_errors
                if (failed_at := _timestamp(error.meta.observed_at)) is None
                or observed_at is None or failed_at >= observed_at]
    if blocking:
        return blind_or("cannot-evaluate",
                        [f"newest catalog evidence is unreadable: {error}" for error in blocking],
                        EXIT_CANNOT_EVALUATE)
    alarm = current_obs.classification_alarm
    if alarm:
        return blind_or("cannot-evaluate",
                        [f"classification degraded: {alarm}"], EXIT_CANNOT_EVALUATE)

    observed_cwd = _observation_cwd(current_obs)
    current = Baseline.from_observation(current_obs)

    age = _observation_age_days(current_obs)
    if max_blind_days is not None and age is None:
        return blind_or("cannot-evaluate", ["observation timestamp is unavailable or invalid"],
                        EXIT_CANNOT_EVALUATE)
    stale = (max_blind_days is not None and age is not None and age > max_blind_days)

    # WHY: drift is historical and stays true however old both samples are, while
    # saturation claims the machine is clipping now, so a stale sample suppresses
    # saturation instead of being outranked by it.
    saturation = [] if stale else _saturation_findings(current_obs, current)

    def outcome(state: str, findings: list[str], code: int) -> int:
        """Saturation outranks whatever else a fresh run found.

        Not because it is worse than drift, but because it does not go away on
        its own: `--update` accepts drift into the baseline, so reporting a
        clipping listing as drift would announce it once and then debounce it
        into silence — the failure mode this outcome exists to end.
        """
        if saturation:
            _emit(as_json, "saturated", saturation + findings, current)
            return EXIT_SATURATED
        _emit(as_json, state, findings, current)
        return code

    store = load_store(baseline_path)
    previous = store.get(observed_cwd)

    if previous is None:
        if update:
            store[observed_cwd] = current
            _write(baseline_path, store)
            return outcome("baseline-recorded", [f"for {observed_cwd}"], EXIT_CLEAN)
        return outcome("cannot-evaluate",
                       [f"no baseline for {observed_cwd} at {baseline_path}; "
                        "run with --update to record one"], EXIT_CANNOT_EVALUATE)

    findings = compare(previous, current)
    notice_eligible = bool(
        findings
        and uncontrolled_as_notice
        and _only_uncontrolled_membership_changed(previous, current)
    )

    # WHY: a notice cannot make an old sample current or healthy, so --update must
    # not accept a stale sample into the baseline.
    if stale and (not findings or notice_eligible):
        relation = (
            "It differs only in uncontrolled membership"
            if notice_eligible
            else "It still matches the baseline"
        )
        _emit(as_json, "blind",
              [f"the newest {label} session is {age}d old, past the "
               f"{max_blind_days}d threshold. {relation}, but nothing new has "
               "been observed: this machine is not being watched."],
              current)
        return EXIT_BLIND

    if update:
        store[observed_cwd] = current
        _write(baseline_path, store)

    if notice_eligible:
        return outcome("notice", findings, EXIT_CLEAN)

    if findings:
        return outcome("drift", findings, EXIT_DRIFT)

    return outcome("clean", findings, EXIT_CLEAN)


def _write(path: Path, store: dict[str, Baseline]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {cwd: asdict(b) for cwd, b in store.items()}
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _emit(as_json: bool, state: str, findings: list[str], current: Baseline | None) -> None:
    if as_json:
        payload = {"state": state, "findings": findings,
                   "observed": asdict(current) if current else None}
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    if current:
        ceiling = ("unmeasured" if current.catalog_kind != "full"
                   or (current.saturated and current.ceiling is None) else
                   current.ceiling if current.ceiling is not None else f">={current.charged_tokens}")
        print(f"{current.surface} {current.harness_build} @ {current.observed_at}: "
              f"{len(current.entry_ids)} entries, {current.charged_tokens} estimated listing tokens, "
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
    parser.add_argument(
        "--surface", action="append", choices=sorted(rc.INTERACTIVE_SURFACES),
        help="a Codex surface whose sessions count as this machine's listing; "
             "repeat to accept several (default: codex-tui). Only the surfaces "
             "a person works in are accepted; codex exec renders a different "
             "listing")
    parser.add_argument(
        "--uncontrolled-as-notice", action="store_true",
        help="exit 0 while still reporting a transition limited to vendor or "
             "account-synced membership; build, saturation, ceiling, and "
             "controlled drift remain failures")
    args = parser.parse_args(argv)
    return run(args.baseline, cwd=args.cwd, update=args.update,
           as_json=args.as_json, max_blind_days=args.max_blind_days,
           uncontrolled_as_notice=args.uncontrolled_as_notice,
           surfaces=tuple(args.surface) if args.surface else (rc.SURFACE_TUI,))


if __name__ == "__main__":
    raise SystemExit(main())
