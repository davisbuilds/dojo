#!/usr/bin/env python3
"""Deterministic scaffolding for the stage-8 structural verification pass.

Splits stage 8 at its natural seam. Extraction, sampling, and arithmetic are
mechanical and belong here; judging whether a fetched page actually supports the
claim attached to it is judgment and stays with the verifying subagent.

    worksheet  report.md      -> claims + citations + a sample to check
    score      worksheet.json -> citation hit rate, broken out by claim kind

The sample is weighted toward quantitative and source-attribution claims: across
every executor profiled so far, mutated numbers and mischaracterized findings are
the dominant failure mode, so a uniform sample under-tests where reports break.

This script never fetches. The verifying agent has its own fetch tool and must
look at the page to fill in a verdict; a liveness check here would only tempt a
"URL resolves" hit rate, which is not what stage 8 measures.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_SAMPLE_SIZE = 12
QUANTITATIVE_SHARE = 0.7

VERDICTS = ("supported", "partial", "unsupported", "unreachable")

MARKDOWN_LINK_RE = re.compile(r"\[(?P<text>[^\]]*)\]\((?P<url>https?://[^\s)]+)\)")
# No lookbehind for "(" — a parenthesised bare URL is a normal citation style.
# Markdown-link URLs are excluded by span, not by pattern.
BARE_URL_RE = re.compile(r"\bhttps?://[^\s<>\]]+")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z(\[])")

MAGNITUDE_RE = re.compile(
    r"""\b\d{1,3}(?:,\d{3})+\b
      | \b\d+(?:\.\d+)?\s*%
      | \b\d+(?:\.\d+)?\s*(?:[KMB]\b|thousand|million|billion|trillion)
      | \$\s*\d+(?:\.\d+)?
      | \b\d{3,}(?:\.\d+)?\b
      | \b\d+(?:\.\d+)?x\b
    """,
    re.VERBOSE | re.IGNORECASE,
)
# "reports that", "finds", "concludes" — attribution verbs whose object is a
# source's position. Mischaracterising these is the other half of the failure.
ATTRIBUTION_RE = re.compile(
    r"\b(?:finds?|found|reports?|concludes?|shows?|showed|claims?|argues?|"
    r"according to|per)\b",
    re.IGNORECASE,
)


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def extract_citations(text: str) -> list[dict]:
    """Every citation in the report, in document order, as C1..Cn."""
    found: list[tuple[int, str, str]] = []
    linked_spans: list[tuple[int, int]] = []

    for match in MARKDOWN_LINK_RE.finditer(text):
        linked_spans.append(match.span())
        found.append((match.start(), match.group("url"), match.group("text").strip()))

    for match in BARE_URL_RE.finditer(text):
        if any(start <= match.start() < end for start, end in linked_spans):
            continue
        found.append((match.start(), match.group(0).rstrip(").,;"), ""))

    found.sort(key=lambda item: item[0])
    return [
        {
            "id": f"C{index}",
            "url": url,
            "anchor_text": anchor,
            "line": line_of(text, offset),
            "offset": offset,
        }
        for index, (offset, url, anchor) in enumerate(found, start=1)
    ]


def prose_blocks(text: str) -> list[tuple[int, int]]:
    """Paragraph spans, excluding headings.

    Sentence splitting alone is not enough: a heading carries no terminal
    punctuation, so "# Findings" runs into the sentence beneath it and the claim
    text (and its line number) drift up the document.
    """
    spans: list[tuple[int, int]] = []
    offset = 0
    block_start: int | None = None
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            if block_start is not None:
                spans.append((block_start, offset))
                block_start = None
        elif block_start is None:
            block_start = offset
        offset += len(line)
    if block_start is not None:
        spans.append((block_start, offset))
    return spans


def sentences(text: str) -> list[tuple[int, int, str]]:
    spans = []
    for block_start, block_end in prose_blocks(text):
        block = text[block_start:block_end]
        bounds = [0] + [m.end() for m in SENTENCE_SPLIT_RE.finditer(block)] + [len(block)]
        for start, end in zip(bounds, bounds[1:]):
            if block[start:end].strip():
                spans.append((block_start + start, block_start + end, block[start:end]))
    return spans


def extract_claims(text: str, citations: list[dict]) -> list[dict]:
    """Sentences worth checking, tagged quantitative/attribution, as Q1..Qn.

    A claim is a sentence carrying at least one citation — that is what stage 8
    can actually check. Uncited prose is a different finding (an unsupported
    assertion), caught by the rubric pass rather than the citation sample.
    """
    claims = []
    for start, end, raw in sentences(text):
        attached = [c["id"] for c in citations if start <= c["offset"] < end]
        if not attached:
            continue
        body = raw.strip()
        claims.append({
            "id": f"Q{len(claims) + 1}",
            "text": body,
            "line": line_of(text, start),
            "quantitative": bool(MAGNITUDE_RE.search(body)),
            "attribution": bool(ATTRIBUTION_RE.search(body)),
            "citations": attached,
        })
    return claims


def spread(items: list[dict], count: int) -> list[dict]:
    """`count` items spaced evenly across `items`, preserving document order."""
    if count >= len(items):
        return list(items)
    step = len(items) / count
    return [items[int(index * step)] for index in range(count)]


def select_sample(claims: list[dict], size: int = DEFAULT_SAMPLE_SIZE) -> list[str]:
    """Claim ids to verify, weighted toward quantitative and attribution claims."""
    priority = [c for c in claims if c.get("quantitative") or c.get("attribution")]
    rest = [c for c in claims if c not in priority]

    take_priority = min(len(priority), round(size * QUANTITATIVE_SHARE))
    chosen = spread(priority, take_priority)

    remaining = size - len(chosen)
    chosen += spread(rest, min(len(rest), remaining))

    # Scarce ordinary claims: spend the leftover budget on more priority claims.
    shortfall = size - len(chosen)
    if shortfall > 0:
        chosen += [c for c in priority if c not in chosen][:shortfall]

    order = {c["id"]: index for index, c in enumerate(claims)}
    return [c["id"] for c in sorted(chosen, key=lambda c: order[c["id"]])]


def build_worksheet(text: str, size: int = DEFAULT_SAMPLE_SIZE) -> dict:
    citations = extract_citations(text)
    claims = extract_claims(text, citations)
    return {
        "citations": citations,
        "claims": claims,
        "sample": select_sample(claims, size),
        "verdicts": {},
    }


def score_worksheet(worksheet: dict) -> dict:
    """Hit rate over judged sample entries, broken out by claim kind.

    `unreachable` leaves the denominator: a dead link is a coverage gap, not
    evidence the claim was wrong. Reporting it separately keeps a report full of
    rotted URLs from scoring the same as one that checks out.
    """
    verdicts = worksheet.get("verdicts") or {}
    sample = worksheet.get("sample") or []
    claims = {c["id"]: c for c in worksheet.get("claims") or []}

    unknown = {v for v in verdicts.values() if v not in VERDICTS}
    if unknown:
        raise ValueError(
            f"unrecognized verdict(s): {', '.join(sorted(unknown))}; "
            f"expected one of {', '.join(VERDICTS)}"
        )

    def tally(ids: list[str]) -> dict:
        judged = [i for i in ids if verdicts.get(i) and verdicts[i] != "unreachable"]
        hits = [i for i in judged if verdicts[i] == "supported"]
        return {
            "judged": len(judged),
            "hits": len(hits),
            "hit_rate": round(len(hits) / len(judged), 4) if judged else 0.0,
        }

    quantitative_ids = [i for i in sample if claims.get(i, {}).get("quantitative")]
    attribution_ids = [i for i in sample if claims.get(i, {}).get("attribution")]
    qualitative_ids = [i for i in sample if i not in quantitative_ids]

    unjudged = [i for i in sample if i not in verdicts]
    result = tally(sample)
    result.update({
        "sampled": len(sample),
        "unreachable": sum(1 for i in sample if verdicts.get(i) == "unreachable"),
        "unjudged": unjudged,
        "complete": not unjudged,
        "quantitative": tally(quantitative_ids),
        "attribution": tally(attribution_ids),
        "qualitative": tally(qualitative_ids),
    })
    return result


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def format_score(result: dict) -> str:
    lines = [
        f"citation hit rate: {result['hit_rate'] * 100:.1f}% "
        f"({result['hits']}/{result['judged']} judged of {result['sampled']} sampled)",
    ]
    for kind in ("quantitative", "attribution", "qualitative"):
        bucket = result[kind]
        if bucket["judged"]:
            lines.append(
                f"  {kind:<13} {bucket['hit_rate'] * 100:5.1f}% "
                f"({bucket['hits']}/{bucket['judged']})"
            )
    if result["unreachable"]:
        lines.append(f"  unreachable   {result['unreachable']} (excluded from denominator)")
    if not result["complete"]:
        lines.append(f"  UNJUDGED      {', '.join(result['unjudged'])}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    sheet = sub.add_parser("worksheet", help="extract claims/citations from a report")
    sheet.add_argument("file", help="report markdown file")
    sheet.add_argument("--size", type=int, default=DEFAULT_SAMPLE_SIZE,
                       help=f"claims to sample (default: {DEFAULT_SAMPLE_SIZE})")

    scorer = sub.add_parser("score", help="score a filled-in worksheet")
    scorer.add_argument("file", help="worksheet JSON file")
    scorer.add_argument("--json", action="store_true", help="emit JSON")

    args = parser.parse_args(argv)
    path = Path(args.file)
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot read {path}: {exc}", file=sys.stderr)
        return 2

    if args.command == "worksheet":
        worksheet = build_worksheet(raw, args.size)
        worksheet["report"] = str(path)
        print(json.dumps(worksheet, indent=2))
        return 0

    try:
        result = score_worksheet(json.loads(raw))
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2) if args.json else format_score(result))
    return 0 if result["complete"] else 1


if __name__ == "__main__":
    sys.exit(main())
