---
date: 2026-06-28
topic: api-design-skill
stage: brainstorm
---

# API Design Skill

## What We Are Building

Create a public dojo skill named `api-design` that helps agents design, review,
and plan robust API and interface contracts before implementation. The skill
should cover HTTP APIs, event and streaming contracts, machine-readable CLI/JSON
surfaces, and typed module boundaries because the local `~/Dev` portfolio uses
all of these as compatibility-sensitive APIs.

The skill should not become a generic encyclopedia. It should provide a compact
workflow in `SKILL.md`, then route to focused reference files when the task
needs protocol-specific depth.

## Why This Direction

The existing Addy Osmani source skill provides useful baseline principles:
contract-first design, consistent errors, boundary validation, additive changes,
pagination, Hyrum's Law, and internal interface discipline. The local project
survey shows that a pure REST skill would miss real contract surfaces:
`habits-ai` has Next API routes and web/iOS drift risk, `agentmonitor` has v1/v2
HTTP APIs plus SSE and ingestion events, `fetchmd` and `tokenmaxxing` expose CLI
JSON/exit-code contracts, and Python projects such as `feed`, `podsave`, and
`prism` rely on Pydantic schemas as stable pipeline boundaries.

Public usefulness points the same way. Strong external guidance from Google,
Microsoft, Stripe, Zalando, Shopify, Pact, OpenAPI, RFC 9457, Joshua Bloch,
Hyrum's Law, and the Rust API Guidelines converges on compatibility, clear
contracts, hard-to-misuse interfaces, explicit errors, idempotency, pagination,
versioning/deprecation, and consumer-aware verification.

## Key Decisions

- Scope the skill as a `workflow`, not a `reference` skill: users need a repeatable
  design/review process and an implementation handoff, not just a catalog of
  API rules.
- Cover "API" broadly as any stable boundary with consumers: HTTP routes,
  GraphQL/RPC-style endpoints, events/SSE/webhooks, exported types, DTOs,
  service-layer boundaries, CLI machine output, and cross-client contracts.
- Keep `SKILL.md` concise: include the decision flow, minimum checklist, output
  contract, verification gates, and sibling-skill routing.
- Put deeper guidance in one-level references: HTTP APIs, interface contracts,
  events/streaming, compatibility/review, and implementation verification.
- Do not add scripts initially: the value is judgment and structured review.
  Deterministic checks can be added later after observing repeated usage.
- Compose with existing dojo skills instead of duplicating them: use
  `write-spec` for implementation plans, `test-strategy` for contract tests,
  `secure-code` for trust-boundary/security review, `create-cli` for CLI
  surface design, and `first-principles` for high-stakes architecture choices.

## Constraints

- Follow dojo's progressive disclosure model and strict skill contract.
- Keep frontmatter trigger language specific enough to activate on API design,
  API review, endpoint/schema/event/CLI contract work, and compatibility changes.
- Avoid copying the third-party source skill verbatim; synthesize and improve it
  for dojo's conventions and public reuse.
- Keep references directly linked from `SKILL.md` and avoid nested reference
  trees.
- Update generated runtime inventory if hook automation does not do it.

## Success Criteria

- `skills/api-design/SKILL.md` passes strict skill validation.
- The skill can produce an API design/review packet with consumers, contract,
  compatibility risk, robustness checks, verification plan, and handoff.
- Protocol-specific details are discoverable without loading all references.
- The skill explicitly routes implementation planning and test/security/CLI
  concerns to the existing dojo skills that own those workflows.
- The dojo manifest and system docs reflect the new skill if required by local
  validation or project conventions.

## Open Questions

- Whether API lint/check scripts are worth adding after real use reveals common
  deterministic checks.

## Next Step

Proceed to planning with `write-spec`, then implement the skill from the spec.
