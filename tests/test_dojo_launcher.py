"""The PATH entry selects its own environment without changing cwd or argv."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def fixture_checkout(tmp_path):
    repo = tmp_path/'checkout with spaces'
    (repo/'bin').mkdir(parents=True)
    (repo/'scripts').mkdir()
    shutil.copy(ROOT/'bin/dojo', repo/'bin/dojo')
    (repo/'scripts/dojo_cli.py').write_text(
        'import json, os, sys\n'
        'print(json.dumps({"prefix": sys.prefix, "cwd": os.getcwd(), "args": sys.argv[1:]}))\n')
    return repo


def test_symlink_launcher_selects_environment_and_preserves_context(tmp_path):
    repo = fixture_checkout(tmp_path)
    (repo/'.venv').symlink_to(Path(sys.prefix), target_is_directory=True)
    shim = tmp_path/'dojo'
    shim.symlink_to(os.path.relpath(repo/'bin/dojo', tmp_path))
    args = ['inspect', 'skill-creator', '--cwd', 'a directory with spaces']
    result = subprocess.run([sys._base_executable, str(shim), *args], cwd=tmp_path,
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert Path(data['prefix']).resolve() == Path(sys.prefix).resolve()
    assert Path(data['cwd']).resolve() == tmp_path.resolve()
    assert data['args'] == args


def test_missing_environment_reports_setup_without_installing(tmp_path):
    repo = fixture_checkout(tmp_path)
    result = subprocess.run([sys._base_executable, str(repo/'bin/dojo'), '--help'],
                            capture_output=True, text=True)
    assert result.returncode == 2
    assert 'uv sync --locked' in result.stderr
    assert not result.stdout
    assert not (repo/'.venv').exists()
