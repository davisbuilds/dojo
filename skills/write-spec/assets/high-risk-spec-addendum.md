## Authority And Safety

- State each actor's observable allowed and forbidden authority.
- State identity, authorization, policy, and evidence-freshness rules.
- State invariants across partial failure, retry, recovery, and unsupported
  external policy.

## Evaluation Scenarios

- EV-NEG-01: Forbidden behavior fails with no prohibited side effect.
- EV-REC-01: Interrupted or partially completed work reaches a safe outcome.
- EV-CON-01: Concurrent or retried work preserves the contract invariants.
- EV-LEG-01: Legacy or version-skewed state is rejected, contained, or migrated
  without widening authority.

## Readiness Review

- Deterministic validation: pending
- Adversarial critique: pending
- Closure critique: pending
- Blocking findings: pending
