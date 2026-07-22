# Test Strategy Verification Checklist

Run through this checklist before considering test work complete.

## Behavior Focus

- [ ] Tests assert on outputs and observable side effects, not internal method calls
- [ ] Test names describe what the system does (e.g., "returns 404 when user not found"), not the method being tested
- [ ] No assertions on execution order unless order is the documented contract

## Dependency Choices

- [ ] Each mock/stub has a clear reason (external API, rate limit, network, >5s latency)
- [ ] No mocks on the system under test
- [ ] No mocks used solely to avoid writing setup code
- [ ] Real database/filesystem used where available and deterministic
- [ ] In-memory fakes preferred over mocks when real dependency is unavailable

## TDD Compliance

- [ ] High-risk changes (big features, major refactors, large codebase changes) used red/green TDD
- [ ] Bug fixes include a regression test written before the fix
- [ ] If TDD was skipped, the reason fits the skip criteria (spike, config, trivial fix, visual)

## Granularity

- [ ] Test layer matches the change type (integration for features, unit for pure functions, etc.)
- [ ] No over-testing of happy paths at the expense of edge cases
- [ ] No redundant tests that verify the same behavior at multiple layers without justification

## Hygiene

- [ ] Tests are independent — no shared mutable state between tests
- [ ] Tests clean up after themselves (temp files, DB records, etc.)
- [ ] No sleep/wait calls unless testing async behavior with proper timeouts
- [ ] Tests run in <10s individually (flag slow tests explicitly)
- [ ] Project-specific test conventions were followed (checked AGENTS.md/CLAUDE.md)

## Authority Boundaries (when applicable)

- [ ] Allowed operations succeed and forbidden operations fail without side effects
- [ ] A real isolated effective-runtime probe complements policy/rendering tests
- [ ] Before/after evidence is observed outside the constrained subject
- [ ] Direct, indirect, ambient, state-class, network, and remote paths are covered when in scope
- [ ] The red test reproduced the actual authority leak before the fix
- [ ] Cached proof is invalidated when policy, binary, host, auth mode, or runtime inputs change
