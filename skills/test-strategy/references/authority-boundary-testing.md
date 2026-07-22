# Effective Authority-Boundary Testing

Load this reference only when software mediates filesystem, credential, process,
network, remote-mutation, or comparable privileged authority. The target is the
effective runtime boundary, not merely the policy or launch configuration.

## Two-Sided Capability Matrix

List each relevant authority with both sides:

| Capability | Allowed operation | Forbidden operation | Host-observed evidence |
| --- | --- | --- | --- |
| Example | Operation that must succeed | Operation that must fail | Before/after state |

An allowed-only test cannot detect an over-broad boundary. A forbidden-only test
can pass because the runtime is broken. Prove both.

## Test Layers

1. Keep deterministic unit tests for policy generation, configuration rendering,
   argument construction, and obvious validation errors.
2. Add an isolated real-runtime probe that launches the same binary, policy,
   authentication mode, and relevant environment as production.
3. Observe effects from outside the constrained process. Snapshot sentinels,
   remote state, processes, and network-visible outcomes before and after; do not
   accept the subject's self-report as proof.

Exercise only authorities in scope, including:

- direct paths and indirect paths such as symlinks, delegated processes, or
  alternate configuration roots;
- ambient credentials, environment variables, credential helpers, and inherited
  configuration;
- tracked, untracked, ignored, generated, and externally stored state;
- network and remote mutations, including partial failure and retry.

Use disposable accounts, namespaces, repositories, directories, and sentinels.
Never probe a destructive boundary against valuable or production state.

## Red/Green And Proof Freshness

For a hardening fix, first demonstrate that the boundary test fails for the
actual leak, not merely because a symbol or fixture is missing. Apply the minimum
fix, then prove allowed behavior still succeeds and forbidden behavior now fails
without side effects.

Fingerprint the effective policy, binary, host/runtime identity, authentication
mode, and relevant inputs. Treat cached proof as invalid when any fingerprinted
input changes. Configuration snapshots remain useful evidence, but they never
substitute for the effective-runtime probe.

## Completion Check

- Both allowed and forbidden rows ran.
- The probe used the effective runtime in isolation.
- Evidence came from an observer outside the constrained subject.
- Direct, indirect, ambient, state-class, network, and remote paths were covered
  when applicable.
- The red test reproduced the real leak before the fix.
- The proof records its invalidation fingerprint.
