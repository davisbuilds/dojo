#!/usr/bin/env python3
"""Run deep-research pipeline end-to-end.

Pipeline:
1) Route depth with depth_router.py
2) Optionally filter findings with evidence_filter.py

Input: JSON via --input or stdin
Output: JSON via --output or stdout
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict


DEPTH_LEVELS = ("quick", "standard", "deep")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run deep-research routing and filtering in one command")
    parser.add_argument("--input", help="Path to input JSON. Reads stdin when omitted.")
    parser.add_argument("--output", help="Path to output JSON. Writes stdout when omitted.")
    parser.add_argument("--override-depth", choices=DEPTH_LEVELS, help="Force quick|standard|deep.")
    parser.add_argument("--max-findings", type=int, help="Override max retained findings for filter stage.")
    parser.add_argument("--depth-only", action="store_true", help="Run only depth routing stage.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print output JSON.")
    return parser.parse_args()


def read_json(path: str | None) -> Dict[str, Any]:
    if path:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        raw = sys.stdin.read().strip()
        data = json.loads(raw) if raw else {}

    if not isinstance(data, dict):
        raise ValueError("Input must be a JSON object")
    return data


def write_json(path: str | None, payload: Dict[str, Any], pretty: bool = False) -> None:
    content = json.dumps(payload, indent=2 if pretty else None, ensure_ascii=True)
    if pretty:
        content += "\n"

    if path:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        sys.stdout.write(content)
        if not pretty:
            sys.stdout.write("\n")


def _run_json_script(script_path: Path, payload: Dict[str, Any], extra_args: list[str]) -> Dict[str, Any]:
    cmd = [sys.executable, str(script_path), *extra_args]
    proc = subprocess.run(
        cmd,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
    )

    if proc.returncode != 0:
        stderr = proc.stderr.strip() or "(no stderr)"
        raise RuntimeError(f"{script_path.name} failed (exit {proc.returncode}): {stderr}")

    out_raw = proc.stdout.strip()
    if not out_raw:
        raise RuntimeError(f"{script_path.name} returned empty output")

    try:
        out = json.loads(out_raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{script_path.name} returned non-JSON output: {exc}") from exc

    if not isinstance(out, dict):
        raise RuntimeError(f"{script_path.name} output must be a JSON object")

    return out


def _script_paths() -> tuple[Path, Path]:
    script_dir = Path(__file__).resolve().parent
    router = script_dir / "depth_router.py"
    filterer = script_dir / "evidence_filter.py"
    return router, filterer


def main() -> int:
    args = parse_args()

    try:
        payload = read_json(args.input)
    except Exception as exc:
        sys.stderr.write(f"Failed to parse input JSON: {exc}\n")
        return 1

    router_path, filter_path = _script_paths()

    if not router_path.exists() or not filter_path.exists():
        sys.stderr.write("Missing required pipeline scripts (depth_router.py/evidence_filter.py).\n")
        return 1

    route_payload = dict(payload)
    route_args: list[str] = []

    if args.override_depth:
        route_args.extend(["--override-depth", args.override_depth])

    try:
        depth_plan = _run_json_script(router_path, route_payload, route_args)
    except Exception as exc:
        sys.stderr.write(f"Depth routing failed: {exc}\n")
        return 1

    findings = payload.get("findings")
    should_filter = isinstance(findings, list) and (not args.depth_only)

    if should_filter:
        filter_payload = dict(payload)
        filter_payload["depth"] = depth_plan.get("selected_depth", "standard")

        if args.max_findings is not None:
            filter_payload["max_findings"] = args.max_findings

        try:
            research_packet = _run_json_script(filter_path, filter_payload, [])
        except Exception as exc:
            sys.stderr.write(f"Evidence filtering failed: {exc}\n")
            return 1
    else:
        research_packet = None

    result: Dict[str, Any] = {
        "depth_plan": depth_plan,
        "research_packet": research_packet,
        "meta": {
            "depth_only": bool(args.depth_only),
            "filter_stage_executed": bool(should_filter),
            "requires_findings_for_filter_stage": True,
        },
    }

    if not should_filter:
        result["meta"]["note"] = (
            "Filter stage was skipped. Provide a 'findings' array in input and omit --depth-only to run full pipeline."
        )

    try:
        write_json(args.output, result, pretty=args.pretty)
    except Exception as exc:
        sys.stderr.write(f"Failed to write output JSON: {exc}\n")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
