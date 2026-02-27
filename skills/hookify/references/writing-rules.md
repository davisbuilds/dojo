# Writing Hookify Rules

## Rule File Format

Rules are markdown files with YAML frontmatter stored as `hookify.{name}.local.md` in a config directory (`.claude/`, `.agents/`, `.codex/`, or `.hookify/`).

```markdown
---
name: rule-identifier
enabled: true
event: bash|file|stop|prompt|all
pattern: regex-pattern
action: warn|block
---

Message shown to agent when rule triggers.
```

## Frontmatter Fields

| Field | Required | Values | Default |
|-------|----------|--------|---------|
| name | yes | kebab-case identifier | — |
| enabled | yes | true / false | — |
| event | yes | bash, file, stop, prompt, all | — |
| pattern | simple | Python regex | — |
| action | no | warn, block | warn |
| conditions | advanced | list of condition objects | — |
| tool_matcher | no | tool name(s) separated by `\|` | — |

## Advanced Conditions

For multi-condition rules, use `conditions` instead of `pattern`:

```yaml
conditions:
  - field: file_path
    operator: regex_match
    pattern: \.env$
  - field: new_text
    operator: contains
    pattern: API_KEY
```

**Fields:** command, file_path, new_text, old_text, content, reason, transcript, user_prompt
**Operators:** regex_match, contains, equals, not_contains, starts_with, ends_with

All conditions must match for the rule to trigger.

## Event Types

- **bash** — Bash tool commands
- **file** — Edit, Write, MultiEdit tools
- **stop** — agent attempting to stop
- **prompt** — user prompt submission
- **all** — all events

## Pattern Tips

Use Python regex. Unquoted YAML values work as-is.

```
rm\s+-rf           dangerous rm
console\.log\(     debug logging
(eval|exec)\(      code injection risk
\.env$             environment files
chmod\s+777        overly permissive
```

## Config Directory Priority

Rules are loaded from these directories (first match for a given rule name wins):
1. `.claude/`
2. `.agents/`
3. `.codex/`
4. `.hookify/`
