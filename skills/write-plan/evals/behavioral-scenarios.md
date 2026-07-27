# Write Plan Risk Readiness — Behavioral Scenarios

These frozen scenarios test prompt behavior after routing. Replay each in a new
session and mark every assertion pass/fail.

Every scenario also requires a resolved `author:` value naming the producing
agent; the literal `<agent>` placeholder is a failure.

## S1 — Routine multi-file feature stays lean

- **Turn:** `Plan the implementation of a read-only report filter from its settled routine spec.`
- **Pass:** Declares `risk_profile: routine`; maps the existing seam and test
  discovery normally; does not add high-risk authority/evidence tables, Task 0,
  or mandatory critique closure; still offers the optional plan-specific
  critique subagent handoff.

## S2 — Remote transaction receives empirical stop gates

- **Turn:** `Plan the credentialed local-and-remote landing workflow from this high-risk spec.`
- **Pass:** Links the high-risk spec; traces every contract/scenario ID; maps
  allowed and forbidden authority, ordered side effects and crash windows,
  evidence producers/consumers/freshness, and executable hooks; creates empirical
  Task 0 probes for direct/indirect paths, ambient credentials, state classes,
  remote effects, and runtime fingerprint invalidation; remains draft until
  critique closure.

## S3 — Migration closes every lifecycle consumer

- **Turn:** `Plan the durable-state migration while old and new workers may coexist and retry.`
- **Pass:** Maps producers, duplicates, cadence, outcomes, supersession, retry,
  compatibility, and cleanup consumers; updates them coherently or records a
  safe transitional invariant; covers legacy and partial-rollout proofs before
  declaring the plan ready.

## S4 — Done When proves useful magnitude

- **Turn:** `Plan a pipeline whose contract requires a useful result rather than merely completing or emitting non-empty output.`
- **Pass:** Every affected `Done When` pins a meaningful magnitude, floor, rate,
  or non-degeneracy bound; verification cannot pass on empty or trivial output.

## S5 — Fix the defect class across adjacent paths

- **Turn:** `Plan the removal of eager materialization from a data workflow with primary and secondary CLI paths plus sibling sources.`
- **Pass:** Maps every path that can materialize the dataset, assigns each a
  `Done When` or explicit out-of-scope note, and verifies cited target lines
  before claiming `Assumptions Verified`.
