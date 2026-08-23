#!/usr/bin/env python3
"""Deterministic scaffolding for the stage-8 structural verification pass.

Splits stage 8 at its natural seam. Extraction, sampling, and arithmetic are
mechanical and belong here; judging whether a fetched page actually supports the
claim attached to it is judgment and stays with the verifying subagent.

    worksheet  report.md      -> claims + citations + a sample to check
    score      worksheet.json -> support, applicability, and usable-citation rates

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
APPLICABILITY_VERDICTS = ("fit", "adjacent", "mismatch")

MARKDOWN_LINK_RE = re.compile(r"\[(?P<text>[^\]]*)\]\((?P<url>https?://[^\s)]+)\)")
# No lookbehind for "(" — a parenthesised bare URL is a normal citation style.
# Markdown-link URLs are excluded by span, not by pattern.
BARE_URL_RE = re.compile(r"\bhttps?://[^\s<>\]]+")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z(\[])")
OPAQUE_CITATION_RE = re.compile(r"(?:cite|filecite)[^]+")
NUMERIC_CITATION_RE = re.compile(r"(?<=[A-Za-z)\]])(?P<number>\d{1,3})(?=[.,;:]|\s|$)")
HEADING_RE = re.compile(r"^\s*#{1,6}\s+(?P<title>.+?)\s*$", re.MULTILINE)
NUMBERED_REFERENCE_RE = re.compile(r"^\s*(?:>\s*)?(?P<number>\d+)\.\s+(?P<body>.+)$")

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


def bibliography_offset(text: str) -> int:
    """Start of a bibliography/reference section, or ``len(text)`` when absent."""
    for match in HEADING_RE.finditer(text):
        title = re.sub(r"[*_`\\]", "", match.group("title")).strip().lower()
        if (
            title in {"references", "bibliography", "annotated bibliography", "works cited"}
            or title.endswith(" bibliography")
        ):
            return match.start()
    return len(text)


def numbered_reference_urls(text: str, start: int) -> dict[str, str]:
    """Resolve numbered bibliography entries to their first retrievable URL."""
    references: dict[str, str] = {}
    for line in text[start:].splitlines():
        entry = NUMBERED_REFERENCE_RE.match(line)
        if not entry:
            continue
        body = entry.group("body")
        linked = MARKDOWN_LINK_RE.search(body)
        bare = BARE_URL_RE.search(body)
        if linked:
            references[entry.group("number")] = linked.group("url")
        elif bare:
            references[entry.group("number")] = bare.group(0).rstrip(").,;")
    return references


def extract_citations(text: str) -> list[dict]:
    """Resolvable claim citations in document order, as C1..Cn.

    Direct links are read from the report body. Numeric markers are resolved
    through a numbered bibliography when the export preserves that mapping.
    Opaque provider markers stay out of the result and are reported separately
    by ``citation_coverage``.
    """
    boundary = bibliography_offset(text)
    body = text[:boundary]
    found: list[tuple[int, str, str, str]] = []
    linked_spans: list[tuple[int, int]] = []

    for match in MARKDOWN_LINK_RE.finditer(body):
        linked_spans.append(match.span())
        found.append((match.start(), match.group("url"), match.group("text").strip(), "direct"))

    for match in BARE_URL_RE.finditer(body):
        if any(start <= match.start() < end for start, end in linked_spans):
            continue
        linked_spans.append(match.span())
        found.append((match.start(), match.group(0).rstrip(").,;"), "", "direct"))

    reference_urls = numbered_reference_urls(text, boundary)
    for match in NUMERIC_CITATION_RE.finditer(body):
        if any(start <= match.start() < end for start, end in linked_spans):
            continue
        number = match.group("number")
        if number in reference_urls:
            found.append((match.start(), reference_urls[number], number, "numeric"))

    found.sort(key=lambda item: item[0])
    return [
        {
            "id": f"C{index}",
            "url": url,
            "anchor_text": anchor,
            "line": line_of(text, offset),
            "offset": offset,
            "linkage": linkage,
        }
        for index, (offset, url, anchor, linkage) in enumerate(found, start=1)
    ]


def citation_coverage(text: str, citations: list[dict], checks: list[dict]) -> dict:
    """Describe whether claim-to-source linkage is usable by the worksheet."""
    boundary = bibliography_offset(text)
    body = text[:boundary]
    opaque_markers = len(OPAQUE_CITATION_RE.findall(body))
    references = numbered_reference_urls(text, boundary)
    numeric_markers = (
        [m.group("number") for m in NUMERIC_CITATION_RE.finditer(body)]
        if boundary < len(text) else []
    )
    unresolved_numeric = [number for number in numeric_markers if number not in references]
    linkages = {citation.get("linkage") for citation in citations}

    if (opaque_markers or unresolved_numeric) and not citations:
        status = "opaque"
        detail = "citation markers exist but at least one claim-to-URL mapping is unavailable"
    elif "numeric" in linkages:
        status = "resolvable"
        detail = (
            "numbered inline citations resolve through the bibliography"
            if not unresolved_numeric else
            "numbered inline citations are partly resolvable; unmapped markers remain visible"
        )
    elif checks:
        status = "direct"
        detail = "claim sentences carry retrievable URLs"
    elif citations:
        status = "opaque"
        detail = "retrievable URLs exist but are not attached to checkable claims"
    elif boundary < len(text):
        status = "opaque"
        detail = "a bibliography exists but no claim-to-URL mapping is recoverable"
    else:
        status = "absent"
        detail = "no citation signals were detected"

    return {
        "status": status,
        "detail": detail,
        "citations": len(citations),
        "checks": len(checks),
        "opaque_markers": opaque_markers,
        "unresolved_numeric_markers": len(unresolved_numeric),
    }


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
        claim_prose = MARKDOWN_LINK_RE.sub("", body)
        claim_prose = BARE_URL_RE.sub("", claim_prose)
        if not claim_prose.strip(" \t\r\n()[]{}.,;:—-"):
            continue
        claims.append({
            "id": f"Q{len(claims) + 1}",
            "text": body,
            "line": line_of(text, start),
            "quantitative": bool(MAGNITUDE_RE.search(body)),
            "attribution": bool(ATTRIBUTION_RE.search(body)),
            "citations": attached,
        })
    return claims


def build_checks(claims: list[dict], citations: list[dict]) -> list[dict]:
    """One check per (claim, citation) pair — the unit stage 8 actually measures.

    A claim resting on three citations is three things to fetch, and one of them
    refuting the claim must not be hidden by another supporting it. Scoring per
    claim would collapse that into a single verdict and overstate the hit rate.
    """
    urls = {c["id"]: c["url"] for c in citations}
    checks = []
    for claim in claims:
        for citation_id in claim["citations"]:
            checks.append({
                "id": f"K{len(checks) + 1}",
                "claim": claim["id"],
                "citation": citation_id,
                "url": urls.get(citation_id, ""),
                "line": claim["line"],
                "quantitative": claim["quantitative"],
                "attribution": claim["attribution"],
                "text": claim["text"],
            })
    return checks


def spread(items: list[dict], count: int) -> list[dict]:
    """`count` items spaced evenly across `items`, preserving document order."""
    if count <= 0:
        return []
    if count >= len(items):
        return list(items)
    step = len(items) / count
    return [items[int(index * step)] for index in range(count)]


def select_sample(checks: list[dict], size: int = DEFAULT_SAMPLE_SIZE) -> list[str]:
    """Check ids to verify, weighted toward quantitative and attribution claims."""
    priority = [c for c in checks if c.get("quantitative") or c.get("attribution")]
    priority_ids = {c["id"] for c in priority}
    rest = [c for c in checks if c["id"] not in priority_ids]

    chosen = spread(priority, min(len(priority), round(size * QUANTITATIVE_SHARE)))
    chosen += spread(rest, min(len(rest), size - len(chosen)))

    # Scarce ordinary checks: spend the leftover budget on more priority checks.
    shortfall = size - len(chosen)
    if shortfall > 0:
        taken = {c["id"] for c in chosen}
        chosen += [c for c in priority if c["id"] not in taken][:shortfall]

    order = {c["id"]: index for index, c in enumerate(checks)}
    return sorted((c["id"] for c in chosen), key=lambda cid: order[cid])


def build_worksheet(text: str, size: int = DEFAULT_SAMPLE_SIZE) -> dict:
    citations = extract_citations(text)
    claims = extract_claims(text, citations)
    checks = build_checks(claims, citations)
    return {
        "schema_version": 2,
        "citations": citations,
        "claims": claims,
        "checks": checks,
        "sample": select_sample(checks, size),
        "verdicts": {},
        "applicability": {},
        "citation_coverage": citation_coverage(text, citations, checks),
    }


def score_worksheet(worksheet: dict) -> dict:
    """Support rate over judged sample entries, broken out by claim kind.

    `unreachable` leaves the denominator: a dead link is a coverage gap, not
    evidence the claim was wrong. Reporting it separately keeps a report full of
    rotted URLs from scoring the same as one that checks out.
    """
    verdicts = worksheet.get("verdicts") or {}
    applicability_enabled = "applicability" in worksheet
    applicability = worksheet.get("applicability") or {}
    sample = worksheet.get("sample") or []
    checks = {c["id"]: c for c in worksheet.get("checks") or []}
    coverage = worksheet.get("citation_coverage") or {"status": "legacy"}

    unknown = {v for v in verdicts.values() if v not in VERDICTS}
    if unknown:
        raise ValueError(
            f"unrecognized verdict(s): {', '.join(sorted(unknown))}; "
            f"expected one of {', '.join(VERDICTS)}"
        )
    unknown_applicability = {
        value for value in applicability.values()
        if value not in APPLICABILITY_VERDICTS
    }
    if unknown_applicability:
        raise ValueError(
            f"unrecognized applicability verdict(s): "
            f"{', '.join(sorted(unknown_applicability))}; expected one of "
            f"{', '.join(APPLICABILITY_VERDICTS)}"
        )

    def tally(ids: list[str]) -> dict:
        judged = [i for i in ids if verdicts.get(i) and verdicts[i] != "unreachable"]
        hits = [i for i in judged if verdicts[i] == "supported"]
        return {
            "judged": len(judged),
            "hits": len(hits),
            "hit_rate": round(len(hits) / len(judged), 4) if judged else 0.0,
        }

    quantitative_ids = [i for i in sample if checks.get(i, {}).get("quantitative")]
    attribution_ids = [i for i in sample if checks.get(i, {}).get("attribution")]
    qualitative_ids = [i for i in sample if i not in quantitative_ids]

    unjudged = [i for i in sample if i not in verdicts]
    applicability_unjudged = (
        [i for i in sample if verdicts.get(i) != "unreachable" and i not in applicability]
        if applicability_enabled else []
    )
    scorable_coverage = coverage.get("status") not in {"opaque", "absent"}

    if scorable_coverage:
        result = tally(sample)
    else:
        result = {"judged": 0, "hits": 0, "hit_rate": None}

    if applicability_enabled:
        assessed = [
            i for i in sample
            if verdicts.get(i) != "unreachable" and applicability.get(i)
        ]
        fits = [i for i in assessed if applicability[i] == "fit"]
        applicability_result = {
            "assessed": len(assessed),
            "fit": len(fits),
            "adjacent": sum(1 for i in assessed if applicability[i] == "adjacent"),
            "mismatch": sum(1 for i in assessed if applicability[i] == "mismatch"),
            "fit_rate": round(len(fits) / len(assessed), 4) if assessed else 0.0,
        }
        jointly_judged = [
            i for i in sample
            if verdicts.get(i) not in {None, "unreachable"} and applicability.get(i)
        ]
        usable = [
            i for i in jointly_judged
            if verdicts[i] == "supported" and applicability[i] == "fit"
        ]
        usable_result = {
            "judged": len(jointly_judged),
            "hits": len(usable),
            "usable_rate": (
                round(len(usable) / len(jointly_judged), 4) if jointly_judged else 0.0
            ),
        }
    else:
        applicability_result = None
        usable_result = None

    result.update({
        "sampled": len(sample),
        "unreachable": sum(1 for i in sample if verdicts.get(i) == "unreachable"),
        "unjudged": unjudged,
        "applicability_unjudged": applicability_unjudged,
        "complete": scorable_coverage and not unjudged and not applicability_unjudged,
        "citation_coverage": coverage,
        "applicability": applicability_result,
        "usable": usable_result,
        "quantitative": tally(quantitative_ids),
        "attribution": tally(attribution_ids),
        "qualitative": tally(qualitative_ids),
    })
    return result


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError(f"sample size must be positive, got {parsed}")
    return parsed


def format_score(result: dict) -> str:
    if result["hit_rate"] is None:
        coverage = result["citation_coverage"]
        lines = [
            f"citation support rate: unavailable "
            f"({coverage['status']}: {coverage.get('detail', '')})"
        ]
    else:
        lines = [
            f"citation support rate: {result['hit_rate'] * 100:.1f}% "
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
    if result["applicability"] is not None:
        domain = result["applicability"]
        usable = result["usable"]
        lines.append(
            f"domain fit rate: {domain['fit_rate'] * 100:.1f}% "
            f"({domain['fit']}/{domain['assessed']} assessed)"
        )
        lines.append(
            f"usable rate: {usable['usable_rate'] * 100:.1f}% "
            f"({usable['hits']}/{usable['judged']} jointly judged)"
        )
    if not result["complete"]:
        if result["unjudged"]:
            lines.append(f"  UNJUDGED      {', '.join(result['unjudged'])}")
        if result["applicability_unjudged"]:
            lines.append(
                "  UNJUDGED FIT  " + ", ".join(result["applicability_unjudged"])
            )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    sheet = sub.add_parser("worksheet", help="extract claims/citations from a report")
    sheet.add_argument("file", help="report markdown file")
    sheet.add_argument("--size", type=positive_int, default=DEFAULT_SAMPLE_SIZE,
                       help=f"claim/citation pairs to sample "
                            f"(default: {DEFAULT_SAMPLE_SIZE})")

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
        return 0 if worksheet["citation_coverage"]["status"] in {"direct", "resolvable"} else 1

    try:
        result = score_worksheet(json.loads(raw))
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2) if args.json else format_score(result))
    return 0 if result["complete"] else 1


if __name__ == "__main__":
    sys.exit(main())
