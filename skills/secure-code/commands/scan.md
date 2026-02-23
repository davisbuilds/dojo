---
name: scan
description: Run semgrep SAST scan on target files and present severity-grouped findings with remediation guidance.
argument-hint: "<file-or-directory...> [--config <semgrep-config>]"
allowed-tools: [Read, Bash(bash skills/secure-code/scripts/scan.sh:*), Bash(python3 skills/secure-code/scripts/parse_findings.py:*), Bash(bash skills/secure-code/scripts/setup.sh:*)]
---

# Scan Command

Run a semgrep security scan on target files and present findings grouped by severity.

## Behavior

1. Verify semgrep is installed. If not, run setup:

```bash
bash skills/secure-code/scripts/setup.sh
```

2. Run semgrep on the specified targets:

```bash
bash skills/secure-code/scripts/scan.sh $ARGUMENTS | python3 skills/secure-code/scripts/parse_findings.py
```

If no arguments are provided, scan the current working directory:

```bash
bash skills/secure-code/scripts/scan.sh . | python3 skills/secure-code/scripts/parse_findings.py
```

3. Present findings in this order:
   1. **Summary** — Total count by severity
   2. **Critical/High findings** — Each with rule ID, CWE, file:line, message
   3. **Medium/Low findings** — Grouped by file
   4. **Remediation guidance** — For critical/high findings, reference `references/secure-coding-guidelines.md` for the relevant vulnerability class

4. If no findings, report a clean scan.

## Custom Rules

To scan with project-specific rules:

```bash
/scan <targets> --config skills/secure-code/rules/trifecta/
```

Or combine with default rules:

```bash
/scan <targets> --config p/default --config skills/secure-code/rules/trifecta/
```

## Rules

- Present findings with full context. Do not minimize or dismiss any finding.
- For critical/high findings, load and reference the relevant section of `references/secure-coding-guidelines.md`.
- Do not auto-fix. Present the finding and recommended fix, then ask the user before making changes.
- If semgrep reports errors (e.g., unsupported language, parse errors), include them in the output.

## Example Invocations

```bash
# Scan a specific file
/scan src/api/handler.py

# Scan a directory
/scan src/

# Scan with custom rules
/scan src/ --config skills/secure-code/rules/trifecta/

# Scan with a specific semgrep registry config
/scan src/ --config p/python
```
