# Changelog

## 2.0.1 - 2026-07-31

- Remove references to skills retired on 2026-07-31 (`gh-fix-issue`,
  `gh-review-pr`, `gh-triage-issues`, `code-review-agents`,
  `autonomous-engineering`, `self-improve`, `vercel-react-native-skills`).
  Sibling sections and routing text only; no behavior change.

## 2.0.0 - 2026-07-15

- Retune trigger to circuit-breaker cases (delegated work, high-risk changes, missing/stale/conflicting evidence, explicit audits); add fast-exit for routine changes covered by repo checks. Adds trigger-cases eval fixture. MAJOR per the skill contract: narrowed trigger semantics are a breaking change for SemVer-honoring consumers.
