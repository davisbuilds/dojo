---
name: api-design
description: Design and review robust API and interface contracts. Use when creating or changing HTTP endpoints, GraphQL/RPC-style APIs, webhooks, SSE/event streams, exported DTOs/types, service-layer boundaries, CLI JSON/stdout/exit-code contracts, versioning/deprecation plans, or any compatibility-sensitive boundary between consumers and providers.
skill-type: workflow
version: 2.0.0
---

# API Design

Design and review interfaces around their actual consumers, compatibility
promises, and failure modes. Apply the relevant checks while implementing an
already-settled change; a separate design packet is not a prerequisite.

## When To Use

- Designing or changing HTTP APIs, GraphQL/RPC endpoints, event streams,
  webhooks, exported types, service boundaries, or CLI machine output.
- Reviewing a compatibility-sensitive boundary or resolving its contract.

## Boundaries

Follow the user's scope: design, review, or authorized implementation. Consulting
this skill does not expand that scope. Reuse accepted requirements and existing
contract evidence. Multiple files or interface types alone do not require a spec
or plan.

Consult relevant sibling guidance without inheriting its workflow or output
requirements. Escalate only when a material contract decision, security concern,
implementation dependency, or verification problem remains unresolved. Follow
higher-priority harness loading rules.

Do not treat undocumented observable behavior as free to break. Establish which
consumers and compatibility promises apply before changing it.

## Workflow

Use the following concerns selectively; resolve the ones that affect this task.

### Consumers and promises

Identify current callers, public versus private promises, and dependencies on
fields, errors, ordering, timing, nullability, or side effects. Find consumers
before changing the provider. Prefer additive changes where compatibility is
promised; document intentional breaks and their migration path.

### Contract decisions

Pin unresolved inputs, outputs, error semantics, identity/ownership, authorization,
and effects. For lists, consider stable ordering, pagination, and limits; for
mutations, retries, idempotency, and partial failure. Reuse existing schemas,
types, examples, and tests instead of producing another version of the contract.

Read only the references relevant to the changed surface:

- `references/http-apis.md` — HTTP/REST/RPC conventions.
- `references/interface-contracts.md` — typed and CLI machine interfaces.
- `references/events-streaming.md` — ordering, replay, delivery, and backpressure.

### Robustness

- Parse and validate at trust boundaries, including third-party responses.
- Preserve authorization and tenant isolation on success and failure paths.
- Avoid leaking secrets, private data, or implementation internals in errors
  and observability output.
- Bound work where payloads, query complexity, concurrency, or timeouts matter.
- Make mutative retries safe or explicitly reject them; account for partial
  effects and recovery where applicable.

### Compatibility and proof

Classify the changed behavior as additive, preserving, changing, or breaking.
Use `references/compatibility-review.md` when consumers or migrations are at
risk. Use `references/implementation-verification.md` to select boundary tests
that prove the affected contract, including relevant failures and permissions.
Existing fresh tests can supply that evidence; do not repeat checks solely
because another skill was consulted. Keep affected schemas, examples, and docs
consistent with the implementation.

## Output

Match the requested task:

- **Design:** unresolved decisions, the resulting contract, and relevant
  examples, risks, and verification. A design packet is useful when a consumer
  needs one, not a mandatory intermediate for implementation.
- **Review:** findings tied to consumer impact and source evidence.
- **Implementation:** the authorized change and its compatibility/verification
  evidence, integrated into the task's existing report.

## Verification

The evidence supports the affected consumer promises, including relevant
negative paths. Unresolved compatibility, authority, recovery, and verification
risks are explicit. Claims about implemented behavior require behavioral proof;
a design or review alone does not establish that the code works.

## Sibling Skills

Consult only the concern that needs help:

- `create-cli` — CLI syntax and human/script UX.
- `secure-code` — a concrete security question or requested security scan.
- `test-strategy` — unresolved test coverage or dependency choices.
- `write-spec` — an unresolved target or requested durable contract.
- `write-plan` — dependencies or rollout ordering that need an execution plan.
- `first-principles` — material architectural alternatives.
