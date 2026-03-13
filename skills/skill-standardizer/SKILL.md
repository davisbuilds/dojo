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
3. Generate actions (dry run by default), including deprecated-name replacement when configured by policy.
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

Default global policy is `prefer-primary-link`:
- Keep a concrete copy in the primary global root (`~/.agents/skills` by default).
- Keep secondary globals (`~/.codex/skills`, `~/.claude/skills`) as symlinks to that primary copy.
- This avoids duplicate skill entries in clients that aggregate multiple global roots.
- Use `--global-policy mirror-copy` when fully independent per-global copies are required.

Codex/Agents dedupe guard (enabled by default):
- `--codex-agents-dedupe` keeps `~/.agents/skills` authoritative for Codex-facing catalogs.
- When enabled, `~/.codex/skills/<skill>` is relinked to `~/.agents/skills/<skill>` to avoid duplicate entries in Codex dropdowns.
- Use `--no-codex-agents-dedupe` only if you explicitly need separate Codex copies.

Preferred global precedence:
1. `~/.agents/skills`
2. `~/.codex/skills`
3. `~/.claude/skills`

## Rename Policy

Deprecated skill names can be mapped to canonical replacements.

Current built-in mapping:
- `json-canvas` -> `obsidian-canvas`

When a deprecated skill name is found:
- audit should report it explicitly instead of treating it as an unrelated extra directory
- sync should back up the deprecated copy, install the canonical replacement in the same root, and remove the old name
- secondary globals and local duplicates should still follow the normal link/copy policy for the replacement skill

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
python3 skills/skill-standardizer/scripts/audit.py \
  --global-policy prefer-primary-link \
  --format text
```

Optional JSON report:

```bash
python3 skills/skill-standardizer/scripts/audit.py \
  --format json \
  --report-out /tmp/skill-drift-report.json
```

### 3) Apply Synchronization

```bash
python3 skills/skill-standardizer/scripts/sync.py \
  --global-policy prefer-primary-link \
  --apply
```

### 4) Verify

```bash
python3 skills/skill-standardizer/scripts/audit.py \
  --global-policy prefer-primary-link \
  --format text
```

## Fix Duplicate Global Skill Entries

When a skill appears multiple times in a client catalog, normalize globals to primary+links:

```bash
python3 skills/skill-standardizer/scripts/sync.py \
  --global-policy prefer-primary-link \
  --enforce-mirror \
  --apply
```

For targeted fixes, provide a scoped canonical root containing only the affected skills.

## Safety Rules

- Never mutate plugin cache directories unless explicitly included.
- Never overwrite without backup in apply mode.
- Never remove a deprecated skill name without creating or confirming the canonical replacement in that root.
- Always print resolved canonical and target roots before applying.
- If no canonical root is found, restrict apply actions to explicit local/global normalization.

## Notes On Portability

Keep core policy and decision logic model-agnostic in `SKILL.md` and scripts.
Platform-specific command syntax or orchestration belongs in optional wrappers or references.

See `references/policy.md` for policy details and tradeoffs.

## When To Use

- When skill copies drift across repository, global, and local directories
- When duplicate skill entries appear in agent client catalogs
- When uncertainty exists about which copy of a skill is canonical
- After adding or updating skills that exist in multiple roots

## Output

- A drift audit report (text or JSON) listing all discovered skills and their sync status
- Backup copies of any files replaced during synchronization
- Symlinks replacing duplicate copies to point at the canonical or primary source

## Verification

- Post-sync audit exits with code `0` (no drift remaining)
- All symlinks resolve to valid targets
- No plugin cache directories were mutated unless explicitly included
- Canonical and target roots are printed before any apply operation
