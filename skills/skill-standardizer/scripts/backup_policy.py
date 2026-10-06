"""Content-based recovery proof. No Git writes and no symlink traversal."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import uuid


def snapshot(root: Path, algorithm: str = 'sha1', ignore=None) -> dict[str, str]:
    """Exact entries, including dotfiles, empty dirs, link text and executable bits."""
    entries = {}

    def visit(path, name):
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            data = os.fsencode(os.readlink(path))
            kind = '120000'
        elif stat.S_ISDIR(mode):
            if name:
                entries[name] = 'directory'
            children = list(path.iterdir())
            omitted = ignore(str(path), [p.name for p in children]) if ignore else set()
            for child in children:
                if child.name not in omitted:
                    visit(child, f'{name}/{child.name}' if name else child.name)
            return
        elif stat.S_ISREG(mode):
            data = path.read_bytes()
            execute_mask = mode & 0o111
            # Git stores only all-or-none executability. Keep partial masks
            # distinct for copy verification, and ineligible for Git recovery.
            kind = {0: '100644', 0o111: '100755'}.get(
                execute_mask, f'partial-execute-{execute_mask:03o}'
            )
        else:
            raise ValueError(f'Unsupported filesystem entry: {path}')
        blob = hashlib.new(algorithm, b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        entries[name] = f'{kind} {blob}'

    visit(root, '')
    return entries


def fingerprint(entries: dict) -> str:
    return hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest()


class GitRecovery:
    def __init__(self, canonical_root: str | None):
        self.repo = None
        self.prefix = None
        self.algorithm = 'sha1'
        self.cache = {}
        if not canonical_root:
            return
        try:
            root = Path(canonical_root).resolve()
            self.repo = Path(self.git_at(root, 'rev-parse', '--show-toplevel').strip().decode())
            self.prefix = root.relative_to(self.repo).as_posix()
            self.algorithm = self.git_at(self.repo, 'rev-parse', '--show-object-format').strip().decode()
        except (OSError, ValueError, subprocess.SubprocessError):
            self.repo = None

    @staticmethod
    def git_at(repo, *args):
        return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.DEVNULL)

    def candidates(self, name):
        if name in self.cache:
            return self.cache[name]
        found = {}
        if self.repo and re.fullmatch(r'[a-z0-9][a-z0-9-]*', name):
            relative = f'{self.prefix}/{name}' if self.prefix != '.' else name
            commits = self.git_at(self.repo, 'log', '--format=%H', '--full-history', 'HEAD', '--', relative).decode().splitlines()
            for commit in commits:
                entries = {}
                for item in self.git_at(self.repo, 'ls-tree', '-rz', commit, '--', relative).split(b'\0'):
                    if not item:
                        continue
                    meta, raw_path = item.split(b'\t', 1)
                    mode, kind, blob = meta.decode().split()
                    path = os.fsdecode(raw_path)
                    # A symlink/submodule at the skill root is not a directory snapshot.
                    if not path.startswith(relative + '/') or kind != 'blob':
                        entries = {}
                        break
                    short = path[len(relative) + 1:]
                    entries[short] = f'{mode} {blob}'
                    for parent in Path(short).parents:
                        if parent != Path('.'):
                            entries[parent.as_posix()] = 'directory'
                if entries:
                    digest = fingerprint(entries)
                    found.setdefault(digest, {'kind': 'git', 'repo': str(self.repo),
                                             'commit': commit, 'path': relative,
                                             'fingerprint': digest, 'algorithm': self.algorithm})
        self.cache[name] = found
        return found

    def prove(self, path: Path, name: str) -> dict | None:
        try:
            if path.is_symlink():
                return {'kind': 'symlink', 'target': os.readlink(path)}
            if not self.repo or not path.is_dir():
                return None
            return self.candidates(name).get(fingerprint(snapshot(path, self.algorithm)))
        except (OSError, ValueError, subprocess.SubprocessError):
            return None  # Unavailable or incomplete history is not a recovery proof.


def still_matches(path: Path, proof: dict) -> bool:
    try:
        if proof['kind'] == 'symlink':
            return path.is_symlink() and os.readlink(path) == proof['target']
        return not path.is_symlink() and fingerprint(snapshot(path, proof['algorithm'])) == proof['fingerprint']
    except (OSError, ValueError):
        return False


def save_record(backup_root: Path, data: dict) -> Path:
    records = backup_root / 'records'
    if records.is_symlink():
        raise ValueError('Recovery records directory must not be a symlink')
    records.mkdir(parents=True, exist_ok=True)
    name = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '-' + uuid.uuid4().hex[:8] + '.json'
    target = records / name
    with target.open('x', encoding='utf-8') as handle:
        os.chmod(target, 0o600)
        json.dump(data, handle, indent=2)
        handle.write('\n')
        handle.flush()
        os.fsync(handle.fileno())
    return target


def discard(path: Path) -> None:
    if path.is_symlink():
        path.unlink()
    else:
        shutil.rmtree(path)
    # Remove only the now-empty run directory, never neighboring contents.
    try:
        path.parent.rmdir()
    except OSError:
        pass


def cleanup_backups(backup_root: Path, canonical_root: str | None, apply: bool = False) -> dict:
    root = backup_root.expanduser().resolve()
    result = {'removed': [], 'retained': [], 'recoverable': [], 'errors': [], 'record_path': None}
    if not root.is_dir():
        return result
    recovery = GitRecovery(canonical_root)
    for run in sorted(root.iterdir()):
        # Include older manually suffixed standardizer runs, never follow run links.
        if run.is_symlink() or not run.is_dir() or not re.fullmatch(r'\d{8}-\d{6}(?:-[\w-]+)?', run.name):
            continue
        for entry in sorted(run.iterdir()):
            match = re.fullmatch(r'([a-z0-9][a-z0-9-]*)-[0-9a-f]{10}(?:-\d+)?', entry.name)
            proof = recovery.prove(entry, match[1]) if match else None
            item = {'backup': str(entry), 'recovery': proof}
            if proof:
                result['recoverable'].append(item)
            else:
                item['reason'] = 'No exact Git match or recognized backup name; preserved'
                result['retained'].append(item)
    if apply and result['recoverable']:
        try:
            result['record_path'] = str(save_record(root, {
                'operation': 'cleanup', 'canonical_root': canonical_root,
                'recoverable': result['recoverable'], 'retained': result['retained'],
            }))
            for item in result['recoverable']:
                path = Path(item['backup'])
                if path.parent.is_symlink() or not still_matches(path, item['recovery']):
                    result['retained'].append({**item, 'reason': 'Changed since inspection; preserved'})
                    continue
                discard(path)
                result['removed'].append(item)
        except (OSError, ValueError) as exc:
            result['errors'].append(str(exc))
    return result
