---
name: skill-standardizer
description: Use when skill copies drift across repositories or agent globals and you need canonicalization, drift auditing, and safe synchronization across local and global skills directories.
---

# Skill Standardizer

Standardizes and unifies skills across canonical, global, and local mirrors.

## What This Skill Solves

Use this skill when you see recurring problems like:
- multiple copies of the same skill with content drift
- platform-specific logic mixed into core `SKILL.md` behavior
- local project installs duplicating global installs
- uncertainty about which copy is canonical

This skill provides a deterministic workflow:
1. Discover roots and classify scope.
2. Audit byte-level and semantic drift.
3. Generate actions (dry run by default).
4. Apply safe synchronization with backups.
5. Re-audit and report final state.

## Canonical Model

Default policy:
- Repository `skills/` is canonical when discoverable.
- User global roots are mirrors:
  - `~/.agents/skills`
  - `~/.codex/skills`
  - `~/.claude/skills`
- Plugin caches (for example `~/.claude/plugins/cache`) are excluded by default.

If no canonical repo is discoverable from current working directory, operate in global/local audit mode and avoid canonical overwrite actions.

## Local vs Global Policy

Default local policy is `prefer-global-link`:
- If a skill exists both locally and globally, local copy should be replaced with a symlink to the preferred global copy.
- If local differs, back it up before relinking.
- Allow explicit keep-local exceptions when needed.

Preferred global precedence:
1. `~/.agents/skills`
2. `~/.codex/skills`
3. `~/.claude/skills`

## Scripts

Run from anywhere; scripts auto-discover repo root when possible.

- `scripts/discover.py`
  - Resolves canonical root, target roots, and discovered skills.
- `scripts/audit.py`
  - Detects drift and emits a JSON report plus readable summary.
  - Exit codes: `0` no drift, `2` drift found, `1` error.
- `scripts/sync.py`
  - Applies planned actions (copy/symlink) with backups.
  - Default is dry run; use `--apply` to execute.

## Standard Workflow

### 1) Discover

```bash
python3 skills/skill-standardizer/scripts/discover.py
```

### 2) Audit (dry run)

```bash
python3 skills/skill-standardizer/scripts/audit.py --format text
```

Optional JSON report:

```bash
python3 skills/skill-standardizer/scripts/audit.py \
  --format json \
  --report-out /tmp/skill-drift-report.json
```

### 3) Apply Synchronization

```bash
python3 skills/skill-standardizer/scripts/sync.py --apply
```

### 4) Verify

```bash
python3 skills/skill-standardizer/scripts/audit.py --format text
```

## Safety Rules

- Never mutate plugin cache directories unless explicitly included.
- Never overwrite without backup in apply mode.
- Always print resolved canonical and target roots before applying.
- If no canonical root is found, restrict apply actions to explicit local/global normalization.

## Notes On Portability

Keep core policy and decision logic model-agnostic in `SKILL.md` and scripts.
Platform-specific command syntax or orchestration belongs in optional wrappers or references.

See `references/policy.md` for policy details and tradeoffs.
