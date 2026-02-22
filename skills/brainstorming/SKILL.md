---
name: brainstorming
description: Use this when requirements are ambiguous, multiple approaches are plausible, or trade-offs need discussion before planning or implementation. Clarifies WHAT to build through one-question-at-a-time collaboration. Can be skipped when requirements are already explicit and well constrained.
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
- Requirements are explicit and testable
- Scope is narrow and well-defined
- The user asks for direct implementation with clear constraints

<HARD-GATE>
If this skill is active, do not write code, modify files, or invoke implementation skills until the user has approved the design summary (or explicitly chooses to stop brainstorming).
</HARD-GATE>

## Core Process

### Phase 0: Assess Clarity

Before asking detailed questions, decide whether brainstorming is needed.

Signals requirements are already clear:
- Acceptance criteria are specific
- Expected behavior is precise
- Existing implementation pattern is identified
- Scope and constraints are explicit

If clear, suggest skipping to planning/implementation and ask for confirmation.

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
`docs/plans/YYYY-MM-DD-<topic>-plan.md`

Use this structure:

```markdown
---
date: YYYY-MM-DD
topic: <kebab-case-topic>
stage: brainstorm
---

# <Topic Title>

## What We Are Building
[Concise problem/solution summary]

## Why This Direction
[Why this approach was chosen over alternatives]

## Key Decisions
- [Decision]: [Rationale]

## Constraints
- [Constraint]

## Success Criteria
- [Criterion]

## Open Questions
- [Unresolved item]

## Next Step
Proceed to planning.
```

### Phase 4: Handoff

Offer explicit next actions:
1. Proceed to planning
2. Refine brainstorming further
3. Stop here for now

### Conditional Skill Coordination

After the design summary is approved, decide whether another skill should take over.

Use this routing logic:

- If implementation steps, file-by-file sequencing, or execution order are needed:
  transition to a planning skill (for example, `writing-plans` if available).
- If the design hinges on CLI UX decisions (flags, args, output contracts):
  transition to a CLI design skill (for example, `create-cli` if available).
- If the design hinges on UI/UX direction, accessibility, or visual systems:
  transition to a frontend/design-review skill (for example, `frontend-design` or `web-design-guidelines` if available).
- If the user needs deep trade-off analysis before choosing a direction:
  transition to a systems reasoning skill (for example, `first-principles` if available).
- If the request is already explicit and implementation-ready:
  skip additional brainstorming and proceed directly to planning/implementation.

When proposing a transition, explain why in one sentence and ask for confirmation.
If the target skill is unavailable in the current harness, use the closest manual fallback and continue.

## Principles

- One question per turn
- Keep outputs concise (about 200-300 words per section when nuanced)
- YAGNI: avoid speculative complexity
- Stay on WHAT; implementation details belong to planning
- Validate alignment incrementally before moving forward

## Optional Platform Add-ons

Platform-specific wrappers, commands, and tool mappings are optional. See `references/platform-mapping.md` and `commands/workflows/brainstorm.md` when running in environments that support slash-command workflows.
