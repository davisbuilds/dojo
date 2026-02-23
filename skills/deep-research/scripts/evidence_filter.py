#!/usr/bin/env python3
"""Evidence filtering and aggregation utility for deep research.

Reads raw findings JSON, scores and deduplicates findings, and emits a compact
research packet with citations and discarded-context logs.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse


DEPTH_LEVELS = ("quick", "standard", "deep")


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


DEPTH_CONFIG = {
    "quick": {
        "threshold": 0.55,
        "max_keep": 6,
        "target_sources": 2,
        "weights": {"relevance": 0.5, "credibility": 0.3, "novelty": 0.1, "recency": 0.1},
    },
    "standard": {
        "threshold": 0.5,
        "max_keep": 12,
        "target_sources": 4,
        "weights": {"relevance": 0.45, "credibility": 0.25, "novelty": 0.2, "recency": 0.1},
    },
    "deep": {
        "threshold": 0.45,
        "max_keep": 24,
        "target_sources": 6,
        "weights": {"relevance": 0.4, "credibility": 0.25, "novelty": 0.25, "recency": 0.1},
    },
}


SOURCE_TYPE_SCORES = {
    "official": 0.95,
    "primary": 0.9,
    "academic": 0.88,
    "government": 0.9,
    "news": 0.72,
    "analysis": 0.65,
    "blog": 0.45,
    "forum": 0.3,
    "social": 0.25,
    "unknown": 0.5,
}


@dataclass
class Finding:
    title: str
    url: str
    summary: str
    source_type: str
    published_at: str
    content_blob: str
    domain: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Filter and aggregate deep research findings")
    parser.add_argument("--input", help="Path to JSON input file. Reads stdin when omitted.")
    parser.add_argument("--output", help="Path to write JSON output. Writes stdout when omitted.")
    parser.add_argument("--depth", choices=DEPTH_LEVELS, help="Override depth tier from input payload.")
    parser.add_argument("--max-findings", type=int, help="Cap number of kept findings.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def read_json(path: str | None) -> dict:
    if path:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        raw = sys.stdin.read().strip()
        data = json.loads(raw) if raw else {}

    if not isinstance(data, dict):
        raise ValueError("Input must be a JSON object")
    return data


def write_json(path: str | None, payload: dict, pretty: bool = False) -> None:
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


def tokenize(text: str) -> set[str]:
    terms = re.findall(r"[a-z0-9]+", text.lower())
    return {t for t in terms if len(t) > 2 and t not in STOPWORDS}


def canonical_url(url: str) -> str:
    try:
        parsed = urlparse(url.strip())
    except Exception:
        return url.strip().lower()

    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]

    path = parsed.path.rstrip("/")
    return f"{host}{path}".strip()


def parse_date(value: str) -> datetime | None:
    if not value:
        return None

    raw = value.strip()
    if not raw:
        return None

    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        dt = datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        pass

    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def recency_score(published_at: str, now: datetime) -> float:
    dt = parse_date(published_at)
    if dt is None:
        return 0.5

    age_days = (now - dt).days
    if age_days <= 30:
        return 1.0
    if age_days <= 180:
        return 0.85
    if age_days <= 365:
        return 0.7
    if age_days <= 3 * 365:
        return 0.45
    return 0.2


def credibility_score(source_type: str, domain: str) -> float:
    source_key = (source_type or "unknown").strip().lower()
    base = SOURCE_TYPE_SCORES.get(source_key, SOURCE_TYPE_SCORES["unknown"])

    d = domain.lower()
    if d.endswith(".gov"):
        base = max(base, 0.9)
    elif d.endswith(".edu"):
        base = max(base, 0.85)
    elif d.endswith(".org"):
        base += 0.03

    return max(0.0, min(1.0, base))


def text_similarity(tokens_a: set[str], tokens_b: set[str]) -> float:
    if not tokens_a or not tokens_b:
        return 0.0
    common = len(tokens_a & tokens_b)
    denom = math.sqrt(len(tokens_a) * len(tokens_b))
    if denom == 0:
        return 0.0
    return common / denom


def relevance_score(brief_terms: set[str], finding_terms: set[str]) -> float:
    if not brief_terms:
        return 0.5
    if not finding_terms:
        return 0.0

    overlap = len(brief_terms & finding_terms)
    # Balance recall against term density so longer briefs are not unfairly penalized.
    recall_like = overlap / max(1, min(len(brief_terms), 12))
    density = overlap / max(1, len(finding_terms))
    return min(1.0, (0.8 * recall_like) + (0.2 * min(1.0, density * 4.0)))


def normalize_finding(raw: dict) -> Finding:
    title = str(raw.get("title") or "").strip()
    url = str(raw.get("url") or "").strip()
    summary = str(raw.get("summary") or raw.get("snippet") or "").strip()
    source_type = str(raw.get("source_type") or "unknown").strip().lower()
    published_at = str(raw.get("published_at") or raw.get("date") or "").strip()
    domain = str(raw.get("domain") or "").strip().lower()

    if not domain and url:
        try:
            domain = urlparse(url).netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]
        except Exception:
            domain = ""

    content_blob = " ".join(
        str(raw.get(k) or "")
        for k in ("title", "summary", "snippet", "content", "notes", "excerpt")
    ).strip()

    return Finding(
        title=title,
        url=url,
        summary=summary,
        source_type=source_type,
        published_at=published_at,
        content_blob=content_blob,
        domain=domain,
    )


def infer_next_queries(research_brief: str, missing_terms: list[str]) -> list[str]:
    queries = []
    if missing_terms:
        top_terms = ", ".join(missing_terms[:4])
        queries.append(f"Find primary sources for: {top_terms}")
        queries.append(f"Find official or regulatory documentation about: {top_terms}")

    queries.append(f"Find contradictory evidence or dissenting views for: {research_brief[:120]}")
    queries.append(f"Find the most recent updates for: {research_brief[:120]}")

    deduped = []
    seen = set()
    for q in queries:
        key = q.lower().strip()
        if key and key not in seen:
            deduped.append(q)
            seen.add(key)
    return deduped[:5]


def main() -> int:
    args = parse_args()

    try:
        payload = read_json(args.input)
    except Exception as exc:
        sys.stderr.write(f"Failed to parse input JSON: {exc}\n")
        return 1

    research_brief = str(payload.get("research_brief") or payload.get("query") or "").strip()
    raw_findings = payload.get("findings")

    if not isinstance(raw_findings, list):
        sys.stderr.write("Input must include a 'findings' array.\n")
        return 1

    depth = (args.depth or payload.get("depth") or payload.get("selected_depth") or "standard").strip().lower()
    if depth not in DEPTH_LEVELS:
        depth = "standard"

    config = DEPTH_CONFIG[depth]
    max_keep = args.max_findings or int(payload.get("max_findings") or config["max_keep"])

    now_value = str(payload.get("now") or "").strip()
    now = parse_date(now_value) if now_value else datetime.now(timezone.utc)
    if now is None:
        now = datetime.now(timezone.utc)

    brief_terms = tokenize(research_brief)

    dedupe_by_url: dict[str, dict] = {}
    discarded: list[dict] = []

    for item in raw_findings:
        if not isinstance(item, dict):
            discarded.append({"title": "", "url": "", "reason": "invalid_item", "score": 0.0})
            continue

        f = normalize_finding(item)
        if not f.content_blob.strip() or not f.url:
            discarded.append({"title": f.title, "url": f.url, "reason": "missing_content", "score": 0.0})
            continue

        terms = tokenize(f.content_blob)
        relevance = relevance_score(brief_terms, terms)

        if relevance < 0.06:
            discarded.append({"title": f.title, "url": f.url, "reason": "off_topic", "score": round(relevance, 4)})
            continue

        credibility = credibility_score(f.source_type, f.domain)
        recency = recency_score(f.published_at, now)

        preliminary = (
            config["weights"]["relevance"] * relevance
            + config["weights"]["credibility"] * credibility
            + config["weights"]["recency"] * recency
        )

        record = {
            "finding": f,
            "terms": terms,
            "relevance": relevance,
            "credibility": credibility,
            "recency": recency,
            "preliminary_score": preliminary,
        }

        key = canonical_url(f.url)
        existing = dedupe_by_url.get(key)
        if existing is None:
            dedupe_by_url[key] = record
        else:
            if record["preliminary_score"] > existing["preliminary_score"]:
                discarded.append(
                    {
                        "title": existing["finding"].title,
                        "url": existing["finding"].url,
                        "reason": "duplicate_url",
                        "score": round(existing["preliminary_score"], 4),
                    }
                )
                dedupe_by_url[key] = record
            else:
                discarded.append(
                    {
                        "title": f.title,
                        "url": f.url,
                        "reason": "duplicate_url",
                        "score": round(record["preliminary_score"], 4),
                    }
                )

    candidates = sorted(dedupe_by_url.values(), key=lambda r: r["preliminary_score"], reverse=True)

    kept_records: list[dict] = []
    threshold = float(payload.get("min_score", config["threshold"]))

    for candidate in candidates:
        if len(kept_records) >= max_keep:
            discarded.append(
                {
                    "title": candidate["finding"].title,
                    "url": candidate["finding"].url,
                    "reason": "over_budget",
                    "score": round(candidate["preliminary_score"], 4),
                }
            )
            continue

        max_similarity = 0.0
        for kept in kept_records:
            sim = text_similarity(candidate["terms"], kept["terms"])
            if sim > max_similarity:
                max_similarity = sim

        novelty = 1.0 - max_similarity
        candidate["novelty"] = novelty

        final_score = (
            config["weights"]["relevance"] * candidate["relevance"]
            + config["weights"]["credibility"] * candidate["credibility"]
            + config["weights"]["recency"] * candidate["recency"]
            + config["weights"]["novelty"] * novelty
        )
        candidate["final_score"] = final_score

        if max_similarity >= 0.78:
            discarded.append(
                {
                    "title": candidate["finding"].title,
                    "url": candidate["finding"].url,
                    "reason": "duplicate_semantic",
                    "score": round(final_score, 4),
                }
            )
            continue

        if final_score < threshold:
            discarded.append(
                {
                    "title": candidate["finding"].title,
                    "url": candidate["finding"].url,
                    "reason": "low_score",
                    "score": round(final_score, 4),
                }
            )
            continue

        kept_records.append(candidate)

    kept_records = sorted(kept_records, key=lambda r: r["final_score"], reverse=True)

    citations = []
    key_findings = []
    coverage_terms: set[str] = set()

    for idx, record in enumerate(kept_records, start=1):
        f: Finding = record["finding"]
        citation_id = f"[{idx}]"

        citations.append(
            {
                "id": citation_id,
                "title": f.title,
                "url": f.url,
                "domain": f.domain,
            }
        )

        summary = f.summary if f.summary else f.content_blob[:300]

        key_findings.append(
            {
                "citation_id": citation_id,
                "title": f.title,
                "url": f.url,
                "summary": summary,
                "relevance": round(record["relevance"], 4),
                "credibility": round(record["credibility"], 4),
                "novelty": round(record.get("novelty", 0.0), 4),
                "recency": round(record["recency"], 4),
                "score": round(record["final_score"], 4),
            }
        )

        coverage_terms |= record["terms"]

    sorted_discarded = sorted(discarded, key=lambda d: d.get("score", 0.0), reverse=True)

    top_brief_terms = [
        t for t in sorted(brief_terms, key=lambda term: (-len(term), term))
        if t not in coverage_terms
    ]
    missing_terms = top_brief_terms[:8]

    confidence_gaps = []
    unique_domains = {c["domain"] for c in citations if c.get("domain")}

    if not key_findings:
        confidence_gaps.append("No findings met relevance and credibility thresholds.")
    if len(unique_domains) < config["target_sources"] and key_findings:
        confidence_gaps.append(
            f"Only {len(unique_domains)} distinct domains retained; target is {config['target_sources']} for depth '{depth}'."
        )

    high_cred_count = sum(1 for k in key_findings if k["credibility"] >= 0.8)
    if key_findings and high_cred_count < max(1, math.ceil(len(key_findings) * 0.4)):
        confidence_gaps.append("Insufficient high-credibility coverage; prioritize official and primary sources.")

    if missing_terms:
        confidence_gaps.append(f"Potentially under-covered brief terms: {', '.join(missing_terms[:6])}.")

    next_queries = infer_next_queries(research_brief, missing_terms)

    output = {
        "research_brief": research_brief,
        "depth": depth,
        "key_findings": key_findings,
        "citations": citations,
        "discarded_context": sorted_discarded,
        "confidence_gaps": confidence_gaps,
        "next_queries": next_queries,
        "stats": {
            "input_findings": len(raw_findings),
            "retained_findings": len(key_findings),
            "discarded_findings": len(sorted_discarded),
            "distinct_domains": len(unique_domains),
            "threshold": threshold,
        },
    }

    try:
        write_json(args.output, output, pretty=args.pretty)
    except Exception as exc:
        sys.stderr.write(f"Failed to write output JSON: {exc}\n")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
