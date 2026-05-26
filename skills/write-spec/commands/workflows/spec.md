---
name: workflows:spec
description: Create a robust spec document from a feature request, ticket, or approved design summary.
argument-hint: "[feature, ticket, or approved summary]"
---

# Spec A Feature Or Change

This command wrapper is a harness add-on for the canonical `write-spec` skill.

Load the `write-spec` skill and follow it exactly. This wrapper adds orchestration only.

## Feature Input

<feature_input> #$ARGUMENTS </feature_input>

If `feature_input` is empty, ask the user for the feature, ticket, or approved design summary before proceeding.

## Flow

### 1. Readiness Gate

If requirements are unclear, ask whether to switch to `/workflows:brainstorm` first.

### 2. Draft Spec

Use `skills/write-spec/assets/spec-template.md` as the scaffold and tailor it to the request.

### 3. Save Spec

Write the spec to:
`docs/specs/YYYY-MM-DD-<topic>-spec.md`

If a brainstorm summary already exists for the topic, reuse that topic slug.

### 4. Validate Spec

Run:

```bash
python3 skills/write-spec/scripts/validate_spec.py docs/specs/<filename>.md
```

Fix any validation errors before presenting the spec.

### 5. Handoff

Offer:
1. Execute in this session.
2. Open a separate execution session.
3. Refine the spec first.

Do not implement code in this workflow.
