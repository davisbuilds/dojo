# Agent-Facing Interfaces

Use when a service, CLI, tool, or data surface must support an agent's work.
Start with the outcomes it needs to support and the authority of its caller.
The interface may serve an external agent without embedding a model itself.

## Choose an operation the agent can use correctly

Expose meaningful capabilities in the domain's vocabulary. Granularity follows
state and responsibility boundaries, not UI buttons or database tables.

For example, `reserve_slot` may need to check availability and create a reservation
atomically. Splitting it into `read_calendar` and `insert_reservation` transfers a
race condition to the caller. Conversely, a single `manage_business` operation
conceals choices the caller may need to make. Offer composable operations where
composition preserves the required invariants; use domain operations where they
make those invariants dependable.

Keep calculation, validation, authorization, and transactional updates in code
when those are the source of correctness. An agent can decide which valid action
to request. Structured inputs can express that decision without making the tool
less useful. Prefer bounded schemas for stable domains; use runtime discovery for
evolving capabilities when discovery improves usability. Discovery exposes what
exists or is available, not permission to invoke everything it finds.

When adapting an existing product, inspect the intended delegated outcomes for
missing capabilities. Reuse its service layer so agent and human paths respect
the same state transitions. Read-only access, drafts requiring release, and
human-only actions can all be deliberate. Do not add delete to an append-only
ledger to complete a CRUD matrix.

## Make context economical and attributable

An agent needs enough context to choose a valid action, not a dump of every
record and tool definition. Make summaries, filtered queries, pagination, and
specific resource lookup available where volume warrants them. Retain stable
identifiers across those views so the agent can act on what it found.

Distinguish no matches from denied access, incomplete retrieval, stale data, and
unsupported queries. Include source or revision information when a later action
depends on what was read. Separate supplied facts, user preferences, external
content, and executable instructions; retrieved content does not become authority.

Prefer one authoritative state with consistent views. That can be a service,
database, or workspace; it need not mean unrestricted shared filesystem access.
A staging area is useful when drafts require validation or publication. Make the
transition to committed state visible to the agent and the human who relies on it.

## Provide evidence operations alongside action operations

An actionable result identifies what happened, to which resource, and what can
be checked next. For asynchronous work, return a durable operation reference and
its current state rather than calling acceptance completion. For a synchronous
operation, a result with the affected resource and revision may be sufficient;
do not introduce a job protocol without a need.

An investigation interface can be more valuable than another action tool:
compare expected and observed state, inspect provenance, run a bounded probe, or
explain why a result is incomplete. Use the same underlying implementation as the
product when measuring its behavior, while checking outcomes against state that
can contradict the action's self-report. A probe that reimplements the product
can drift; a check that only repeats the producer's assertion can miss its failure.

For example, an index experiment can run on a disposable database copy and
report which queries were compared, which failed, and what each timing measures.
A partial route sample must not masquerade as whole-application coverage. A sum
of separately timed query medians is not endpoint latency. These distinctions
allow the consuming agent to reason about the result without guessing its scope.

Keep mutation scope enforceable in the tool. A flag labelled "snapshot only" is
not a boundary if an arbitrary SQL script can attach and modify another database.
Validate the allowed operation before executing it. Label retained snapshots,
transcripts, or other content-bearing evidence so cleanup and sharing decisions
can account for them.

## Keep recovery visible in the contract

For writes that may be retried after a timeout, provide a way to determine whether
the original request took effect. An idempotency key, stable external reference,
or authoritative lookup may solve this; choose the mechanism the operation needs.
An ambiguous response is not evidence that nothing happened.

Where concurrent writers matter, reject or reconcile stale updates using the
underlying service's concurrency controls. Return enough information to recover
without silently overwriting newer work. Cancellation, deletion, and compensation
are different operations; describe the supported effect rather than promising
universal undo.

Evaluate the actual consumer path. Useful checks include whether an agent can
find the operation, select the intended resource, distinguish partial results,
and recover from an ambiguous failure. Direct API tests establish contract
behavior; they do not alone prove that an agent can discover and use it well.
