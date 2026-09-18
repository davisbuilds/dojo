---
name: brainstorming
description: Clarify what to build from a vague idea or feature request. Use when requirements are unclear, multiple directions need exploration, or material trade-offs need discussion before planning. Reuse settled direction; save a design summary only when requested or useful for downstream work.
skill-type: workflow
version: 3.0.0
---

# Brainstorming

Help the user settle the decisions that matter. A useful conversation and concise
synthesis are sufficient unless a durable design summary has a real consumer.

## When To Use

- A request has materially different interpretations or unresolved trade-offs.
- The user wants to explore alternatives before choosing a direction.

If the request is already clear, continue the authorized task. Do not ask for
permission merely to skip brainstorming or switch skills.

## Boundaries

Stay within the requested scope. A discussion-only request does not authorize
implementation. When the user has authorized implementation, resolve material
uncertainty and continue once the direction is settled; do not manufacture a
separate approval gate because this skill was consulted.

Consult sibling guidance only for the concern that needs it. Reading a sibling
does not activate its workflow or require its artifacts. Follow higher-priority
harness loading rules.

## Workflow

Ground the discussion in available project context and the user's stated goals.
Resolve repository lookups yourself. Ask about decisions that materially change
scope, behavior, constraints, or the meaning of success; do not repeat questions
already answered. Use one focused question when the answer determines the next
question; batch independent questions when that is easier for the user.

Compare plausible approaches and recommend one with the reasons that matter.
There is no fixed option count: don't invent alternatives or a formal comparison
when the direction is clear. Explain meaningful trade-offs and remaining
uncertainty without prescribing a full implementation plan.

Summarize the settled direction, constraints, and open decisions. Concrete
success criteria are welcome if they are already clear; do not defer a useful
decision solely because another skill names that phase.

## Output

Default to a concise conversational synthesis. Write or update a design summary
when requested, required by the project, or useful for coordination, later
execution, or preserving decisions. Reuse an existing artifact rather than
creating a duplicate.

For a new saved summary, use `docs/design/YYYY-MM-DD-<topic>-design.md` and the
following scaffold as useful. Resolve `author` to the producing agent. The body
sections are suggestions, not a completeness checklist.

```markdown
---
date: YYYY-MM-DD
author: <agent>
topic: <kebab-case-topic>
stage: brainstorm
---

# <Topic Title>

## Problem / Context
[The user's goal and the decisions needing discussion]

## Chosen Direction
[The approach and why it fits]

## Alternatives Considered
[Only meaningful alternatives and trade-offs]

## What Good Looks Like
[Agreed outcomes, reusing any existing acceptance criteria]

## Open Questions
[Only unresolved decisions, or None]

## Constraints
[Relevant limits and existing authority]
```

Recommend a next step only when it helps. Continue already-authorized work when
appropriate; otherwise end with the synthesis or the decision needing user input.
No compulsory handoff menu, critique, or closing phrase.

## Verification

The synthesis reflects the user's intent, relevant trade-offs, and unresolved
questions. Distinguish a recommendation from a user-approved direction. Saved
summaries preserve the decisions and resolved author metadata; conversation-only
work needs no file. Implementation authority comes from the user, not the summary.

## Resources

- `references/platform-mapping.md` — optional harness invocation details.
- `commands/workflows/brainstorm.md` — command wrapper for supported harnesses.

## Sibling Skills

- `write-spec` — when the target needs a durable falsifiable contract.
- `write-plan` — when dependencies or rollout ordering need an execution plan.
- `first-principles` — for a material architectural trade-off needing deeper analysis.
- `deep-research` — when missing external evidence affects the decision.
