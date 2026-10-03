## 2.0.0 - 2026-10-03

- Replace scanner-oracle and same-file trifecta verdicts with scoped security investigation and agent authority tracing.
- Preserve Semgrep matches, errors, coverage and execution provenance; combine repeated configs and make incomplete evidence nonzero. Do not install tools or accept autofix flags.
- Retire the regex trifecta script, generic co-occurrence rules, and automatic setup script. Keep /trifecta-check as an authority-review command.
- Add regression tests and a real-engine positive/negative control; narrow rule-authoring and security references.

## 1.0.2 - 2026-08-14

- Anchor runnable script commands and their bundled-resource operands (`--config <skill-dir>/rules/`) to <skill-dir> so they resolve outside a dojo checkout

# Changelog

## 1.0.1 - 2026-07-31

- Remove references to skills retired on 2026-07-31 (`gh-fix-issue`,
  `gh-review-pr`, `gh-triage-issues`, `code-review-agents`,
  `autonomous-engineering`, `self-improve`, `vercel-react-native-skills`).
  Sibling sections and routing text only; no behavior change.
