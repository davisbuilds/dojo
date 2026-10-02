"""Review packets must describe the requested Git surface, not a nearby one."""
from pathlib import Path
import subprocess

COLLECTOR = Path(__file__).resolve().parents[1] / 'skills/local-review/scripts/collect_review_context.sh'


def git(repo, *args):
    return subprocess.run(['git', *args], cwd=repo, check=True, capture_output=True, text=True).stdout


def repository(tmp_path):
    git(tmp_path, 'init', '-b', 'main')
    git(tmp_path, 'config', 'user.email', 'test@example.com')
    git(tmp_path, 'config', 'user.name', 'Test')
    (tmp_path / 'value.txt').write_text('original\n')
    git(tmp_path, 'add', 'value.txt')
    git(tmp_path, '-c', 'commit.gpgsign=false', 'commit', '-m', 'baseline')
    return tmp_path


def collect(repo, mode):
    return subprocess.run(['bash', str(COLLECTOR), '--mode', mode], cwd=repo,
                          check=True, capture_output=True, text=True).stdout


def test_working_review_includes_staged_unstaged_and_untracked(tmp_path):
    repo = repository(tmp_path)
    (repo / 'value.txt').write_text('staged_change\n')
    git(repo, 'add', 'value.txt')
    (repo / 'other.txt').write_text('untracked_change\n')
    output = collect(repo, 'working')
    assert '+staged_change' in output
    assert '+untracked_change' in output
    (repo / 'value.txt').write_text('TODO working_change\n')
    assert '+TODO working_change' in collect(repo, 'working')


def test_deletion_only_is_a_reviewable_change(tmp_path):
    repo = repository(tmp_path)
    (repo / 'value.txt').unlink()
    output = collect(repo, 'working')
    assert 'No changes detected' not in output
    assert '-original' in output
    git(repo, 'add', 'value.txt')
    assert '-original' in collect(repo, 'staged')


def test_staged_review_does_not_substitute_working_contents(tmp_path):
    repo = repository(tmp_path)
    (repo / 'value.txt').write_text('staged_change\n')
    git(repo, 'add', 'value.txt')
    (repo / 'value.txt').write_text('TODO working_change\n')
    output = collect(repo, 'staged')
    assert '+staged_change' in output
    assert 'working_change' not in output


def test_branch_deletion_uses_merge_base_and_ignores_working_files(tmp_path):
    repo = repository(tmp_path)
    git(repo, 'switch', '-c', 'feature')
    git(repo, 'rm', 'value.txt')
    git(repo, '-c', 'commit.gpgsign=false', 'commit', '-m', 'delete value')
    (repo / 'value.txt').write_text('untracked_working_value\n')
    output = collect(repo, 'branch')
    assert '-original' in output
    assert 'untracked_working_value' not in output
