"""Exercise the optional loop scaffold through its public CLI and generated check."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/loop-design/scripts/scaffold_loop.py'


def blueprint(kind='task', **overrides):
    return {
        'schema_version': 2,
        'name': 'sample-loop',
        'kind': kind,
        'goal': 'Investigate the current failure.',
        'evidence': 'Reproduce the failure, then check the proposed explanation against the trace.',
        'stop_when': 'Stop after 20 minutes or if required data is unavailable.',
        **overrides,
    }


def scaffold(tmp_path, bp, out=None):
    source = tmp_path / 'input.json'
    source.write_text(json.dumps(bp))
    out = out or tmp_path / 'bundle'
    result = subprocess.run(
        [sys.executable, str(SCRIPT), '--blueprint', str(source), '--out-dir', str(out)],
        cwd=tmp_path, capture_output=True, text=True,
    )
    return result, out


@pytest.mark.parametrize('kind', ['task', 'monitor', 'experiment'])
def test_scaffolds_evidence_without_requiring_a_completion_command(tmp_path, kind):
    result, out = scaffold(tmp_path, blueprint(kind))
    assert result.returncode == 0, result.stderr
    assert {p.name for p in out.iterdir()} == {'LOOP.md', 'blueprint.json'}
    prompt = (out / 'LOOP.md').read_text()
    assert '20 minutes' in prompt
    assert 'trace' in prompt
    assert kind in prompt
    assert json.loads((out / 'blueprint.json').read_text())['kind'] == kind


def test_checkpoint_is_opt_in_and_regeneration_preserves_running_state(tmp_path):
    bp = blueprint(checkpoint=True)
    result, out = scaffold(tmp_path, bp)
    assert result.returncode == 0, result.stderr
    state = out / 'checkpoint.md'
    assert 'Next action' in state.read_text()
    state.write_text('Paused: job-123 may still be running; inspect before retrying.\n')
    before = {p.name: p.read_bytes() for p in out.iterdir()}
    result, _ = scaffold(tmp_path, bp)
    assert result.returncode != 0
    assert {p.name: p.read_bytes() for p in out.iterdir()} == before


def test_check_runs_once_from_declared_cwd_and_preserves_output_and_exit(tmp_path):
    work = tmp_path / "work ' $(touch should-not-exist)"
    work.mkdir()
    command = "printf 'observation {{GOAL}}\\n'; printf 'detail\\n' >&2; printf x >> calls; exit 7"
    result, out = scaffold(tmp_path, blueprint(check={
        'command': command, 'cwd': str(work),
    }))
    assert result.returncode == 0, result.stderr
    assert not (work / 'calls').exists(), 'scaffolding must not execute the command'
    check = out / 'check.sh'
    assert os.access(check, os.X_OK)
    run = subprocess.run([str(check)], cwd=tmp_path, capture_output=True, text=True)
    assert run.returncode == 7
    assert run.stdout == 'observation {{GOAL}}\n'
    assert run.stderr == 'detail\n'
    assert (work / 'calls').read_text() == 'x'
    assert not (tmp_path / 'should-not-exist').exists()
    # A real passing command is a control for the failure/exit propagation check.
    result, other = scaffold(tmp_path, blueprint(check={
        'command': 'test -f calls', 'cwd': str(work),
    }), tmp_path / 'passing-bundle')
    assert result.returncode == 0, result.stderr
    assert subprocess.run([str(other / 'check.sh')], cwd=tmp_path).returncode == 0
    work.rename(tmp_path / 'moved')
    failed = subprocess.run([str(check)], cwd=tmp_path, capture_output=True, text=True)
    assert failed.returncode != 0
    assert not (tmp_path / 'calls').exists(), 'missing cwd must not fall through'


@pytest.mark.parametrize('overrides, diagnostic', [
    ({'name': '../escape'}, 'name'),
    ({'kind': 'forever'}, 'kind'),
    ({'evidence': ''}, 'evidence'),
    ({'stop_when': []}, 'stop_when'),
    ({'checkpoint': 'false'}, 'checkpoint'),
    ({'check': {'command': 'true', 'cwd': '.'}}, 'absolute'),
    ({'check': {'command': 'true'}}, 'cwd'),
    ({'stop_whne': 'typo'}, 'stop_whne'),
    ({'schema_version': 1, 'done_when': 'true'}, 'migration'),
])
def test_invalid_blueprint_fails_before_creating_output(tmp_path, overrides, diagnostic):
    result, out = scaffold(tmp_path, blueprint(**overrides))
    assert result.returncode != 0
    assert diagnostic in result.stderr
    assert not out.exists()


def test_legacy_blueprint_requires_explicit_migration(tmp_path):
    result, out = scaffold(tmp_path, {'name': 'legacy', 'goal': 'Fix tests', 'done_when': 'true'})
    assert result.returncode != 0
    assert 'migration' in result.stderr
    assert not out.exists()


def test_existing_output_symlink_is_not_followed(tmp_path):
    target = tmp_path / 'state'
    target.mkdir()
    link = tmp_path / 'bundle'
    link.symlink_to(target, target_is_directory=True)
    result, _ = scaffold(tmp_path, blueprint(), link)
    assert result.returncode != 0
    assert list(target.iterdir()) == []
