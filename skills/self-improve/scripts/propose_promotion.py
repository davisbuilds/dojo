#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from self_improve_lib import asset_path, compact_timestamp, copy_latest, ensure_store, iso_now, latest_markdown, render_template, slugify


TARGETS = ["auto", "discard", "keep-local", "promote-memory-note", "promote-skill-candidate"]


def infer_target(summary_text: str) -> str:
    record_count_match = re.search(r"Records included:\s+(\d+)", summary_text)
    record_count = int(record_count_match.group(1)) if record_count_match else 0
    lowered = summary_text.lower()
    if "recurring" in lowered or "repeat" in lowered or "reusable" in lowered:
        return "promote-skill-candidate"
    if record_count >= 3 or "improvement" in lowered:
        return "promote-memory-note"
    if record_count <= 1:
        return "keep-local"
    return "promote-memory-note"


def blast_radius_for(target: str) -> str:
    if target == "promote-skill-candidate":
        return "Moderate. Produces a reusable workflow draft that may later influence routing or repeated execution patterns."
    if target == "promote-memory-note":
        return "Low to moderate. Affects durable operating guidance in a harness-local memory surface after explicit review."
    if target == "keep-local":
        return "Low. Retained in the learning store only."
    return "Minimal. No durable change should be made."


def evidence_excerpt(summary_text: str) -> str:
    lines = [line for line in summary_text.splitlines() if line.strip()]
    excerpt = lines[:12]
    return "\n".join(f"> {line}" for line in excerpt)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a promotion proposal from a compact self-improvement summary")
    parser.add_argument("--store", required=True, help="Workspace path or .self-improve store path")
    parser.add_argument("--summary-file", help="Specific summary file to use; defaults to summaries/latest.md")
    parser.add_argument("--target", choices=TARGETS, default="auto", help="Promotion target")
    parser.add_argument("--title", default="", help="Optional proposal title")
    parser.add_argument("--rationale", default="", help="Optional rationale override")
    args = parser.parse_args()

    paths = ensure_store(args.store)
    summary_file = Path(args.summary_file).expanduser().resolve() if args.summary_file else latest_markdown(Path(paths["summaries"]))
    if summary_file is None or not summary_file.exists():
        raise SystemExit("No summary file found. Run compact_learnings.py first.")

    summary_text = summary_file.read_text(encoding="utf-8")
    target = args.target if args.target != "auto" else infer_target(summary_text)
    title = args.title.strip() or f"Promote {target} from {summary_file.stem}"
    rationale = args.rationale.strip() or (
        "This proposal is based on a compacted learning summary and should be reviewed before any durable behavior change."
    )
    verification_steps = "\n".join(
        [
            "- Re-read the summary and confirm the pattern is real, not anecdotal.",
            "- Check that the target tier matches the evidence and blast radius.",
            "- Validate any resulting artifact before promotion into the main catalog or memory surface.",
        ]
    )

    proposal_text = render_template(
        asset_path("promotion-proposal-template.md"),
        {
            "generated_at": iso_now(),
            "target": target,
            "summary_file": str(summary_file),
            "title": title,
            "rationale": rationale,
            "evidence_excerpt": evidence_excerpt(summary_text),
            "blast_radius": blast_radius_for(target),
            "verification_steps": verification_steps,
        },
    )

    out_path = Path(paths["proposals"]) / f"{compact_timestamp()}-{slugify(title)}.md"
    out_path.write_text(proposal_text, encoding="utf-8")
    copy_latest(out_path, Path(paths["proposals"]) / "latest.md")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
