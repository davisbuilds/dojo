"""Run the skill-standardizer suite under pytest and pin its process isolation.

The suite ships beside the skill with a stdlib-only direct runner (see Test
Tiers in docs/system/ARCHITECTURE.md). Its tests point the harness-home
variables at fixtures and chdir into temporary directories. Both are
process-global, so every test must restore them; otherwise a later test starts
in a deleted cwd or reads another test's fixture homes.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "skills" / "skill-standardizer" / "scripts" / "test_skill_standardizer.py"
HOME_ENV_NAMES = ("AGENTS_HOME", "CODEX_HOME", "CLAUDE_HOME")
STATES = ("absent", "preexisting", "empty")
# Each rotation assigns one state per variable, so across the three every
# variable starts absent, set, and set-but-empty.
ROTATIONS = [STATES[i:] + STATES[:i] for i in range(len(STATES))]


def load_suite():
    # Distinct module name: pytest may import this file as test_skill_standardizer_suite.
    spec = importlib.util.spec_from_file_location("skill_standardizer_suite", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


suite = load_suite()


def snapshot() -> dict[str, str | None]:
    try:
        cwd = os.getcwd()
    except FileNotFoundError:
        cwd = "<deleted cwd>"
    return {"cwd": cwd, **{name: os.environ.get(name) for name in HOME_ENV_NAMES}}


def arrange(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, states) -> dict[str, str | None]:
    """Start in a synthetic cwd with each harness-home variable in the given state."""
    # A home a test forgets to set falls back under this HOME, never a real install.
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    anchor = tmp_path / "anchor"
    anchor.mkdir()
    monkeypatch.chdir(anchor)
    for name, state in zip(HOME_ENV_NAMES, states):
        if state == "absent":
            monkeypatch.delenv(name, raising=False)
        elif state == "empty":
            monkeypatch.setenv(name, "")
        else:
            monkeypatch.setenv(name, str(tmp_path / "preexisting" / name.lower()))
    return snapshot()


def test_runner_lists_every_suite_test():
    names = [test.__name__ for test in suite.TESTS]
    defined = {name for name, value in vars(suite).items() if name.startswith("test_") and callable(value)}
    assert len(names) == len(set(names))
    assert set(names) == defined


@pytest.mark.parametrize("states", ROTATIONS, ids="-".join)
@pytest.mark.parametrize("name", [test.__name__ for test in suite.TESTS])
def test_suite_case_passes_and_restores_process_state(name, states, tmp_path, monkeypatch):
    before = arrange(tmp_path, monkeypatch, states)
    getattr(suite, name)()
    assert snapshot() == before


@pytest.mark.parametrize("order", ["forward", "reverse"])
def test_suite_passes_in_either_order_in_one_process(order, tmp_path, monkeypatch):
    before = arrange(tmp_path, monkeypatch, STATES)
    tests = suite.TESTS if order == "forward" else tuple(reversed(suite.TESTS))
    for test in tests:
        test()
        assert snapshot() == before, f"{test.__name__} leaked process state"


def enter_and_repoint(td: str) -> None:
    os.chdir(td)
    for name in HOME_ENV_NAMES:
        os.environ[name] = str(Path(td) / name.lower())


@pytest.mark.parametrize("state", STATES)
def test_isolated_tempdir_restores_each_variable_state(state, tmp_path, monkeypatch):
    before = arrange(tmp_path, monkeypatch, [state] * len(HOME_ENV_NAMES))
    with suite.isolated_tempdir() as td:
        enter_and_repoint(td)
    assert snapshot() == before
    assert not Path(td).exists()


def test_isolated_tempdir_restores_after_a_failure(tmp_path, monkeypatch):
    before = arrange(tmp_path, monkeypatch, STATES)
    with pytest.raises(RuntimeError, match="fixture failure"):
        with suite.isolated_tempdir() as td:
            enter_and_repoint(td)
            raise RuntimeError("fixture failure")
    assert snapshot() == before
    assert not Path(td).exists()


def test_isolated_tempdir_leaves_the_directory_before_removing_it(tmp_path, monkeypatch):
    before = arrange(tmp_path, monkeypatch, STATES)
    removals = []
    real_rmtree = shutil.rmtree

    def recording_rmtree(path, *args, **kwargs):
        removals.append((os.fspath(path), snapshot()["cwd"]))
        return real_rmtree(path, *args, **kwargs)

    monkeypatch.setattr(shutil, "rmtree", recording_rmtree)
    with suite.isolated_tempdir() as td:
        enter_and_repoint(td)
    assert removals == [(td, before["cwd"])]


def test_direct_runner_needs_no_pytest(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    env = {name: value for name, value in os.environ.items() if name not in HOME_ENV_NAMES}
    env["HOME"] = str(home)

    def run(*args: str) -> subprocess.CompletedProcess[str]:
        # -S drops site-packages, where pytest is installed.
        return subprocess.run(
            [sys.executable, "-I", *args], cwd=tmp_path, env=env, capture_output=True, text=True,
        )

    assert run("-c", "import pytest").returncode == 0
    without_site = run("-S", "-c", "import pytest")
    assert without_site.returncode != 0
    assert "No module named 'pytest'" in without_site.stderr

    result = run("-S", str(SCRIPT_PATH))
    assert result.returncode == 0, result.stdout + result.stderr
    passed = [line for line in result.stdout.splitlines() if line.startswith("PASS ")]
    assert len(passed) == len(suite.TESTS)
    assert "All skill-standardizer regression tests passed." in result.stdout
