# Interface Contracts

Use this reference for exported types, DTOs, service-layer APIs, SDK/library
functions, internal module boundaries, Pydantic/Zod schemas, and CLI machine
contracts.

## Typed Boundaries

- Design input and output types separately.
- Keep helper types file-local unless another module is meant to consume them.
- Prefer domain-specific types over plain strings/numbers for IDs, money, units,
  time ranges, and state transitions.
- Use discriminated unions or tagged variants for state with different required
  fields.
- Avoid boolean parameter traps; use named options or richer types when meaning is
  not obvious at the call site.
- Use builders/options objects for complex or evolving construction.

## Parse At Boundaries

- Parse untrusted data into a stronger type at the boundary.
- After parsing, internal code should be able to rely on the type instead of
  repeatedly checking the same conditions.
- Validate environment variables, config files, database JSON blobs, external API
  responses, request bodies, and CLI input before use.
- Do not parse by scattered ad hoc string checks when a structured schema/parser
  is available in the project.

## DTO And Domain Separation

- Do not expose database rows directly unless the row shape is intentionally the
  public contract.
- Keep API DTOs stable even if persistence or third-party provider shapes change.
- Normalize provider-specific errors and payloads before crossing internal
  service boundaries.
- Treat serialized JSON field names as consumer-visible API, even inside a CLI or
  local pipeline.

## Evolution Rules

- Add optional fields before requiring them.
- Add enum values only when consumers are expected to tolerate unknown values.
- Never reuse a field name for a new meaning.
- Avoid changing nullability, units, timezone interpretation, sorting, or default
  limits without a migration plan.
- For TypeScript, avoid widening exported types in ways that let invalid states
  compile.
- For Python/Pydantic, keep serialization aliases and model config stable when
  consumers read emitted JSON.

## CLI Machine Contracts

For CLI APIs, apply `create-cli` for full design. At API-review level, ensure:

- Machine-readable output has an explicit schema and stable top-level shape.
- Human output and diagnostics go to stderr when stdout is intended for piping.
- `--json` output remains parseable on success and failure if promised.
- Exit codes are documented and tested.
- `--quiet`, `--verbose`, color, TTY detection, and `NO_COLOR` do not change
  machine-output semantics.
- Config/env/flag precedence is deterministic.

## Hard-To-Misuse Interfaces

- Make the easy call the correct call.
- Require explicit names for dangerous or irreversible options.
- Make illegal states unrepresentable when the language allows it.
- Return structured results instead of forcing callers to parse messages.
- Prefer explicit errors over sentinel values when absence and failure differ.
- Avoid exposing timing/order/concurrency details unless they are intended
  commitments.

## Review Red Flags

- Exported type is only used in one file and has no documented consumer.
- Function accepts several same-typed primitives whose order is easy to swap.
- JSON output changes field names or nesting without migration.
- Third-party API payload is cast directly to a trusted internal type.
- Internal enum value leaks into a public API.
- Error handling requires consumers to string-match human messages.

## Source Anchors

- Joshua Bloch, "How to Design a Good API and Why it Matters":
  https://research.google.com/pubs/archive/32713.pdf
- Hyrum's Law: https://www.hyrumslaw.com/
- Rust API Guidelines checklist: https://rust-lang.github.io/api-guidelines/checklist.html
- Parse, don't validate: https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/
