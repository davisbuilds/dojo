#!/bin/sh
""":"
if command -v python >/dev/null 2>&1; then
    exec python "$0" "$@"
fi
exec python3 "$0" "$@"
":"""
"""Deterministic trigger-eval scaffold for skill routing assertions."""

import argparse
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9-]{1,}")
STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "when",
    "this",
    "that",
    "from",
    "into",
    "your",
    "their",
    "user",
    "users",
    "using",
    "use",
    "skill",
    "skills",
    "create",
    "creating",
    "build",
    "before",
    "after",
    "work",
    "code",
    "generate",
    "edit",
    "check",
    "run",
    "existing",
    "asks",
    "want",
    "wants",
    "like",
    "need",
    "needs",
    "also",
    "specific",
    "api",
    "via",
    "requires",
    "github",
    "session",
}


def parse_frontmatter(skill_md: Path) -> dict[str, Any]:
    text = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n?", text, re.DOTALL)
    if not match:
        return {}
    try:
        parsed = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def normalize_tokens(text: str) -> set[str]:
    return {
        token
        for token in TOKEN_RE.findall(text.lower())
        if token not in STOPWORDS and len(token) > 2
    }


def build_skill_index(skills_root: Path, selected: set[str] | None) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    all_name_tokens: dict[str, list[str]] = {}
    for skill_md in sorted(skills_root.glob("*/SKILL.md")):
        skill = skill_md.parent.name
        if selected and skill not in selected:
            continue
        fm = parse_frontmatter(skill_md)
        description = fm.get("description", "")
        if not isinstance(description, str):
            description = ""

        declared = fm.get("triggers", [])
        if not isinstance(declared, list):
            declared = []
        declared = [t.strip() for t in declared if isinstance(t, str) and t.strip()]

        combined = f"{skill} {description}"
        name_tokens = set(skill.lower().split("-"))
        index[skill] = {
            "description": description,
            "tokens": normalize_tokens(combined),
            "name_tokens": name_tokens,
            "declared_triggers": declared,
        }
        for token in name_tokens:
            all_name_tokens.setdefault(token, []).append(skill)

    # Compute discriminating name tokens: exclude tokens shared across multiple skills
    for skill, data in index.items():
        data["disc_name_tokens"] = {
            t for t in data["name_tokens"] if len(all_name_tokens.get(t, [])) == 1
        }

    return index


def score_trigger(prompt: str, case_type: str, skill: str, skill_data: dict[str, Any]) -> float:
    prompt_lower = prompt.lower()
    prompt_tokens = normalize_tokens(prompt)
    skill_tokens = skill_data["tokens"]
    name_tokens = skill_data.get("disc_name_tokens", skill_data["name_tokens"])

    if not prompt_tokens:
        lexical = 0.0
    else:
        overlap = len(prompt_tokens & skill_tokens)
        lexical = overlap / max(1, len(prompt_tokens))

    name_overlap = len(prompt_tokens & name_tokens) / max(1, len(name_tokens))

    explicit_boost = 0.0
    explicit_skill = None
    explicit_match = re.search(r"\$([a-z0-9-]+)", prompt_lower)
    if explicit_match:
        explicit_skill = explicit_match.group(1)
    if f"${skill}" in prompt_lower:
        explicit_boost += 0.9
    elif skill in prompt_lower:
        explicit_boost += 0.45
    elif explicit_skill and explicit_skill != skill:
        explicit_boost -= 0.25

    intent_boost = 0.0
    if case_type == "explicit":
        intent_boost += 0.1
    elif case_type == "negative":
        intent_boost -= 0.05

    score = (0.55 * lexical) + (0.25 * name_overlap) + explicit_boost + intent_boost
    return max(0.0, min(1.0, score))


def threshold_for(case_type: str) -> float:
    if case_type == "explicit":
        return 0.22
    if case_type == "negative":
        return 0.35
    if case_type == "contextual":
        return 0.15
    return 0.09


def safe_div(num: float, den: float) -> float:
    return 0.0 if den == 0 else num / den


