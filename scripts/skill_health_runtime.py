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
