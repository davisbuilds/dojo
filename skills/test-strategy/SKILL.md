---
name: test-strategy
description: Guide agents to follow preferred testing methodology — red/green TDD, real dependencies over mocks, behavior-based tests, and effective-runtime authority-boundary probes. Use when writing tests, planning test coverage, deciding between TDD and test-after, correcting excessive mocking, or testing filesystem, credential, process, network, or remote-mutation permissions. Triggers on 'write tests', 'add test coverage', 'how should I test this', 'TDD', 'test strategy', 'test plan', 'test the permission boundary'.
skill-type: reference
version: 1.1.0
---

# Test Strategy

Testing methodology that encodes preferred practices for how agents should approach testing decisions.

## When To Use

- Writing tests for new features, bug fixes, or refactors
- Deciding whether to use TDD or test-after
- Choosing between real dependencies and mocks
- Planning what to test and at what granularity
- Reviewing existing tests for methodology issues
- Testing software that mediates filesystem, credential, process, network, or
  remote-mutation authority

## Core Principles

1. **Test behavior, not implementation.** Assert on outputs and observable side effects. Never assert on internal method calls, private state, or execution order unless order is the contract.

2. **Real dependencies over mocks.** Use the actual database, filesystem, or service when feasible. Mocks hide integration bugs and make tests brittle to refactoring.

3. **Red/green TDD for high-risk work.** Use the full cycle (failing test → minimal pass → refactor) for big features, major refactors, and large codebase changes. Skip TDD for trivial changes, configuration, or exploratory spikes.

4. **One assertion per concern.** Each test should verify one behavior. Multiple assertions are fine if they describe the same logical outcome.

5. **Tests are documentation.** Test names should describe the behavior under test, not the method name. A reader should understand what the system does by reading test names alone.

## When To TDD

Use red/green TDD when:
- Building a new feature with clear acceptance criteria
- Major refactors where existing behavior must be preserved
- Large codebase changes touching multiple modules
- Bug fixes (write a test that reproduces the bug first)
- Any work where the cost of regression is high

Skip TDD when:
- Exploratory spikes or prototypes (throw-away code)
- Pure configuration changes (env vars, CI files)
- Trivial one-line fixes with obvious correctness
- UI layout changes better verified visually

## Mock Decision Framework

Prefer this hierarchy (top = best):

1. **Real dependency** — actual DB, filesystem, service
2. **In-memory fake** — SQLite for Postgres, fake SMTP server
3. **Stub** — returns canned data, no behavior verification
4. **Mock** — last resort, verifies interaction

Mocks are acceptable when:
- External API with rate limits, costs, or flakiness (Stripe, OpenAI, etc.)
- Service requires network access unavailable in CI
- Dependency is genuinely slow (>5s) and cannot be optimized
- Testing error/edge cases that are hard to trigger with real dependencies

Mocks are not acceptable when:
- Mocking the thing you're testing
- Mocking to avoid writing setup code
- Mocking stable internal interfaces that rarely change
- The real dependency runs in <1s and is deterministic

## Test Granularity Guide

| Change Type | Test Layer | Notes |
|---|---|---|
| New feature | Integration + key unit tests | Verify the feature works end-to-end, unit test complex logic |
| Bug fix | Regression test at the layer the bug lives | Reproduce first, then fix |
| Refactor | Existing tests should still pass | Add tests only if coverage gaps exist |
| API endpoint | Request-level integration test | Test the HTTP contract, not controller internals |
| Pure function | Unit test | Fast, isolated, high value |
| UI component | E2E or visual test | Playwright when available in project tooling |
| Database migration | Migration test or manual verification | Test both up and down migrations |

## Conditional Authority-Boundary Testing

When the system mediates privileged authority, read
`references/authority-boundary-testing.md`. Prove a two-sided capability matrix:
allowed operations succeed and forbidden operations fail without prohibited
side effects. Pair deterministic policy/rendering tests with an isolated
effective-runtime probe and host-observed before/after evidence. Keep this path
out of routine test work that does not cross an authority boundary.

## Workflow

1. Identify the change type and select test granularity from the guide above.
2. Decide whether an authority boundary activates the conditional reference.
3. Decide TDD vs test-after based on the criteria in "When To TDD."
4. Choose the dependency approach using the mock decision framework.
5. Write tests that assert on behavior and observable outcomes.
6. Name tests to describe what the system does, not how it does it.
7. Run the full relevant test suite before claiming done.

## Boundaries

- This skill covers *what* and *how* to test, not *when to claim done* (use `verify-before-complete` for that)
- Do not generate test scaffolding scripts — agents already know test file mechanics
- Do not override project-specific test conventions if they exist (check project AGENTS.md/CLAUDE.md first)
- Do not add tests for code you didn't change unless explicitly asked

## Output

- Tests that follow the methodology above
- Clear test names describing behavior under test
- Appropriate use of real dependencies vs mocks based on the decision framework
- Test granularity matched to the change type

## Verification

- Tests assert on behavior/outputs, not implementation details
- No unnecessary mocks (each mock has a documented reason from the acceptable list)
- TDD was used for high-risk changes; test-after was justified for others
- Test names are readable as behavior descriptions
- The verification checklist in `references/verification-checklist.md` passes
- When authority is in scope, allowed and forbidden behavior is proven against
  the effective runtime with host-observed evidence and a freshness fingerprint

## Resources

- `references/verification-checklist.md` — post-test self-review checklist
- `references/authority-boundary-testing.md` — conditional capability matrix,
  effective-runtime probe, ambient/indirect path, and proof-freshness guidance

## Sibling skills

One of four `reference`-typed *Disciplines* — modes that govern *how* the agent operates.

- `verify-before-complete` — completion-claim gate. Common downstream: the tests this methodology produces feed that gate's evidence requirements.
- `first-principles` — reasoning methodology. Orthogonal axis: that one is for architectural decisions; this one is for testing decisions.
- `caveman` — output-style mode. Orthogonal.
- `diagnose` — common upstream caller; the regression test in Phase 5 should follow this skill's methodology.
