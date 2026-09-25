---
name: test-strategy
description: Guide agents to follow preferred testing methodology — red/green TDD, real dependencies over mocks, behavior-based tests, and effective-runtime authority-boundary probes. Use when writing tests, planning test coverage, deciding between TDD and test-after, correcting excessive mocking, or testing filesystem, credential, process, network, or remote-mutation permissions. Triggers on 'write tests', 'add test coverage', 'how should I test this', 'TDD', 'test strategy', 'test plan', 'test the permission boundary'.
skill-type: reference
version: 2.0.0
---

# Test Strategy

Prefer tests that distinguish correct behavior from a plausible regression and
remain useful when the implementation changes. Follow the project's testing
conventions and the user's requested scope.

## When To Use

Use when selecting coverage, writing tests, choosing dependency fidelity, or
testing a privileged boundary. Consultation may resolve one testing decision;
it need not produce a test plan, new suite, or verification report.

## Coverage and Development Order

- Assert observable behavior and contract-relevant side effects. Internal calls
  or execution order belong in assertions when they are part of the contract.
- Prefer a focused regression test that fails on the original bug. Check that
  it reaches the faulty behavior; a missing import or unrelated refusal is not
  the red signal. For new features and high-risk behavior changes, prefer
  red/green development where the target is established; honor explicit TDD
  requirements. Do not invent a failing test merely to demonstrate process.
- For behavior-preserving refactors, use existing meaningful tests as the
  baseline. Add characterization or regression coverage where a material gap
  exists, rather than requiring a new red phase for unchanged behavior.
- Choose the lowest layer that faithfully exercises the contract. Add an
  integration or runtime check where wiring or environment can invalidate the
  lower-level result. Config and UI changes may need configuration, runtime, or
  visual checks instead of synthetic unit tests.
- Stop adding tests when the relevant risks are covered. Skip new tests for
  reversible, low-impact edits with no meaningful behavior to assert.

## Dependency Fidelity

Prefer real dependencies when they are practical, deterministic, and safe to
exercise. Use controlled substitutes for costly, unavailable, nondeterministic,
or destructive dependencies and for otherwise inaccessible failures. Select
the substitute by which semantics the claim depends on, not a fixed ranking or
latency threshold: SQLite is not evidence of PostgreSQL-specific behavior.

Avoid mocking the behavior under test. When a substitute hides a consequential
integration assumption, cover it with a relevant contract/integration check or
state the unverified boundary. No per-mock justification document is required.
Live services, credentials, and external side effects remain subject to the
task's actual authorization.

## Tests That Pass for the Wrong Reason

Pay particular attention when an earlier guard can short-circuit the target,
the expected value is derived from the implementation, or the assertion depends
on a detector reporting nothing.

- Use a known positive control for a decision that rests on absence or refusal.
  For example, show the operation succeeds when the restricting condition is
  removed. Reuse a suitable existing control; do not duplicate it in every test.
- When coverage of a consequential fix is uncertain, temporarily remove or
  perturb the fix in an isolated copy and check that the intended test fails.
  A passing mutation reveals a gap. Mutation probes are a targeted diagnostic,
  not a requirement for every changed line; a demonstrated pre-fix failure may
  already answer the question.
- Keep the oracle independent enough to catch the defect. Compare against a
  trusted contract, reference result, or behavior invariant instead of
  restating the same implementation in the test.

## Conditional Authority-Boundary Testing

When the system mediates filesystem, credential, process, network, or remote
authority, read `references/authority-boundary-testing.md`. Preserve its key
obligation: prove allowed operations work and forbidden operations fail without
prohibited effects in the effective runtime. Configuration tests alone do not
prove enforcement. Keep these probes out of ordinary tests unrelated to an
authority boundary.

## Boundaries

Testing guidance does not authorize implementation changes, live external
requests, or repairs outside the requested task. A request for a test plan can
end with recommendations. Preserve required project checks and accepted user
preferences; do not route every test task into a separate completion workflow.

## Output

Deliver the requested tests or testing advice with the relevant results and
material coverage limits.

## Verification

Run required project checks and the checks needed for the change. Reuse evidence whose code/configuration and environment still apply;
broaden or repeat execution when new changes, failures, or uncovered risks
justify it. Restore any temporary mutation and keep probes isolated.

## Resources

- `references/verification-checklist.md` — optional review questions for uncertain
  coverage or a test-review request; no mandatory second pass.
- `references/authority-boundary-testing.md` — conditional runtime proof guidance.
- `evals/behavioral-scenarios.md` — intended behavior replay cases, not measured
  live-agent results.
- `evals/trigger-cases.json` — lexical routing fixtures.

## Sibling skills

- `verify-before-complete` — assessing whether available evidence supports a
  consequential completion claim.
- `diagnose` — finding the cause of an unclear test or runtime failure.
