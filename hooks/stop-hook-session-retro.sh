#!/usr/bin/env bash
# Stop hook: remind agent to capture a session retro before ending.
# Non-blocking — prints a nudge to stderr, always exits 0.

echo "Reminder: if this session produced non-obvious learnings, run /retro to update the project's ref docs (AGENTS.md / CLAUDE.md) before ending." >&2
exit 0
