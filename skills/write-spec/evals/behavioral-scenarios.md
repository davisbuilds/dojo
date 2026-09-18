# Write Spec Risk Readiness — Behavioral Scenarios

These frozen scenarios test prompt behavior after routing. Replay each in a new
session and mark every assertion pass/fail.

Saved artifacts require a resolved `author:` naming the producing agent; a
consultation that needs no artifact has no metadata requirement. These are manual
replay cases, not recorded model-performance results.

## S1 — Routine multi-file feature stays lean

- **Turn:** `Write a spec for adding a read-only filter to an existing report. It touches the API and UI but has no migration or privileged effects.`
- **Pass:** Declares `risk_profile: routine`; uses the normal mechanism-free
  sections; does not add authority maps, fixed high-risk scenarios, Task 0, or a
  mandatory critique gate. Reports the requested contract without a compulsory
  critique offer, handoff menu, or new planning workflow.

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

## S4 — Acceptance cannot pass on trivial output

- **Turn:** `Write a spec whose pipeline must produce a useful recommendation, not merely finish or emit one row.`
- **Pass:** Pins a meaningful output floor or rate and a non-degenerate input
  condition; does not accept bare `> 0`, non-emptiness, or completion.

## S5 — Refactor equivalence starts with an edge-defined oracle

- **Turn:** `Write a behavior-preserving refactor spec for an ordering pipeline whose current key may contain ties and duplicates.`
- **Pass:** Defines reference behavior on ties, duplicates, and empty input;
  requires probing the uniqueness/order assumption against representative real
  data; includes those edges in differential evaluation.

## S6 — Settled implementation does not acquire a spec prerequisite

- **Turn:** `Implement the report filter using the accepted behavior and tests
  in this ticket. The CLI and service both need changes; no design decisions
  remain open.`
- **Pass:** Reuses the accepted target and relevant evidence; does not create a
  spec or ask permission to skip one because the change touches multiple files.
  A material gap discovered in the ticket is resolved explicitly rather than
  silently guessed away.

## S7 — Existing high-risk contract remains authoritative

- **Fixture:** An accepted high-risk contract with a known unresolved recovery
  decision and `readiness: draft`.
- **Turn:** `Use this contract to prepare the release plan; avoid duplicate docs.`
- **Pass:** Reuses the contract but resolves its blocking decision and readiness
  before dependent planning. Does not erase high-risk requirements, downgrade
  risk, or manufacture another copy of the same contract.
