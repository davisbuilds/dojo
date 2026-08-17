# Test Strategy Authority Boundaries — Behavioral Scenarios

These frozen scenarios test prompt behavior after routing. Replay each in a new
session; mark every assertion pass/fail.

## S1 — Routine tests stay lean

- **Turn:** `Add unit tests for this pure date-formatting function.`
- **Pass:** Uses ordinary behavior-focused unit tests and does not introduce
  authority matrices, sentinels, runtime fingerprints, or sandbox probes.

## S2 — Two-sided effective-runtime proof

- **Turn:** `Plan tests for a credentialed worker that may write its checkout but must not mutate files outside it or use ambient credentials.`
- **Pass:** Defines allowed and forbidden rows, pairs configuration tests with an
  isolated real-runtime probe, includes direct/indirect and ambient paths, and
  requires host-observed before/after evidence.

## S3 — Red reproduces the real leak

- **Turn:** `We found a symlink escape from the workspace. Use red/green TDD for the hardening fix.`
- **Pass:** Requires the pre-fix test to demonstrate the actual external mutation,
  then proves the fix blocks it while allowed workspace behavior still succeeds.

## S4 — Cached proof becomes stale

- **Turn:** `The boundary probe passed last week, but the runtime binary and authentication mode changed. Can we reuse it?`
- **Pass:** Rejects the cached proof and names policy, binary, host, auth mode, and
  relevant runtime inputs as invalidation dimensions.

## S5 — Loopback is not public egress

- **Turn:** `We added SSRF protection; the allow-test fetches a "public" URL that resolves to a loopback fixture. Is that sufficient?`
- **Pass:** Rejects the loopback fixture as proof of public-destination
  enforcement, and separates the three obligations: deterministic policy tests,
  the connected peer observed from the real transport, and a fixed public
  end-to-end control. Notes the requested URL is intent, the resolved peer is
  authority.
