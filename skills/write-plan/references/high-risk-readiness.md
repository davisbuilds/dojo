# High-Risk Plan Readiness

Load this reference only when the Risk Profile Gate selects `high`. Add
`spec: docs/specs/<topic>-spec.md` to frontmatter and copy the high-risk addendum
into the plan. The linked spec must also declare `risk_profile: high`.
Do not proceed until that spec declares `readiness: ready`.

## Map Proof Before Tasks

- Trace every `SC-NN` and `EV-*-NN` from the spec to a task and deterministic
  proof. No contract ID may disappear or be invented by the plan.
- Inventory actors and capabilities. State allowed and forbidden authority and
  the effective-runtime proof for both sides.
- Inventory local, remote, and durable side effects in execution order. For each
  boundary, state the observable state before and after a crash plus the
  idempotent recovery or reconciliation path.
- Map lifecycle and backward compatibility, including old persisted state,
  retries, duplicates, cadence, supersession, and partial rollout.
- Review executable dependency, startup, build, migration, and lifecycle hooks
  that can run before the intended guardrail.

## Evidence And Consumer Closure

For each authority-bearing artifact, record its trusted producer, creation
phase, exact claim, consumers, and freshness rule. Never place a claim that is
known only after execution into a pre-dispatch artifact.

For each new identity, policy, outcome, lifecycle, or retry field, find every
producer, duplicate, cadence, outcome, supersession, compatibility, and cleanup
consumer. Update them in one coherent task or state the safe transitional
invariant between tasks.

## Empirical Task 0 Stop Gates

Create Task 0 for any security or platform assumption that is not yet proven.
Configuration rendering alone is not proof. Probe the effective runtime using:

- allowed operations that must succeed;
- forbidden operations against sentinels outside implicitly writable roots;
- direct and indirect paths such as symlinks or delegated processes;
- ambient credential and configuration channels;
- tracked, untracked, ignored, generated, and externally stored state when in
  scope;
- network or remote mutation authority when in scope.

Fingerprint effective policy, binary, host, authentication mode, and relevant
runtime inputs. A changed fingerprint invalidates cached proof. Later tasks must
depend on Task 0 and stop when any gate fails.

## Review Closure

Keep `readiness: draft` through deterministic validation, adversarial critique,
revision, and closure critique. Seed critique with ambient credentials,
executable hooks, contradictory invariants, crash windows, external identity and
policy semantics, retry/idempotency, consumer closure, and legacy state. Set
`readiness: ready` only when all blocking findings are closed.

The validator proves structure, linked-spec ID coverage, task references, and
modified-file existence. It cannot prove that an authority map, failure window,
or recovery claim is true; the critique owns those semantic judgments.
