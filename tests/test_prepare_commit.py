"""Exercise the publication inventory against real repositories, without GitHub."""
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/gh-commit-push-pr/scripts/prepare_commit.sh'


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()


@pytest.fixture
def repo(tmp_path):
    repo = tmp_path / 'repo with spaces'
    repo.mkdir()
    git(repo, 'init', '-b', 'main')
    git(repo, 'config', 'user.name', 'Fixture')
    git(repo, 'config', 'user.email', 'fixture@example.invalid')
    git(repo, '-c', 'commit.gpgsign=false', 'commit', '--allow-empty', '-m', 'base fixture')
    git(repo, 'switch', '-c', 'feature')
    return repo


def report(repo, *args):
    return subprocess.run(['bash', str(SCRIPT), str(repo), *args], text=True, capture_output=True)


def test_clean_worktree_exposes_committed_work_without_mutation(repo):
    (repo / 'file with spaces.txt').write_text('change\n')
    git(repo, 'add', '.')
    git(repo, '-c', 'commit.gpgsign=false', 'commit', '-m', 'ready for publication')
    before = git(repo, 'rev-parse', 'HEAD'), git(repo, 'status', '--porcelain')
    result = report(repo, 'main')
    assert result.returncode == 0, result.stderr
    assert 'ready for publication' in result.stdout
    assert 'file with spaces.txt' in result.stdout
    assert before == (git(repo, 'rev-parse', 'HEAD'), git(repo, 'status', '--porcelain'))


def test_detached_head_is_identified(repo):
    git(repo, 'checkout', '--detach')
    result = report(repo, 'main')
    assert result.returncode == 0, result.stderr
    assert 'DETACHED' in result.stdout


def test_no_base_is_explicit_and_dirty_inventory_preserves_paths(repo):
    (repo / 'new file.txt').write_text('untracked\n')
    result = report(repo)
    assert result.returncode == 0, result.stderr
    assert 'base not supplied' in result.stdout.lower()
    assert 'new file.txt' in result.stdout
    assert 'upstream not configured' in result.stdout.lower()
    assert git(repo, 'status', '--porcelain') == '?? "new file.txt"'


def test_invalid_base_fails_instead_of_reporting_no_work(repo):
    result = report(repo, 'missing-base')
    assert result.returncode != 0
    assert 'missing-base' in result.stderr


def test_upstream_range_distinguishes_unpushed_commit(repo):
    git(repo, 'branch', '--set-upstream-to=main')
    git(repo, '-c', 'commit.gpgsign=false', 'commit', '--allow-empty', '-m', 'unpushed fixture')
    result = report(repo, 'main')
    assert result.returncode == 0, result.stderr
    assert 'Upstream: main' in result.stdout
    assert 'Ahead: 1; behind: 0' in result.stdout


def test_staged_and_unstaged_changes_are_not_rearranged(repo):
    item = repo / 'two versions.txt'
    item.write_text('staged\n')
    git(repo, 'add', '.')
    item.write_text('unstaged\n')
    before = git(repo, 'diff', '--cached'), git(repo, 'diff')
    result = report(repo, 'main')
    assert result.returncode == 0, result.stderr
    assert 'AM "two versions.txt"' in result.stdout
    assert before == (git(repo, 'diff', '--cached'), git(repo, 'diff'))


def test_unborn_repository_reports_no_commit_ranges(tmp_path):
    git(tmp_path, 'init', '-b', 'main')
    result = report(tmp_path)
    assert result.returncode == 0, result.stderr
    assert 'No commits yet' in result.stdout
    assert git(tmp_path, 'status', '--porcelain') == ''


def test_non_repository_is_an_error(tmp_path):
    result = report(tmp_path)
    assert result.returncode != 0
    assert 'not a git repository' in result.stderr
