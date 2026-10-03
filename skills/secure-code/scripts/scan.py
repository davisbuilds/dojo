#!/usr/bin/env python3
"""Run Semgrep without mutating targets; preserve results and execution evidence."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


def classify(data, exit_code):
    if exit_code not in (0, None):
        return 'failed'
    if not isinstance(data, dict) or not all(isinstance(data.get(k), list) for k in ('results', 'errors')):
        return 'invalid'
    for match in data['results']:
        if not isinstance(match, dict) or not isinstance(match.get('extra', {}), dict):
            return 'invalid'
        if not isinstance(match.get('start', {}), dict):
            return 'invalid'
        if not isinstance(match.get('extra', {}).get('metadata', {}), dict):
            return 'invalid'
    if data['errors']:
        return 'partial'
    paths = data.get('paths')
    if not isinstance(paths, dict) or not isinstance(paths.get('scanned'), list):
        return 'unknown'
    if not paths['scanned']:
        return 'empty'
    return 'completed' if exit_code == 0 else 'unknown'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('targets', nargs='*', default=['.'])
    parser.add_argument('--config', action='append', help='Repeat to combine rule sources; default p/default')
    args = parser.parse_args()
    targets = args.targets or ['.']
    configs = args.config or ['p/default']
    engine = shutil.which('semgrep')
    command = [engine or 'semgrep', 'scan', '--json', '--verbose', '--disable-version-check', '--metrics=off']
    for config in configs:
        command.extend(['--config', config])
    command.extend(['--', *targets])
    evidence = {'status': 'failed', 'exit_code': None, 'cwd': str(Path.cwd()),
                'targets': targets, 'command': command, 'configs': [],
                'started_at': datetime.now(timezone.utc).isoformat()}
    for config in configs:
        item = {'source': config}
        if Path(config).is_file():
            try:
                item['sha256'] = hashlib.sha256(Path(config).read_bytes()).hexdigest()
            except OSError as exc:
                item['hash_error'] = str(exc)
        evidence['configs'].append(item)
    data = {'results': [], 'errors': []}
    try:
        missing = [target for target in targets if not Path(target).exists()]
        if missing:
            raise ValueError(f'Targets do not exist: {missing}')
        if not engine:
            raise ValueError('Semgrep is not installed; no scan ran.')
        result = subprocess.run(command, text=True, capture_output=True)
        evidence.update(exit_code=result.returncode, stderr=result.stderr)
        try:
            parsed = json.loads(result.stdout)
        except json.JSONDecodeError:
            parsed = None
        evidence['status'] = classify(parsed, result.returncode)
        if isinstance(parsed, dict):
            data = parsed
        else:
            data['errors'].append({'message': 'Invalid Semgrep JSON output'})
        # Add absent collections only after classifying the original response.
        data.setdefault('results', [])
        data.setdefault('errors', [])
    except (OSError, ValueError) as exc:
        data['errors'].append({'message': str(exc)})
    data['_scan'] = evidence
    print(json.dumps(data, indent=2))
    return 0 if evidence['status'] == 'completed' else 2


if __name__ == '__main__':
    sys.exit(main())
