---
name: audit-skill
description: Security audit for agent skills — prompt-injection and exfiltration scanning with an A–F trust score. Use when reviewing a skill for security, auditing a skill before installation, checking for prompt injection, or when the user says 'audit skill', 'check skill security', 'trust score', 'is this skill safe'. On-demand via /audit-skill.
skill-type: workflow
compatibility: "Requires python3, PyYAML. Layer 3 code audit requires semgrep CLI (brew install semgrep). Semgrep rule downloads require network on first run."
version: 1.0.3
---

# audit-skill

## Overview

Three-layer security audit for agent skills, producing a trust score with actionable findings.

| Layer | Focus | Weight |
|-------|-------|--------|
| 1. Structural | Frontmatter, allowed-tools blast radius, file inventory, network inference, size | 25% |
| 2. Instructions | Prompt injection, encoding tricks, exfiltration, overreach | 35% |
| 3. Code | Secrets, dangerous patterns, semgrep SAST, trifecta detection | 40% |

## When To Use

Use this skill when:
- auditing an external or local skill before use
- evaluating prompt-injection or exfiltration risk in skill instructions
- producing a trust score for skill governance decisions
- the user asks for `/audit-skill`

## Principles

- **Deterministic first**: Pattern matching and static analysis provide ground truth. LLM analysis supplements but never overrides tool output.
- **Fully offline**: No cloud APIs or network calls required. Semgrep uses local rules.
- **Composable**: Each layer runs independently. Reuses `secure-code` skill for Layer 3 SAST.
- **Graceful degradation**: If semgrep is unavailable, Layer 3 still runs regex-based checks.

## Bundled Resources

- `scripts/audit_skill.py` — the audit runner invoked in every Workflow command below.
- `rules/skill-scripts.yaml` — the semgrep ruleset Layer 3 loads (`eval`/`exec` on
  non-literals, subprocess with shell, credential exfiltration). Edit this to change
  what code analysis catches; it is the deterministic half of the trust score.

## Boundaries

- Do not certify a skill as safe solely from score; include concrete findings.
- Do not skip CRITICAL findings because weighted score is otherwise high.
- Do not mutate target skills automatically during audit runs.

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

## Output Requirements

Return:
- trust grade and numeric score
- per-layer findings summary
- explicit CRITICAL/HIGH findings with file paths
- recommended remediation order

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

## Sibling skills

Part of the skill-management toolchain (security gate) and adjacent to general security skills.

- `skill-evals` — orthogonal: contract/structure validation. Run both before publishing — this skill catches malicious behavior, that one catches malformed structure.
- `skill-installer` — common downstream caller. Run this skill against any third-party skill before installing.
- `secure-code` — broader semgrep-based scan for application code. This skill is scoped to *agent skills*; use `secure-code` for product/library code.
