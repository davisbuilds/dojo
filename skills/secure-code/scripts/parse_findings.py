#!/usr/bin/env python3
"""Render scan evidence without treating matches or absence as security verdicts."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scan import classify


def status(data):
    if not isinstance(data, dict):
        return 'invalid'
    structural = classify(data, 0)
    if structural == 'invalid':
        return structural
    evidence = data.get('_scan', {})
    reported = evidence.get('status') if isinstance(evidence, dict) else None
    if reported == 'completed' and structural != 'completed':
        return structural
    return reported or classify(data, None)


def parse_findings(data: dict) -> str:
    state = status(data)
    lines = [f'## Scan evidence: {state}',
             'Rule matches are investigation leads, not confirmed vulnerabilities.']
    if not isinstance(data, dict) or state == 'invalid':
        return '\n'.join(lines)
    evidence = data.get('_scan', {})
    evidence = evidence if isinstance(evidence, dict) else {}
    lines.append(f"Engine version: {data.get('version', 'unknown')}; exit code: {evidence.get('exit_code', 'unknown')}")
    if evidence.get('targets'):
        lines.append(f"Requested targets: {evidence['targets']}")
    paths = data.get('paths', {})
    if isinstance(paths, dict):
        scanned = paths.get('scanned')
        lines.append(f"Reported scanned files: {len(scanned) if isinstance(scanned, list) else 'unknown'}")
        skipped = paths.get('skipped')
        lines.append(f"Skipped-file detail: {len(skipped) if isinstance(skipped, list) else 'not reported'}")
        for item in skipped if isinstance(skipped, list) else []:
            lines.append(f'- Skipped: {item}')
    for error in data.get('errors', []) or []:
        lines.append(f'- Scan error: {error}')
    if evidence.get('stderr') and state != 'completed':
        lines.append(f"Scanner diagnostics:\n{evidence['stderr']}")
    results = data.get('results', [])
    if not isinstance(results, list):
        lines.append('Invalid results collection.')
        return '\n'.join(lines)
    lines.append(f'## Rule matches: {len(results)}')
    for match in results:
        if not isinstance(match, dict):
            lines.append(f'Invalid result: {match}')
            continue
        extra = match.get('extra', {})
        cwe = extra.get('metadata', {}).get('cwe', [])
        cwe = ', '.join(map(str, cwe)) if isinstance(cwe, list) else str(cwe)
        lines.append(f"- [{extra.get('severity', 'unknown')}] {match.get('check_id', '?')} "
                     f"at {match.get('path', '?')}:{match.get('start', {}).get('line', '?')} "
                     f"{cwe}\n  {extra.get('message', '')}")
    lines.append('No-match results do not establish safety; assess exclusions, rule scope, and untested boundaries.')
    return '\n'.join(lines)


def main():
    try:
        data = json.loads(Path(sys.argv[1]).read_text()) if len(sys.argv) > 1 else json.load(sys.stdin)
    except (OSError, ValueError) as exc:
        print(f'Invalid scan evidence: {exc}', file=sys.stderr)
        return 2
    print(parse_findings(data))
    return 0 if status(data) == 'completed' else 2


if __name__ == '__main__':
    sys.exit(main())
