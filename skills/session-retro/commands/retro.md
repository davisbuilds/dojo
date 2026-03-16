---
name: retro
description: Capture non-obvious session learnings into existing project reference docs using the session-retro skill.
argument-hint: "[optional scope hint]"
allowed-tools: [Read, Edit, Write]
---

# Retro

Load `session-retro` and apply its process to append high-signal learnings from the current session.

## Behavior

1. Inventory the existing reference docs in the current project:
   - Root docs: prefer `AGENTS.md`, then `CLAUDE.md`, then `README.md` when they fit the learning.
   - Canonical docs: use existing `docs/system/*` and `docs/project/*` reference files when they are a better fit.
2. Propose candidate learnings from the current session, then filter to non-obvious items that save future agents meaningful time.
3. Route each learning to exactly one canonical doc and avoid duplicate entries across multiple files.
4. Prefer append-only additions, but allow the smallest in-place structured edit when append-only would duplicate or stale a canonical ref doc.
5. Present the exact grouped diff and wait for user approval.
6. After approval, apply only the narrow approved edits, matching existing formatting.

## Rules

- Update only docs that already exist.
- One learning, one home.
- Prefer append-only; use in-place edits only when clearly warranted.
- Maximum 5 learnings in one run.
- Maximum 3 files in one run unless the user asks for more.
- Keep entries concrete and actionable.
