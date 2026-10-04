#!/usr/bin/env python3
"""Collect static skill evidence. Never execute target code or certify trust."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import stat
import subprocess
import sys

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from instruction_audit import prompt_injection_scan, encoding_scan, exfiltration_scan, overreach_scan

SECURE_CODE_DIR = Path(__file__).resolve().parents[2] / 'secure-code'
AUDIT_RULES = Path(__file__).resolve().parents[1] / 'rules/skill-scripts.yaml'
CODE_SUFFIXES = {'.py', '.sh', '.bash', '.js', '.ts', '.jsx', '.tsx'}
MAX_TEXT_BYTES = 2 * 1024 * 1024
SECRET_PATTERNS = [
    (r"""(?:api_key|apikey|api_secret|secret_key|auth_token|access_token|private_key)\s*[=:]\s*['"][A-Za-z0-9_\-/.+]{16,}['"]""", "hardcoded-secret"),
    (r"""['"]sk-[A-Za-z0-9]{20,}['"]""", "openai-key"),
    (r"""['"]ghp_[A-Za-z0-9]{36}['"]""", "github-token"),
    (r"""['"]AKIA[A-Z0-9]{16}['"]""", "aws-access-key"),
]

DANGEROUS_PATTERNS = [
    (r"""\beval\s*\(""", "eval-call"),
    (r"""\bexec\s*\(""", "exec-call"),
    (r"""\brm\s+-rf\b""", "rm-rf"),
    (r"""\bcurl\b.*\|\s*bash""", "curl-pipe-bash"),
    (r"""\bwget\b.*\|\s*bash""", "wget-pipe-bash"),
    (r"""\bchmod\s+777\b""", "chmod-777"),
    (r"""\bos\.system\s*\(""", "os-system"),
    (r"""shell\s*=\s*True""", "shell-true"),
]



def inventory(path):
    """Do not follow links or open devices. This is a snapshot, not an OS sandbox."""
    entries, texts, errors = [], {}, []

    def walk_error(exc):
        errors.append(str(exc))

    for root, dirs, files in os.walk(path, followlinks=False, onerror=walk_error):
        for name in sorted(dirs + files):
            file = Path(root) / name
            rel = str(file.relative_to(path))
            try:
                mode = file.lstat().st_mode
                if stat.S_ISLNK(mode):
                    entries.append({'path': rel, 'kind': 'symlink', 'status': 'not-read'})
                    errors.append(f'{rel}: symlink not followed')
                    if name in dirs:
                        dirs.remove(name)
                    continue
                if stat.S_ISDIR(mode):
                    if name in ('.git', '__pycache__'):
                        dirs.remove(name)
                        entries.append({'path': rel, 'kind': 'directory', 'status': 'excluded'})
                    continue
                if not stat.S_ISREG(mode):
                    entries.append({'path': rel, 'kind': 'special', 'status': 'not-read'})
                    errors.append(f'{rel}: not a regular file')
                    continue
                item = {'path': rel, 'kind': 'file', 'status': 'read'}
                entries.append(item)
                with file.open('rb') as stream:
                    data = stream.read(MAX_TEXT_BYTES + 1)
                if len(data) > MAX_TEXT_BYTES:
                    raise ValueError('exceeds 2 MiB text inspection limit')
                item['sha256'] = hashlib.sha256(data).hexdigest()
                if b'\0' in data:
                    raise ValueError('binary content not inspected')
                texts[rel] = data.decode('utf-8')
            except (OSError, ValueError) as exc:
                if entries and entries[-1]['path'] == rel:
                    entries[-1]['status'] = 'not-read'
                errors.append(f'{rel}: {exc}')
    return entries, texts, errors


def code_indicators(texts):
    indicators = []
    for rel, text in texts.items():
        if Path(rel).suffix not in CODE_SUFFIXES:
            continue
        for line_no, line in enumerate(text.splitlines(), 1):
            for patterns, kind in ((SECRET_PATTERNS, 'secret'), (DANGEROUS_PATTERNS, 'execution')):
                for pattern, category in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        indicators.append({'category': f'{kind}-{category}', 'file': rel,
                                           'line': line_no, 'message': f'Pattern: {category}; inspect source context.'})
                        break
    return indicators


def run_scan(command, timeout=120):
    """Bound the wrapper and its scanner descendants as one POSIX process group."""
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, start_new_session=True) as process:
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except BaseException:
            # Killing just scan.py leaves Semgrep (and its core workers) alive.
            # SIGKILL also handles a hung descendant that ignores SIGTERM.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.communicate()
            raise
        return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)


