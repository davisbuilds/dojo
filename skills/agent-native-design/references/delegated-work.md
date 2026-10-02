# Delegated Work

Use when a system carries out a responsibility through agents, especially across
sessions, tools, or organizations. Scale the machinery to the duration and
consequence: a one-shot draft may need no scheduler, durable queue, or handoff.

## Separate judgment from enforcement

Express the outcome, relevant context, permitted discretion, and reasons to
return control. Let the agent choose an approach where that freedom serves the
job. Preserve fixed ordering where dependencies or an irreversible effect require
it. Reuse the user's established authorization rather than asking again at every
step, but do not infer additional authority from a broad outcome.

An invoice assistant might interpret a service report and propose line items.
The billing service should still enforce totals, account ownership, and the
conditions for issuing an invoice. Neither a convincing explanation nor another
agent's approval substitutes for the executing service's authorization check.

When mistakes recur, repair the owning cause: missing data, ambiguous interfaces,
unreliable implementation, or unclear instructions. More prompt rules are one
possible response. A correction log is evidence for improvement, not an automatic
source of standing policy or permission.

## Make ongoing responsibility durable

For work that survives a session, preserve enough state to resume without
replaying committed effects: current intent, responsibility owner, relevant
constraints, committed actions, unresolved questions, and the next recoverable
step. Put each fact in its authoritative store and reference it where possible;
a longer transcript is not necessarily a usable checkpoint.

Separate the execution lifecycle from the business outcome. A worker exiting,
an agent saying "done," and a customer receiving the intended result may be
three different events. Explicit completion signals help coordination; verify
the consequential effect with an appropriate readback or external observation.

A changed instruction may invalidate queued work or a prepared action. Bind
consequential actions to the relevant task or resource revision, and recheck it
at the point of commitment when stale work could cause harm. Determine what a
stop request can actually stop; already committed effects may require a separate
recovery action. Show unresolved outcomes instead of labelling them cancelled.

## Coordinate across agents without multiplying ambiguity

Use another agent when it contributes access, expertise, independent evidence,
or useful parallel work. More agents do not themselves establish better judgment
or independent verification, especially when they share the same faulty premise.

At a handoff, distinguish these questions when relevant:

- Who is responsible for the next action, and how does acceptance become known?
- What intent, constraints, evidence, and current state does the recipient need?
- What authority is actually delegated, by whom, for which resources and duration?
- How are progress, requests for clarification, and results correlated to the work?
- What happens after a lost reply, duplicate delivery, expiry, or changed intent?

Receiving a task or context does not grant the sender's permissions. Preserve
identity and access boundaries at each hop, including reads and onward disclosure.
Supply useful references or scoped context rather than copying all private memory.
Treat a counterparty's assertion as an assertion until the required evidence exists.

Use an existing protocol, service, or queue when it fits. Verify the concrete
platform's supported interfaces: access to a model API does not establish access
to a user's existing assistant, its memory, or its cancellation controls. Identify
unsupported integration assumptions before making them architectural dependencies.

## Bound execution and learn from outcomes

For unattended work, decide what ends a run: success evidence, an exhausted
budget, a deadline, a non-recoverable error, or a need for human judgment. Bound
retries around the external effect and available evidence, not just a loop count.
An uncertain write requires reconciliation before a retry that could duplicate it.

Make exceptions legible enough that a person can change the decision or take over
without replaying the whole session. Continue routine work within the delegated
scope; interruption should serve a decision, not demonstrate caution.

Verify the failure modes the design claims to handle. For a recurring process,
that might mean recovering after a committed write with a lost reply, rejecting
stale queued work, or resuming under the intended identity and permissions.
Measure accepted outcomes together with human attention, rework, and operating
cost. Low detected error rates are weak evidence when failures are not observable.
