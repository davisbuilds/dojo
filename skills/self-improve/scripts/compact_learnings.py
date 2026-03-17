#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from self_improve_lib import asset_path, compact_timestamp, copy_latest, ensure_store, iso_now, list_records, render_template


def format_kind_breakdown(counter: Counter[str]) -> str:
    if not counter:
        return "- None"
    return "\n".join(f"- `{kind}`: {count}" for kind, count in sorted(counter.items()))


def format_items(records: list[dict[str, object]]) -> str:
    if not records:
        return "- No records found."

    lines: list[str] = []
    for record in records:
        record_id = str(record.get("record_id", "unknown"))
        kind = str(record.get("kind", "unknown"))
        created_at = str(record.get("created_at", "unknown"))
        summary = str(record.get("summary", "")).strip() or "No summary"
        evidence = str(record.get("evidence", "")).strip()
        tags = record.get("tags", [])
        tag_text = ", ".join(str(tag) for tag in tags) if isinstance(tags, list) and tags else "none"
        raw_path = str(record.get("_path", ""))

        lines.append(f"- `{record_id}` [{kind}] {created_at}")
        lines.append(f"  Summary: {summary}")
        if evidence:
            lines.append(f"  Evidence: {evidence}")
        lines.append(f"  Tags: {tag_text}")
        lines.append(f"  Raw: `{raw_path}`")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compact raw self-improvement records into a markdown summary")
    parser.add_argument("--store", required=True, help="Workspace path or .self-improve store path")
    parser.add_argument("--limit", type=int, default=20, help="Maximum number of recent records to include")
    args = parser.parse_args()

    paths = ensure_store(args.store)
    records = list_records(paths["root"])[: max(args.limit, 1)]
    counter: Counter[str] = Counter(str(record.get("kind", "unknown")) for record in records)

    summary = render_template(
        asset_path("learning-summary-template.md"),
        {
            "generated_at": iso_now(),
            "store_root": str(paths["root"]),
            "record_count": str(len(records)),
            "kind_breakdown": format_kind_breakdown(counter),
            "items": format_items(records),
        },
    )

    out_path = Path(paths["summaries"]) / f"{compact_timestamp()}-summary.md"
    out_path.write_text(summary, encoding="utf-8")
    copy_latest(out_path, Path(paths["summaries"]) / "latest.md")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
