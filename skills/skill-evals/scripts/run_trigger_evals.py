#!/bin/sh
""":"
if command -v python >/dev/null 2>&1; then
    exec python "$0" "$@"
fi
exec python3 "$0" "$@"
":"""
"""Deterministic trigger-eval scaffold for skill routing assertions.

Scoring is TF-IDF cosine over stemmed tokens. Routing is inherently comparative
("which skill wins this prompt?"), so the default `--cases` assertion model is
*ranking*: the highest-scoring skill must be an expected trigger, and no avoided
skill may tie or beat it. Absolute-threshold assertions remain available via
`--threshold` for fixtures that want them, and for the "matches nothing" case a
prompt that should route to no skill is asserted against a floor.

The `--from-triggers` mode is unchanged in contract: every declared trigger phrase
must self-route to its owner without being tied or beaten by another skill.
"""

import argparse
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9-]{1,}")

# Only true grammar/function words. Domain vocabulary ("code", "review", "diff")
# is down-weighted by IDF from the corpus, not by a hand-maintained list — that
# list was both incomplete and overreaching in a catalog of coding skills.
GRAMMAR = {
    "the", "and", "for", "with", "when", "this", "that", "from", "into", "your",
    "their", "you", "not", "are", "was", "were", "its", "has", "had", "have",
    "will", "would", "can", "could", "should", "any", "all", "one", "two", "new",
    "out", "via", "per", "but", "also", "them", "they", "what", "which", "who",
    "how", "why", "get", "got", "let", "been", "being", "than", "then", "there",
    "here", "some", "such", "only", "just", "very", "more", "most", "other",
    "each", "both", "use", "using", "used", "make", "made", "want", "wants",
    "need", "needs", "like", "about",
}

# Floor score below which an avoided skill counts as "did not route" for a
# matches-nothing (empty-trigger) case. Cosine + boost stays well under this for
# genuinely unrelated prompts.
MATCH_NOTHING_FLOOR = 0.30

# Minimum score a ranking winner must clear to count as a real route. Without it,
# argmax "wins" at 0.0 when `--skills` is narrowed to one candidate or the whole
# field ties at zero on an unrelated prompt, passing a positive case vacuously.
# Kept low: legitimate weak-signal routes score around 0.10, so this only rejects
# the degenerate "nothing actually matched" case.
MIN_WINNER_SCORE = 0.05


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


def stem(token: str) -> str:
    """Light suffix stripping so 'spots'/'spot' and 'scanning'/'scan' collide.

    Deliberately conservative and plural-first: getting regular plurals right
    ('articles' -> 'article', not 'articl') matters more than perfect verb
    stemming. Silent-e verbs ('merge'/'merging') are left imperfect on purpose —
    chasing them adds ambiguity for little routing gain.
    """
    if len(token) <= 3:
        return token
    # Plurals.
    if token.endswith("ies") and len(token) > 4:
        return token[:-3] + "y"          # ponies -> pony
    if token.endswith("es") and token[-3] in "sxzo":
        return token[:-2]                # boxes -> box, processes -> process
    if token.endswith("s") and not token.endswith(("ss", "us")):
        token = token[:-1]               # spots -> spot, articles -> article
    # Gerund / past tense (skip short stems to avoid mangling).
    for suf in ("ing", "ed"):
        if token.endswith(suf) and len(token) - len(suf) >= 4:
            base = token[: -len(suf)]
            # Undouble a doubled consonant: scanning -> scann -> scan. Leave
            # ll/ss/zz alone (spelling -> spell, processing -> process).
            if len(base) >= 4 and base[-1] == base[-2] and base[-1] not in "lsz":
                base = base[:-1]
            return base
    return token


def normalize_tokens(text: str) -> list[str]:
    # Split hyphenated compounds ("citation-ready" -> "citation", "ready") so a
    # description's compounds match plain words in a prompt. Skill-name matching
    # is handled separately, so this does not weaken it.
    tokens: list[str] = []
    for raw in TOKEN_RE.findall(text.lower()):
        for part in raw.split("-"):
            if part not in GRAMMAR and len(part) > 2:
                tokens.append(stem(part))
    return tokens


def _tfidf_vector(tokens: list[str], idf: dict[str, float]) -> dict[str, float]:
    if not tokens:
        return {}
    tf = Counter(tokens)
    vec = {t: (1.0 + math.log(c)) * idf.get(t, _default_idf(idf)) for t, c in tf.items()}
    norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
    return {t: v / norm for t, v in vec.items()}


def _default_idf(idf: dict[str, float]) -> float:
    # An unseen token is maximally rare: treat it as at least as informative as
    # the rarest token in the corpus.
    return max(idf.values()) if idf else 1.0


