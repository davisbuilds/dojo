## Risk Profile Gate

Classify each new artifact before drafting:

- `routine` — the default; keep the normal template and validation path lean.
- `high` — use when credentials or privilege separation, remote/destructive
  effects, cross-system state agreement, retries/concurrency/queues, executable
  untrusted input, external policy decisions, or persisted-state migration can
  make a plausible-looking artifact unsafe or infeasible.

Record `risk_profile: routine|high` and `readiness: draft|ready` separately from
delivery `status`. Legacy artifacts without these fields remain routine/draft.
For `high`, load this skill's high-risk reference and addendum; do not add those
sections to routine work. Reclassify when repository evidence reveals a trigger.
