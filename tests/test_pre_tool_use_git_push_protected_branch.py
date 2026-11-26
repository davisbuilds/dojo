"""The push guard must block every spelling of a push to a protected branch."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parents[1] / "hooks" / "pre-tool-use-git-push-protected-branch.sh"


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    return tmp_path


def run(repo: Path, command: str, branch: str = "feature") -> int:
    subprocess.run(["git", "symbolic-ref", "HEAD", f"refs/heads/{branch}"], cwd=repo, check=True)
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    return subprocess.run(
        ["bash", str(HOOK)], cwd=repo, input=payload, capture_output=True, text=True
    ).returncode


@pytest.mark.parametrize(
    "command",
    [
        "git push origin main",
        "git push origin feature:main",
        "git push origin HEAD:main",
        "git push origin HEAD:refs/heads/main",
        "git push origin +main",
        "git push origin +feature:main",
        "git push --force origin main",
        "git push --all origin",
        "git -C . push origin main",
        "git status && git push origin main",
    ],
)
def test_pushes_to_main_are_blocked_from_any_branch(repo: Path, command: str) -> None:
    assert run(repo, command) == 2


@pytest.mark.parametrize(
    "command",
    ["git push", "git push origin", "git push origin HEAD", "git push origin +HEAD", "git push origin @"],
)
def test_pushes_of_the_current_branch_are_blocked_on_main(repo: Path, command: str) -> None:
    assert run(repo, command, branch="main") == 2
    assert run(repo, command, branch="feature") == 0


@pytest.mark.parametrize(
    "command",
    [
        "git push origin feature",
        "git push origin +feature",
        "git push origin main:feature",
        "git push -u origin feature",
        'git commit -m "do not push origin main"',
        "git log main..feature",
        "echo git push origin main-backup",
        "DOJO_ALLOW_PROTECTED_PUSH=1 git push origin main",
    ],
)
def test_other_commands_are_allowed(repo: Path, command: str) -> None:
    assert run(repo, command) == 0
