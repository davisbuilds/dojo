## 1.3.0 - 2026-08-14

- Report a dangling symlink as DANGLING_SKILL_LINK rather than a missing SKILL.md

## 1.2.0 - 2026-08-12

- Detect STALE_SECONDARY_GLOBAL and repair it by removing the entry (with backup) instead of
  relinking to a source that no longer exists; stop resolving action destinations so an entry
  that is a symlink is acted on rather than its target. Adds backup retention: `--keep-backups`
  (default 10, `0` keeps everything) prunes old run directories after a successful apply, since
  nothing else aged them out and they accumulate one directory per run.

## 1.1.0 - 2026-07-16

- Add built-in KNOWN_NON_SKILL_DIRS allowlist, keyed by root kind; exempts codex-primary-runtime in ~/.codex/skills.

## 1.0.1 - 2026-07-16

- Fix audit exit code to track real drift: 2 only when actions are planned, 1 on error-severity issues, 0 otherwise. Previously any warning forced exit 2, contradicting the documented contract.
