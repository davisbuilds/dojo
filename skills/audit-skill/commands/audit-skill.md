---
name: audit-skill
description: Run a security audit on an agent skill directory and present trust score with findings.
argument-hint: "<skill-directory> [--quick] [--json] [--layer 1|2|3]"
allowed-tools: [Read, Bash(python3 skills/audit-skill/scripts/audit_skill.py:*), Bash(bash skills/secure-code/scripts/scan.sh:*), Bash(python3 skills/secure-code/scripts/trifecta_audit.py:*)]
---

# Audit Skill Command

Run a three-layer security audit on a skill directory and present the trust score with findings.

## Behavior

1. Run the audit on the specified skill directory:

```bash
python3 skills/audit-skill/scripts/audit_skill.py $ARGUMENTS
```

If no arguments are provided, prompt the user for a skill directory path.

2. Present results in this order:
   1. **Trust score** — Grade, score, pass/fail, per-layer breakdown
   2. **Critical/High findings** — Each with ID, message, file:line, category, remediation
   3. **Medium/Low findings** — Grouped by layer
   4. **Remediation guidance** — For critical/high findings, load `references/remediation-guide.md`

3. If the score fails (< 70 or has CRITICAL findings), recommend specific fixes.

4. If no findings, report a clean audit with the trust score.

## Rules

- Present all findings. Do not minimize or dismiss any finding.
- For critical/high findings, load `references/remediation-guide.md` for detailed fix guidance.
- Do not auto-fix. Present findings and recommendations, then ask the user before making changes.
- If semgrep is not installed, note that Layer 3 ran in degraded mode (regex only).

## Example Invocations

```bash
# Full audit of a skill
/audit-skill skills/secure-code/

# Quick audit (skip semgrep)
/audit-skill skills/my-skill/ --quick

# JSON output for CI integration
/audit-skill skills/my-skill/ --json

# Audit only the instruction layer
/audit-skill skills/my-skill/ --layer 2
```