def build_skill_index(skills_root: Path, selected: set[str] | None) -> dict[str, dict[str, Any]]:
    """Index skills into TF-IDF vectors.

    IDF is always computed over the *entire* catalog under `skills_root`, even when
    `selected` narrows the returned/scored set, so subset scores stay comparable to
    full-catalog scores. Each returned skill_data carries a shared `idf` reference
    so `score_trigger` can vectorize a prompt with the same weighting.
    """
    corpus: dict[str, dict[str, Any]] = {}
    name_token_owners: dict[str, list[str]] = {}

    for skill_md in sorted(skills_root.glob("*/SKILL.md")):
        skill = skill_md.parent.name
        fm = parse_frontmatter(skill_md)
        description = fm.get("description", "")
        if not isinstance(description, str):
            description = ""
        declared = fm.get("triggers", [])
        if not isinstance(declared, list):
            declared = []
        declared = [t.strip() for t in declared if isinstance(t, str) and t.strip()]

        # The scored vector is name + description only. Declared triggers are
        # deliberately excluded: folding them in would make `--from-triggers`
        # circular (a skill's own trigger phrase would always match its vector),
        # defeating the check that the description actually carries the phrase.
        doc_text = f"{skill.replace('-', ' ')} {description}"
        tokens = normalize_tokens(doc_text)
        name_tokens = set(skill.lower().split("-"))
        corpus[skill] = {
            "description": description,
            "tokens": tokens,
            "name_tokens": name_tokens,
            "declared_triggers": declared,
        }
        for token in name_tokens:
            name_token_owners.setdefault(token, []).append(skill)

    # Corpus-wide IDF over every skill (not just the selected subset).
    n_docs = len(corpus)
    df: Counter[str] = Counter()
    for data in corpus.values():
        df.update(set(data["tokens"]))
    idf = {t: math.log((n_docs + 1) / (df_t + 1)) + 1.0 for t, df_t in df.items()}

    for skill, data in corpus.items():
        data["idf"] = idf
        data["vector"] = _tfidf_vector(data["tokens"], idf)
        data["disc_name_tokens"] = {
            t for t in data["name_tokens"] if len(name_token_owners.get(t, [])) == 1
        }

    if selected is None:
        return corpus
    return {name: data for name, data in corpus.items() if name in selected}


def score_trigger(prompt: str, case_type: str, skill: str, skill_data: dict[str, Any]) -> float:
    """TF-IDF cosine between the prompt and the skill, plus explicit-mention boosts."""
    idf = skill_data.get("idf", {})
    prompt_vec = _tfidf_vector(normalize_tokens(prompt), idf)
    skill_vec = skill_data.get("vector", {})
    cosine = sum(weight * skill_vec.get(token, 0.0) for token, weight in prompt_vec.items())

    prompt_lower = prompt.lower()
    boost = 0.0
    if f"${skill}" in prompt_lower:
        boost += 0.9
    elif skill in prompt_lower or skill.replace("-", " ") in prompt_lower:
        boost += 0.35
    explicit = re.search(r"\$([a-z0-9-]+)", prompt_lower)
    if explicit and explicit.group(1) != skill and f"${skill}" not in prompt_lower:
        boost -= 0.25

    return max(0.0, min(1.0, cosine + boost))


def threshold_for(case_type: str) -> float:
    if case_type == "explicit":
        return 0.20
    if case_type == "negative":
        return 0.30
    if case_type == "contextual":
        return 0.12
    return 0.10


def safe_div(num: float, den: float) -> float:
    return 0.0 if den == 0 else num / den


def _skill_rows(counters: dict[str, dict[str, int]]) -> list[dict[str, Any]]:
    rows = []
    for skill, row in sorted(counters.items()):
        tp, fp, tn, fn = row["tp"], row["fp"], row["tn"], row["fn"]
        precision = safe_div(tp, tp + fp)
        recall = safe_div(tp, tp + fn)
        f1 = safe_div(2 * precision * recall, precision + recall)
        rows.append(
            {
                "skill": skill, "tp": tp, "fp": fp, "tn": tn, "fn": fn,
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1": round(f1, 4),
            }
        )
    return rows


