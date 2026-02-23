---
name: audit-skill
description: >-
  Security audit for agent skills using a three-layer deterministic architecture:
  structural validation, instruction scanning (prompt injection, encoding tricks,
  exfiltration, overreach), and code analysis (secrets, dangerous patterns, semgrep SAST,
  trifecta detection). Produces a trust score (A-F) with per-layer breakdown.
  Use when reviewing a skill for security, auditing a skill before installation,
  checking for prompt injection, or when the user says 'audit skill', 'check skill security',
  'trust score', 'is this skill safe', or 'audit-skill'. On-demand via /audit-skill command.
compatibility: "Requires python3, PyYAML. Layer 3 code audit requires semgrep CLI (brew install semgrep)."
---

# audit-skill

## Overview

Three-layer security audit for agent skills, producing a trust score with actionable findings.

| Layer | Focus | Weight |
|-------|-------|--------|
| 1. Structural | Frontmatter, allowed-tools blast radius, file inventory, network inference, size | 25% |
| 2. Instructions | Prompt injection, encoding tricks, exfiltration, overreach | 35% |
| 3. Code | Secrets, dangerous patterns, semgrep SAST, trifecta detection | 40% |

## Principles

- **Deterministic first**: Pattern matching and static analysis provide ground truth. LLM analysis supplements but never overrides tool output.
- **Fully offline**: No cloud APIs or network calls required. Semgrep uses local rules.
- **Composable**: Each layer runs independently. Reuses `secure-code` skill for Layer 3 SAST.
- **Graceful degradation**: If semgrep is unavailable, Layer 3 still runs regex-based checks.

## Workflow

### Full Audit

```bash
python3 skills/audit-skill/scripts/audit_skill.py <skill-directory>
```

### Quick Audit (Layers 1-2 only, no semgrep)

```bash
python3 skills/audit-skill/scripts/audit_skill.py <skill-directory> --quick
```

### JSON Output

```bash
python3 skills/audit-skill/scripts/audit_skill.py <skill-directory> --json
```

### Single Layer

```bash
python3 skills/audit-skill/scripts/audit_skill.py <skill-directory> --layer 1
python3 skills/audit-skill/scripts/audit_skill.py <skill-directory> --layer 2
python3 skills/audit-skill/scripts/audit_skill.py <skill-directory> --layer 3
```

## Trust Score Interpretation

| Grade | Score | Meaning |
|-------|-------|---------|
| A | 90-100 | Low risk. Minimal or no findings. |
| B | 75-89 | Acceptable. Minor issues to address. |
| C | 60-74 | Caution. Several findings need attention. |
| D | 40-59 | High risk. Significant security concerns. |
| F | 0-39 | Unsafe. Critical issues present. |

**Pass condition**: Score >= 70 AND no CRITICAL findings.

## Severity Handling

| Severity | Action |
|----------|--------|
| CRITICAL | Flag immediately. Automatic fail regardless of score. |
| HIGH | Flag prominently. Recommend remediation before use. |
| MEDIUM | Report with context. Fix recommended. |
| LOW | Report in summary. Informational. |

## Remediation

For finding-specific remediation guidance, load `references/remediation-guide.md`. For code-level vulnerability details, cross-reference `skills/secure-code/references/secure-coding-guidelines.md`.
