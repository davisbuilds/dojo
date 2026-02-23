# Writing Custom Semgrep Rules

Guide for creating project-specific semgrep rules to extend the secure-code skill.

## Rule File Structure

Semgrep rules are YAML files. Each file can contain multiple rules:

```yaml
rules:
  - id: my-project.rule-name
    patterns:
      - pattern: dangerous_function($ARG)
    message: "Avoid dangerous_function — use safe_alternative instead."
    languages: [python]
    severity: WARNING
    metadata:
      cwe: ["CWE-78"]
      category: security
```

## Key Fields

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique identifier. Use `project.category.name` convention. |
| `patterns` / `pattern` | Yes | What to match. See pattern syntax below. |
| `message` | Yes | Explanation shown to the user. Include the fix. |
| `languages` | Yes | Target languages: `python`, `javascript`, `typescript`, `go`, `java`, etc. |
| `severity` | Yes | `ERROR` (critical/high), `WARNING` (medium), `INFO` (low) |
| `metadata` | No | CWE tags, categories, references |

## Pattern Syntax

### Basic patterns

```yaml
# Match a specific function call
pattern: eval($INPUT)

# Match with metavariable
pattern: subprocess.run($CMD, shell=True)

# Match any argument
pattern: requests.get($URL, ...)
```

### Combining patterns

```yaml
# All must match (AND)
patterns:
  - pattern: $FUNC($INPUT, ...)
  - metavariable-regex:
      metavariable: $FUNC
      regex: (eval|exec)

# Any can match (OR)
pattern-either:
  - pattern: eval($X)
  - pattern: exec($X)

# Match pattern but exclude safe cases
patterns:
  - pattern: $OBJ.query($SQL)
  - pattern-not: $OBJ.query("...", $PARAMS)
```

### Taint mode (data flow tracking)

```yaml
rules:
  - id: taint-sqli
    mode: taint
    pattern-sources:
      - pattern: request.args.get(...)
    pattern-sinks:
      - pattern: cursor.execute($QUERY, ...)
    message: "User input flows into SQL query."
    languages: [python]
    severity: ERROR
```

## Where to Place Rules

```
skills/secure-code/rules/
├── trifecta/
│   └── trifecta-cooccurrence.yaml  # Built-in trifecta rules
└── custom/
    └── my-project-rules.yaml       # Your project-specific rules
```

Run custom rules:

```bash
bash skills/secure-code/scripts/scan.sh <targets> --config skills/secure-code/rules/custom/
```

## Testing Rules

Create a test file with annotated examples:

```python
# ruleid: my-project.unsafe-query
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# ok: my-project.unsafe-query
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

Run with `semgrep --test`:

```bash
semgrep --test --config rules/custom/my-rules.yaml tests/
```

## Tips

- Start with `pattern-either` for OR logic before reaching for taint mode
- Use `metavariable-regex` to constrain metavariables without listing every case
- Keep messages actionable — include what to do instead
- Tag with CWE numbers for cross-referencing with scan findings
- Test rules against both vulnerable and safe code samples

## References

- [Semgrep rule syntax](https://semgrep.dev/docs/writing-rules/rule-syntax)
- [Semgrep pattern examples](https://semgrep.dev/docs/writing-rules/pattern-examples)
- [Semgrep playground](https://semgrep.dev/playground) for interactive testing
