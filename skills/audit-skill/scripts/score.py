#!/usr/bin/env python3
"""Trust score computation for skill audits."""

import json

SEVERITY_DEDUCTIONS = {
    "CRITICAL": 20,
    "HIGH": 10,
    "MEDIUM": 5,
    "LOW": 2,
    "INFORMATIONAL": 0,
}

LAYER_WEIGHTS = {
    1: 0.25,  # Structural
    2: 0.35,  # Instructions
    3: 0.40,  # Code
}

GRADE_THRESHOLDS = [
    (90, "A"),
    (75, "B"),
    (60, "C"),
    (40, "D"),
    (0, "F"),
]


def compute_trust_score(findings: list[dict], has_scripts: bool = True) -> dict:
    """Compute a trust score from audit findings.

    Args:
        findings: List of finding dicts with 'severity' and 'layer' keys.
        has_scripts: Whether the skill has a scripts/ directory.

    Returns:
        Dict with total score, grade, per-layer breakdown, and pass/fail.
    """
    weights = dict(LAYER_WEIGHTS)
    if not has_scripts:
        # Redistribute Layer 3 weight proportionally to Layers 1 and 2
        base = weights[1] + weights[2]
        weights[1] = weights[1] / base
        weights[2] = weights[2] / base
        weights[3] = 0.0

    # Per-layer raw scores (start at 100 each)
    layer_scores = {1: 100.0, 2: 100.0, 3: 100.0}
    layer_finding_counts = {1: 0, 2: 0, 3: 0}
    has_critical = False

    for f in findings:
        sev = f.get("severity", "INFORMATIONAL")
        layer = f.get("layer", 1)
        deduction = SEVERITY_DEDUCTIONS.get(sev, 0)
        layer_scores[layer] = max(0, layer_scores[layer] - deduction)
        layer_finding_counts[layer] += 1
        if sev == "CRITICAL":
            has_critical = True

    # Weighted total
    total = sum(layer_scores[l] * weights[l] for l in (1, 2, 3))
    total = max(0, min(100, round(total, 1)))

    # Grade
    grade = "F"
    for threshold, letter in GRADE_THRESHOLDS:
        if total >= threshold:
            grade = letter
            break

    passed = total >= 70 and not has_critical

    return {
        "score": total,
        "grade": grade,
        "passed": passed,
        "has_critical": has_critical,
        "layers": {
            layer: {
                "score": round(layer_scores[layer], 1),
                "weight": weights[layer],
                "findings": layer_finding_counts[layer],
            }
            for layer in (1, 2, 3)
        },
        "total_findings": len(findings),
    }


def format_score_markdown(score: dict) -> str:
    """Format trust score as markdown."""
    status = "PASS" if score["passed"] else "FAIL"
    lines = [
        f"## Trust Score: {score['score']}/100 (Grade {score['grade']}) — {status}",
        "",
        "| Layer | Score | Weight | Findings |",
        "|-------|-------|--------|----------|",
    ]
    layer_names = {1: "Structural", 2: "Instructions", 3: "Code"}
    for layer in (1, 2, 3):
        info = score["layers"][layer]
        pct = f"{info['weight']:.0%}"
        lines.append(
            f"| {layer_names[layer]} | {info['score']}/100 | {pct} | {info['findings']} |"
        )
    lines.append("")
    lines.append(f"**Total findings**: {score['total_findings']}")
    if score["has_critical"]:
        lines.append("**CRITICAL findings present** — automatic fail regardless of score.")
    return "\n".join(lines)


def format_score_json(score: dict) -> str:
    """Format trust score as JSON."""
    return json.dumps(score, indent=2)
