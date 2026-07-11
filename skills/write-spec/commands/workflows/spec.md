---
name: workflows:spec
description: Write a falsifiable contract (the target) from a feature request, ticket, or approved design summary — before sequencing the build.
argument-hint: "[feature, ticket, or approved design summary]"
---

# Spec A Feature Or Change

This command wrapper is a harness add-on for the canonical `write-spec` skill.

Load the `write-spec` skill and follow it exactly. A spec is a **contract** (WHAT
must be true), not a plan (HOW to build it). This wrapper adds orchestration only.

## Feature Input

<feature_input> #$ARGUMENTS </feature_input>

If `feature_input` is empty, ask the user for the feature, ticket, or approved
design summary before proceeding.

## Flow

### 1. Decision-Readiness Gate

If requirements are unclear, ask whether to switch to `/workflows:brainstorm`
first. Otherwise, resolve facts available in the project and ask the user only
questions that change scope, success criteria, safety boundaries, or verification.
For non-trivial work, apply the proportionate uncertainty lenses in the canonical
skill. Do not hand off a contract with a blocking open question.

### 2. Draft Contract

Use `skills/write-spec/assets/spec-template.md` as the scaffold. State the
problem, the falsifiable contract (with at least one verification command),
success criteria, and evaluation. Keep mechanism out — no files, task breakdowns,
or implementation steps.

### 3. Save Contract

Write the contract to:
`docs/specs/YYYY-MM-DD-<topic>-spec.md`

If a design summary already exists for the topic
(`docs/design/YYYY-MM-DD-<topic>-design.md`), reuse that topic slug.

### 4. Validate Contract

Run:

```bash
python3 skills/write-spec/scripts/validate_spec.py docs/specs/<filename>.md
```

Fix any validation errors before presenting the contract. The validator fails if
plan-shaped content (task breakdowns, files, steps) leaked in.

### 5. Handoff

Confirm `Open Questions` is `None` or any retained item is explicitly
non-blocking before offering planning. Return to the decision-readiness gate when
an item would change the contract.

Offer:
1. Hand off to `/workflows:plan` (write-plan) to sequence the build.
2. Review the contract with a critique subagent: if the harness supports
   subagents, launch one seeded with the spec's path and the originating context
   to critique the contract (falsifiable? mechanism leaked? criteria concrete?
   evaluation gate right? problem real?) and propose improvements. If subagents
   are unavailable, run the same critique inline via `verify-before-complete`.
3. Refine the contract first.

Do not implement code in this workflow.
