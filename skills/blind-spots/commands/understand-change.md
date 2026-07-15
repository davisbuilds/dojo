---
name: understand-change
description: Blind spot pass on a proposed change — what it touches, what it can break, and what you don't know you don't know.
argument-hint: "[the proposed change to scope]"
---

# Blind Spot Pass On A Proposed Change

This command wrapper is a harness add-on for **scope mode** of the canonical
`blind-spots` skill.

Load `blind-spots` and follow it exactly. This wrapper selects the mode and
supplies the target; all behavior lives in `SKILL.md`.

## Change Description

<change_description> #$ARGUMENTS </change_description>

If `change_description` is empty, ask which proposed change to scope before
proceeding. Do not guess.

## Flow

1. **Calibrate.** Ask what the user already knows about this area and what they
   are unsure of. Assume competence; do not re-explain fundamentals.
2. Fix the target. If it is broader than one coherent change, narrow it with the
   user first.
3. Ground in the repository. Reuse an existing spec, plan, or design doc rather
   than regenerating it.
4. Map the entry point and boundaries, the call or data path that matters, and
   the likely blast radius.
5. **Name the unknowns** — known unknowns, unknown unknowns, and what the
   repository simply cannot tell you. This is the deliverable, not a footnote.

Keep current behavior (repository evidence) distinct from proposed intent (the
user's request), and label any conflict or stale artifact.

## Constraints

- Explain; do not plan. No architecture decision, no acceptance criteria, no task
  sequence — those belong to `first-principles`, `write-spec`, and `write-plan`.
- Chat only. Write no file unless the user explicitly asks for one.
- Never invent a system relationship. Mark inference as inference and unknowns as
  unknown.
