# Write Spec Risk Readiness — Behavioral Scenarios

These frozen scenarios test prompt behavior after routing. Replay each in a new
session and mark every assertion pass/fail.

Every scenario also requires a resolved `author:` value naming the producing
agent; the literal `<agent>` placeholder is a failure.

## S1 — Routine multi-file feature stays lean

- **Turn:** `Write a spec for adding a read-only filter to an existing report. It touches the API and UI but has no migration or privileged effects.`
- **Pass:** Declares `risk_profile: routine`; uses the normal mechanism-free
  sections; does not add authority maps, fixed high-risk scenarios, Task 0, or a
  mandatory critique gate.

## S2 — Remote transactional workflow activates high risk

- **Turn:** `Write a spec for a credentialed worker that stages a local change, mutates a remote repository, and must recover safely if either side fails.`
- **Pass:** Declares `risk_profile: high` and `readiness: draft`; assigns stable
  `SC-NN` and negative/recovery/concurrency/legacy scenario IDs; states observable
  authority, identity/freshness, side-effect, unsupported-policy, and recovery
  outcomes without naming implementation files or ordered steps; does not claim
  completion before critique closure.

## S3 — Persisted-state migration covers legacy outcomes

- **Turn:** `Write a spec for migrating durable workflow state while old and new workers may overlap during rollout.`
- **Pass:** Activates high risk; makes compatibility and supersession observable;
  includes recovery, concurrency, and legacy-state scenarios; preserves the
  mechanism-free WHAT/HOW boundary.
