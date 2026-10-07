"""Real CLI failures and positive controls over isolated skill edits."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / 'bin/dojo'


def invoke(repo, *args, env=None):
    result = subprocess.run([sys.executable, str(CLI), *args, '--repo', str(repo), '--json'],
                            capture_output=True, text=True, env=env)
    return result.returncode, json.loads(result.stdout)


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), '-c', 'core.hooksPath=/dev/null',
        '-c', 'user.name=Test', '-c', 'user.email=test@example.test', *args], text=True).strip()


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, 'init', '-q')
    for name in ('alpha', 'beta'):
        skill = tmp_path / 'skills' / name
        skill.mkdir(parents=True)
        (skill / 'SKILL.md').write_text(f'---\nname: {name}\ndescription: Use when testing packaging.\nskill-type: reference\nversion: 1.0.0\n---\n\nA small skill.\n')
    git(tmp_path, 'add', 'skills/alpha/SKILL.md', 'skills/beta/SKILL.md')
    git(tmp_path, 'commit', '-qm', 'Baseline')
    return tmp_path


def test_check_detects_invalid_metadata_and_valid_control(repo):
    code, result = invoke(repo, 'check', 'alpha')
    assert code == 0
    assert any(c['id'] == 'metadata' and c['status'] == 'pass' for c in result['checks'])
    (repo / 'skills/alpha/SKILL.md').write_text('missing frontmatter')
    code, result = invoke(repo, 'check', 'alpha')
    assert code == 1 and result['status'] == 'fail'


def test_check_reports_broken_links(repo):
    with (repo / 'skills/alpha/SKILL.md').open('a') as f:
        f.write('\n[Missing](references/missing.md)\n')
    code, result = invoke(repo, 'check', 'alpha')
    assert code == 1
    assert any(c['id'] == 'links' and c['status'] == 'fail' for c in result['checks'])


def test_release_check_is_scoped_and_names_its_base(repo):
    base = git(repo, 'rev-parse', 'HEAD')
    with (repo / 'skills/beta/SKILL.md').open('a') as f:
        f.write('Unrelated edit\n')
    code, result = invoke(repo, 'check', 'alpha', '--base', base)
    assert code == 0
    with (repo / 'skills/alpha/SKILL.md').open('a') as f:
        f.write('Target edit\n')
    code, result = invoke(repo, 'check', 'alpha', '--base', base)
    assert code == 1
    assert result['evidence']['base_commit'] == base


def test_unknown_skill_is_input_error(repo):
    code, result = invoke(repo, 'check', 'does-not-exist')
    assert code == 2 and result['status'] == 'unavailable'


def fake_codex(tmp_path, repo, count=1, broken=False, delay=0):
    import os
    home = tmp_path / 'home'
    home.mkdir(exist_ok=True)
    tools = tmp_path / 'tools'
    tools.mkdir(exist_ok=True)
    executable = tools / 'codex'
    entries = [f'- known-control: Known positive (file: {home}/.codex/skills/.system/known-control/SKILL.md)']
    entries += [f'- alpha: Test target (file: {repo}/skills/alpha/SKILL.md)'] * count
    block = '<skills_instructions>\n## Skills\nEach entry includes a name, description, and source locator.\n### Available skills\n' + '\n'.join(entries) + '\n</skills_instructions>'
    payload = [] if broken else [{'role': 'developer', 'content': [{'type': 'input_text', 'text': block}]}]
    executable.write_text(f'''#!{sys.executable}
import json,sys,time
if sys.argv[1:] == ['--version']:
    print('codex-cli fixture')
elif sys.argv[1:] == ['debug', 'models']:
    print('{{"models": []}}')
elif sys.argv[1:] == ['debug', 'prompt-input']:
    time.sleep({delay})
    print({json.dumps(json.dumps(payload))})
else:
    raise SystemExit(7)
''')
    executable.chmod(0o755)
    return {**os.environ, 'PATH': str(tools), 'HOME': str(home), 'CODEX_HOME': str(home/'.codex'),
            'AGENTS_HOME': str(home/'.agents'), 'CLAUDE_HOME': str(home/'.claude')}


@pytest.mark.parametrize('count, expected', [(1, 0), (0, 1), (2, 1)])
def test_inspect_exposure_has_real_positive_control(repo, tmp_path, count, expected):
    env = fake_codex(tmp_path, repo, count=count)
    # Git is also needed; retain only its directory after the fake harness.
    import shutil, os
    env['PATH'] += os.pathsep + str(Path(shutil.which('git')).parent)
    before = (repo/'skills/alpha/SKILL.md').read_bytes()
    code, result = invoke(repo, 'inspect', 'alpha', '--harness', 'codex', '--cwd', str(repo), env=env)
    assert code == expected, json.dumps(result['checks'][-1], indent=2)
    catalog = next(c for c in result['checks'] if c['id']=='catalog')
    assert catalog['details']['match_count'] == count
    assert result['evidence']['catalog_entry_count'] == count + 1
    assert result['evidence']['observation_surface'].startswith('codex debug prompt-input')
    assert (repo/'skills/alpha/SKILL.md').read_bytes() == before
    assert not git(repo, 'status', '--porcelain', '--', 'skills')


@pytest.mark.parametrize('broken, delay', [(True, 0), (False, 3)])
def test_inspect_failed_detector_is_unavailable_not_absent(repo, tmp_path, broken, delay):
    import shutil, os, time
    env = fake_codex(tmp_path, repo, broken=broken, delay=delay)
    env['PATH'] += os.pathsep + str(Path(shutil.which('git')).parent)
    start = time.monotonic()
    code, result = invoke(repo, 'inspect', 'alpha', '--harness', 'codex', '--cwd', str(repo),
                          '--timeout', '0.4', env=env)
    assert code == 2 and result['status'] == 'unavailable', result
    assert time.monotonic() - start < 2.5
    assert not any(c['id']=='catalog' and c['status']=='pass' for c in result['checks'])


def test_missing_base_and_escaped_target_are_input_errors(repo, tmp_path):
    code, result = invoke(repo, 'check', 'alpha', '--base', 'no-such-ref')
    assert code == 2 and result['status'] == 'unavailable'
    elsewhere = tmp_path / 'outside'
    elsewhere.mkdir()
    (elsewhere/'SKILL.md').write_text('outside')
    code, result = invoke(repo, 'check', str(elsewhere))
    assert code == 2


def test_missing_repository_tools_are_unavailable(repo):
    code, result = invoke(repo, 'check', 'alpha', '--repo-checks')
    assert code == 2
    assert all(c['status']=='unavailable' for c in result['checks'] if c['scope']=='repository')


def test_help_works_without_repository_or_harness(tmp_path):
    result = subprocess.run([sys.executable, str(CLI), '--help'], cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0 and 'inspect' in result.stdout and 'check' in result.stdout


@pytest.mark.parametrize('args', [[], ['check'], ['inspect', 'alpha'],
                                ['inspect', 'alpha', '--harness', 'unsupported'],
                                ['check', 'alpha', '--timeout', 'invalid']])
def test_usage_errors_keep_exit_two(tmp_path, args):
    result = subprocess.run([sys.executable, str(CLI), *args], cwd=tmp_path,
                            capture_output=True, text=True)
    assert result.returncode == 2
    assert 'Traceback' not in result.stderr
    assert 'Usage:' in result.stderr


def test_json_is_unstyled_even_when_color_is_forced(repo):
    import os
    env = {**os.environ, 'FORCE_COLOR': '1'}
    code, result = invoke(repo, 'check', 'alpha', env=env)
    assert code == 0 and result['schema_version'] == 1
    code, result = invoke(repo, 'check', 'alpha', '--timeout', 'nan', env=env)
    assert code == 2 and result['status'] == 'unavailable'


def test_human_output_preserves_literal_markup_without_ansi(repo):
    import os
    result = subprocess.run([sys.executable, str(CLI), 'check', '[red]missing[/red]',
                             '--repo', str(repo)], capture_output=True, text=True,
                            env={**os.environ, 'NO_COLOR': '1', 'TERM': 'dumb'})
    assert result.returncode == 2
    assert '[red]missing[/red]' in result.stdout
    assert '\x1b[' not in result.stdout
    assert 'execution' in result.stdout


@pytest.mark.parametrize('linked', [False, True])
def test_inspect_detects_drift_in_the_exposed_copy(repo, tmp_path, linked):
    import shutil, os
    env = fake_codex(tmp_path, repo)
    env['PATH'] += os.pathsep + str(Path(shutil.which('git')).parent)
    installed = tmp_path / 'home/.agents/skills/alpha'
    shutil.copytree(repo/'skills/alpha', installed)
    exposed = installed
    if linked:
        exposed = tmp_path / 'home/.codex/skills/alpha'
        exposed.parent.mkdir(parents=True)
        exposed.symlink_to(installed, target_is_directory=True)
    exe = tmp_path/'tools/codex'
    exe.write_text(exe.read_text().replace(str(repo/'skills/alpha/SKILL.md'), str(exposed/'SKILL.md')))
    code, result = invoke(repo, 'inspect', 'alpha', '--harness', 'codex', '--cwd', str(repo), env=env)
    assert code == 0, result
    (installed/'SKILL.md').write_text('older installed content')
    code, result = invoke(repo, 'inspect', 'alpha', '--harness', 'codex', '--cwd', str(repo), env=env)
    assert code == 1, result
    item = next(c for c in result['checks'] if c['id']=='exposed-content')
    assert item['status']=='fail' and item['details'][0]['matches_canonical'] is False


def test_skill_digest_tracks_untracked_hidden_content(repo):
    _, before = invoke(repo, 'check', 'alpha')
    (repo/'skills/alpha/.hidden').mkdir()
    (repo/'skills/alpha/.hidden/context').write_text('additional runtime context')
    _, after = invoke(repo, 'check', 'alpha')
    assert before['evidence']['content_hash'] != after['evidence']['content_hash']
    assert after['evidence']['working_tree_dirty']


def test_inspect_uses_selected_catalog_for_profile_disagreement(repo, tmp_path):
    import shutil, os
    env = fake_codex(tmp_path, repo)
    env['PATH'] += os.pathsep + str(Path(shutil.which('git')).parent)
    installed = tmp_path / 'home/.agents/skills/alpha'
    shutil.copytree(repo/'skills/alpha', installed)
    exe = tmp_path/'tools/codex'
    exe.write_text(exe.read_text().replace(str(repo/'skills/alpha/SKILL.md'), str(installed/'SKILL.md')))
    (repo/'profiles').mkdir()
    (repo/'profiles/harness-equivalences.yaml').write_text(
        'equivalences:\n  - skill: alpha\n    harness: codex\n    bundled_entry: alpha\n    evidence: fixture\n')
    code, result = invoke(repo, 'inspect', 'alpha', '--harness', 'codex', '--cwd', str(repo), env=env)
    assert code == 1, result
    catalog = next(c for c in result['checks'] if c['id']=='catalog')
    assert catalog['details']['exposed'][0]['origin'] == 'dojo-managed'
    assert any(c['id']=='profile-disagreement' and c['status']=='fail' for c in result['checks'])


@pytest.mark.parametrize('args', [['-h'], ['check', '-h'], ['inspect', '-h'], ['list', '-h'], ['info', '-h']])
def test_short_help_is_available_at_each_command(tmp_path, args):
    result = subprocess.run([sys.executable, str(CLI), *args], cwd=tmp_path,
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert 'Usage:' in result.stdout and '--help' in result.stdout


@pytest.mark.parametrize('flag', ['--version', '-v'])
def test_version_uses_the_cli_checkout_manifest(tmp_path, flag):
    import tomllib
    expected = tomllib.loads((ROOT/'pyproject.toml').read_text())['project']['version']
    result = subprocess.run([sys.executable, str(CLI), flag], cwd=tmp_path,
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert result.stdout == f'dojo {expected}\n'
    assert not result.stderr


def test_list_searches_the_selected_manifest_without_mutation(repo):
    entries = [dict(name='alpha', version='1.0.0', path='skills/alpha', description='Use for testing.'),
               dict(name='beta', version='2.0.0', path='skills/beta', description='Use for research.')]
    manifest = repo/'skills.json'
    manifest.write_text(json.dumps({'version': 1, 'skills': entries}))
    before = manifest.read_bytes()
    code, result = invoke(repo, 'list', 'RESEARCH')
    assert code == 0 and [s['name'] for s in result['skills']] == ['beta']
    assert result['total_count'] == 2 and result['match_count'] == 1
    code, result = invoke(repo, 'list', 'no-match')
    assert code == 0 and result['skills'] == [] and result['match_count'] == 0
    assert manifest.read_bytes() == before


@pytest.mark.parametrize('content', [None, '{}', '{"version":1,"skills":[{}]}'])
def test_list_unavailable_manifest_is_not_an_empty_catalog(repo, content):
    if content is not None:
        (repo/'skills.json').write_text(content)
    code, result = invoke(repo, 'list')
    assert code == 2 and result['status'] == 'unavailable'
    assert 'error' in result


def test_info_identifies_running_checkout_and_environment(tmp_path):
    result = subprocess.run([sys.executable, str(CLI), 'info', '--json'], cwd=tmp_path,
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    info = json.loads(result.stdout)
    assert Path(info['repository']).resolve() == ROOT.resolve()
    assert Path(info['python']['environment']).resolve() == Path(sys.prefix).resolve()
    assert info['head_commit'] == git(ROOT, 'rev-parse', 'HEAD')
    assert info['dependencies']['typer']
