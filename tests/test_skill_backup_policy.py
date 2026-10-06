"""Recovery policy uses actual Git history and filesystem replacements."""
from pathlib import Path
import json
import shutil
import subprocess
import sys

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills/skill-standardizer/scripts'
sys.path.insert(0, str(SCRIPTS))
import skill_standardizer_lib as lib


def git(repo, *args):
    return subprocess.check_output(
        ['git', '-C', str(repo), '-c', 'core.hooksPath=/dev/null',
         '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test', *args],
        text=True,
    ).strip()


@pytest.fixture
def history(tmp_path):
    repo = tmp_path / 'repo'
    repo.mkdir()
    git(repo, 'init', '-q')
    skill = repo / 'skills/alpha'
    skill.mkdir(parents=True)
    (skill / 'SKILL.md').write_text('old contents\n')
    git(repo, 'add', 'skills/alpha/SKILL.md')
    git(repo, 'commit', '-qm', 'Old version')
    old = git(repo, 'rev-parse', 'HEAD')
    installed = tmp_path / 'installed/alpha'
    shutil.copytree(skill, installed)
    (skill / 'SKILL.md').write_text('new contents\n')
    git(repo, 'add', 'skills/alpha/SKILL.md')
    git(repo, 'commit', '-qm', 'New version')
    report = {'canonical_root': str(repo / 'skills'), 'actions': [
        {'action': 'sync_copy', 'skill': 'alpha', 'source': str(skill), 'dest': str(installed)},
    ]}
    return repo, skill, installed, report, old


def test_git_recoverable_copy_is_discarded_after_verified_install(history, tmp_path):
    repo, source, installed, report, old = history
    result = lib.apply_actions(report, True, str(tmp_path / 'backups'))
    assert not result['errors']
    assert (installed / 'SKILL.md').read_text() == 'new contents\n'
    assert result['backups'] == []
    receipt = json.loads(Path(result['record_path']).read_text())
    recovery = receipt['backups'][0]['recovery']
    assert recovery['commit'] == old
    assert recovery['path'] == 'skills/alpha'
    assert receipt['installations'][0]['source_recovery']['commit'] == git(repo, 'rev-parse', 'HEAD')
    assert not Path(receipt['backups'][0]['backup']).exists()


@pytest.mark.parametrize('extra', ['local-note.md', '.private-note', '__pycache__/untracked.pyc'])
def test_untracked_contents_are_preserved(history, tmp_path, extra):
    _, _, installed, report, _ = history
    note = installed / extra
    note.parent.mkdir(parents=True, exist_ok=True)
    note.write_text('not in Git')
    result = lib.apply_actions(report, True, str(tmp_path / 'backups'))
    assert not result['errors']
    assert len(result['backups']) == 1
    assert (Path(result['backups'][0]['backup']) / extra).read_text() == 'not in Git'


def test_failed_verification_keeps_rollback(history, tmp_path, monkeypatch):
    _, _, installed, report, _ = history
    def broken_copy(source, dest):
        dest.mkdir(parents=True)
        (dest / 'SKILL.md').write_text('partial copy')
    monkeypatch.setattr(lib, '_replace_with_copy', broken_copy)
    result = lib.apply_actions(report, True, str(tmp_path / 'backups'))
    assert result['errors']
    assert (Path(result['backups'][0]['backup']) / 'SKILL.md').read_text() == 'old contents\n'


def test_receipt_failure_preserves_rollback(history, tmp_path):
    _, _, _, report, _ = history
    backups = tmp_path / 'backups'
    backups.mkdir()
    (backups / 'records').write_text('cannot create receipt directory here')
    result = lib.apply_actions(report, True, str(backups))
    assert result['errors']
    assert (Path(result['backups'][0]['backup']) / 'SKILL.md').exists()


def test_dry_run_never_creates_recovery_files(history, tmp_path):
    _, _, installed, report, _ = history
    backups = tmp_path / 'backups'
    result = lib.apply_actions(report, False, str(backups))
    assert not backups.exists()
    assert (installed / 'SKILL.md').read_text() == 'old contents\n'
    assert not result['applied']


