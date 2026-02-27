---
description: List all configured hookify rules
allowed-tools: ["Glob", "Read"]
---

# List Hookify Rules

1. Glob for `**/hookify.*.local.md` in `.claude/`, `.agents/`, `.codex/`, `.hookify/`
2. Read each file, extract frontmatter
3. Present as table: Name | Enabled | Event | Pattern | Action | File
4. Show total count (enabled vs disabled)