def run_audit(skill_path, quick=False, layers=None, semgrep=False):
    try:
        path = Path(skill_path).resolve()
    except (OSError, RuntimeError) as exc:
        return {'status': 'failed', 'error': f'Cannot resolve target: {exc}'}
    if not path.is_dir():
        return {'status': 'failed', 'error': f'Not a directory: {skill_path}'}
    entries, texts, errors = inventory(path)
    run_layers = layers or [1, 2, 3]
    coverage = {name: {'status': 'not-requested'} for name in ('structure', 'instructions', 'code', 'semgrep')}
    result = {'schema_version': 2, 'skill': str(path), 'status': 'completed',
              'inventory': entries, 'coverage': coverage, 'errors': errors, 'indicators': [],
              'limitations': ['Static snapshot only; target scripts are not executed.',
                              'Indicators require contextual investigation; zero indicators is not a safety verdict.',
                              'External references, dependencies and effective harness permissions are not resolved.',
                              '.git and __pycache__ directories are excluded; symlinks are not followed.']}
    if 'SKILL.md' not in texts:
        errors.append('SKILL.md is missing or unreadable')
    if 1 in run_layers:
        coverage['structure'] = {'status': 'completed', 'files': ['SKILL.md'] if 'SKILL.md' in texts else []}
        match = re.match(r'\A---\s*\n(.*?)\n---(?:\s*\n|$)', texts.get('SKILL.md', ''), re.S)
        try:
            fm = yaml.safe_load(match.group(1)) if match else None
            if not isinstance(fm, dict):
                raise ValueError('Missing or invalid mapping frontmatter')
            # Declarations are evidence, not a claim about effective permission.
            tools = fm.get('allowed-tools')
            compatibility = fm.get('compatibility')
            if tools is not None and not (isinstance(tools, str) or
                    isinstance(tools, list) and all(isinstance(tool, str) for tool in tools)):
                raise ValueError('Invalid allowed-tools declaration')
            if compatibility is not None and not isinstance(compatibility, str):
                raise ValueError('Invalid compatibility declaration')
            result['declared_tools'] = tools
            result['declared_compatibility'] = compatibility
        except (yaml.YAMLError, ValueError) as exc:
            result['indicators'].append({'category': 'frontmatter', 'file': 'SKILL.md', 'line': 1,
                                         'message': f'Cannot interpret frontmatter ({type(exc).__name__}); inspect source.'})
    if 2 in run_layers:
        files = [(path / rel, text) for rel, text in texts.items() if Path(rel).suffix.lower() == '.md']
        coverage['instructions'] = {'status': 'completed', 'files': [str(f.relative_to(path)) for f, _ in files]}
        for check in (prompt_injection_scan, encoding_scan, exfiltration_scan, overreach_scan):
            result['indicators'].extend(check(path, files))
    if 3 in run_layers and not quick:
        code = {rel: text for rel, text in texts.items() if Path(rel).suffix in CODE_SUFFIXES}
        coverage['code'] = {'status': 'completed', 'files': list(code)}
        result['indicators'].extend(code_indicators(code))
        if semgrep:
            coverage['semgrep'] = {'status': 'unavailable'}
            wrapper = SECURE_CODE_DIR / 'scripts/scan.sh'
            if not shutil.which('semgrep') or not wrapper.is_file():
                errors.append('Requested Semgrep analysis is unavailable (requires CLI and sibling secure-code).')
            elif not code:
                coverage['semgrep'] = {'status': 'empty', 'files': []}
            else:
                try:
                    proc = run_scan(['bash', str(wrapper), '--config', str(AUDIT_RULES), '--',
                                     *[str(path / rel) for rel in code]])
                    packet = json.loads(proc.stdout)
                    evidence = packet.get('_scan', {})
                    state = evidence.get('status', 'invalid')
                    if proc.returncode and state == 'completed':
                        state = 'failed'
                    coverage['semgrep'] = {'status': state, 'version': packet.get('version'),
                                           'invocation': evidence, 'paths': packet.get('paths'), 'errors': packet.get('errors', [])}
                    if state != 'completed':
                        errors.append(f'Semgrep analysis: {state}')
                    for item in packet.get('results', []):
                        # Do not echo source snippets or interpolated rule messages (may contain secrets).
                        result['indicators'].append({'category': item['check_id'], 'file': item['path'],
                                                     'line': item.get('start', {}).get('line'),
                                                     'message': 'Semgrep match; inspect source and rule preconditions.'})
                except (OSError, subprocess.TimeoutExpired, ValueError, AttributeError, KeyError, TypeError) as exc:
                    coverage['semgrep'] = {'status': 'failed'}
                    errors.append(f'Semgrep analysis failed: {type(exc).__name__}')
    if errors:
        result['status'] = 'partial'
        # A layer's file list records what succeeded; inventory errors limit the overall scope.
    return result


def format_markdown(result):
    if 'error' in result:
        return f"Audit failed: {result['error']}"
    lines = [f"# Skill evidence: {result['status']}",
             'No trust score or automatic installation recommendation.',
             f"Inventory: {len(result['inventory'])} entries"]
    for name, data in result['coverage'].items():
        lines.append(f"- {name}: {data['status']} ({len(data.get('files', []))} files listed)")
    for error in result['errors']:
        lines.append(f'- Coverage gap: {error}')
    lines.append(f"## Indicators requiring investigation: {len(result['indicators'])}")
    for item in result['indicators']:
        lines.append(f"- {item['file']}:{item.get('line', '?')} [{item['category']}] {item['message']}")
    lines.extend(result['limitations'])
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('skill_directory')
    parser.add_argument('--quick', action='store_true', help='Skip code analysis; record the omission')
    parser.add_argument('--layer', type=int, choices=[1, 2, 3], help='Only structure, instructions, or code')
    parser.add_argument('--semgrep', action='store_true', help='Also run the installed scanner with bundled local rules')
    parser.add_argument('--json', action='store_true', dest='json_output')
    args = parser.parse_args()
    if args.semgrep and (args.quick or args.layer in (1, 2)):
        parser.error('--semgrep requires code analysis')
    result = run_audit(args.skill_directory, args.quick, [args.layer] if args.layer else None, args.semgrep)
    print(json.dumps(result, indent=2) if args.json_output else format_markdown(result))
    return 0 if result['status'] == 'completed' else 2


if __name__ == '__main__':
    sys.exit(main())
