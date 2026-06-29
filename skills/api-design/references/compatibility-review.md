# Compatibility Review

Use this reference when changing an existing API/interface or creating a contract
that must survive future consumers.

## Contents

- Consumer Inventory
- Change Taxonomy
- Versioning Strategy
- Deprecation And Migration
- Consumer-Driven Verification
- Documentation Drift
- Review Red Flags
- Source Anchors

## Consumer Inventory

Identify:

- Direct code callers
- Generated SDKs or clients
- Mobile apps and older released binaries
- Scripts and automation
- Dashboards, reports, exports, and analytics jobs
- Third-party or partner integrations
- Tests that encode current behavior
- Documentation examples users may have copied

If consumers are unknown, assume observable behavior may be depended on and
prefer additive changes.

## Change Taxonomy

Usually safe:

- Add optional response fields.
- Add optional request fields with defaults.
- Add new endpoints without changing old ones.
- Add enum values only if consumers are required to tolerate unknown values.
- Loosen validation when it does not change stored/output semantics.

Risky or breaking:

- Remove, rename, or change type of a field.
- Change nullability, units, timezone, ordering, defaults, or pagination behavior.
- Change status code, error shape, error code, or retryability.
- Make optional input required.
- Tighten validation for previously accepted values.
- Reinterpret an enum/string value.
- Change side effects, idempotency, authorization, or visibility.
- Change CLI stdout JSON, stderr conventions, or exit codes.

## Versioning Strategy

Choose the smallest versioning mechanism that preserves consumers:

- No version: for private/internal surfaces with coordinated deploys.
- Additive evolution: preferred for most JSON and typed contracts.
- Field-level deprecation: when old and new fields can coexist.
- Endpoint or schema version: when behavior cannot be made compatible.
- Date or release version: when public API consumers need migration windows.
- Compatibility alias: when renamed concepts must coexist temporarily.

Avoid maintaining multiple versions casually. Every version multiplies testing,
docs, observability, and support obligations.

## Deprecation And Migration

A credible deprecation plan includes:

- Current behavior and replacement behavior
- Affected consumers and detection method
- Timeline and removal criteria
- Warnings in docs, changelog, response headers/logs, or API health reports
- Dual-read/write or adapter plan when needed
- Tests for old and new behavior during the transition
- Rollback plan if consumers are still active

## Consumer-Driven Verification

Use consumer-driven contracts when:

- Provider and consumer are deployed independently.
- Consumers are numerous or hard to audit.
- Schema validity alone is not enough to prove behavior.
- Backward compatibility is a release gate.

OpenAPI or type schemas prove shape. Consumer contracts prove expected
interactions and examples.

## Documentation Drift

Treat docs as part of the API:

- Update docs/schema/types in the same change as implementation.
- Keep examples runnable or at least syntactically valid.
- Mention auth, errors, pagination, rate limits, idempotency, and versioning.
- Remove stale docs when behavior is removed.
- Make migration notes concrete enough for an external consumer.

## Review Red Flags

- "Internal only" API has multiple independent callers.
- No one checked mobile/SDK/CLI/script consumers.
- Tests update snapshots without explaining consumer impact.
- New enum value has no unknown-value handling story.
- Version bump is proposed without deprecation, docs, or support plan.
- Old behavior is removed because it was "undocumented."

## Source Anchors

- Hyrum's Law: https://www.hyrumslaw.com/
- Martin Fowler, Consumer-Driven Contracts:
  https://martinfowler.com/articles/consumerDrivenContracts.html
- Pact documentation: https://docs.pact.io/
- Shopify API versioning: https://shopify.dev/docs/api/usage/versioning
