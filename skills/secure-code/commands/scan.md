---
name: scan
description: Collect targeted Semgrep evidence and investigate actionable security findings.
argument-hint: "[targets] [--config rules]"
---

# Security scan

Use the targets and concern from the request. If scope is absent, the current
repository is the default. Follow the secure-code investigation and output
contract; tool matches need source and runtime context.

Invoke `bash <skill-dir>/scripts/scan.sh` with the chosen targets and repeated
`--config` arguments as needed. Preserve its JSON output and exit status, then
use `python3 <skill-dir>/scripts/parse_findings.py <scan-output.json>` to render it.
Do not let a shell pipeline hide failure or call incomplete evidence clean.

Prefer existing project rules; `p/default` is a network-backed fallback, not
comprehensive coverage. If Semgrep is missing, report that limitation and continue
useful source investigation. Setup is separate from scanning.

Investigate high-value leads, including boundaries a syntax scanner cannot
establish. Report supported vulnerabilities, unresolved concerns, and material
coverage limitations; do not promote every rule match into a PR finding.
