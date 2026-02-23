#!/usr/bin/env python3
"""Parse semgrep JSON output into severity-grouped markdown for LLM consumption."""

import json
import sys

SEVERITY_ORDER = {"CRITICAL": 0, "ERROR": 1, "WARNING": 2, "INFO": 3}
SEVERITY_LABELS = {"CRITICAL": "CRITICAL", "ERROR": "HIGH", "WARNING": "MEDIUM", "INFO": "LOW"}


def parse_findings(data: dict) -> str:
    results = data.get("results", [])
    if not results:
        return "No findings detected."

    # Group by severity, then by file
    by_severity: dict[str, list[dict]] = {}
    for r in results:
        sev = r.get("extra", {}).get("severity", "INFO").upper()
        by_severity.setdefault(sev, []).append(r)

    # Summary counts
    counts = {SEVERITY_LABELS.get(s, s): len(items) for s, items in by_severity.items()}
    summary_parts = []
    for label in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        if label in counts:
            summary_parts.append(f"{counts[label]} {label.lower()}")
    summary = f"**Summary:** {', '.join(summary_parts)} finding{'s' if sum(counts.values()) != 1 else ''}\n"

    lines = [summary, "---\n"]

    for sev in sorted(by_severity.keys(), key=lambda s: SEVERITY_ORDER.get(s, 99)):
        label = SEVERITY_LABELS.get(sev, sev)
        items = by_severity[sev]

        # Group by file within severity
        by_file: dict[str, list[dict]] = {}
        for r in items:
            path = r.get("path", "unknown")
            by_file.setdefault(path, []).append(r)

        lines.append(f"## {label}\n")

        for path, file_items in sorted(by_file.items()):
            lines.append(f"### `{path}`\n")
            for r in file_items:
                rule_id = r.get("check_id", "unknown-rule")
                message = r.get("extra", {}).get("message", "No message")
                start_line = r.get("start", {}).get("line", "?")
                end_line = r.get("end", {}).get("line", "?")
                metadata = r.get("extra", {}).get("metadata", {})
                cwe = metadata.get("cwe", [])
                cwe_str = f" | CWE: {', '.join(cwe)}" if cwe else ""

                lines.append(f"- **{rule_id}** (line {start_line}-{end_line}{cwe_str})")
                lines.append(f"  {message}\n")

    # Errors from semgrep
    errors = data.get("errors", [])
    if errors:
        lines.append("## Scan Errors\n")
        for err in errors:
            msg = err.get("message", err.get("long_msg", str(err)))
            lines.append(f"- {msg}")

    return "\n".join(lines)


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)

    print(parse_findings(data))


if __name__ == "__main__":
    main()
