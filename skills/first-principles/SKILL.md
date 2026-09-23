---
name: first-principles
description: "Systems-level reasoning for high-stakes technical decisions. Use when choosing between architectures, evaluating trade-offs, or planning a non-mechanical refactor. For debugging a specific failure use diagnose; for clarifying an ambiguous WHAT use brainstorming."
skill-type: reference
version: 3.0.0
---

# First Principles

Scrutinize the problem framing and make consequential recommendations whose
basis and limits are clear. Challenge assumptions in the proposed solution,
existing implementation, and your own recommendation with the same standard.
Disagree directly when evidence warrants it, explaining the practical consequence.

## When To Use

- An architectural choice or non-mechanical refactor has consequential trade-offs.
- A proposed mechanism may be solving the wrong problem or carrying inherited
  constraints that deserve examination.
- A design review needs to identify which assumptions could change the decision.

## Boundaries

- Skip mechanical work and settled choices that have no material new uncertainty.
- Preserve the user's objective, preferences, and authority. Challenge mechanisms
  without silently replacing requirements. Reopen an accepted decision only when
  consequential new evidence or a conflict warrants it; explain what changed.
- Use the lenses below where they help. They are not sequential stages, a required
  checklist, or a demand for alternatives when no credible contender exists.
- Consultation adds reasoning to the current task. It does not require a separate
  report, a spec/plan pipeline, implementation, or extra approval.

## Decision Lenses

### Separate constraints from inherited choices

Identify the outcome that matters and what actually constrains it: consumer
contracts, authority boundaries, resources, or physical limits. Distinguish those
from current implementation choices, conventions, and untested assumptions.
Existing practice can carry useful evidence and migration costs; being conventional
is neither a sufficient justification nor a reason to discard it.

Question whether a proposed mechanism is necessary for the outcome. Consider
keeping the current approach or a smaller change when either is a credible option.
Decompose only where it exposes a dependency or uncertainty that matters.

### Find the assumptions that could change the choice

Focus on assumptions whose failure would alter the recommendation. Explain the
connection: if this assumption is false, which option becomes preferable, and why?
Distinguish observed facts, inferences, and unresolved questions using available
source, runtime, or domain evidence. Avoid unsupported confidence labels or an
inventory of premises that do not affect the decision.

Look for evidence that would disconfirm the favored approach. When an unknown
matters, identify a bounded probe or the missing input that could resolve it.
Use existing evidence when it is sufficient; a familiar pattern is a starting
point, not proof that it fits this case.

### Weigh reversibility and further investigation

Account for the cost of changing course: migration, public contracts, persisted
data, operational dependencies, and effects that cannot simply be rolled back.
A small diff can still make an expensive commitment.

Prefer a bounded experiment when it can settle an important uncertainty cheaply
and within the user's authority. Investigate further when the result could change
the choice and the cost of being wrong warrants it. When further analysis is
unlikely to matter, act within the agreed scope and state any remaining limits.
Check whether the recommendation remains reasonable across plausible conditions
rather than depending on one optimistic estimate.

### Follow the complexity and name reconsideration conditions

Trace costs across the system. A simpler interface may move complexity into
callers, operators, recovery, or future migrations. Compare concrete consequences
for the relevant consumers rather than counting abstractions or invoking a design
principle as a verdict.

For consequential recommendations, explain what would change your mind: a failed
assumption, new requirement, workload boundary, or observed operational friction.
Do not invent a numeric threshold to make the recommendation look precise; name
how to establish one when the decision requires it.

## Worked Example

Suppose the user asks whether a background-job service needs a new message broker.
The existing service already stores jobs in a database, and the accepted contract
requires jobs to survive restarts. The design question is which mechanism meets
that contract at an acceptable operating cost; adding a broker is one option.

A recommendation to retain database-backed jobs might depend on safe concurrent
claiming and adequate throughput. Inspect the existing implementation and test
those properties under representative conditions if they remain uncertain. A
successful enqueue alone does not establish recovery or duplicate-effect behavior.
Compare the recovery and operating burden of both designs. If the existing path
meets the contract, keeping it may avoid an unnecessary service; failed recovery
checks or an unmet workload requirement could change that recommendation. The
request for advice does not itself authorize a migration or a production load test.

## Verification

Judge the recommendation by whether its decisive assumptions, evidence, concrete
trade-offs, and material uncertainties are clear. For a consequential unresolved
assumption, identify how to resolve it or explain why a bounded decision can
proceed despite it. Reuse accepted success criteria; when authorized implementation
follows, check the behavior on which the recommendation depended.

Present the conclusion and the evidence needed to assess it in the user's
requested format. No required decision matrix, option count, or reasoning transcript.

## Resources

- `evals/behavioral-scenarios.md` — authored cases for decision quality and scope;
  these are replay criteria, not measured model-performance results.

## Related Guidance

- `diagnose` — investigate a specific failure whose cause is unclear.
- `brainstorming` — clarify an unresolved target or product direction.
- `deep-research` — gather external evidence when the decision depends on it.
- `write-spec` / `write-plan` — consult when material contract or execution
  decisions need resolution, or when a durable artifact has an actual consumer.
  They are not automatic next stages.
