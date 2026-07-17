#!/usr/bin/env python3
"""Debounce state for the SessionStart skill-drift notice.

The SessionStart hook runs the skill-standardizer audit and, when installed
global copies have diverged from canonical, injects a one-line notice into the
session. To stay effective without nagging, it speaks only when the *set* of
drifted skills changes — not on every session while the same drift persists.

This module holds that decision logic (pure, unit-tested) plus small state-file
IO. The audit call itself lives in the bash hook, which passes the drifted-skill
list in; keeping IO and policy here makes the behavior testable without a shell.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def should_emit(current: list[str], prior: list[str]) -> bool:
    """Emit the notice only when there is drift and its set has changed.

    `current` / `prior` are sorted lists of drifted skill names. Returns False
    when clean (nothing to say) or when the set matches what was last reported
    (already seen — do not nag).
    """
    return bool(current) and current != prior


def format_notice(drifted: list[str]) -> str:
    """Render the SessionStart notice for a non-empty drifted-skill set."""
    names = ", ".join(drifted)
    count = len(drifted)
    noun = "skill" if count == 1 else "skills"
    return (
        f"## Skill Drift\n\n"
        f"{count} installed global {noun} diverged from canonical: {names}. "
        f"Propagate with:\n\n"
        f"    python3 skills/skill-standardizer/scripts/sync.py "
        f"--only-existing --global-policy prefer-primary-link --apply\n\n"
        f"Then re-audit. (Informational — not a blocker.)\n"
    )


def load_prior(state_path: Path) -> list[str]:
    """Read the last-reported drifted-skill set; [] when absent or unreadable."""
    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    drifted = data.get("drifted", []) if isinstance(data, dict) else []
    return sorted(str(name) for name in drifted)


def save_current(state_path: Path, current: list[str], updated: str) -> None:
    """Persist the current drifted-skill set as the new baseline."""
    state_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"drifted": sorted(current), "updated": updated}
    state_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def extract_drifted(report: dict) -> list[str]:
    """Pull the diverged-install set (CONTENT_DRIFT) from an audit report."""
    issues = report.get("issues", []) if isinstance(report, dict) else []
    return sorted(
        {issue["skill"] for issue in issues if issue.get("code") == "CONTENT_DRIFT"}
    )


def run(report: dict, state_path: Path, now: str) -> str:
    """Decide, persist the new baseline, and return the notice text ("" = silent).

    Always refreshes the baseline — including clearing it when drift resolves —
    so the next session compares against the true current state.
    """
    current = extract_drifted(report)
    prior = load_prior(state_path)
    emit = should_emit(current, prior)
    save_current(state_path, current, now)
    return format_notice(current) if emit else ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Debounced skill-drift notice.")
    parser.add_argument("--state", required=True, help="Path to the debounce state file.")
    parser.add_argument(
        "--report",
        help="Path to an audit JSON report; reads stdin when omitted.",
    )
    args = parser.parse_args(argv)

    raw = Path(args.report).read_text(encoding="utf-8") if args.report else sys.stdin.read()
    try:
        report = json.loads(raw)
    except ValueError:
        # A malformed/empty report is not worth failing a session over.
        return 0

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    notice = run(report, Path(args.state), now)
    if notice:
        print(notice)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
