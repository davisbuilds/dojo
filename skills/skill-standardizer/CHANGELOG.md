## 1.1.0 - 2026-07-16

- Add built-in KNOWN_NON_SKILL_DIRS allowlist, keyed by root kind; exempts codex-primary-runtime in ~/.codex/skills.

## 1.0.1 - 2026-07-16

- Fix audit exit code to track real drift: 2 only when actions are planned, 1 on error-severity issues, 0 otherwise. Previously any warning forced exit 2, contradicting the documented contract.
