---
name: secure-code
description: >-
  Static analysis security scanning and architectural trifecta detection using semgrep.
  Use when reviewing code for security vulnerabilities, running SAST scans, checking for
  the lethal trifecta (private data + untrusted input + external comms co-occurrence),
  or when the user says 'scan', 'security scan', 'trifecta check', 'check for vulnerabilities',
  'SAST', or 'secure this code'. On-demand via /scan and /trifecta-check commands.
compatibility: "Requires semgrep CLI (brew install semgrep), python3"
---

# secure-code

## Overview

Integrate semgrep as a deterministic SAST oracle into the agent workflow. Two capabilities:

1. **Security scanning** (`/scan`): Run semgrep on target files, parse findings into severity-grouped markdown.
2. **Trifecta detection** (`/trifecta-check`): Detect architectural anti-patterns where private data access, untrusted input processing, and external communication co-occur in a single file.

## Principles

- **Conservative posture**: Present findings with context. Do not auto-fix security issues without explicit user approval.
- **Deterministic first**: semgrep provides ground truth. LLM analysis supplements but never overrides tool output.
- **Minimal context**: Load references only when remediating specific vulnerability classes.

## Setup

Run setup before first use:

```bash
bash skills/secure-code/scripts/setup.sh
```

## Scan Workflow

1. Run semgrep on target files:

```bash
bash skills/secure-code/scripts/scan.sh <targets> | python3 skills/secure-code/scripts/parse_findings.py
```

2. Present findings grouped by severity: CRITICAL > HIGH > MEDIUM > LOW.
3. For each finding, include: rule ID, CWE (if tagged), file:line, message, severity.
4. If remediating, load `references/secure-coding-guidelines.md` for the relevant vulnerability class.
5. Propose fixes only with user approval. Never silently patch security issues.

## Trifecta Audit Workflow

1. Run trifecta detection:

```bash
python3 skills/secure-code/scripts/trifecta_audit.py <targets>
```

2. For flagged files, explain which three legs are present and where.
3. Load `references/lethal-trifecta.md` for separation guidance.
4. Recommend architectural refactoring to isolate legs into separate modules.

## Custom Rules

Project-specific semgrep rules live in `rules/`. Run them with:

```bash
bash skills/secure-code/scripts/scan.sh <targets> --config skills/secure-code/rules/
```

See `references/writing-custom-rules.md` for authoring guidance.

## Severity Handling

| Severity | Action |
|----------|--------|
| CRITICAL | Flag immediately. Block merge recommendation. |
| HIGH | Flag prominently. Recommend fix before merge. |
| MEDIUM | Report with context. Fix recommended but not blocking. |
| LOW | Report in summary. Informational. |

## Network

semgrep rule downloads require network access on first run. After initial fetch, rules are cached locally. Use `--metrics=off` and `--disable-version-check` to minimize network calls.
