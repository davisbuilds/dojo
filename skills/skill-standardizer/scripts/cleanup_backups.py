#!/usr/bin/env python3
"""Remove only provably recoverable standardizer backups; dry-run by default."""
import argparse
import json
from pathlib import Path

from backup_policy import cleanup_backups


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backup-root', required=True, help='Explicit standardizer backup directory')
    parser.add_argument('--canonical-root', help='Canonical skills directory in a Git checkout')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    result = cleanup_backups(Path(args.backup_root), args.canonical_root, args.apply)
    print(json.dumps(result, indent=2))
    return 1 if result['errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
