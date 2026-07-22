## High-Risk Readiness

### Traceability

| Contract ID | Task | Proof |
| --- | --- | --- |
| SC-01 | Task 0 | `command` |
| EV-NEG-01 | Task 0 | `command` |
| EV-REC-01 | Task N | `command` |
| EV-CON-01 | Task N | `command` |
| EV-LEG-01 | Task N | `command` |

### Capability And Authority Map

| Actor | Allowed | Forbidden | Effective-runtime proof |
| --- | --- | --- | --- |
| Actor | Allowed outcome | Forbidden outcome | `command` plus host observation |

### Side Effects And Failure Windows

| Effect | Before | After | Recovery |
| --- | --- | --- | --- |
| Effect | Observable state | Observable state | Idempotent action |

### Evidence Lifecycle

| Evidence | Trusted producer | Created | Claim | Consumers | Freshness |
| --- | --- | --- | --- | --- | --- |
| Artifact | Producer | Phase/task | Exact claim | Named consumers | Invalidation rule |

### Consumer Closure

- Map producers, duplicates, cadence, outcomes, supersession, retries,
  compatibility, and cleanup consumers; update atomically or state the safe
  transitional invariant.

### Lifecycle And Compatibility

- State behavior for legacy state, version skew, partial rollout, retry, and
  supersession.

### Execution Hooks

- Review dependency, startup, build, migration, and lifecycle hooks that may run
  before the intended guardrail.

### Capability Stop Gates

- Task 0 probes allowed and forbidden effective-runtime behavior, indirect
  paths, ambient authority, relevant state classes, and fingerprint invalidation.

### Readiness Review

- Deterministic validation: pending
- Adversarial critique: pending
- Closure critique: pending
- Blocking findings: pending
