---
name: quiz-change
description: Quiz the user on an implemented change, one question at a time, teaching with repository evidence after each answer. Never scored, never gating.
argument-hint: "[change target — working, staged, branch, commit, or PR]"
---

# Quiz Me On An Implemented Change

This command wrapper is a harness add-on for **quiz mode** of the canonical
`change-comprehension` skill.

Load `change-comprehension` and follow it exactly. This wrapper selects the mode
and supplies the target; all behavior lives in `SKILL.md`.

## Change Target

<change_target> #$ARGUMENTS </change_target>

If `change_target` is empty, resolve the obvious candidate (working tree, staged
changes, current branch) and confirm it with the user. If no change is
identifiable, ask for one. Never quiz against a change you have not read.

## Flow

1. Read the actual diff and whatever verification evidence exists. Know the
   answers before asking the questions.
2. Propose a bounded topic set sized to the change's risk and surface area, and
   let the user adjust it.
3. Ask **one** substantive question, then stop and wait.
4. After each answer — including "I don't know" — say what was right, then
   correct or extend with concrete repository evidence.
5. Close with a recap of strengths and what is worth revisiting.

## Constraints

- One substantive question per turn. Never leak the answer before the user
  responds.
- No score, no pass/fail, no correctness claim about the code, no merge verdict.
- The user may skip a topic, change depth, or stop at any point. Honor it
  immediately; none of it is failure.
- Chat only. Write no file unless the user explicitly asks for one.
- This is not a code review. Defects belong to `local-review` / `gh-review-pr`;
  completion evidence belongs to `verify-before-complete`.
