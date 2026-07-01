---
name: api-design
description: Design and review robust API and interface contracts. Use when creating or changing HTTP endpoints, GraphQL/RPC-style APIs, webhooks, SSE/event streams, exported DTOs/types, service-layer boundaries, CLI JSON/stdout/exit-code contracts, versioning/deprecation plans, or any compatibility-sensitive boundary between consumers and providers.
skill-type: workflow
version: 1.0.0
---

# API Design

Design, review, and hand off API/interface contracts that are explicit, stable,
hard to misuse, and robust under real production failure modes.

## Scope

Use this skill for:

- HTTP APIs, route handlers, REST/RPC-style endpoints, and GraphQL schemas
- Webhooks, event payloads, queues, SSE streams, and ingestion contracts
- Exported types, DTOs, service interfaces, SDK/library surfaces, and module boundaries
- CLI machine contracts: `--json`, stdout/stderr, exit codes, config/env precedence
- Compatibility-sensitive changes with known or possible consumers

## Boundaries

- Do not implement broad code changes directly from this skill; hand off to
  `write-plan` when implementation spans files or phases (or `write-spec` first if
  the target still needs to be pinned as a falsifiable contract).
- Do not duplicate security review, CLI design, or test methodology that sibling
  skills already own.
- Do not treat undocumented behavior as free to break; observable behavior can
  be a consumer contract.

## Workflow

### 1. Classify The Surface

Identify every boundary being created or changed:

- **HTTP/API route**: method, path, request, response, errors, auth, rate limits
- **Event/stream**: event name, schema, ordering, replay, delivery semantics
- **CLI/machine output**: args/flags, stdout/stderr, JSON schema, exit codes
- **Typed interface**: exported type, DTO, service method, SDK/library function
- **Cross-client contract**: web/mobile/backend/database shape or behavior

If CLI design is central, route to `create-cli` after capturing the API-level
compatibility concerns.

### 2. Identify Consumers And Promises

Before designing fields or code, write down:

- Consumers: current callers, future callers, humans, scripts, SDKs, mobile apps,
  background jobs, third-party integrations
- Promise level: public, partner, internal multi-module, private implementation
- Compatibility risk: fields, status codes, ordering, timing, nullability, error
  text/codes, side effects, retry behavior, pagination defaults
- Migration needs: deprecation window, changelog/docs, dual reads/writes,
  compatibility aliases, feature flags, version negotiation

Treat every observable behavior as a potential dependency. Prefer additive,
optional, extension-friendly changes over type changes, removals, renamed fields,
or overloaded meanings.

### 3. Design Contract First

Specify the contract before implementation:

- Resource or domain model: nouns, ownership, identity, lifecycle
- Inputs: path/query/body fields, command args, event fields, typed parameters
- Outputs: success shape, empty states, generated fields, timestamps, ordering
- Errors: stable machine-readable code, human message, details shape, retryability
- Authz/authn: caller identity, tenant/user scoping, permission failures
- Side effects: idempotency, partial failure, transactional boundaries
- Lists: pagination, filtering, sorting, stable cursors or page semantics
- Limits: rate limits, max payload size, timeout behavior, concurrency rules
- Observability: logs, metrics, traces, audit events, correlation/request IDs
- Documentation: OpenAPI/schema/docs/examples or typed public declarations

Read `references/http-apis.md` for HTTP-specific details, `references/events-streaming.md`
for event/stream contracts, and `references/interface-contracts.md` for typed or
CLI-facing interfaces.

### 4. Review Robustness

Check implementation risks before coding:

- Validate and parse at trust boundaries; convert untrusted input into strong
  domain types before internal logic.
- Validate third-party responses before using them in decisions or rendering.
- Keep internal helper types private unless they are intended consumer contracts.
- Make unsafe retries safe with idempotency keys, natural idempotence, or explicit
  duplicate handling.
- Bound work: payload sizes, pagination limits, timeouts, concurrency, and query
  complexity.
- Do not leak internals, secrets, tenant data, stack traces, SQL details, or model
  prompts in error responses.
- Define negative paths: malformed input, unauthorized, forbidden, not found,
  conflict, validation failure, rate limited, dependency failure, timeout.

Use `secure-code` when the boundary combines untrusted input, private data, auth,
external calls, SSRF/file/network access, or sensitive logs.

### 5. Plan Compatibility And Verification

For new APIs:

- Include compatibility hooks from the start: pagination, extensible objects,
  stable error shape, version/deprecation policy where needed.
- Add request/contract tests at the boundary, not only unit tests inside the
  implementation.

For changed APIs:

- Classify each change as additive, behavior-preserving, behavior-changing, or
  breaking.
- Find consumers before changing the provider.
- Preserve old behavior or create a migration path when consumers may depend on it.

Read `references/compatibility-review.md` and `references/implementation-verification.md`.
Use `test-strategy` for the actual test plan and `write-plan` for multi-step
implementation plans (the API contract can feed `write-spec` first).

## Output

Return one of these artifacts, matching the user's task:

- **API design packet**: consumers, contract, examples, errors, compatibility
  decisions, robustness notes, verification plan, and open questions.
- **Review findings**: ordered risks with file/line references when reviewing code,
  each tied to consumer impact and a concrete fix.
- **Implementation handoff**: scoped contract decisions plus a recommendation to
  proceed with `write-spec` (pin the contract) or `write-plan` (sequence multi-file
  implementation), `test-strategy`, `secure-code`, or `create-cli`.

## Verification

Before calling an API design/review complete, confirm:

- Consumers and compatibility promises are explicit.
- Inputs, outputs, errors, auth, side effects, and list semantics are specified.
- Trust boundaries and validation/parsing locations are clear.
- Retry/idempotency, rate limits, timeouts, and partial failures are addressed
  where relevant.
- Contract tests or request-level integration tests are planned.
- Documentation/schema/types will change in the same work as implementation.
- Adjacent skills have been used or explicitly routed when their scope applies.

## Resources

- `references/http-apis.md` — HTTP/REST/RPC-style endpoint design and review.
- `references/interface-contracts.md` — typed module, DTO, SDK/library, and CLI
  machine-output contracts.
- `references/events-streaming.md` — webhooks, event payloads, queues, SSE, and
  streaming contracts.
- `references/compatibility-review.md` — breaking-change taxonomy, versioning,
  deprecation, migrations, and consumer-driven review.
- `references/implementation-verification.md` — contract tests, negative paths,
  observability checks, docs sync, and release gates.

## Sibling Skills

- `write-spec` — make the target falsifiable: turn the API direction into a
  contract (`docs/specs/`) before sequencing.
- `write-plan` — sequence the build: tasks, files, steps (`docs/plans/`) when
  implementation spans multiple files, phases, migrations, or verification gates.
- `test-strategy` — use for behavior-first API tests, request-level integration
  tests, contract tests, and mock/real-dependency decisions.
- `secure-code` — use for security-sensitive APIs, trust boundaries, authz/authn,
  private data, SSRF/file/network access, or external communications.
- `create-cli` — use when designing CLI args/flags, help text, JSON output,
  stdout/stderr, exit codes, prompts, config/env precedence, or dry-run behavior.
- `first-principles` — use when API architecture tradeoffs dominate the risk.
