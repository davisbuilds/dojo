#!/usr/bin/env python3
"""Discover skill roots and inventories."""

from __future__ import annotations

import argparse
import sys

from skill_standardizer_lib import print_json, resolve_context, root_describe


class Args(argparse.Namespace):
    canonical_root: str | None
    root: list[str] | None
    include_plugin_caches: bool
    format: str


def parse_args(argv: list[str]) -> Args:
    parser = argparse.ArgumentParser(description="Discover skill roots and inventories.")
    parser.add_argument(
        "--canonical-root",
        help="Canonical root (repo root or skills directory). Auto-discovered when omitted.",
    )
    parser.add_argument(
        "--root",
        action="append",
        help="Additional skills root to include (repeatable).",
    )
    parser.add_argument(
        "--include-plugin-caches",
        action="store_true",
        help="Include plugin cache roots (excluded by default).",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format.",
    )
    return parser.parse_args(argv, namespace=Args())


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    context = resolve_context(
        canonical_root_arg=args.canonical_root,
        root_args=args.root,
        include_plugin_caches=args.include_plugin_caches,
    )
    payload = root_describe(context)

    if args.format == "json":
        print_json(payload)
        return 0

    canonical = payload.get("canonical_root") or "none"
    print(f"Canonical root: {canonical}")
    print("Roots:")
    for root in payload["roots"]:
        suffix = " (missing)" if not root["exists"] else ""
        print(
            f"- {root['kind']}: {root['path']} | skills={root['skill_count']}{suffix}"
        )
        if root["invalid_entries"]:
            print(f"  invalid: {', '.join(root['invalid_entries'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
