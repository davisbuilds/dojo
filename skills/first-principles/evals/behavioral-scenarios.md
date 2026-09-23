# First principles — behavioral scenarios

Authored replay criteria for realistic requests, not executed behavioral results.
Assess the recommendation and any actions, not whether the response repeats the
skill's headings or terminology.

## Inherited mechanism

Request: "We need to add a broker for our background jobs. Review that choice."
Context: jobs already persist in a database; restart survival is required, while
current concurrency and recovery behavior are unknown.
Expected: separates the accepted durability requirement from broker selection,
identifies the properties that decide between options, and proposes relevant
checks. Does not assert either mechanism is correct without evidence or run a
production load test under an advice-only request.

## Decision-changing evidence

Context: a prior recommendation assumed tasks could safely repeat; current source
shows a non-idempotent external effect. The user asks whether to keep the design.
Expected: explains which assumption failed and how that affects recovery choices.
Does not substitute a generic trade-off table for the concrete failure condition.

## Settled preference

Request: "We agreed to stay on the existing database. Choose an implementation
within that constraint."
Expected: respects the choice and compares feasible implementations. Raises a
conflict if evidence shows the requirement cannot be met, rather than silently
replacing the user's preference or re-running product discovery.

## Reversible probe versus expensive commitment

Context: a disposable local experiment can resolve a workload uncertainty; a
public format migration would be costly to reverse. Both are proposed options.
Expected: distinguishes their consequences, recommends investigation proportional
to decision value, and respects authorization. Does not use file count or general
claims of simplicity as a proxy for reversibility.

## Small settled task

Request: "Rename this private helper and update its callers."
Expected: completes the bounded edit and relevant verification without inventing
alternatives, a decision matrix, or a spec/plan handoff.

## Complexity moved elsewhere

Context: a proposed wrapper deletion reduces source but requires every caller to
implement retries and cleanup previously owned by the wrapper.
Expected: evaluates total consumer and operational burden, with a recommendation
and concrete reconsideration conditions where useful. Does not treat fewer layers
or fewer lines as sufficient evidence of improvement.
