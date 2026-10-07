"""Configured hooks must work after uv sync, without harness PATH activation."""
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def checkout(tmp_path):
    repo = tmp_path / 'checkout with spaces'
    repo.mkdir()
    subprocess.run(['git', 'init', '-q', str(repo)], check=True)
    shutil.copytree(ROOT/'hooks', repo/'hooks', ignore=shutil.ignore_patterns('__pycache__'))
    (repo/'scripts').mkdir()
    for name in ('generate_skills_manifest.py', 'gen_catalog.py'):
        shutil.copy(ROOT/'scripts'/name, repo/'scripts'/name)
    validator = repo/'skills/skill-creator/scripts'
    validator.mkdir(parents=True)
    shutil.copy(ROOT/'skills/skill-creator/scripts/quick_validate.py', validator)
    (repo/'skills/alpha').mkdir()
    (repo/'.venv').symlink_to(Path(sys.prefix), target_is_directory=True)
    tools = tmp_path/'tools'
    tools.mkdir()
    # A known failing ambient Python proves the configured hook selects .venv.
    python = tools/'python3'
    python.write_text('#!/bin/sh\necho "ambient Python used" >&2\nexit 1\n')
    python.chmod(0o755)
    env = {**os.environ, 'PATH': str(tools)+os.pathsep+os.environ['PATH']}
    assert subprocess.run(['python3'], env=env, capture_output=True).returncode == 1
    return repo, env


def command(config, hook):
    settings = json.loads((ROOT/config/'settings.json').read_text())
    return next(shlex.split(h['command']) for events in settings['hooks'].values()
                for event in events for h in event['hooks'] if h['command'].endswith(hook))


@pytest.mark.parametrize('config', ['.claude', '.agents'])
def test_configured_python_hooks_use_checkout_environment(checkout, config):
    repo, env = checkout
    payload = {'tool_name': 'Write', 'tool_input': {
        'file_path': str(repo/'skills/alpha/SKILL.md'), 'content': 'missing frontmatter'}}
    pre = subprocess.run(command(config, 'pre-tool-use-validate-skill.sh'), cwd=repo,
                         env=env, input=json.dumps(payload), capture_output=True, text=True)
    assert pre.returncode == 2, pre.stderr
    assert 'ambient Python used' not in pre.stderr
    (repo/'skills/alpha/SKILL.md').write_text(
        '---\nname: alpha\ndescription: Use when testing.\nversion: 1.0.0\n---\n')
    post = subprocess.run(command(config, 'post-tool-use-regen-manifest.sh'), cwd=repo,
                          env=env, input=json.dumps(payload), capture_output=True, text=True)
    assert post.returncode == 0, post.stderr
    manifest = json.loads((repo/'skills.json').read_text())
    assert manifest['skills'][0]['name'] == 'alpha'
    assert (repo/'docs/catalog/index.html').is_file()


def test_missing_hook_environment_reports_setup_error(checkout):
    repo, env = checkout
    (repo/'.venv').unlink()
    result = subprocess.run(command('.claude', 'pre-tool-use-validate-skill.sh'),
                            cwd=repo, env=env, input='{}', capture_output=True, text=True)
    assert result.returncode == 1
    assert 'uv sync --locked' in result.stderr
    assert 'ambient Python used' not in result.stderr
    assert not (repo/'.venv').exists()
