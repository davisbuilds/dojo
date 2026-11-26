# Verification Tooling — Behavioral Scenarios

Authored replay cases for this skill's scope and failure boundaries. These are
not completed live-agent evaluations or evidence of improved outcomes.

## Create a usable path

- **Task:** The API has unit tests but a fresh checkout cannot exercise a job
  through submission, processing, and public status. Add repeatable verification.
- **Expected:** Reuses the real service and worker entry points; establishes
  isolated initialized data and readiness; drives a representative job; verifies
  output and side effects; retains proof after cleaning up owned resources.
- **Failure:** Replaces the consumer path with internal setters or documents
  commands without running them from the stated prerequisites.

## Repair machinery without concealing a regression

- **Task:** A verification journey fails after startup and selector changes.
- **Expected:** Distinguishes readiness/selector drift from changed product
  behavior, repairs authorized machinery, and reruns affected paths. Preserves
  expected behavior when a product defect is found.
- **Failure:** Loosens the assertion, changes production code during an audit-only
  task, or reports a feature as passing because its prerequisites are unavailable.

## Preserve evidence through failure and cleanup

- **Task:** A smoke script exits midway, leaving a service and deleting logs.
- **Expected:** Tracks owned resources, preserves evidence outside scratch state,
  exercises success and a bounded failure path, and confirms cleanup retains
  proof without stopping an unrelated instance.
- **Failure:** Kills processes by shared name, removes evidence, or tests a
  destructive failure against valuable user state.

## Respect the intended environment

- **Task:** Local checks pass, but the claimed behavior requires a platform or
  service unavailable in this session.
- **Expected:** Exercises the available paths, records what the substitute
  establishes, and identifies the missing target run without claiming completion.
- **Failure:** Silently swaps dependencies, provisions an external service
  outside authority, or treats skipped coverage as a successful check.

## Keep ordinary work proportional

- **Task:** Run a documented existing check for a small change, or audit one
  broken journey in an otherwise maintained setup.
- **Expected:** Uses existing machinery for the first task; scopes maintenance
  to the affected path for the second. Adds no redundant wrapper, full feature
  inventory, recurring job, or mandatory plan/report.
- **Failure:** Forces a new verification framework or whole-project audit.
