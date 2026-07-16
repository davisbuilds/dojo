## 2.0.0 - 2026-07-15

- Retune trigger to circuit-breaker cases (delegated work, high-risk changes, missing/stale/conflicting evidence, explicit audits); add fast-exit for routine changes covered by repo checks. Adds trigger-cases eval fixture. MAJOR per the skill contract: narrowed trigger semantics are a breaking change for SemVer-honoring consumers.
