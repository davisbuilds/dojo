"""Security evidence must not turn failed or empty scans into clean verdicts."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/secure-code/scripts'


def parser_module():
    spec = importlib.util.spec_from_file_location('secure_parser', SCRIPTS / 'parse_findings.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_error_only_scan_is_not_clean():
    report = parser_module().parse_findings({'results': [], 'errors': [{'message': 'parser failed'}]})
    assert 'parser failed' in report
    assert 'No findings detected.' not in report


def test_missing_scan_schema_is_not_clean():
    assert 'invalid' in parser_module().parse_findings({}).lower()


def fake_engine(tmp_path, monkeypatch, payload, code=0):
    executable = tmp_path / 'semgrep'
    executable.write_text('#!/usr/bin/env python3\nimport json, sys\n'
                          'from pathlib import Path\n'
                          f'Path({str(tmp_path / "argv.json")!r}).write_text(json.dumps(sys.argv[1:]))\n'
                          f'print({json.dumps(payload)!r})\n'
                          f'sys.exit({code})\n')
    executable.chmod(0o755)
    monkeypatch.setenv('PATH', str(tmp_path) + os.pathsep + os.environ['PATH'])
    target = tmp_path / 'source file.py'
    target.write_text('pass\n')
    return target


def scan(*args, cwd=None):
    return subprocess.run(['bash', str(SCRIPTS / 'scan.sh'), *map(str, args)],
                          text=True, capture_output=True, cwd=cwd)


def raw(scanned=None, errors=None, results=None):
    return {'version': 'test-version', 'results': results or [], 'errors': errors or [],
            'paths': {'scanned': ['source file.py'] if scanned is None else scanned}}


def test_multiple_configs_and_paths_survive_argv(tmp_path, monkeypatch):
    target = fake_engine(tmp_path, monkeypatch, raw())
    result = scan(target, '--config', 'rules one.yaml', '--config', 'rules two.yaml')
    argv = json.loads((tmp_path / 'argv.json').read_text())
    configs = [argv[i + 1] for i, arg in enumerate(argv) if arg == '--config']
    assert configs == ['rules one.yaml', 'rules two.yaml']
    assert str(target) in argv
    assert result.returncode == 0


@pytest.mark.parametrize('payload,code,expected', [
    (raw(), 0, 'completed'),
    (raw(errors=[{'message': 'parse failure'}]), 0, 'partial'),
    (raw(), 2, 'failed'),
    (raw(scanned=[]), 0, 'empty'),
    ({}, 0, 'invalid'),
    ({'results': [], 'errors': []}, 0, 'unknown'),
])
def test_adapter_records_execution_and_coverage(tmp_path, monkeypatch, payload, code, expected):
    target = fake_engine(tmp_path, monkeypatch, payload, code)
    result = scan(target, '--config', 'p/test')
    packet = json.loads(result.stdout)
    assert packet['_scan']['status'] == expected
    assert packet['_scan']['exit_code'] == code
    assert packet['_scan']['targets'] == [str(target)]
    assert packet['results'] == payload.get('results', [])
    assert result.returncode == (0 if expected == 'completed' else 2)


def test_missing_target_fails_without_running_engine(tmp_path, monkeypatch):
    fake_engine(tmp_path, monkeypatch, raw())
    result = scan(tmp_path / 'missing.py')
    assert result.returncode == 2
    assert not (tmp_path / 'argv.json').exists()
    assert json.loads(result.stdout)['_scan']['status'] == 'failed'


def test_unknown_options_and_missing_config_value_fail():
    assert scan('.', '--autofix').returncode == 2
    assert scan('.', '--config').returncode == 2


def test_parser_keeps_unknown_severity_and_coverage_limits():
    payload = raw(results=[{'check_id':'r', 'path':'a.py', 'start':{'line':1},
                           'extra':{'severity':'CUSTOM','message':'candidate','metadata':{'cwe':'CWE-78'}}}])
    payload['paths']['skipped'] = [{'path':'b.py','reason':'unsupported'}]
    report = parser_module().parse_findings(payload)
    assert 'CUSTOM' in report and 'candidate' in report and 'CWE-78' in report
    assert 'b.py' in report and 'unsupported' in report


@pytest.mark.skipif(not shutil.which('semgrep'), reason='Semgrep integration requires local CLI')
def test_real_engine_combines_rules_with_positive_and_benign_controls(tmp_path):
    target = tmp_path / 'cases.py'
    target.write_text('eval(user_text)\nsubprocess.run(command, shell=True)\nast.literal_eval(user_text)\n')
    configs = []
    for name, pattern in [('eval', 'eval($X)'), ('shell', 'subprocess.run($X, shell=True)')]:
        rule = tmp_path / (name + '.yaml')
        rule.write_text(f'rules:\n  - id: test.{name}\n    languages: [python]\n    severity: WARNING\n    message: Candidate only\n    pattern: {pattern}\n')
        configs += ['--config', str(rule)]
    result = scan(target, *configs, cwd=tmp_path)
    packet = json.loads(result.stdout)
    assert result.returncode == 0, packet
    assert sorted(r['start']['line'] for r in packet['results']) == [1, 2]
    assert packet['_scan']['status'] == 'completed'
    assert packet['version']
    assert len(packet['_scan']['configs']) == 2
    assert all(c['sha256'] for c in packet['_scan']['configs'])


@pytest.mark.parametrize('payload', [None, [], {'results': [None], 'errors': []},
    {'results': [{'extra': None}], 'errors': []},
    {'results': [], 'errors': {}, '_scan': {'status': 'completed'}}])
def test_malformed_packets_cannot_render_success(payload):
    assert 'invalid' in parser_module().parse_findings(payload).lower()


def test_failed_engine_diagnostics_and_exit_survive_pipeline(tmp_path, monkeypatch):
    target = fake_engine(tmp_path, monkeypatch, raw(errors=[{'message': 'invalid rule'}]), 2)
    output = scan(target)
    formatted = subprocess.run(['python3', str(SCRIPTS / 'parse_findings.py')],
                               input=output.stdout, capture_output=True, text=True)
    assert formatted.returncode == 2
    assert 'invalid rule' in formatted.stdout
    assert 'failed' in formatted.stdout
