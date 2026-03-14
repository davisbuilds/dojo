---
date: 2026-03-13
topic: skill-standardization
type: runbook
device: mac-mini
status: completed
---

# Skill Standardization Runbook

This document describes what was done on the Mac mini to standardize global skills, and provides instructions for replicating the same topology on other devices (e.g., MacBook).

## Goal

Ensure all three global skill roots (`~/.agents/skills`, `~/.codex/skills`, `~/.claude/skills`) have identical skill sets with `~/.agents/skills` as the single gold copy, all content synced from canonical `dojo/skills`.

## What Was Done (Mac Mini, 2026-03-13)

### Phase 1: Normalize Global Topology

**Problem:** Skills were scattered across roots with inconsistent concrete/symlink topology. Some skills existed in `.codex` or `.claude` but not `.agents`. Duplicates existed (e.g., `skill-creator` in both `.codex/skills/` and `.codex/skills/.system/`).

**Actions:**

1. Backed up all three roots to `/tmp/skill-global-backup-*`.
2. Promoted 10 concrete skills from `.codex` (and `.codex/.system`) to `.agents`:
   - `create-cli`, `deep-research`, `first-principles`, `gemini-imagen`, `imagegen`, `playwright`, `screenshot`, `vercel-deploy`, `vercel-preview-logs`, `skill-creator`
3. Replaced all `.codex` entries with symlinks to `~/.agents/skills/<skill>`.
4. Replaced all `.claude` entries with symlinks to `~/.agents/skills/<skill>`.
5. Removed duplicate `.codex/skills/.system/skill-creator` (kept top-level symlink to `.agents`).
6. Added missing symlinks so all three roots mirror the same 26-skill set.

### Phase 2: Sync From Canonical Dojo

**Problem:** Installed skill content had drifted from canonical `dojo/skills`.

**Actions:**

1. For each skill in `.agents` that also exists in `dojo/skills` (23 skills), replaced the `.agents` copy with the canonical dojo version.
2. Three skills were not in dojo and left as-is: `imagegen`, `subagent-driven-development`, `json-canvas` (handled by rename).

### Phase 3: Rename json-canvas to obsidian-canvas

**Problem:** `json-canvas` was renamed to `obsidian-canvas` in dojo but globals still had the old name.

**Actions:**

1. Removed `.agents/skills/json-canvas`, copied `dojo/skills/obsidian-canvas` in its place.
2. Removed `json-canvas` symlinks from `.codex` and `.claude`, added `obsidian-canvas` symlinks.

### Phase 5: Rename imagegen to gpt-imagen

**Problem:** `imagegen` was renamed to `gpt-imagen` in dojo but globals still had the old name.

**Actions:**

1. Removed `.agents/skills/imagegen`, copied `dojo/skills/gpt-imagen` in its place.
2. Removed `imagegen` symlinks from `.codex` and `.claude`, added `gpt-imagen` symlinks.

### Phase 6: Remove subagent-driven-development

**Problem:** `subagent-driven-development` was not in dojo and its functionality is redundant — Claude Code's native Agent tool with `subagent_type` specialization already covers the orchestration pattern. The skill also referenced a non-existent "superpowers" skill ecosystem.

**Actions:**

1. Removed from all three global roots (`.agents`, `.codex`, `.claude`).

### Phase 7: Curate Global Skill Set

**Problem:** Some globally installed skills had low value-per-token (thin CLI wrappers, niche framework skills), while useful general-purpose skills were missing.

**Reasoning:** Context is sacred. Every globally loaded skill competes for context window space. The bar for global inclusion: broadly useful across projects, not easily replicated by native agent capabilities, and high signal-to-noise.

**Removed (4):**

- `vercel-react-native-skills` — niche; only relevant for React Native/Expo projects. Better as project-local.
- `vercel-composition-patterns` — narrow; compound component patterns useful but only during React component library work.
- `vercel-deploy` — thin wrapper around `vercel` CLI. Not worth permanent context.
- `vercel-preview-logs` — thin wrapper around `vercel logs`. Same reasoning.

**Added (3):**

- `test-strategy` — guides test architecture decisions (what to test, testing pyramid, mocking strategy). Broadly applicable.
- `local-review` — structured code review on working tree/staged/branch diffs without needing a PR. Fills a gap.
- `compact-session` — session handoff summaries when hitting context limits. Already used project-locally, valuable globally.

### Phase 8: Fix Broken Project Symlinks

**Problem:** `dojo/.claude/skills/{brainstorming,writing-plans}` had broken relative symlinks.

**Actions:**

1. Replaced with absolute symlinks to `/Users/dg-mac-mini/.agents/skills/<skill>`.

## Final State

- **`.agents/skills`**: 24 concrete skills (gold copy)
- **`.codex/skills`**: 24 symlinks to `.agents` (plus `.system/` with `skill-installer`, `slides`, `spreadsheets` — untouched)
- **`.claude/skills`**: 24 symlinks to `.agents`
- **All three roots have identical skill sets**
- **Zero broken symlinks across all roots**

### Complete Skill List (24)

All 24 skills are sourced from canonical `dojo/skills`.

```
audit-skill
brainstorming
compact-session
create-cli
deep-research
find-skills
first-principles
gemini-imagen
gpt-imagen
local-review
obsidian-bases
obsidian-canvas
obsidian-markdown
playwright
screenshot
secure-code
session-retro
skill-creator
skill-standardizer
test-strategy
vercel-react-best-practices
verify-before-complete
web-design-guidelines
writing-plans
```

### Skills Removed