def evaluate_cases(
    skills: dict[str, dict[str, Any]],
    cases: list[dict[str, Any]],
    mode: str = "ranking",
) -> dict[str, Any]:
    """Score labeled cases under either the ranking or threshold assertion model.

    Ranking (default): the top-scoring skill must be an expected trigger, and each
    avoided skill must score strictly below the winner. A case with no expected
    trigger ("matches nothing") passes when every avoided skill stays under
    `MATCH_NOTHING_FLOOR`.

    Threshold: each labeled skill is asserted against `threshold_for(case_type)`,
    the older absolute-score model.

    A case may set `"known_hard": true` to mark a genuine lexical-ceiling collision
    (e.g. a prompt that names a competing skill's core verb). Its assertions are
    tallied under `known_hard_*` and excluded from `failed`, so the case stays
    visible without faking a pass or being deleted. A real agent
    (`scripts/behavioral_evals.py`) is the backstop for these.

    Both emit per-skill assertion entries with a boolean `passed`, so downstream
    checks that grep for `"passed": false` keep working. Entries from a known_hard
    case carry `"known_hard": true` so a grep can exclude them.
    """
    assertions: list[dict[str, Any]] = []
    counters: dict[str, dict[str, int]] = defaultdict(lambda: {"tp": 0, "fp": 0, "tn": 0, "fn": 0})

    for raw_case in cases:
        if not isinstance(raw_case, dict):
            continue
        case_id = str(raw_case.get("id", "case"))
        case_type = str(raw_case.get("type", "implicit")).lower()
        prompt = str(raw_case.get("prompt", ""))
        known_hard = bool(raw_case.get("known_hard", False))
        expected = raw_case.get("expected", {})
        if not isinstance(expected, dict):
            expected = {}

        should_trigger = [s for s in expected.get("trigger", []) if s in skills]
        should_avoid = [s for s in expected.get("avoid", []) if s in skills]

        scores = {s: score_trigger(prompt, case_type, s, data) for s, data in skills.items()}
        rec = lambda skill, exp, pred, sc, winner="__unset__": _record(  # noqa: E731
            assertions, counters, case_id, case_type, skill, exp, pred, sc,
            known_hard=known_hard, winner=winner,
        )

        if mode == "threshold":
            for skill in should_trigger:
                rec(skill, True, scores[skill] >= threshold_for(case_type), scores[skill])
            for skill in should_avoid:
                rec(skill, False, scores[skill] >= threshold_for(case_type), scores[skill])
            continue

        # Ranking mode.
        if should_trigger:
            winner = max(scores, key=scores.get)
            winner_score = scores[winner]
            # Any expected trigger winning is correct; passing is case-level, so a
            # non-winning-but-acceptable trigger is not a failure. The winner must
            # also clear the floor, or nothing really routed.
            case_ok = winner in should_trigger and winner_score >= MIN_WINNER_SCORE
            for skill in should_trigger:
                rec(skill, True, case_ok, scores[skill], winner=winner)
            for skill in should_avoid:
                rec(skill, False, scores[skill] >= winner_score, scores[skill], winner=winner)
        else:
            # Matches-nothing: every avoided skill must stay under the floor.
            for skill in should_avoid:
                rec(skill, False, scores[skill] >= MATCH_NOTHING_FLOOR, scores[skill])

    hard = [a for a in assertions if a.get("known_hard")]
    normal = [a for a in assertions if not a.get("known_hard")]
    passed = sum(1 for a in normal if a["passed"])
    failed = len(normal) - passed
    return {
        "summary": {
            "cases": len(cases),
            "assertions": len(assertions),
            "passed": passed,
            "failed": failed,
            "known_hard_passed": sum(1 for a in hard if a["passed"]),
            "known_hard_failed": sum(1 for a in hard if not a["passed"]),
            "mode": mode,
        },
        "skills": _skill_rows(counters),
        "assertions": assertions,
    }


def _record(assertions, counters, case_id, case_type, skill, expected_bool,
            predicted, score, known_hard=False, winner="__unset__"):
    passed = predicted == expected_bool
    if expected_bool and predicted:
        counters[skill]["tp"] += 1
    elif (not expected_bool) and predicted:
        counters[skill]["fp"] += 1
    elif (not expected_bool) and (not predicted):
        counters[skill]["tn"] += 1
    else:
        counters[skill]["fn"] += 1
    entry = {
        "case_id": case_id, "skill": skill, "expected": expected_bool,
        "predicted": predicted, "score": round(score, 4), "passed": passed,
        "type": case_type,
    }
    if known_hard:
        entry["known_hard"] = True
    if winner != "__unset__":
        entry["winner"] = winner
    assertions.append(entry)


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
                    "skill": owner, "trigger": phrase,
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
    parser.add_argument(
        "--threshold",
        action="store_true",
        help="Assert cases against an absolute score threshold instead of the default ranking model",
    )
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

    mode = "threshold" if args.threshold else "ranking"
    output = evaluate_cases(skills, cases, mode=mode)

    declared_failed = 0
    if args.from_triggers:
        declared = evaluate_declared_triggers(skills)
        output["declared_triggers"] = declared
        declared_failed = declared["summary"]["failed"]

    print(json.dumps(output, indent=2) if args.pretty else json.dumps(output))
    return 1 if (output["summary"]["failed"] or declared_failed) else 0


if __name__ == "__main__":
    sys.exit(main())
