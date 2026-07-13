---
name: understand-change
description: Explain the scope of a proposed change — entry points, call paths, blast radius, and unknowns — before it gets implemented.
argument-hint: "[the proposed change to scope]"
---

# Understand A Proposed Change

This command wrapper is a harness add-on for **scope mode** of the canonical
`change-comprehension` skill.

Load `change-comprehension` and follow it exactly. This wrapper selects the mode
and supplies the target; all behavior lives in `SKILL.md`.

## Change Description

<change_description> #$ARGUMENTS </change_description>

If `change_description` is empty, ask which proposed change to scope before
proceeding. Do not guess.

## Flow

1. Fix the target. If it is broader than one coherent change, narrow it with the
   user first.
2. Ground in the repository. Reuse an existing spec, plan, or design doc rather
   than regenerating it.
3. Explain the entry point and boundaries, the call or data path that matters,
   the likely blast radius, and the consequential unknowns.
4. Keep current behavior (repository evidence) distinct from proposed intent
   (the user's request or contract), and label any conflict or stale artifact.

## Constraints

- Explain; do not plan. No architecture decision, no acceptance criteria, no task
  sequence — those belong to `first-principles`, `write-spec`, and `write-plan`.
- Chat only. Write no file unless the user explicitly asks for one.
- Never invent a system relationship. Mark inference as inference and unknowns as
  unknown.
