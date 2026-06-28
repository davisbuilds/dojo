# HTTP API Design

Use this reference for HTTP, REST, RPC-over-HTTP, Next route handlers, Express
routers, and similar request/response APIs.

## Contents

- Design Checklist
- Review Red Flags
- Source Anchors

## Design Checklist

### Model Resources First

- Start with resources, ownership, identity, and lifecycle.
- Prefer nouns and stable relationships over action-specific endpoint sprawl.
- Use custom action endpoints only when standard create/read/update/delete/list
  semantics do not fit.
- Keep server-generated fields output-only: IDs, timestamps, audit fields, derived
  values, status transitions.

### Methods And Semantics

- `GET`: safe read, cacheable when appropriate.
- `POST`: create or command with side effects; support idempotency keys when
  clients may retry.
- `PATCH`: partial update; omitted fields remain unchanged.
- `PUT`: complete replacement only when callers can send the whole resource.
- `DELETE`: define whether delete is idempotent, soft, hard, async, or reversible.

Do not rely on HTTP method names alone; document side effects and retry safety.

### Request Shape

- Validate path, query, headers, and body at the edge.
- Separate create/update input schemas from output schemas.
- Avoid accepting fields the server ignores silently; either reject or document
  extension behavior.
- Bound payload size, list limits, date ranges, and query complexity.
- Treat third-party response payloads as untrusted input before transforming them
  into API responses.

### Response Shape

- Return a consistent envelope only if the project already uses one; otherwise
  favor direct resource objects for single resources and explicit list containers.
- List responses should include data plus pagination metadata or links.
- Include stable IDs and timestamps where consumers need synchronization.
- Use nullable fields deliberately. Prefer omitted optional fields for future
  extension only when the project convention supports that.
- Avoid response shapes that change type based on state.

### Errors

Pick one error shape and apply it everywhere. Include:

- Stable machine code
- Human-readable message
- Optional structured details
- Retryability or rate-limit metadata when relevant
- Correlation/request ID when useful for support

Map status codes consistently:

| Status | Use |
| --- | --- |
| `400` | Malformed syntax, invalid JSON, invalid query format |
| `401` | Not authenticated |
| `403` | Authenticated but not authorized |
| `404` | Resource absent or intentionally hidden |
| `409` | Conflict, duplicate, stale version, state transition conflict |
| `422` | Semantically valid request shape with invalid domain data |
| `429` | Rate limited; include retry guidance |
| `500` | Server error; do not expose internals |
| `503` | Temporary dependency/service unavailability |

Consider RFC 9457 Problem Details when the project does not already have a
standard error shape.

### Lists, Filtering, Sorting

- Add pagination before the first public release of any collection endpoint.
- Define default limit, max limit, ordering, and tie-breakers.
- Prefer cursor pagination when data changes frequently or offsets get expensive.
- Make filter names, enum values, date formats, and timezone behavior explicit.
- Document empty-list behavior separately from not-found behavior.

### Idempotency And Retries

- Make naturally idempotent operations idempotent in practice.
- For non-idempotent creates or commands, support client-provided idempotency keys
  when network retries are expected.
- Store enough idempotency metadata to detect parameter mismatches.
- Define expiry and replay behavior.
- Respect `Retry-After` or equivalent headers for throttling.

### Auth, Authorization, And Tenancy

- Authenticate before reading private resources.
- Authorize every object by tenant/user/project scope, not just route access.
- Avoid distinguishable `403`/`404` behavior when it leaks existence.
- Do not accept user IDs, tenant IDs, or ownership fields from the client unless
  the caller is explicitly authorized to act across scopes.

### Observability

- Log request ID, route, status, duration, caller class, and high-level failure
  category.
- Do not log secrets, tokens, prompts, raw private payloads, or sensitive PII.
- Emit metrics for latency, error rate, traffic, saturation/rate-limit hits, and
  dependency failures.
- Preserve correlation IDs across async jobs and downstream calls.

### Documentation And Schema

- Keep OpenAPI/schema/docs/examples in the same change as implementation.
- Document auth, rate limits, idempotency, pagination, errors, and examples, not
  just happy-path fields.
- If SDKs or clients are generated from schema, treat schema drift as a release
  blocker.

## Review Red Flags

- Endpoint returns different top-level shapes for success states.
- `POST` create has no idempotency story but clients may retry.
- List endpoint lacks pagination or stable ordering.
- Error format differs across routes.
- Validation is scattered inside internal helpers instead of at boundaries.
- Route accepts tenant/user ownership fields from ordinary clients.
- Internal exception text or stack traces reach clients.
- Docs/schema/types are not updated with behavior changes.

## Source Anchors

- Google AIP resource design: https://google.aip.dev/121
- Google AIP pagination: https://google.aip.dev/158
- Google AIP errors: https://google.aip.dev/193
- Microsoft REST API Guidelines: https://github.com/microsoft/api-guidelines
- RFC 9457 Problem Details: https://www.rfc-editor.org/info/rfc9457/
- Stripe idempotency: https://docs.stripe.com/api/idempotent_requests
