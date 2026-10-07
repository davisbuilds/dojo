"""Read-only entry point for skill packaging checks and Codex catalog evidence."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

TOOL_ROOT = Path(__file__).resolve().parents[1]
NAME = re.compile(r'[a-z0-9][a-z0-9-]*')


def load(relative):
    """Reuse owning tools; importing them does not invoke their CLI main functions."""
    path = TOOL_ROOT / relative
    name = 'dojo_' + path.stem
    if name in sys.modules:
        return sys.modules[name]
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run(argv, cwd, timeout=60):
    """Bound tool execution, including descendants on supported Unix hosts."""
    with subprocess.Popen(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, start_new_session=os.name == 'posix') as proc:
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
        except (subprocess.TimeoutExpired, KeyboardInterrupt):
            if os.name == 'posix':
                os.killpg(proc.pid, signal.SIGKILL)
            else:
                proc.kill()
            proc.communicate()
            raise
    return proc.returncode, stdout, stderr


def git(repo, *args):
    code, out, err = run(['git', '-C', str(repo), *args], repo)
    if code:
        raise ValueError(f'Git {args[0]} unavailable: {err.strip()}')
    return out.strip()


def target_path(repo, value):
    candidate = repo / 'skills' / value if NAME.fullmatch(value) else Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = Path.cwd() / candidate
    target = candidate.resolve()
    if target.parent != (repo / 'skills').resolve() or not (target / 'SKILL.md').is_file():
        raise ValueError('Target must name an existing direct skill directory in the selected repository')
    return target


def add(result, name, status, scope, source, details):
    result['checks'].append(dict(id=name, status=status, scope=scope, source=source, details=details))


def content_hash(path):
    standardizer = load('skills/skill-standardizer/scripts/skill_standardizer_lib.py')
    backup = load('skills/skill-standardizer/scripts/backup_policy.py')
    # Installation links identify a bundle; compare its contents, not the link text.
    # Links inside the bundle retain the standardizer's structural semantics.
    return backup.fingerprint(backup.snapshot(path.resolve(strict=True), ignore=standardizer._copy_ignore))


def identity(repo, target):
    return {
        'repository': str(repo), 'head_commit': git(repo, 'rev-parse', '--verify', 'HEAD'),
        'working_tree_dirty': bool(git(repo, 'status', '--porcelain')),
        'skill_path': str(target),
        'content_hash': content_hash(target),
        'hash_method': 'SHA256 of entry paths, Git blob hashes, types and execute masks; standardizer cache exclusions',
        'tool_repository': str(TOOL_ROOT),
        'tool_commit': git(TOOL_ROOT, 'rev-parse', 'HEAD'),
        'tool_working_tree_dirty': bool(git(TOOL_ROOT, 'status', '--porcelain')),
    }


def check(args, repo, target, result):
    contract = load('skills/skill-evals/scripts/validate_skill_contract.py')
    quick = load('skills/skill-creator/scripts/quick_validate.py')
    metadata = contract.evaluate_skill(target, quick.validate_skill, strict=True)
    add(result, 'metadata', 'fail' if metadata['required_failures'] else 'pass',
        'selected skill', 'validate_skill_contract.evaluate_skill', metadata)

    links = load('scripts/check_links.py')
    problems = links.check(repo / 'skills', living_docs=[],
                          files=links.markdown_files(target, []), repo_root=repo)
    add(result, 'links', 'fail' if problems else 'pass', 'selected skill Markdown',
        'check_links.check', problems)

    if args.base:
        base = git(repo, 'rev-parse', '--verify', f'{args.base}^{{commit}}')
        result['evidence']['base_ref'] = args.base
        result['evidence']['base_commit'] = base
        versions = load('skills/skill-evals/scripts/check_skill_versions.py')
        problems = versions.check_versions(repo, repo / 'skills', base, True, {target.name})
        add(result, 'release', 'fail' if problems else 'pass', 'selected skill changes against base',
            'check_skill_versions.check_versions', problems)
    else:
        add(result, 'release', 'skipped', 'selected skill', 'check_skill_versions', 'Supply --base to check release changes')

    if args.repo_checks:
        commands = [
            ('manifest', ['scripts/generate_skills_manifest.py', '--check']),
            ('composed-docs', ['scripts/gen_skill_docs.py', '--check']),
            ('adapters', ['scripts/gen_harness_adapters.py', '--check', '--skip-symlinks']),
            ('catalog', ['scripts/gen_catalog.py', '--check']),
        ]
        for name, command in commands:
            script = repo / command[0]
            if not script.is_file():
                add(result, name, 'unavailable', 'repository', command[0], 'Script missing in selected checkout')
                continue
            code, out, err = run([sys.executable, str(script), *command[1:]], repo, args.timeout)
            status = 'pass' if code == 0 else 'fail' if code == 1 and 'Traceback (most recent call last)' not in err else 'unavailable'
            add(result, name, status, 'repository', command, {'exit_code': code, 'stdout': out, 'stderr': err})
    else:
        add(result, 'generated-files', 'skipped', 'repository', 'existing generators --check', 'Enable --repo-checks')
    result['limitations'] = [
        'Packaging and conservative Markdown links only; plain-text resource mentions are not resolved.',
        'No skill scripts, test suites, security review, routing, or task-outcome evaluation executed.',
        'Existing release rules apply; new skills without a versioned base have no bump comparison.',
    ]


def configuration(cwd, codex_home, skill):
    """Report declarations only; the harness owns configuration precedence."""
    import tomllib
    paths = [codex_home / 'config.toml']
    paths.extend(p / '.codex/config.toml' for p in [cwd, *cwd.parents])
    declarations = []
    for path in dict.fromkeys(paths):
        if not path.is_file():
            continue
        config = tomllib.loads(path.read_text())
        rules = config.get('skills', {}).get('config', [])
        selected = [r for r in rules if r.get('name') == skill or
                    Path(str(r.get('path', ''))).name == skill or
                    Path(str(r.get('path', ''))).parent.name == skill]
        if selected:
            declarations.append({'file': str(path), 'rules': [
                {k: r[k] for k in ('path', 'name', 'enabled') if k in r} for r in selected]})
    return declarations


def inspect(args, repo, target, result):
    cwd = Path(args.cwd).expanduser().resolve()
    if not cwd.is_dir():
        raise ValueError('Probe --cwd must be an existing directory')
    standardizer = load('skills/skill-standardizer/scripts/skill_standardizer_lib.py')
    versions = load('skills/skill-evals/scripts/check_skill_versions.py')
    codex_home = Path(os.environ.get('CODEX_HOME', Path.home() / '.codex')).expanduser()
    candidates = [target, codex_home / 'skills/.system' / target.name]
    candidates.extend(p / target.name for p in standardizer.global_roots().values())
    # Candidate locations are filesystem inventory, not claims about harness loading.
    candidates.extend(p / folder / 'skills' / target.name
                      for p in [cwd, *cwd.parents] for folder in ('.agents', '.codex'))
    copies = []
    for path in dict.fromkeys(candidates):
        if not path.exists() and not path.is_symlink():
            continue
        copies.append({
            'path': str(path), 'resolved_path': str(path.resolve()), 'symlink': path.is_symlink(),
            'version': versions.current_skill_version(path / 'SKILL.md'),
            'content_hash': content_hash(path) if path.is_dir() else None,
        })
    add(result, 'copies', 'pass', 'candidate locations on this host', 'standardizer roots and backup-policy content fingerprint', copies)
    add(result, 'configuration', 'pass', 'user and ancestor declarations; precedence not evaluated',
        'skills.config only', configuration(cwd, codex_home, target.name))
    import yaml
    equivalence_path = repo / 'profiles/harness-equivalences.yaml'
    if equivalence_path.is_file():
        document = yaml.safe_load(equivalence_path.read_text())
        rules = [r for r in document.get('equivalences', [])
                 if r.get('skill') == target.name and r.get('harness') == 'codex']
        add(result, 'profile-policy', 'pass', 'Dojo declaration; not an installed profile', str(equivalence_path), rules)
    else:
        rules = []
        add(result, 'profile-policy', 'skipped', 'Dojo declaration', str(equivalence_path), 'No declaration file')

    command = [sys.executable, str(TOOL_ROOT / 'scripts/profiles/probe_codex.py'), '--cwd', str(cwd), '--skills-root', str(repo / 'skills'), '--json']
    code, stdout, stderr = run(command, cwd, args.timeout)
    if code:
        add(result, 'catalog', 'unavailable', 'fresh Codex prompt-input', command,
            {'exit_code': code, 'stderr': stderr[-2000:]})
        return
    listing = json.loads(stdout)
    if not isinstance(listing.get('entries'), list) or not listing['entries']:
        raise ValueError('Probe returned no usable catalog entries; absence is not established')
    probe = load('scripts/profiles/probe_codex.py')
    exposed = [dict(e, absolute_path=probe._absolute(e['locator'], listing['root_lines']))
               for e in listing['entries'] if e['name'] == target.name]
    result['evidence']['harness'] = listing['fingerprint']
    result['evidence']['probe_cwd'] = str(cwd)
    result['evidence']['observation_surface'] = 'codex debug prompt-input (fresh rendering, not a running session)'
    result['evidence']['catalog_entry_count'] = len(listing['entries'])
    status = 'pass' if len(exposed) == 1 else 'fail'
    if not exposed and listing.get('warning'):
        status = 'unavailable'
    add(result, 'catalog', status, 'target exposure in fresh Codex prompt-input', command,
        {'exposed': exposed, 'listing_warning': listing.get('warning'), 'match_count': len(exposed)})
    contents = []
    for entry in exposed:
        skill_file = Path(entry['absolute_path'])
        if entry['locator_kind'] != 'file' or not skill_file.is_file():
            contents.append({'path': entry['absolute_path'], 'matches_canonical': None})
        else:
            digest = content_hash(skill_file.parent)
            contents.append({'path': str(skill_file), 'content_hash': digest,
                             'matches_canonical': digest == result['evidence']['content_hash']})
    if contents:
        matches = [item['matches_canonical'] for item in contents]
        content_status = 'unavailable' if None in matches else 'pass' if all(matches) else 'fail'
        add(result, 'exposed-content', content_status, 'exposed bundle vs selected canonical bundle',
            'content fingerprint comparison; no body-loading claim', contents)
    if rules and any(e['origin'] == 'dojo-managed' for e in exposed):
        add(result, 'profile-disagreement', 'fail', 'profile declaration vs observed exposure',
            'harness-equivalences and Codex prompt-input',
            'Profile would suppress Dojo, but its copy is exposed; reconcile intended rollout')
    result['limitations'] = [
        'A fresh prompt rendering does not prove a running desktop session refreshed or loaded the skill body.',
        'Candidate paths and config declarations are not a complete effective-config trace or plugin inventory.',
        'No config edits, synchronization, model turn, or quality evaluation performed.',
    ]


@dataclass
class Request:
    command: str
    skill: str
    repo: str
    json: bool
    timeout: float
    base: str | None = None
    repo_checks: bool = False
    cwd: str | None = None


def execute(args: Request):
    result = dict(schema_version=1, command=args.command, target=args.skill, status='unavailable',
                  observed_at=datetime.now(timezone.utc).isoformat(), evidence={}, checks=[], limitations=[])
    try:
        if args.timeout <= 0 or not args.timeout < float('inf'):
            raise ValueError('--timeout must be finite and greater than zero')
        repo = Path(args.repo).expanduser().resolve()
        target = target_path(repo, args.skill)
        result['target'] = target.name
        result['evidence'] = identity(repo, target)
        (check if args.command == 'check' else inspect)(args, repo, target, result)
        if content_hash(target) != result['evidence']['content_hash']:
            add(result, 'input-stability', 'unavailable', 'selected skill', 'content hash recheck',
                'Skill changed during inspection; rerun against stable inputs')
    except Exception as exc:
        add(result, 'execution', 'unavailable', 'requested operation', type(exc).__name__, str(exc))
    states = {c['status'] for c in result['checks']}
    result['status'] = 'unavailable' if 'unavailable' in states else 'fail' if 'fail' in states else 'pass'
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        render(result)
    return {'pass': 0, 'fail': 1, 'unavailable': 2}[result['status']]


def render(result):
    """Human presentation only; JSON bypasses Rich entirely."""
    console = Console(markup=False, highlight=False)
    styles = {'pass': 'green', 'fail': 'red', 'unavailable': 'yellow', 'skipped': 'dim'}
    console.print(f"{result['command']} {result['target']}: {result['status']}",
                  style=styles[result['status']])
    table = Table('Status', 'Check', 'Scope', box=None, padding=(0, 1))
    for item in result['checks']:
        table.add_row(item['status'], item['id'], item['scope'], style=styles[item['status']])
    console.print(table)
    for item in result['checks']:
        if item['status'] != 'pass' or result['command'] == 'inspect':
            console.print(f"{item['id']}: " + json.dumps(item['details']))
    console.print('Evidence: ' + json.dumps(result['evidence']))
    for limit in result['limitations']:
        console.print('Limit: ' + limit)


app = typer.Typer(help=__doc__, add_completion=False, pretty_exceptions_enable=False,
                  no_args_is_help=False)
Repo = Annotated[str, typer.Option(help='Trusted canonical Dojo checkout (default: CLI checkout)')]
Json = Annotated[bool, typer.Option('--json', help='Emit one schema-versioned JSON result')]
Timeout = Annotated[float, typer.Option(help='Per external-check timeout in seconds')]
Skill = Annotated[str, typer.Argument(help='Canonical skill name or directory path')]


@app.command('check')
def check_command(
    skill: Skill,
    repo: Repo = str(TOOL_ROOT),
    json_output: Json = False,
    timeout: Timeout = 60,
    base: Annotated[str | None, typer.Option(help='Git release comparison base; omitted means release check is skipped')] = None,
    repo_checks: Annotated[bool, typer.Option('--repo-checks', help='Also run repository-wide generated-file checks')] = False,
):
    """Check selected skill packaging; optional release and repository checks."""
    raise typer.Exit(execute(Request('check', skill, repo, json_output, timeout,
                                    base=base, repo_checks=repo_checks)))


class Harness(str, Enum):
    codex = 'codex'


@app.command('inspect')
def inspect_command(
    skill: Skill,
    harness: Annotated[Harness, typer.Option(help='Harness to inspect (currently Codex only)')],
    repo: Repo = str(TOOL_ROOT),
    json_output: Json = False,
    timeout: Timeout = 60,
    cwd: Annotated[str | None, typer.Option(help='Harness invocation directory (default: current directory)')] = None,
):
    """Inspect copies and fresh Codex catalog exposure without a model turn."""
    raise typer.Exit(execute(Request('inspect', skill, repo, json_output, timeout,
                                    cwd=cwd if cwd is not None else os.getcwd())))


def main(argv=None):
    app(args=argv, prog_name='dojo')


if __name__ == '__main__':
    main()
