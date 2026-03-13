---
name: standardize-skills
description: Audit and standardize skill copies across canonical, global, and local directories with backup-safe synchronization.
argument-hint: "[optional roots or policy flags]"
---

# Standardize Skills

Load `skill-standardizer` and run this sequence:

1. Discover roots:

```bash
python3 skills/skill-standardizer/scripts/discover.py
```

2. Audit drift:

```bash
python3 skills/skill-standardizer/scripts/audit.py \
  --enforce-mirror \
  --global-policy prefer-primary-link \
  --format text
```

3. If user confirms apply, synchronize:

```bash
python3 skills/skill-standardizer/scripts/sync.py \
  --enforce-mirror \
  --global-policy prefer-primary-link \
  --apply
```

4. Re-audit and summarize final status.

Default local policy is `prefer-global-link`.
Default global policy is `prefer-primary-link` to avoid duplicate catalog entries across aggregated global roots.
Codex/Agents dedupe is enabled by default (`--codex-agents-dedupe`) so `~/.agents/skills` remains authoritative and `~/.codex/skills` is relinked to avoid Codex duplicate entries.
Deprecated-name replacement is policy-driven; for example `json-canvas` is replaced by `obsidian-canvas`.
Use `--keep-local-skill <name>` for local-only exceptions.
