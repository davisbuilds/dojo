## 2.0.0 - 2026-10-03

- Terminate the scanner process group on audit timeout or interruption, including nested workers; add a real-process regression for the orphaned-scanner failure.

- Replace weighted trust grades and automatic pass/fail with contextual skill investigation and schema-v2 static evidence (inventory, coverage, errors, indicators).
- Make Semgrep opt-in; surface missing tools and failed/partial scans. Remove the scoring and structural-audit entry points and the trifecta detector integration.
- Inspect fenced instructions without treating keywords as vulnerabilities; omit source excerpts from indicators and record unreadable/binary/link gaps without executing targets.
- Repair and narrow bundled rules, remove prose autofixes and unsupported claims, and add positive/negative fixtures and orchestration regressions.

## 1.0.4 - 2026-08-14

- Anchor runnable script commands to <skill-dir> so they resolve outside a dojo checkout

## 1.0.3 - 2026-08-01

- Condense the internal audit-phase list in the description to its scope and output; triggers unchanged.

# Changelog

## 1.0.2 - 2026-07-31

- Document the bundled `rules/skill-scripts.yaml` semgrep ruleset, which was
  shipped but unreferenced from SKILL.md and therefore undiscoverable. Raised in
  review of PR #50.

## 1.0.1 - 2026-07-31

- Trim the description from 551 to 385 chars by removing the three-layer architecture detail. Trigger phrases preserved.
