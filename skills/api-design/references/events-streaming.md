# Events And Streaming Contracts

Use this reference for webhooks, event ingestion APIs, queues, pub/sub payloads,
Server-Sent Events, streaming responses, and live update feeds.

## Event Contract

For every event type, define:

- Event name and version
- Producer and consumers
- Required and optional fields
- Stable event ID or dedupe key
- Subject/resource ID
- Timestamp semantics and timezone
- Causality/correlation IDs
- Delivery semantics: at-most-once, at-least-once, exactly-once illusion, replay
- Ordering guarantees, if any
- Retention/replay window
- Privacy classification and redaction rules

## Schema Evolution

- Add optional fields; do not rename or remove fields without a migration path.
- Version event names or schema versions when consumers cannot safely ignore new
  shapes.
- Reserve namespaces or extension objects for producer-specific metadata.
- Document whether consumers must ignore unknown fields.
- Keep examples for old and new versions during migration.

## Idempotency And Deduplication

- Consumers should be able to process duplicate events safely.
- Include an event ID, operation ID, or natural dedupe key.
- Make handler side effects idempotent or record processed IDs.
- Define retry and dead-letter behavior for poison messages.

## Ordering And Replay

- Do not imply total ordering unless the system enforces it.
- If ordering matters, define partition key, sequence number, or cursor.
- Streaming APIs should define reconnect behavior and `Last-Event-ID` or cursor
  semantics when replay is supported.
- Backfills and replays should be distinguishable from new real-time events when
  consumers need that distinction.

## SSE And Streaming Responses

- Define event names, data schema, heartbeat cadence, reconnect delay, and close
  conditions.
- Bound active clients and memory used for replay history.
- Include filters in the contract if clients can subscribe to subsets.
- Do not rely on clients receiving every live event unless replay is available.
- Test disconnect/reconnect, slow clients, malformed filters, and client-limit
  errors.

## Webhooks

- Sign payloads and document signature verification.
- Include timestamp and replay protection.
- Support retries with clear backoff and terminal failure behavior.
- Provide stable event IDs and idempotency guidance.
- Document acknowledgement timing and acceptable response codes.

## Review Red Flags

- Event type has no version or compatibility policy.
- Consumers must infer order from wall-clock timestamps.
- Retry can duplicate side effects.
- Event payload exposes private internals or provider-specific raw data.
- SSE endpoint has no heartbeat, max clients, or reconnect story.
- Webhook lacks signature verification or replay protection.

## Source Anchors

- Zalando RESTful API and Event Guidelines:
  https://opensource.zalando.com/restful-api-guidelines/
- GraphQL best practices for evolving schemas:
  https://graphql.org/learn/best-practices/
- GitHub REST best practices for webhooks/rate behavior:
  https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api
