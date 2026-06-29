# Implementation Verification

Use this reference to turn an API design or review into concrete verification.
Pair with `test-strategy` when writing tests.

## Test Layers

- **Schema/type tests**: parser accepts valid payloads and rejects invalid ones.
- **Request-level integration tests**: exercise the actual route/handler boundary.
- **Consumer contract tests**: verify examples expected by real consumers.
- **Permission tests**: authenticated, unauthenticated, unauthorized, cross-tenant.
- **Failure-path tests**: malformed input, validation, not found, conflict,
  dependency failure, timeout, rate limit.
- **Compatibility tests**: old fields/aliases/versions still work during migration.
- **Observability tests/checks**: logs/metrics/traces exist without leaking secrets.

Do not rely only on controller unit tests for API behavior. Test the observable
contract at the boundary when feasible.

## Contract Test Checklist

For each endpoint/interface/event/CLI output:

- Happy path returns the documented success shape.
- Minimal valid input works.
- Maximal valid input works.
- Unknown or future fields behave as documented.
- Invalid JSON/input returns the standard error shape.
- Validation failures include stable machine-readable details.
- Auth and authorization failures do not leak private resource existence.
- Empty state differs from not found.
- Pagination limit, ordering, and cursor/page behavior are stable.
- Duplicate/retried mutative requests are safe or explicitly rejected.
- Docs/examples match tested behavior.

## Idempotency And Retry Tests

For mutative APIs:

- Repeating the same idempotency key and same parameters returns the same result
  or a documented replay response.
- Reusing an idempotency key with different parameters fails deterministically.
- Retry after dependency timeout does not duplicate side effects.
- Delete/update operations behave predictably when repeated.
- Rate-limit responses include retry guidance when promised.

## Event And Stream Tests

- Duplicate event handling is safe.
- Out-of-order events do not corrupt state or are rejected explicitly.
- Replay from cursor/last event ID works when documented.
- Slow or disconnected clients are cleaned up.
- Client limit and backpressure behavior is observable.
- Webhook signatures, timestamp tolerance, and replay protection are tested.

## CLI Contract Tests

Use `create-cli` for full CLI design. Verify:

- `--json` output parses on success.
- Failure output follows the documented machine contract if one exists.
- Human diagnostics go to stderr when stdout is machine-readable.
- Exit codes match documented failure classes.
- TTY/color/verbosity settings do not break parsers.

## Release Gates

Before shipping:

- Run project-specific lint/type/test/build checks.
- Run API-specific contract/integration tests.
- Regenerate OpenAPI/schema/client artifacts if applicable.
- Update docs, examples, changelog, and migration notes.
- Check logs/metrics/traces for the new route/event/contract.
- Confirm generated manifests or dead-code gates account for exported public
  types intentionally used outside the repository.

## Review Red Flags

- Tests assert internal service calls instead of observable API behavior.
- Only happy-path tests exist.
- Snapshot update hides a response shape change.
- No test proves backward compatibility during migration.
- Docs examples are not covered by any test or manual verification.
- Security-sensitive boundary changed without authz and cross-tenant tests.

## Source Anchors

- Test Strategy skill: `../../test-strategy/SKILL.md`
- Pact documentation: https://docs.pact.io/
- OpenAPI Specification: https://swagger.io/specification/
- GitHub REST API best practices:
  https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api
