---
name: workflows:plan
description: Create a robust implementation plan document from a feature request, ticket, or approved design summary.
argument-hint: "[feature, ticket, or approved summary]"
---

# Plan A Feature Or Change

This command wrapper is a harness add-on for the canonical `writing-plans` skill.

Load the `writing-plans` skill and follow it exactly. This wrapper adds orchestration only.

## Feature Input

<feature_input> #$ARGUMENTS </feature_input>

If `feature_input` is empty, ask the user for the feature, ticket, or approved design summary before proceeding.

## Flow

### 1. Readiness Gate

If requirements are unclear, ask whether to switch to `/workflows:brainstorm` first.

### 2. Draft Plan

Use `skills/writing-plans/assets/implementation-plan-template.md` as the scaffold and tailor it to the request.

### 3. Save Plan

Write the plan to:
`docs/plans/YYYY-MM-DD-<topic>-implementation.md`

If a brainstorm summary already exists for the topic, reuse that topic slug.

### 4. Validate Plan

Run:

```bash
python3 skills/writing-plans/scripts/validate_plan.py docs/plans/<filename>.md
```

Fix any validation errors before presenting the plan.

### 5. Handoff

Offer:
1. Execute in this session.
2. Open a separate execution session.
3. Refine the plan first.

Do not implement code in this workflow.
