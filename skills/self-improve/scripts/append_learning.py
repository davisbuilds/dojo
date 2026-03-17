#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from self_improve_lib import compact_timestamp, ensure_store, iso_now, slugify, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Append a structured self-improvement learning record")
    parser.add_argument("--store", required=True, help="Workspace path or .self-improve store path")
    parser.add_argument("--kind", required=True, choices=["error", "learning", "improvement"], help="Learning kind")
    parser.add_argument("--summary", required=True, help="Short description of the learning")
    parser.add_argument("--evidence", default="", help="Concrete evidence for the learning")
    parser.add_argument("--tags", default="", help="Comma-separated tags")
    parser.add_argument("--source", default="manual", help="Where this learning came from")
    parser.add_argument("--context", default="", help="Optional task context")
    args = parser.parse_args()

    paths = ensure_store(args.store)
    record_id = f"{compact_timestamp()}-{args.kind}-{slugify(args.summary)}"
    path = Path(paths["inbox"]) / f"{record_id}.json"
    tags = [tag.strip() for tag in args.tags.split(",") if tag.strip()]

    payload = {
        "schema_version": 1,
        "record_id": record_id,
        "created_at": iso_now(),
        "kind": args.kind,
        "summary": args.summary.strip(),
        "evidence": args.evidence.strip(),
        "tags": tags,
        "source": args.source.strip(),
        "context": args.context.strip(),
        "status": "new",
    }
    write_json(path, payload)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
