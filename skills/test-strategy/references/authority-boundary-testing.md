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

## Match Network Proof to the Claim

A loopback server or an injected dialer can prove parsing and refusal logic,
but cannot prove that production connected to the public address it validated.
For claims about public-destination enforcement and working public egress,
keep these obligations distinct:

1. **Deterministic policy tests** for URL parsing, allow/deny rules, and refusal
   paths. These can and should use fixtures.
2. **The actual connected peer**, observed from the real transport — the resolved
   remote address the socket reached, not the URL the subject was asked to fetch.
   The requested URL is intent; the peer is authority.
3. **A fixed public end-to-end control** that exercises the real egress path to a
   known external destination.

These are evidence boundaries, not a demand for public network access on every
test task. A parser-only claim needs policy tests; a claim about the real
transport needs peer observation; a claim about working public egress needs
an authorized external control. If the relevant runtime or network access is
unavailable, state which claim remains unverified rather than silently treating
a substitute as proof.

A loopback fixture must never be cited as proof that a "public" destination is
enforced: the transport never left the host. An SSRF allow-test whose "public"
request terminates at a loopback fixture proves nothing about production egress.

## Red/Green And Proof Freshness

For a hardening fix, first demonstrate that the boundary test fails for the
actual leak in disposable state, not merely because a symbol or fixture is
missing. An existing reproducible pre-fix failure can supply this evidence. Do
not reenact an exploit against valuable state to satisfy the sequence. Apply
the fix, then prove allowed behavior still succeeds and forbidden behavior now fails
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
- Network evidence matches the claim: policy logic, real peer, and public egress
  are distinguished; no loopback fixture stood in for public-destination proof.
- The hardening regression check demonstrates the real pre-fix failure safely,
  or the missing evidence and its consequence for the claim are explicit.
- The proof records its invalidation fingerprint.
