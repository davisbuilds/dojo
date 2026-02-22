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
python3 skills/skill-standardizer/scripts/audit.py --format text
```

3. If user confirms apply, synchronize:

```bash
python3 skills/skill-standardizer/scripts/sync.py --apply
```

4. Re-audit and summarize final status.

Default local policy is `prefer-global-link`.
Use `--keep-local-skill <name>` for local-only exceptions.
