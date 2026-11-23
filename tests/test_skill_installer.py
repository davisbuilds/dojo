"""Exercise skill-installer's two scripts through their CLIs, offline.

The installer runs as a subprocess with HOME, CODEX_HOME and CLAUDE_HOME
pointed at a temporary directory. A global git `insteadOf` rewrite maps
https://github.com/ onto local fixture repositories, so `--method git` follows
the real clone and sparse-checkout path without any network access. The lister
is imported and its GitHub request is replaced, because its only network call
is the contents API.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "skills" / "skill-installer" / "scripts"
INSTALL = SCRIPTS / "install-skill-from-github.py"
LIST = SCRIPTS / "list-skills.py"


def _git(*args: str, cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


@pytest.fixture
def sandbox(tmp_path: Path) -> dict[str, Path]:
    home = tmp_path / "home"
    home.mkdir()
    remotes = tmp_path / "remotes"
    remotes.mkdir()
    gitconfig = tmp_path / "gitconfig"
    gitconfig.write_text(
        f'[url "file://{remotes}/"]\n\tinsteadOf = https://github.com/\n'
        "\tinsteadOf = git@github.com:\n"
        "[protocol \"file\"]\n\tallow = always\n"
        "[user]\n\tname = Test\n\temail = test@example.invalid\n"
        "[init]\n\tdefaultBranch = main\n",
        encoding="utf-8",
    )
    return {"home": home, "remotes": remotes, "gitconfig": gitconfig, "tmp": tmp_path}


def _env(sandbox: dict[str, Path], **extra: str) -> dict[str, str]:
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in {"CODEX_HOME", "CLAUDE_HOME", "GITHUB_TOKEN", "GH_TOKEN"}
    }
    env.update(
        HOME=str(sandbox["home"]),
        GIT_CONFIG_GLOBAL=str(sandbox["gitconfig"]),
        GIT_CONFIG_NOSYSTEM="1",
        GIT_TERMINAL_PROMPT="0",
        TMPDIR=str(sandbox["tmp"]),
    )
    env.update(extra)
    return env


def _make_remote(sandbox: dict[str, Path], build) -> None:
    """Create owner/repo as a local repository with one commit on main."""
    repo = sandbox["remotes"] / "owner" / "repo.git"
    repo.mkdir(parents=True)
    env = _env(sandbox)
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True, env=env)
    build(repo)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, env=env)
    subprocess.run(["git", "commit", "-q", "-m", "fixture"], cwd=repo, check=True, env=env)


def _skill(root: Path, name: str) -> Path:
    skill = root / "skills" / name
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Fixture.\n---\n\n# {name}\n", encoding="utf-8"
    )
    return skill


def _install(sandbox: dict[str, Path], *args: str, **env: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(INSTALL), "--repo", "owner/repo", "--method", "git", *args],
        capture_output=True,
        text=True,
        env=_env(sandbox, **env),
        timeout=60,
    )


def test_agent_claude_installs_into_claude_home_only(sandbox):
    _make_remote(sandbox, lambda repo: _skill(repo, "demo"))
    claude_home = sandbox["tmp"] / "claude"
    codex_home = sandbox["tmp"] / "codex"

    result = _install(
        sandbox,
        "--agent", "claude", "--path", "skills/demo",
        CLAUDE_HOME=str(claude_home), CODEX_HOME=str(codex_home),
    )

    assert result.returncode == 0, result.stderr
    assert (claude_home / "skills" / "demo" / "SKILL.md").is_file()
    assert not codex_home.exists()
    assert f"Installed demo to {claude_home / 'skills' / 'demo'}" in result.stdout


def test_default_agent_is_codex_and_unset_home_falls_back_to_dot_dir(sandbox):
    _make_remote(sandbox, lambda repo: _skill(repo, "demo"))

    result = _install(sandbox, "--path", "skills/demo")

    assert result.returncode == 0, result.stderr
    assert (sandbox["home"] / ".codex" / "skills" / "demo" / "SKILL.md").is_file()
    assert not (sandbox["home"] / ".claude").exists()


def test_dest_overrides_agent_home_and_existing_destination_is_refused(sandbox):
    _make_remote(sandbox, lambda repo: _skill(repo, "demo"))
    dest = sandbox["tmp"] / "custom-skills"

    first = _install(sandbox, "--agent", "claude", "--dest", str(dest), "--path", "skills/demo")
    assert first.returncode == 0, first.stderr
    assert (dest / "demo" / "SKILL.md").is_file()
    assert not (sandbox["home"] / ".claude").exists()

    (dest / "demo" / "LOCAL-EDIT").write_text("keep me", encoding="utf-8")
    second = _install(sandbox, "--agent", "claude", "--dest", str(dest), "--path", "skills/demo")
    assert second.returncode == 1
    assert "Destination already exists" in second.stderr
    assert (dest / "demo" / "LOCAL-EDIT").read_text(encoding="utf-8") == "keep me"


def test_symlink_inside_skill_pointing_outside_is_rejected(sandbox):
    def build(repo: Path) -> None:
        skill = _skill(repo, "leaky")
        (repo / "secret.txt").write_text("outside the skill", encoding="utf-8")
        (skill / "notes.txt").symlink_to("../../secret.txt")

    _make_remote(sandbox, build)
    dest = sandbox["tmp"] / "skills"

    result = _install(sandbox, "--dest", str(dest), "--path", "skills/leaky")

    assert result.returncode == 1
    assert "Unsupported symbolic link in skill" in result.stderr
    assert not (dest / "leaky").exists()


def test_symlinked_skill_path_is_rejected_with_the_real_error(sandbox):
    def build(repo: Path) -> None:
        _skill(repo, "real")
        (repo / "skills" / "alias").symlink_to("real")

    _make_remote(sandbox, build)
    dest = sandbox["tmp"] / "skills"

    result = _install(sandbox, "--dest", str(dest), "--path", "skills/alias")

    # Git's sparse checkout refuses the non-directory path before validation;
    # the SSH retry must surface that error, not its own leftover-directory one.
    assert result.returncode == 1
    assert "skills/alias" in result.stderr
    assert "already exists" not in result.stderr
    assert not (dest / "alias").exists()


def test_symlink_within_skill_to_a_file_is_copied(sandbox):
    def build(repo: Path) -> None:
        skill = _skill(repo, "linked")
        (skill / "real.md").write_text("content", encoding="utf-8")
        (skill / "alias.md").symlink_to("real.md")

    _make_remote(sandbox, build)
    dest = sandbox["tmp"] / "skills"

    result = _install(sandbox, "--dest", str(dest), "--path", "skills/linked")

    assert result.returncode == 0, result.stderr
    assert (dest / "linked" / "alias.md").read_text(encoding="utf-8") == "content"


# --- list-skills -----------------------------------------------------------


def _load_lister():
    sys.path.insert(0, str(SCRIPTS))
    try:
        spec = importlib.util.spec_from_file_location("list_skills", LIST)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(SCRIPTS))
    return module


@pytest.fixture
def lister(monkeypatch, tmp_path):
    module = _load_lister()
    listing = [
        {"name": "alpha", "type": "dir"},
        {"name": "beta", "type": "dir"},
        {"name": "README.md", "type": "file"},
    ]
    monkeypatch.setattr(module, "_request", lambda url: json.dumps(listing).encode())
    for var in ("CODEX_HOME", "CLAUDE_HOME"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    return module


def _listed(module, capsys, *args: str) -> dict[str, bool]:
    assert module.main(["--format", "json", *args]) == 0
    return {row["name"]: row["installed"] for row in json.loads(capsys.readouterr().out)}


def test_list_annotations_follow_the_selected_agent_home(lister, capsys, tmp_path, monkeypatch):
    claude_home = tmp_path / "claude"
    (claude_home / "skills" / "beta").mkdir(parents=True)
    monkeypatch.setenv("CLAUDE_HOME", str(claude_home))
    (tmp_path / "home" / ".codex" / "skills" / "alpha").mkdir(parents=True)

    assert _listed(lister, capsys, "--agent", "claude") == {"alpha": False, "beta": True}
    assert _listed(lister, capsys) == {"alpha": True, "beta": False}


def test_list_dest_overrides_agent_home(lister, capsys, tmp_path):
    dest = tmp_path / "custom"
    (dest / "alpha").mkdir(parents=True)

    assert _listed(lister, capsys, "--agent", "claude", "--dest", str(dest)) == {
        "alpha": True,
        "beta": False,
    }
