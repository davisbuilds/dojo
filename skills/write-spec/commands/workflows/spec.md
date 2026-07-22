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
or implementation steps. Replace `author: <agent>` with the producing agent's
most specific available model or harness identifier; never leave the placeholder
unresolved.

Classify `risk_profile` using the canonical gate. For `high`, load
`references/high-risk-contract.md`, append `assets/high-risk-spec-addendum.md`,
and keep `readiness: draft` through critique closure. Keep routine specs lean.

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
plan-shaped content (task breakdowns, files, steps) leaked in. For high-risk
contracts it also fails missing scenario classes, duplicate IDs, or incomplete
structural readiness evidence.

### 5. Handoff

Confirm `Open Questions` is `None` or any retained item is explicitly
non-blocking before offering planning. Return to the decision-readiness gate when
an item would change the contract.

For `risk_profile: high`, run adversarial critique, revise blocking findings,
run closure critique, and set `readiness: ready` only when none remain. Use a
critique subagent when supported and authorized; otherwise critique inline.

Then offer:
1. Hand off to `/workflows:plan` (write-plan) to sequence the build.
2. Review a routine contract with a critique subagent (or
   `verify-before-complete` inline when subagents are unavailable), seeded with
   the contract path and originating context. Check falsifiability, mechanism
   leaks, concrete success criteria, evaluation, and problem grounding.
3. Refine the contract before sequencing.

Do not implement code in this workflow.
