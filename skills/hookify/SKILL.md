---
name: hookify
description: Create and manage lightweight guard-rail hooks from markdown rule files. Harness-agnostic — works with Claude Code, Agents SDK, or any harness supporting stdin/stdout hooks. Use when the user says "hookify", "create a hook", "prevent this behavior", "add a guard rail", or wants to analyze conversation for unwanted patterns. Commands - /hookify, /hookify:list, /hookify:configure, /hookify:help.
---

# Hookify

Markdown-driven guard rails. Define rules as `.local.md` files, hookify enforces them at tool-use time.

## When To Use

Use this skill when:
- a user asks to add or tune guard rails/hooks
- recurring unsafe behavior should be warned or blocked
- you need markdown-managed policy rules across harnesses

## How It Works

1. Hook scripts (Python) run on PreToolUse, PostToolUse, Stop, UserPromptSubmit events
2. Scripts load `hookify.*.local.md` rules from config directories (`.claude/`, `.agents/`, `.codex/`, `.hookify/`)
3. Rules match via regex against tool inputs — matching rules warn or block the operation
4. Rules are read dynamically on every hook invocation — no restart needed

## Setup Per Harness

The hook scripts live in `scripts/hooks/`. Point your harness at them.

### Claude Code (`.claude/settings.json`)

```json
{
  "hooks": {
    "PreToolUse": [{ "hooks": [{ "type": "command", "command": "python3 path/to/skills/hookify/scripts/hooks/pretooluse.py" }] }],
    "PostToolUse": [{ "hooks": [{ "type": "command", "command": "python3 path/to/skills/hookify/scripts/hooks/posttooluse.py" }] }],
    "Stop": [{ "hooks": [{ "type": "command", "command": "python3 path/to/skills/hookify/scripts/hooks/stop.py" }] }],
    "UserPromptSubmit": [{ "hooks": [{ "type": "command", "command": "python3 path/to/skills/hookify/scripts/hooks/userpromptsubmit.py" }] }]
  }
}
```

### Agents SDK (`.agents/settings.json`)

Same format as Claude Code — the Agents SDK mirrors the hook schema.

### Other Harnesses

Any harness that pipes JSON to stdin and reads JSON from stdout can use the hook scripts directly:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /"}}' | python3 scripts/hooks/pretooluse.py
```

Set `HOOKIFY_HARNESS=generic` (or any non-claude value) to get plain JSON output instead of Claude-specific fields.

### Standalone / No Hook Support

For harnesses without hook events, include a reminder in the agent's system prompt or AGENTS.md to check rules manually before destructive operations.

## Commands

| Command | Description |
|---------|-------------|
| `/hookify [behavior]` | Create rules from instructions or conversation analysis |
| `/hookify:list` | List all configured rules |
| `/hookify:configure` | Toggle rules on/off interactively |
| `/hookify:help` | Show help and rule format reference |

## Rule Format

See `references/writing-rules.md` for the full spec. Minimum viable rule:

```markdown
---
name: warn-dangerous-rm
enabled: true
event: bash
pattern: rm\s+-rf
---

Dangerous rm command detected. Verify the path.
```

## Examples

See `assets/examples/` for ready-to-copy rule files.

## Output Requirements

Return:
- created/updated rule filenames
- event + pattern + action summary per rule
- minimal activation instructions for the target harness

## Boundaries

- Do not deploy blocking rules without clearly communicating impact.
- Do not add over-broad regex patterns that trigger on common safe actions.
- Do not claim enforcement is active unless hook wiring is configured.

## Verification

Before completion:
- validate rule frontmatter and required fields
- run at least one representative test input per new/edited rule
- confirm the configured harness path references the expected hook script
