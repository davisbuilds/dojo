#!/usr/bin/env python3
"""Write an optional loop brief; never run commands or configure a runtime.

Schema 2 supports bounded tasks, recurring monitors, and experiments. Evidence
and stopping rules are separate; a successful check is not automatically done.
Standard library only. Shell checks require POSIX sh on the execution host.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shlex
import sys

TEMPLATES = Path(__file__).resolve().parent.parent / 'assets' / 'templates'
KINDS = {
    'task': 'Finish only when the evidence supports the goal; report incomplete work at a limit.',
    'monitor': 'A healthy sample ends this run, not the schedule. Distinguish no change from unavailable data.',
    'experiment': 'Compare with the baseline and retain the result, including negative results. A better score alone does not authorize adoption.',
}
FIELDS = {
    'schema_version', 'name', 'kind', 'goal', 'evidence', 'stop_when',
    'authority', 'runtime', 'constraints', 'checkpoint', 'check',
}


def require_text(data: dict, key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip() or '\x00' in value:
        raise ValueError(f'{key} must be nonempty text without NUL characters')
    return value


def validate(bp: object) -> dict:
    if not isinstance(bp, dict):
        raise ValueError('blueprint must be a JSON object')
    if type(bp.get('schema_version')) is not int or bp['schema_version'] != 2:
        raise ValueError('schema_version must be 2; see references/blueprint-spec.md for migration from v1')
    unknown = bp.keys() - FIELDS
    if unknown:
        raise ValueError(f'unknown fields: {", ".join(sorted(unknown))}; see references/blueprint-spec.md for migration')
    bp = dict(bp)
    name = require_text(bp, 'name')
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) or len(name) > 64:
        raise ValueError('name must be a lowercase slug of at most 64 characters')
    if require_text(bp, 'kind') not in KINDS:
        raise ValueError('kind must be task, monitor, or experiment')
    for key in ('goal', 'evidence', 'stop_when'):
        require_text(bp, key)
    bp.setdefault('authority', 'Read-only. No external writes, publication, or dispatch authorized by this brief.')
    bp.setdefault('runtime', 'Unconfigured: choose the runner and wire its limits, cancellation, state, and reporting before execution.')
    for key in ('authority', 'runtime'):
        require_text(bp, key)
    bp.setdefault('constraints', [])
    if not isinstance(bp['constraints'], list):
        raise ValueError('constraints must be an array of nonempty strings')
    for constraint in bp['constraints']:
        require_text({'constraint': constraint}, 'constraint')
    bp.setdefault('checkpoint', False)
    if type(bp['checkpoint']) is not bool:
        raise ValueError('checkpoint must be true or false')
    if 'check' in bp:
        check = bp['check']
        if not isinstance(check, dict) or check.keys() != {'command', 'cwd'}:
            raise ValueError('check must contain exactly command and cwd')
        require_text(check, 'command')
        cwd = Path(require_text(check, 'cwd'))
        if not cwd.is_absolute() or not cwd.is_dir():
            raise ValueError('check.cwd must be an existing absolute directory on this host')
        bp['check'] = {**check, 'cwd': str(cwd.resolve())}
    return bp


def render(template: str, mapping: dict[str, str]) -> str:
    # One pass: user text resembling a placeholder remains literal.
    source = (TEMPLATES / template).read_text(encoding='utf-8')
    return re.sub(r'\{\{([A-Z_]+)\}\}', lambda match: mapping[match[1]], source)


def build_files(bp: dict) -> dict[str, str]:
    mapping = {key.upper(): bp[key] for key in
               ('name', 'kind', 'goal', 'evidence', 'stop_when', 'authority', 'runtime')}
    mapping.update({
        'KIND_GUIDANCE': KINDS[bp['kind']],
        'CONSTRAINTS': '\n'.join(f'- {c}' for c in bp['constraints']) or 'Use the owning project’s applicable constraints.',
        'STATE': ('Keep checkpoint.md beside this brief current; replace stale state, link retained evidence.'
                  if bp['checkpoint'] else
                  'Use the runtime’s existing durable state. If none exists, choose a recovery location before execution.'),
        'CHECK': ('Optional evidence command: run check.sh beside this brief. It runs once in the declared cwd, '
                  'preserving stdout, stderr, and exit status. Interpret the result using the evidence criteria; '
                  'failure can mean unavailable evidence, not unfinished work. Inspect the command before running it.'
                  if 'check' in bp else 'No check script generated. Use the evidence criteria above.'),
    })
    files = {'LOOP.md': render('LOOP.md.tpl', mapping),
             'blueprint.json': json.dumps(bp, indent=2, ensure_ascii=False) + '\n'}
    if bp['checkpoint']:
        files['checkpoint.md'] = render('checkpoint.md.tpl', mapping)
    if 'check' in bp:
        mapping.update({'CHECK_CWD': shlex.quote(bp['check']['cwd']),
                        'CHECK_COMMAND': shlex.quote(bp['check']['command'])})
        files['check.sh'] = render('check.sh.tpl', mapping)
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--blueprint', help='Schema-2 JSON blueprint. CLI fields override the file.')
    parser.add_argument('--out-dir', help='New output directory (default: .loops/<name>). Existing paths are refused.')
    for key in ('name', 'kind', 'goal', 'evidence', 'stop_when', 'authority', 'runtime'):
        parser.add_argument('--' + key.replace('_', '-'), choices=list(KINDS) if key == 'kind' else None)
    parser.add_argument('--checkpoint', action='store_true', default=None,
                        help='Add a compact checkpoint when the runtime does not already own one.')
    args = parser.parse_args(argv)
    try:
        bp = json.loads(Path(args.blueprint).read_text(encoding='utf-8')) if args.blueprint else {'schema_version': 2}
        if not isinstance(bp, dict):
            raise ValueError('blueprint must be a JSON object')
        for key in ('name', 'kind', 'goal', 'evidence', 'stop_when', 'authority', 'runtime', 'checkpoint'):
            value = getattr(args, key)
            if value is not None:
                bp[key] = value
        bp = validate(bp)
        files = build_files(bp)
        out = Path(args.out_dir) if args.out_dir else Path('.loops') / bp['name']
        # Refuse even an empty directory or symlink: regeneration must not erase
        # state or leave stale v1 executables beside a new brief.
        out.mkdir(parents=True, exist_ok=False)
        for name, content in files.items():
            target = out / name
            with target.open('x', encoding='utf-8') as stream:
                stream.write(content)
            if name == 'check.sh':
                target.chmod(0o755)
    except (ValueError, OSError) as error:
        print(f'[loop-design] {error}', file=sys.stderr)
        return 1
    print(f'[loop-design] Wrote {out}: {", ".join(files)}')
    print('Design only: no commands executed; scheduling, limits, permissions, and notifications are not configured.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