def test_cleanup_discards_only_recoverable_entries(history, tmp_path):
    from backup_policy import cleanup_backups
    repo, _, installed, _, old = history
    root = tmp_path / 'backups'
    run = root / '20261006-120000'
    exact = run / 'alpha-0123456789'
    unknown = run / 'alpha-aaaaaaaaaa'
    shutil.copytree(installed, exact)
    shutil.copytree(installed, unknown)
    (unknown / '.local-note').write_text('unique')
    external = tmp_path / 'outside'
    external.mkdir()
    (external / 'keep').write_text('untouched')
    link = run / 'alpha-bbbbbbbbbb'
    link.symlink_to(external, target_is_directory=True)
    (root / '20261006-130000').symlink_to(external, target_is_directory=True)
    dry = cleanup_backups(root, str(repo / 'skills'))
    assert exact.exists() and link.is_symlink()
    assert not (root / 'records').exists()
    result = cleanup_backups(root, str(repo / 'skills'), apply=True)
    assert not exact.exists()
    assert not link.is_symlink()
    assert (unknown / '.local-note').read_text() == 'unique'
    assert (external / 'keep').read_text() == 'untouched'
    assert len(result['removed']) == 2
    record = json.loads(Path(result['record_path']).read_text())
    assert record['recoverable'][0]['recovery']['kind'] in {'git', 'symlink'}
    assert any(x['recovery'].get('commit') == old for x in record['recoverable'])


@pytest.mark.parametrize('change', ['executable', 'empty-dir', 'internal-link'])
def test_git_proof_detects_more_than_file_text(history, change, tmp_path):
    from backup_policy import GitRecovery
    repo, _, installed, _, _ = history
    if change == 'executable':
        (installed / 'SKILL.md').chmod(0o755)
    elif change == 'empty-dir':
        (installed / 'empty').mkdir()
    else:
        (installed / 'SKILL.md').unlink()
        (installed / 'SKILL.md').symlink_to(tmp_path / 'missing')
    assert GitRecovery(str(repo / 'skills')).prove(installed, 'alpha') is None


def test_no_git_means_preserve(history, tmp_path):
    _, source, installed, report, _ = history
    report['canonical_root'] = str(tmp_path / 'no-git')
    result = lib.apply_actions(report, True, str(tmp_path / 'backups'))
    assert not result['errors']
    assert len(result['backups']) == 1
    assert (Path(result['backups'][0]['backup']) / 'SKILL.md').read_text() == 'old contents\n'


def test_cleanup_record_failure_prevents_deletion(history, tmp_path):
    from backup_policy import cleanup_backups
    repo, _, installed, _, _ = history
    root = tmp_path / 'backups'
    exact = root / '20261006-120000/alpha-0123456789'
    shutil.copytree(installed, exact)
    (root / 'records').write_text('blocked')
    result = cleanup_backups(root, str(repo / 'skills'), apply=True)
    assert result['errors'] and not result['removed']
    assert (exact / 'SKILL.md').read_text() == 'old contents\n'


def test_cleanup_rechecks_after_recording(history, tmp_path, monkeypatch):
    import backup_policy
    repo, _, installed, _, _ = history
    root = tmp_path / 'backups'
    exact = root / '20261006-120000/alpha-0123456789'
    shutil.copytree(installed, exact)
    save = backup_policy.save_record
    def changed_during_recording(*args):
        record = save(*args)
        (exact / 'SKILL.md').write_text('concurrent edit')
        return record
    monkeypatch.setattr(backup_policy, 'save_record', changed_during_recording)
    result = backup_policy.cleanup_backups(root, str(repo / 'skills'), apply=True)
    assert not result['errors'] and not result['removed']
    assert (exact / 'SKILL.md').read_text() == 'concurrent edit'
    assert 'Changed' in result['retained'][0]['reason']


def test_git_proof_matches_internal_link_text_without_following_it(history, tmp_path):
    from backup_policy import GitRecovery
    repo, source, _, _, _ = history
    (source / 'missing-link').symlink_to('unavailable-target')
    git(repo, 'add', 'skills/alpha/missing-link')
    git(repo, 'commit', '-qm', 'Track link')
    copy = tmp_path / 'copy'
    shutil.copytree(source, copy, symlinks=True)
    proof = GitRecovery(str(repo / 'skills')).prove(copy, 'alpha')
    assert proof and proof['commit'] == git(repo, 'rev-parse', 'HEAD')


@pytest.mark.parametrize('mode', [0o645, 0o654, 0o744])
def test_partial_execute_masks_are_not_git_recoverable(history, mode):
    from backup_policy import GitRecovery
    repo, source, installed, _, _ = history
    (source / 'SKILL.md').chmod(0o755)
    git(repo, 'add', 'skills/alpha/SKILL.md')
    git(repo, 'commit', '-qm', 'Executable skill file')
    shutil.rmtree(installed)
    shutil.copytree(source, installed)
    (installed / 'SKILL.md').chmod(mode)
    assert GitRecovery(str(repo / 'skills')).prove(installed, 'alpha') is None
