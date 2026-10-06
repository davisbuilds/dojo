# Skill Standardization Policy

This reference defines default policy for `skill-standardizer`.

## Scope Model

- `canonical`: repository `skills/` directory (when discoverable)
- `global`: user-level agent skill directories
- `local`: project-specific skill directories
- `plugin-cache`: excluded by default; treated as external, mutable by plugin updates

## Drift Types

- `CONTENT_DRIFT`: same skill name, different content hash
- `DEPRECATED_SKILL_NAME`: installed skill uses an old name that should be replaced by the canonical name
- `GLOBAL_DRIFT`: global roots disagree without canonical alignment
- `GLOBAL_DUPLICATE_PRIMARY*`: secondary global copy should be linked to primary global source
- `GLOBAL_DUPLICATE_PREFERRED*`: secondary global copy should be linked to preferred existing global source
- `CODEX_AGENTS_DUPLICATE*`: Codex global copy should symlink to Agents source to avoid duplicate Codex catalog entries
- `LOCAL_DUPLICATE_GLOBAL`: local copy duplicates global and should be linked.
  A local entry that symlinks to the **global copy or straight to canonical**
  is already correct and is not reported — project roots link to canonical,
  because project scope exists for skills that are deliberately not global.
- `INVALID_SKILL_DIR`: directory under skills root missing `SKILL.md`
- `DANGLING_SKILL_LINK`: symlink under a skills root whose target no longer
  exists. Split from `INVALID_SKILL_DIR` because the repair differs — recreate
  the link, rather than author a missing file
- `MISSING_GLOBAL_MIRROR`: canonical skill missing in global (only when `--enforce-mirror`)
- `MISSING_GLOBAL_LINK`: canonical skill missing as a secondary global link (only when `--enforce-mirror` and link policy)
- `MISSING_CODEX_LINK_TO_AGENTS`: Codex global is missing a link to the Agents source
- `SELECTED_SKILL_NOT_FOUND`: a requested `--skill` name was not found in any scanned root

## Resolution Defaults

- Local policy default: `prefer-global-link`
- Global policy default: `prefer-primary-link`
  - Keep primary global root as the concrete copy
  - Link secondary global roots to the primary copy
  - Use `--global-policy mirror-copy` to keep independent copies in each global root
- Codex/Agents dedupe default: enabled (`--codex-agents-dedupe`)
  - Keep `~/.agents/skills` authoritative for Codex-facing catalogs
  - Re-link `~/.codex/skills/<skill>` to `~/.agents/skills/<skill>` to avoid duplicate entries in Codex
- Global precedence:
  1. `~/.agents/skills`
  2. `~/.codex/skills`
  3. `~/.claude/skills`
- Action mode default: dry run
- Apply mode stages replaced destinations until verification; retain only unique or uncertain copies after success
- Deprecated-name replacement default:
  - Back up the deprecated directory
  - Install the canonical replacement in the same root
  - Remove the old name after the replacement exists

## Deprecated Name Mappings

- `error-handling-review` -> `local-review`
- `type-design-review` -> `local-review`
- `agent-native-architecture` -> `agent-native-design`
- `json-canvas` -> `obsidian`
- `obsidian-markdown` -> `obsidian`
- `obsidian-bases` -> `obsidian`
- `obsidian-canvas` -> `obsidian`
- `imagegen` -> `gpt-imagen`

Treat the canonical replacement as the source of truth for future audits and sync operations.

## Intersection Mode (`--only-existing`)

When enabled, canonical sync only targets skills already present in the destination root. This prevents the standardizer from installing all canonical skills into globals — only the intersection of {canonical} ∩ {installed} is synced.

## Selected Skill Mode (`--skill`)

Use `--skill <name>` to restrict audit and sync planning to one skill; repeat the flag for a small set. This is the right mode when a newly authored canonical skill should be installed into global harness roots without widening the global catalog to every canonical skill.

Selected mode still treats a replacement and every deprecated name that resolves to it as one unit. For example, selecting `obsidian`, `obsidian-canvas`, or `json-canvas` keeps cleanup of all four former Obsidian names in scope.

Combine `--skill` with `--enforce-mirror` to install a selected canonical skill into globals. Combine it with `--only-existing` when the selected skill should only be repaired where it already exists.

## Topology Normalization (`--normalize-primary`)

When enabled, concrete skills found in secondary global roots are promoted to the primary global root and the secondary copies are replaced with symlinks. This handles the common case where skills were originally installed in `~/.codex/skills` or `~/.claude/skills` and need to be consolidated into `~/.agents/skills` as the single gold copy.

## Recovery and Retention

Git history is the recovery source for committed skills. Before replacing or
removing an installed entry, sync moves it to a timestamped run under
`--backup-root`. It verifies copies against the source snapshot (excluding the
normal generated-file copy exclusions), checks link targets, and confirms
removals. Failed applies preserve available rollback data; they do not restore
it automatically.

After a successful apply, a prior directory can be discarded only if its complete
tree matches a committed version of that skill in canonical Git history reachable
from `HEAD`. The proof includes file bytes, entry types, executable bits, relative
paths, and symlink text. Partial execute masks (such as mode `0645`) are
not Git-recoverable and remain preserved. It ignores nothing: even untracked cache files and empty
directories prevent a match. Git does not preserve timestamps, ownership, extended
attributes, or non-executable permission bits; these are not part of this skill
content recovery guarantee. Missing history or a failed proof means preserve.

Before discarding anything, write a mode-0600 JSON record under `records/` with
original destination, backup path, recovery coordinates, and installation evidence.
A backed-up symlink needs only its exact target text, never a copy of the target.
Cleanup of legacy runs records the backup path because their original destination
may no longer be known. Records describe recoverability, not a deletion completion
journal. Keep the referenced Git history available for later recovery.

Unknown copies have no automatic expiry. `cleanup_backups.py` inspects only
recognized standardizer run/entry names under an explicitly supplied root; it
never follows run or entry symlinks. Dry-run is default; `--apply` records proofs
before deletion and rechecks contents. Unrecognized or unmatched entries remain.
It does not manage unrelated backup directories. The count-based `--keep-backups`
option was removed in 2.0.0 because age does not establish recoverability.

## Safety Constraints

- No writes in dry-run mode
- No plugin cache writes unless explicitly included via flag
- Backup before replace/relink
- Keep-local exceptions supported via `--keep-local-skill`

## Suggested CI Usage

Audit drift in CI:

```bash
python3 <skill-dir>/scripts/audit.py --format text
```

Treat exit code `2` as drift detected.
