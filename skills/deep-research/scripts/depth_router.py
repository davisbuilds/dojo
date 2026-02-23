#!/usr/bin/env python3
"""Depth routing utility for deep research tasks.

Selects quick, standard, or deep search depth using simple task signals.
Reads JSON input from --input or stdin and writes JSON to --output or stdout.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from typing import Any, Dict, List


DEPTH_LEVELS = ("quick", "standard", "deep")


@dataclass(frozen=True)
class DepthBudget:
    min_searches: int
    max_searches: int
    min_tracks: int
    max_tracks: int
    target_kept_findings: int
    max_kept_findings: int


BUDGETS: Dict[str, DepthBudget] = {
    "quick": DepthBudget(
        min_searches=3,
        max_searches=6,
        min_tracks=1,
        max_tracks=1,
        target_kept_findings=4,
        max_kept_findings=6,
    ),
    "standard": DepthBudget(
        min_searches=8,
        max_searches=20,
        min_tracks=2,
        max_tracks=4,
        target_kept_findings=8,
        max_kept_findings=12,
    ),
    "deep": DepthBudget(
        min_searches=20,
        max_searches=80,
        min_tracks=4,
        max_tracks=8,
        target_kept_findings=16,
        max_kept_findings=24,
    ),
}


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "i",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "was",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "with",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Route a research task to quick/standard/deep depth")
    parser.add_argument("--input", help="Path to JSON input. Reads stdin when omitted.")
    parser.add_argument("--output", help="Path to write JSON output. Writes stdout when omitted.")
    parser.add_argument(
        "--override-depth",
        choices=DEPTH_LEVELS,
        help="Force a specific depth tier regardless of heuristics.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output.",
    )
    return parser.parse_args()


def read_json(path: str | None) -> Dict[str, Any]:
    if path:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        raw = sys.stdin.read().strip()
        data = json.loads(raw) if raw else {}

    if not isinstance(data, dict):
        raise ValueError("Input must be a JSON object")
    return data


def write_json(path: str | None, payload: Dict[str, Any], pretty: bool = False) -> None:
    dump = json.dumps(payload, indent=2 if pretty else None, ensure_ascii=True)
    if pretty:
        dump += "\n"

    if path:
        with open(path, "w", encoding="utf-8") as f:
            f.write(dump)
    else:
        sys.stdout.write(dump)
        if not pretty:
            sys.stdout.write("\n")


def tokenize(text: str) -> List[str]:
    terms = re.findall(r"[a-z0-9]+", text.lower())
    return [t for t in terms if len(t) > 2 and t not in STOPWORDS]


def infer_task_type(payload: Dict[str, Any], brief: str) -> str:
    explicit = str(payload.get("task_type", "")).strip().lower()
    if explicit:
        return explicit

    text = brief.lower()
    if any(k in text for k in ("compare", "versus", "vs", "trade-off", "tradeoff")):
        return "comparison"
    if any(k in text for k in ("due diligence", "risk", "compliance", "regulatory", "legal")):
        return "due-diligence"
    if any(k in text for k in ("summarize", "overview", "intro", "explain")):
        return "overview"
    if any(k in text for k in ("latest", "today", "recent", "news", "current")):
        return "current-events"
    if any(k in text for k in ("best", "top", "list", "recommend")):
        return "ranking"
    return "general"


def signal_score(payload: Dict[str, Any], brief: str, task_type: str) -> tuple[int, List[str]]:
    score = 0
    reasons: List[str] = []

    flags = payload.get("task_context")
    if not isinstance(flags, dict):
        flags = {}

    high_stakes = bool(payload.get("high_stakes", flags.get("high_stakes", False)))
    requires_current = bool(payload.get("requires_current_info", flags.get("requires_current_info", False)))
    multi_entity = bool(payload.get("multi_entity_comparison", flags.get("multi_entity_comparison", False)))
    unknown_scope = bool(payload.get("unknown_scope", flags.get("unknown_scope", False)))

    if high_stakes:
        score += 3
        reasons.append("High-stakes task requires stronger source coverage.")

    if requires_current:
        score += 1
        reasons.append("Freshness-sensitive topic requires wider retrieval.")

    if multi_entity:
        score += 2
        reasons.append("Multi-entity comparison benefits from parallel tracks.")

    if unknown_scope:
        score += 2
        reasons.append("Unclear scope needs exploratory breadth before narrowing.")

    task_weights = {
        "ranking": 0,
        "overview": 1,
        "general": 1,
        "current-events": 2,
        "comparison": 3,
        "due-diligence": 4,
        "literature-review": 4,
    }
    score += task_weights.get(task_type, 1)
    reasons.append(f"Task type '{task_type}' contributes {task_weights.get(task_type, 1)} points.")

    brief_terms = tokenize(brief)
    if len(brief_terms) >= 35:
        score += 2
        reasons.append("Long brief suggests broader constraint surface.")
    elif len(brief_terms) >= 20:
        score += 1
        reasons.append("Moderate brief complexity suggests standard depth.")

    if any(k in brief.lower() for k in ("risk", "failure", "safety", "security", "compliance")):
        score += 2
        reasons.append("Risk-sensitive language detected; increase depth.")

    if any(k in brief.lower() for k in ("quick", "fast", "short answer", "tl;dr")):
        score -= 1
        reasons.append("Request indicates a short-turnaround preference.")

    return score, reasons


def pick_depth(score: int) -> str:
    if score <= 2:
        return "quick"
    if score <= 6:
        return "standard"
    return "deep"


def build_output(
    selected_depth: str,
    score: int,
    reasons: List[str],
    task_type: str,
    override_applied: bool,
) -> Dict[str, Any]:
    budget = BUDGETS[selected_depth]

    return {
        "selected_depth": selected_depth,
        "override_applied": override_applied,
        "score": score,
        "task_type": task_type,
        "reasons": reasons,
        "budgets": {
            "searches": {
                "min": budget.min_searches,
                "max": budget.max_searches,
            },
            "tracks": {
                "min": budget.min_tracks,
                "max": budget.max_tracks,
            },
            "findings": {
                "target_kept": budget.target_kept_findings,
                "max_kept": budget.max_kept_findings,
            },
            "stop_rules": [
                "Stop when two consecutive query rounds add no materially new findings.",
                "Stop when required claim categories have at least two independent sources.",
                "Stop when confidence gaps are exhausted or search budget max is reached.",
            ],
        },
    }


def main() -> int:
    args = parse_args()

    try:
        payload = read_json(args.input)
    except Exception as exc:
        sys.stderr.write(f"Failed to parse input JSON: {exc}\n")
        return 1

    brief = str(payload.get("research_brief") or payload.get("query") or payload.get("task") or "").strip()
    task_type = infer_task_type(payload, brief)

    requested_override = args.override_depth or str(payload.get("override_depth", "")).strip().lower()
    override_applied = requested_override in DEPTH_LEVELS

    if override_applied:
        selected_depth = requested_override
        score = -1
        reasons = [f"Depth override applied: {requested_override}."]
    else:
        score, reasons = signal_score(payload, brief, task_type)
        selected_depth = pick_depth(score)

    out = build_output(
        selected_depth=selected_depth,
        score=score,
        reasons=reasons,
        task_type=task_type,
        override_applied=override_applied,
    )

    try:
        write_json(args.output, out, pretty=args.pretty)
    except Exception as exc:
        sys.stderr.write(f"Failed to write output JSON: {exc}\n")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
