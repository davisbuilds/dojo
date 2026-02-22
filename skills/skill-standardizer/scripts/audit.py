#!/usr/bin/env python3
"""Audit skill drift across canonical, global, and local roots."""

from __future__ import annotations

import argparse
import sys

from skill_standardizer_lib import (
    build_audit_report,
    print_json,
    resolve_context,
    summarize_report,
    write_json,
)


class Args(argparse.Namespace):
    canonical_root: str | None
    root: list[str] | None
    include_plugin_caches: bool
    local_policy: str
    keep_local_skill: list[str] | None
    enforce_mirror: bool
    format: str
    report_out: str | None


def parse_args(argv: list[str]) -> Args:
    parser = argparse.ArgumentParser(description="Audit skill drift.")
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
        "--local-policy",
        choices=["prefer-global-link", "keep-local"],
        default="prefer-global-link",
        help="How to treat local duplicates when global copy exists.",
    )
    parser.add_argument(
        "--keep-local-skill",
        action="append",
        help="Skill name to exempt from local relinking (repeatable).",
    )
    parser.add_argument(
        "--enforce-mirror",
        action="store_true",
        help="Treat missing canonical skills in globals as drift and propose creation.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format.",
    )
    parser.add_argument(
        "--report-out",
        help="Write JSON report to file.",
    )
    return parser.parse_args(argv, namespace=Args())


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    context = resolve_context(
        canonical_root_arg=args.canonical_root,
        root_args=args.root,
        include_plugin_caches=args.include_plugin_caches,
    )

    report = build_audit_report(
        context=context,
        local_policy=args.local_policy,
        keep_local_skills=set(args.keep_local_skill or []),
        enforce_mirror=args.enforce_mirror,
    )

    if args.report_out:
        write_json(args.report_out, report)

    if args.format == "json":
        print_json(report)
    else:
        print(summarize_report(report))

    issue_count = len(report["issues"])
    if issue_count:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
