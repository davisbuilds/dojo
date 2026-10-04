## 1.3.7 - 2026-10-04

- Retire deprecated symlinks themselves without following or moving their targets; cover primary-copy and secondary-link migrations.

## 1.3.6 - 2026-10-03

- Map obsidian-markdown, obsidian-bases, obsidian-canvas, and json-canvas to the consolidated obsidian skill.
- Selected mode treats every deprecated name that resolves to the same replacement as one unit, so selecting one alias keeps its sibling aliases' cleanup in scope.

## 1.3.5 - 2026-10-02

- Migrate both retired specialist review names to local-review with backups; cover consolidation when the replacement is already installed.
- Preserve every deprecated-name cleanup when multiple aliases share one replacement write; migrate both review lenses in one apply even when local-review is absent.

## 1.3.4 - 2026-10-02

- Register `agent-native-architecture` → `agent-native-design` so existing installs migrate with backups, including when either name is selected.
- Cover migration across all three global roots, preservation of old copies, selection boundaries, and convergence to the normal link policy.

## 1.3.3 - 2026-10-01

- Exempt Claude Code's account-synced skills cache (`synced` in the Claude global root) from invalid-directory reports.
- Never plan a sync action onto an exempt directory; report `RESERVED_NAME_COLLISION` instead.

## 1.3.2 - 2026-08-22

- Generalize dangling-link provenance so public source does not depend on a private consumer repository.

## 1.3.1 - 2026-08-14

- Anchor runnable script commands to <skill-dir> so they resolve outside a dojo checkout

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