def evaluate_declared_triggers(skills: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Assert each skill's declared `triggers:` self-route without collisions.

    For every declared trigger phrase, score it against every skill. The owning
    skill must clear the explicit-case threshold and must not be tied or beaten
    by any other skill (a tie/loss is a routing collision).
    """
    case_type = "explicit"
    threshold = threshold_for(case_type)
    assertions: list[dict[str, Any]] = []

    for owner in sorted(skills):
        triggers = skills[owner].get("declared_triggers", [])
        for phrase in triggers:
            scores = {
                skill: score_trigger(phrase, case_type, skill, data)
                for skill, data in skills.items()
            }
            self_score = scores[owner]
            competitors = sorted(
                ((s, sc) for s, sc in scores.items() if s != owner),
                key=lambda item: item[1],
                reverse=True,
            )
            top_other, top_other_score = competitors[0] if competitors else (None, 0.0)

            routes = self_score >= threshold
            collision = top_other is not None and top_other_score >= self_score
            passed = routes and not collision

            assertions.append(
                {
                    "skill": owner,
                    "trigger": phrase,
                    "self_score": round(self_score, 4),
                    "routes": routes,
                    "collision_with": top_other if collision else None,
                    "collision_score": round(top_other_score, 4) if collision else None,
                    "passed": passed,
                }
            )

    passed = sum(1 for item in assertions if item["passed"])
    failed = len(assertions) - passed
    skills_with_triggers = sum(1 for s in skills.values() if s.get("declared_triggers"))

    return {
        "summary": {
            "skills_with_triggers": skills_with_triggers,
            "assertions": len(assertions),
            "passed": passed,
            "failed": failed,
        },
        "assertions": assertions,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic trigger eval scaffold for skills")
    parser.add_argument("--cases", help="Path to trigger case JSON file")
    parser.add_argument(
        "--from-triggers",
        action="store_true",
        help="Derive cases from skills' declared `triggers:` and assert self-routing without collisions",
    )
    parser.add_argument("--skills-root", default="skills", help="Path to skills directory (default: skills)")
    parser.add_argument("--skills", help="Comma-separated subset of skills to score")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    if not args.cases and not args.from_triggers:
        parser.error("provide --cases <file> and/or --from-triggers")

    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[3]

    skills_root = Path(args.skills_root)
    if not skills_root.is_absolute():
        skills_root = (repo_root / skills_root).resolve()

    if not skills_root.is_dir():
        print(f"Skills root not found: {skills_root}", file=sys.stderr)
        return 1

    selected = None
    if args.skills:
        selected = {name.strip() for name in args.skills.split(",") if name.strip()}

    skills = build_skill_index(skills_root, selected)
    if not skills:
        print("No skills available for scoring", file=sys.stderr)
        return 1

    # Mode: derive cases from declared `triggers:` only.
    if args.from_triggers and not args.cases:
        output = evaluate_declared_triggers(skills)
        print(json.dumps(output, indent=2) if args.pretty else json.dumps(output))
        return 1 if output["summary"]["failed"] else 0

    cases_path = Path(args.cases)
    if not cases_path.is_absolute():
        cases_path = (repo_root / cases_path).resolve()
    if not cases_path.exists():
        print(f"Cases file not found: {cases_path}", file=sys.stderr)
        return 1

    payload = json.loads(cases_path.read_text(encoding="utf-8"))
    cases = payload.get("cases", [])
    if not isinstance(cases, list) or not cases:
        print("No cases found", file=sys.stderr)
        return 1

    assertions: list[dict[str, Any]] = []
    counters = defaultdict(lambda: {"tp": 0, "fp": 0, "tn": 0, "fn": 0})

    for raw_case in cases:
        if not isinstance(raw_case, dict):
            continue
        case_id = str(raw_case.get("id", "case"))
        case_type = str(raw_case.get("type", "implicit")).lower()
        prompt = str(raw_case.get("prompt", ""))
        expected = raw_case.get("expected", {})
        if not isinstance(expected, dict):
            expected = {}

        should_trigger = expected.get("trigger", [])
        should_avoid = expected.get("avoid", [])
        if not isinstance(should_trigger, list):
            should_trigger = []
        if not isinstance(should_avoid, list):
            should_avoid = []

        labeled = []
        labeled.extend([(skill, True) for skill in should_trigger if skill in skills])
        labeled.extend([(skill, False) for skill in should_avoid if skill in skills])

        for skill, expected_bool in labeled:
            score = score_trigger(prompt, case_type, skill, skills[skill])
            predicted = score >= threshold_for(case_type)
            passed = predicted == expected_bool

            if expected_bool and predicted:
                counters[skill]["tp"] += 1
            elif (not expected_bool) and predicted:
                counters[skill]["fp"] += 1
            elif (not expected_bool) and (not predicted):
                counters[skill]["tn"] += 1
            elif expected_bool and (not predicted):
                counters[skill]["fn"] += 1

            assertions.append(
                {
                    "case_id": case_id,
                    "skill": skill,
                    "expected": expected_bool,
                    "predicted": predicted,
                    "score": round(score, 4),
                    "passed": passed,
                    "type": case_type,
                }
            )

    skill_rows = []
    for skill, row in sorted(counters.items()):
        tp, fp, tn, fn = row["tp"], row["fp"], row["tn"], row["fn"]
        precision = safe_div(tp, tp + fp)
        recall = safe_div(tp, tp + fn)
        f1 = safe_div(2 * precision * recall, precision + recall)
        skill_rows.append(
            {
                "skill": skill,
                "tp": tp,
                "fp": fp,
                "tn": tn,
                "fn": fn,
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1": round(f1, 4),
            }
        )

    passed = sum(1 for item in assertions if item["passed"])
    failed = len(assertions) - passed

    output = {
        "summary": {
            "cases": len(cases),
            "assertions": len(assertions),
            "passed": passed,
            "failed": failed,
        },
        "skills": skill_rows,
        "assertions": assertions,
    }

    declared_failed = 0
    if args.from_triggers:
        declared = evaluate_declared_triggers(skills)
        output["declared_triggers"] = declared
        declared_failed = declared["summary"]["failed"]

    if args.pretty:
        print(json.dumps(output, indent=2))
    else:
        print(json.dumps(output))

    return 1 if (failed or declared_failed) else 0


if __name__ == "__main__":
    sys.exit(main())
