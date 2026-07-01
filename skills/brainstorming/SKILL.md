---
name: brainstorming
description: Use this when requirements are ambiguous, multiple approaches are plausible, or trade-offs need discussion before planning or implementation. Clarifies WHAT to build through one-question-at-a-time collaboration. Can be skipped when requirements are already explicit and well constrained.
skill-type: workflow
version: 1.0.0
---

# Brainstorming

This skill clarifies **WHAT** to build before deciding **HOW** to build it.

## When To Use

Use brainstorming when:
- The request is vague or open-ended
- Multiple reasonable interpretations exist
- Trade-offs have not been discussed
- Scope and success criteria are unclear

You can skip brainstorming when:
- Requirements are already explicit, testable, and well-scoped
- Scope is narrow and well-defined
- The user asks for direct implementation with clear constraints

## Boundaries

- If the task is already direction-clear, suggest skipping ahead to `write-spec` (the contract) or execution and ask for confirmation
- Do not write code, modify files, or invoke implementation skills until the user has approved the design summary (or explicitly chooses to stop brainstorming)
- Stay on WHAT to build; implementation details belong to planning

## Core Process

### Phase 0: Assess Clarity

Before asking detailed questions, decide whether brainstorming is needed.

Signals requirements are already clear:
- Acceptance criteria are specific
- Expected behavior is precise
- Existing implementation pattern is identified
- Scope and constraints are explicit

If clear, suggest skipping ahead to `write-spec` (the contract) or implementation and ask for confirmation.

### Phase 1: Understand Intent

Gather context from the current project quickly (relevant files, docs, and existing patterns), then ask clarifying questions one at a time.

Questioning guidelines:
1. Prefer multiple-choice prompts when natural options exist.
2. Start broad (goal/users), then narrow (constraints/edge cases).
3. Validate assumptions explicitly.
4. Ask for success criteria early.

Topics to cover:
- Problem and motivation
- User/persona and usage context
- Constraints (technical, schedule, dependencies)
- Success criteria and acceptance shape
- Edge cases and non-goals

### Phase 2: Explore Approaches

Propose 2-3 concrete approaches.

For each approach include:
- 2-3 sentence summary
- Pros
- Cons
- Best-fit conditions

Lead with your recommendation and rationale. Prefer the simplest option that satisfies stated needs.

### Phase 3: Capture Design Summary

Write the approved design summary to:
`docs/design/YYYY-MM-DD-<topic>-design.md`

This is a *feeder*, not a proto-spec: it captures **direction**, and stops short of
falsifiable acceptance criteria. Those harden into a contract in `write-spec` — do
not finalize metrics or success thresholds here.

Use this structure:

```markdown
---
date: YYYY-MM-DD
topic: <kebab-case-topic>
stage: brainstorm
---

# <Topic Title>

## Problem / Context
[Who is hurting, what they do today, why this matters now]

## Options Considered
- [Option]: [trade-offs — pros / cons / best-fit conditions]

## Chosen Direction
[The selected approach and why it beats the alternatives]

## What Good Looks Like
[Directional signals of success — not falsifiable metrics; those belong to write-spec]

## Open Questions
- [Unresolved item]

## Constraints
- [Constraint]
```

### Phase 4: Handoff

Offer explicit next actions:
1. Hand off to `write-spec` to turn the chosen direction into a falsifiable contract.
2. **Review the direction with a critique subagent.** If the harness supports
   subagents (e.g. a Task/agent tool), launch one seeded with the design summary's
   path **and** the originating goal/context, instructed to critique the *chosen
   direction* — are the alternatives fairly weighed? is this the simplest option
   that meets the need? are the open questions actually open (vs. quietly decided)?
   — and to propose improvements. Apply or discuss before routing to `write-spec`.
   If subagents are unavailable, run the same critique inline via
   `verify-before-complete`.
3. Refine brainstorming further, or stop here for now.

When a handoff is appropriate, use this routing logic:
- Direction is settled and needs a falsifiable target → `write-spec` (the contract)
- CLI UX decisions (flags, args, output contracts) → `create-cli`
- UI/UX direction or visual systems → `frontend-design` or `web-design-guidelines`
- Deep architectural trade-off analysis → `first-principles`

Explain why in one sentence and ask for confirmation. If the target skill is unavailable, use the closest manual fallback.

## Output

- A design summary document at `docs/design/YYYY-MM-DD-<topic>-design.md`
- Clear next-step recommendation (spec the contract, refine, or stop)

## Verification

- Design summary has YAML frontmatter with `stage: brainstorm`
- The chosen direction is clear and traceable to the alternatives it beat
- `What Good Looks Like` is directional (falsifiable criteria are deferred to `write-spec`)
- At least one approach was evaluated with pros/cons before choosing
- User explicitly approved the design direction

## Resources

- `references/platform-mapping.md` — platform-specific handoff and coordination mappings
- `commands/workflows/brainstorm.md` — slash-command wrapper for harnesses that support it

## Principles

- One question per turn
- Keep outputs concise (about 200-300 words per section when nuanced)
- YAGNI: avoid speculative complexity
- Stay on WHAT; implementation details belong to planning
- Validate alignment incrementally before moving forward

## Sibling skills

Pre-execution pipeline: **brainstorm → spec → plan**
(`docs/design/` → `docs/specs/` → `docs/plans/`).

- `write-spec` — downstream. Once the direction is settled, hand off to make it a
  falsifiable contract (the WHAT). `write-plan` then sequences the build (the HOW).
- `first-principles` — escalate to here when the brainstorm reaches a high-stakes architectural or trade-off decision that needs systems-level reasoning, not just option exploration.
- `deep-research` — parallel evidence gathering when the brainstorm depends on facts you don't have (library behavior, API contracts, prior art).
