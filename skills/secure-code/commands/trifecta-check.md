---
name: trifecta-check
description: Detect the lethal trifecta — co-occurrence of private data access, untrusted input processing, and external communication in a single file.
argument-hint: "<file-or-directory...>"
allowed-tools: [Read, Bash(python3 skills/secure-code/scripts/trifecta_audit.py:*)]
---

# Trifecta Check Command

Detect the lethal trifecta anti-pattern: files where private data access, untrusted input processing, and external communication co-occur.

## Behavior

1. Run the trifecta audit on specified targets:

```bash
python3 skills/secure-code/scripts/trifecta_audit.py $ARGUMENTS
```

If no arguments are provided, scan the current working directory:

```bash
python3 skills/secure-code/scripts/trifecta_audit.py .
```

2. Parse the JSON output and present results:
   1. **Summary** — Number of files scanned, number with trifecta detected
   2. **Flagged files** — For each file with all three legs:
      - Which legs are present and where (line numbers)
      - Sample code showing each leg
      - Why this combination is dangerous
   3. **Partial matches** — Files with 2 of 3 legs (lower priority, informational)
   4. **Remediation** — Load `references/lethal-trifecta.md` and recommend specific separation strategies

3. If no trifecta detected, report clean with a note about partial matches if any exist.

## Rules

- Focus on files with all three legs first. Two-leg files are informational only.
- For each flagged file, explain the specific attack vector enabled by the co-occurrence.
- Reference `references/lethal-trifecta.md` for architectural separation guidance.
- Do not auto-refactor. Present the finding and recommended architecture, then ask the user before making changes.

## Example Invocations

```bash
# Check a specific file
/trifecta-check src/api/webhook_handler.py

# Check a directory
/trifecta-check src/

# Check multiple files
/trifecta-check src/api/handler.py src/api/webhook.py src/api/notify.py
```
