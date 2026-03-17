# Adapter Patterns

These patterns are optional. The core `self-improve` workflow should work in any filesystem-oriented harness without them.

## Portable Core

The portable contract is:

1. Write structured records to a dedicated store.
2. Compact the store before loading it into context.
3. Generate promotion proposals before lasting changes.
4. Extract draft skills from repeated patterns instead of mutating live skills immediately.

## Optional Adapters

### Workspace Memory File

If a harness supports a durable memory file, treat `promote-memory-note` as a separate approval step that copies proposal-approved learnings into that file.

### Reminder Hook

If a harness supports stop hooks or reminders, prompt the agent to compact or propose promotion after a session that produced repeated mistakes or reusable fixes. Do not auto-promote.

### Scheduled Compaction

If a harness can run periodic jobs, compact the inbox into `summaries/latest.md` on a cadence. Keep raw inbox files available for audit.

## Platform Notes

Codex, Claude Code, OpenClaw, and other harnesses may expose different memory surfaces or hook systems. Keep those details in harness-local docs or examples, not in the core `SKILL.md`.