- `subagent-driven-development` — redundant with Claude Code's native Agent tool; referenced non-existent "superpowers" skill ecosystem
- `imagegen` — renamed to `gpt-imagen` (canonical dojo copy)
- `json-canvas` — renamed to `obsidian-canvas` (canonical dojo copy)
- `vercel-react-native-skills` — niche; better as project-local
- `vercel-composition-patterns` — narrow; better as project-local
- `vercel-deploy` — thin CLI wrapper; not worth permanent context
- `vercel-preview-logs` — thin CLI wrapper; not worth permanent context

### .codex/.system Skills (untouched)

- `skill-installer`, `slides`, `spreadsheets` — Codex-specific system skills, not part of standardization

---

## Instructions for MacBook Replication

> **Important:** The MacBook reportedly has MORE skills installed than intended (all dojo skills were added). The goal is to match the Mac mini's topology, not blindly sync everything.

### Pre-Requisites

1. Pull latest dojo from origin (canonical content was updated in Tasks 1-3).
2. Back up all three global roots before any changes:
   ```bash
   BACKUP="/tmp/skill-global-backup-$(date +%Y%m%d-%H%M%S)"
   mkdir -p "$BACKUP"
   cp -a ~/.agents/skills "$BACKUP/agents-skills"
   cp -a ~/.codex/skills "$BACKUP/codex-skills"
   cp -a ~/.claude/skills "$BACKUP/claude-skills"
   ```

### Step 1: Audit Current MacBook State

```bash
# List what's in each root
for root in ~/.agents/skills ~/.codex/skills ~/.claude/skills; do
  echo "=== $root ==="
  ls -la "$root"/
done
```

### Step 2: Determine Target Skill Set

The Mac mini's canonical set is the 24 skills listed above. On the MacBook:

- **Keep** any of the 24 skills above that are already installed.
- **Remove** any skills NOT in the 24-skill list. This includes: skills added by mistake during the MacBook's initial run, `subagent-driven-development` (redundant), `imagegen` (renamed to `gpt-imagen`), `json-canvas` (renamed to `obsidian-canvas`), `vercel-react-native-skills`, `vercel-composition-patterns`, `vercel-deploy`, `vercel-preview-logs` (low value-per-token, better project-local).
- **Add** any of the 24 that are missing. Likely additions: `test-strategy`, `local-review`, `compact-session`.

### Step 3: Normalize Topology

For every skill that should exist:

1. Ensure a concrete copy exists in `~/.agents/skills/<skill>`.
2. Ensure `~/.codex/skills/<skill>` is a symlink: `../../.agents/skills/<skill>`.
3. Ensure `~/.claude/skills/<skill>` is a symlink: `../../.agents/skills/<skill>`.
4. Remove any duplicate entries (e.g., `.codex/.system/skill-creator` if a top-level symlink exists).

### Step 4: Sync Content From Dojo

For all 24 dojo-sourced skills:

```bash
CANONICAL="/path/to/dojo/skills"
AGENTS="$HOME/.agents/skills"

for skill in audit-skill brainstorming compact-session create-cli deep-research find-skills first-principles gemini-imagen gpt-imagen local-review obsidian-bases obsidian-canvas obsidian-markdown playwright screenshot secure-code session-retro skill-creator skill-standardizer test-strategy vercel-react-best-practices verify-before-complete web-design-guidelines writing-plans; do
  rm -rf "$AGENTS/$skill"
  cp -a "$CANONICAL/$skill" "$AGENTS/$skill"
done
```

### Step 5: Handle Renames and Removals

```bash
# Remove skills that are redundant or low value-per-token
for skill in subagent-driven-development vercel-react-native-skills vercel-composition-patterns vercel-deploy vercel-preview-logs; do
  rm -rf ~/.agents/skills/$skill
  rm -f ~/.codex/skills/$skill
  rm -f ~/.claude/skills/$skill
done

# json-canvas -> obsidian-canvas
rm -rf ~/.agents/skills/json-canvas
rm -f ~/.codex/skills/json-canvas
rm -f ~/.claude/skills/json-canvas
# obsidian-canvas should already be in .agents from Step 4
ln -sf ../../.agents/skills/obsidian-canvas ~/.codex/skills/obsidian-canvas
ln -sf ../../.agents/skills/obsidian-canvas ~/.claude/skills/obsidian-canvas

# imagegen -> gpt-imagen
rm -rf ~/.agents/skills/imagegen
rm -f ~/.codex/skills/imagegen
rm -f ~/.claude/skills/imagegen
# gpt-imagen should already be in .agents from Step 4
ln -sf ../../.agents/skills/gpt-imagen ~/.codex/skills/gpt-imagen
ln -sf ../../.agents/skills/gpt-imagen ~/.claude/skills/gpt-imagen
```

### Step 6: Fix Broken Symlinks

```bash
for root in ~/.agents/skills ~/.codex/skills ~/.claude/skills; do
  for entry in "$root"/*; do
    [ -L "$entry" ] || continue
    if [ ! -e "$entry" ]; then
      echo "BROKEN: $entry -> $(readlink "$entry")"
    fi
  done
done
```

### Step 7: Verify

```bash
# Counts should all be 24
for root in ~/.agents/skills ~/.codex/skills ~/.claude/skills; do
  echo "$root: $(ls -1 "$root" | grep -v '^\.' | wc -l | tr -d ' ') skills"
done

# Parity check
diff <(ls ~/.agents/skills | sort) <(ls ~/.codex/skills | grep -v '^\.' | sort)
diff <(ls ~/.agents/skills | sort) <(ls ~/.claude/skills | sort)

# No broken symlinks
for root in ~/.agents/skills ~/.codex/skills ~/.claude/skills; do
  for entry in "$root"/*; do
    [ -L "$entry" ] && [ ! -e "$entry" ] && echo "BROKEN: $entry"
  done
done
```
