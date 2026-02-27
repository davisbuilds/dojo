---
description: Enable or disable hookify rules interactively
allowed-tools: ["Glob", "Read", "Edit", "AskUserQuestion"]
---

# Configure Hookify Rules

1. Glob for `**/hookify.*.local.md` in config directories
2. Read each, extract name and enabled state
3. AskUserQuestion (multiSelect) showing current state of each rule
4. Toggle `enabled: true/false` in selected files using Edit
5. Confirm changes
