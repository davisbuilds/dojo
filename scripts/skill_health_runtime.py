"""Opt-in runtime layer for the skill health report (feedback-loop phase 2).

Consumes AgentMonitor's `GET /api/v2/analytics/skills/health` and folds
per-skill trigger health into the static report produced by `skills_health.py`.
This module performs no network I/O at import time; it acts only when
`skills_health.py` is invoked with runtime flags.

Design notes:
- dojo-scoping is inherent in the static report: `build_report` lists exactly
  the skills under `skills/`, so a health row whose name is not already a report
  entry is non-dojo and ignored.
- Misfire is displayed with its eligible denominator, labeled experimental, and
  is never a ranking input (the signal is under validation upstream).
"""

from __future__ import annotations

import json
import urllib.request

DEFAULT_URL = "http://127.0.0.1:3141/api/v2/analytics/skills/health"

# Fields every health row must carry for the join to be meaningful.
_REQUIRED_ROW_KEYS = ("name", "invocations", "neverFired")


def load_health_rows(*, url: str | None, path: str | None) -> list[dict]:
    """Return the `data` rows from a health payload (file or live endpoint).

    Raises RuntimeError on connection failure, timeout, non-JSON, a missing
    `data` list, or an item that lacks the required keys — never a partial or
    fabricated result.
    """
    source = path or url or "<none>"
    try:
        if path is not None:
            with open(path, "r", encoding="utf-8") as fh:
                raw = fh.read()
        else:
            if url is None:
                raise RuntimeError("load_health_rows requires either url or path")
            with urllib.request.urlopen(url, timeout=5) as resp:
                raw = resp.read().decode("utf-8")
    except RuntimeError:
        raise
    except Exception as exc:  # noqa: BLE001 — surface any I/O failure honestly
        raise RuntimeError(f"could not read skill health from {source}: {exc}") from exc

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"skill health from {source} was not valid JSON: {exc}") from exc

    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise RuntimeError(f"skill health from {source} is missing a 'data' list")

    rows = payload["data"]
    for row in rows:
        if not isinstance(row, dict) or any(key not in row for key in _REQUIRED_ROW_KEYS):
            raise RuntimeError(
                f"skill health from {source} has a malformed row "
                f"(each row needs {', '.join(_REQUIRED_ROW_KEYS)}): {row!r}"
            )
    return rows


def enrich_report(report: dict, rows: list[dict], *, source: str) -> dict:
    """Fold runtime health into the per-skill report, scoped to dojo skills.

    Attaches runtime fields to each existing report entry (keyed by `skill`).
    Health rows whose name is not already a dojo report entry are non-dojo and
    ignored. Dojo skills with no matching row are marked unknown
    (`never_fired=None`), distinct from an explicit `never_fired=False`.
    Mutates and returns `report`.
    """
    rows_by_name = {row["name"]: row for row in rows}

    for entry in report["skills"]:
        row = rows_by_name.get(entry["skill"])
        if row is None:
            entry.update(
                invocations=0,
                never_fired=None,
                last_invoked_at=None,
                misfire_rate=None,
                misfire_eligible=0,
                misfires=None,
            )
            continue
        entry.update(
            invocations=row["invocations"],
            never_fired=row["neverFired"],
            last_invoked_at=row.get("lastInvokedAt"),
            misfire_rate=row.get("misfireRate"),
            misfire_eligible=row.get("misfireEligible", 0),
            misfires=row.get("misfires"),
        )

    report["summary"]["runtime_source"] = source
    report["summary"]["never_fired"] = sum(
        1 for e in report["skills"] if e.get("never_fired") is True
    )
    report["summary"]["invoked"] = sum(
        1 for e in report["skills"] if e.get("invocations", 0) > 0
    )
    return report


def _rank_key(entry: dict) -> tuple:
    """Ordering key for the runtime section. Misfire is deliberately absent.

    Groups, in order: never-fired dojo skills (0), a rarely-fired band
    0<inv<3 (1), the measured rest by invocations ascending (2), and skills
    with no runtime data (3). Ties within a group break by name.
    """
    never_fired = entry.get("never_fired")
    invocations = entry.get("invocations", 0)
    if never_fired is True:
        group = 0
    elif never_fired is None:
        group = 3
    elif 0 < invocations < 3:
        group = 1
    else:
        group = 2
    # Only group 2 sorts by volume; the others sort by name alone.
    volume = invocations if group == 2 else 0
    return (group, volume, entry["skill"])


def rank_runtime_skills(report: dict) -> list[dict]:
    """Return the report's dojo skills in runtime-actionability order."""
    return sorted(report["skills"], key=_rank_key)


def _format_misfire(entry: dict) -> str:
    eligible = entry.get("misfire_eligible") or 0
    if eligible == 0:
        return "misfire —"
    return f"misfire {entry.get('misfires', 0)}/{eligible} (experimental)"


def _format_status(entry: dict) -> str:
    if entry.get("never_fired") is True:
        return "never-fired"
    if entry.get("never_fired") is None:
        return "no data"
    return f"{entry.get('invocations', 0)}x"


def render_runtime_section(report: dict) -> list[str]:
    """Render the ranked runtime-health section as a list of lines.

    Skills with runtime data are listed individually in actionability order;
    skills with no matching health row carry no signal and are collapsed into a
    single count line (the full set is still in the `--json` output).
    """
    summary = report["summary"]
    ranked = rank_runtime_skills(report)
    measured = [e for e in ranked if e.get("never_fired") is not None]
    no_data = [e for e in ranked if e.get("never_fired") is None]

    lines = [
        "",
        f"Runtime health (source: {summary.get('runtime_source')}):",
        f"  {summary.get('invoked', 0)} invoked, "
        f"{summary.get('never_fired', 0)} never-fired",
    ]
    for entry in measured:
        lines.append(
            f"  {_format_status(entry):<12} {entry['skill']:<32} {_format_misfire(entry)}"
        )
    if no_data:
        lines.append(
            f"  no data: {len(no_data)} dojo skills not present in the health payload"
        )
    return lines


# Static disclaimer: never-fired is always relative to the queried window.
_FINDINGS_CAVEAT = (
    "_Never-fired is relative to the queried range; a skill may fire outside it. "
    "Review before filing — this is a proposal, not an auto-filed entry._"
)


def render_findings(report: dict) -> str:
    """Render BACKLOG-shaped findings for never-fired dojo skills.

    One block per never-fired dojo skill (alphabetical), matching the repo's
    BACKLOG item shape (What / Why it matters / Sketch + `noted` status). Emits
    a maintainer proposal only; nothing is written to any file.
    """
    never_fired = sorted(
        (e["skill"] for e in report["skills"] if e.get("never_fired") is True)
    )

    lines = ["## Proposed findings: never-fired dojo skills", "", _FINDINGS_CAVEAT, ""]
    if not never_fired:
        lines.append("No never-fired dojo skills in the queried health data.")
        return "\n".join(lines)

    for skill in never_fired:
        lines.extend(
            [
                f"#### {skill}: never fires in tracked sessions",
                "Status: noted",
                f"- **What**: `{skill}` was invoked 0 times across the tracked "
                "AgentMonitor sessions.",
                "- **Why it matters**: A never-fired skill is dead weight in the "
                "catalog and the shared context budget — its description may not "
                "trigger, or the capability may be redundant.",
                f"- **Sketch**: Review `{skill}`'s `description` triggers against "
                "real tasks; sharpen the trigger or retire the skill, then "
                "re-check with `skill-evals`.",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"
