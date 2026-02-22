# Skill Standardization Policy

This reference defines default policy for `skill-standardizer`.

## Scope Model

- `canonical`: repository `skills/` directory (when discoverable)
- `global`: user-level agent skill directories
- `local`: project-specific skill directories
- `plugin-cache`: excluded by default; treated as external, mutable by plugin updates

## Drift Types

- `CONTENT_DRIFT`: same skill name, different content hash
- `GLOBAL_DRIFT`: global roots disagree without canonical alignment
- `LOCAL_DUPLICATE_GLOBAL`: local copy duplicates global and should be linked
- `INVALID_SKILL_DIR`: directory under skills root missing `SKILL.md`
- `MISSING_GLOBAL_MIRROR`: canonical skill missing in global (only when `--enforce-mirror`)

## Resolution Defaults

- Local policy default: `prefer-global-link`
- Global precedence:
  1. `~/.agents/skills`
  2. `~/.codex/skills`
  3. `~/.claude/skills`
- Action mode default: dry run
- Apply mode always backs up replaced destinations

## Safety Constraints

- No writes in dry-run mode
- No plugin cache writes unless explicitly included via flag
- Backup before replace/relink
- Keep-local exceptions supported via `--keep-local-skill`

## Suggested CI Usage

Audit drift in CI:

```bash
python3 skills/skill-standardizer/scripts/audit.py --format text
```

Treat exit code `2` as drift detected.
