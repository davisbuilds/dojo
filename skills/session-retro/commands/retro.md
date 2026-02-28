---
name: retro
description: Capture non-obvious session learnings into AGENTS.md or CLAUDE.md using the session-retro skill.
argument-hint: "[optional scope hint]"
allowed-tools: [Read, Edit, Write]
---

# Retro

Load `session-retro` and apply its process to append high-signal learnings from the current session.

## Behavior

1. Identify the project reference doc at repo root:
   - Prefer `AGENTS.md` when both `AGENTS.md` and `CLAUDE.md` exist.
2. Propose candidate learnings from the current session, then filter to non-obvious items that save future agents meaningful time.
3. Map each learning to the correct section (gotchas, commands/features, dependencies/setup).
4. Present the exact one-line additions as a diff and wait for user approval.
5. After approval, append only (no rewrites/reordering), matching existing formatting.

## Rules

- One line per learning.
- Append-only edits; do not modify existing lines.
- Maximum 5 learnings in one run.
- Keep entries concrete and actionable.
