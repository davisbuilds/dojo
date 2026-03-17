#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from self_improve_lib import asset_path, compact_timestamp, render_template, slugify


def extract_title(proposal_text: str, proposal_path: Path) -> str:
    match = re.search(r"## Title\s+(.+?)(?:\n## |\Z)", proposal_text, re.DOTALL)
    if not match:
        return proposal_path.stem.replace("-", " ").title()
    return match.group(1).strip().splitlines()[0]


def extract_notes(proposal_text: str) -> str:
    match = re.search(r"## Evidence\s+(.+?)(?:\n## |\Z)", proposal_text, re.DOTALL)
    if not match:
        return "Review the source proposal for evidence before promoting this draft."
    return match.group(1).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract a draft skill candidate from a self-improve proposal")
    parser.add_argument("--proposal", required=True, help="Path to proposal markdown")
    parser.add_argument("--output", required=True, help="Output directory for the draft skill")
    parser.add_argument("--skill-name", default="", help="Optional explicit candidate skill name")
    args = parser.parse_args()

    proposal_path = Path(args.proposal).expanduser().resolve()
    if not proposal_path.exists():
        raise SystemExit(f"Proposal not found: {proposal_path}")

    proposal_text = proposal_path.read_text(encoding="utf-8")
    title = extract_title(proposal_text, proposal_path)
    skill_name = args.skill_name.strip() or slugify(Path(args.output).name or title)
    description = (
        f"Draft reusable workflow extracted from self-improve proposal '{title}'. "
        "Use when the same repeated pattern appears again and the draft has been reviewed."
    )
    notes = extract_notes(proposal_text)

    output_dir = Path(args.output).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    skill_text = render_template(
        asset_path("skill-candidate-template.md"),
        {
            "skill_name": skill_name,
            "description": description,
            "title": title,
            "notes": notes + f"\n\nExtracted at {compact_timestamp()} from `{proposal_path}`.",
        },
    )
    skill_path = output_dir / "SKILL.md"
    skill_path.write_text(skill_text, encoding="utf-8")
    print(skill_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
