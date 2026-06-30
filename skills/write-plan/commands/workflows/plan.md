---
name: workflows:plan
description: Turn a settled target (a write-spec contract, ticket, or clear request) into a seam-aware execution plan with task breakdown, files, ordered steps, and verification.
argument-hint: "[contract path, ticket, or clear request]"
---

# Plan The Build

This command wrapper is a harness add-on for the canonical `write-plan` skill.

Load the `write-plan` skill and follow it exactly. A plan is the HOW (task
breakdown, files, ordered steps), held to a contract's end-state. This wrapper
adds orchestration only.

## Target Input

<target_input> #$ARGUMENTS </target_input>

If `target_input` is empty, ask for the contract path, ticket, or request before
proceeding.

## Flow

### 1. Contract Gate

If a `docs/specs/<topic>-spec.md` contract exists, plan against it and reuse its
topic slug. If no contract exists and the work is non-trivial or touches coupled
code, ask whether to switch to `/workflows:spec` first.

### 2. Map Before You Cut

For tasks touching existing/coupled code, trace the data/call path, pick the
thinnest seam that satisfies the contract, and record `Assumptions Verified`.

### 3. Draft Plan

Use `skills/write-plan/assets/plan-template.md` as the scaffold. Each `Done When`
must trace to the contract's end-state.

### 4. Save Plan

Write the plan to:
`docs/plans/YYYY-MM-DD-<topic>-plan.md`

### 5. Validate Plan

Run:

```bash
python3 skills/write-plan/scripts/validate_plan.py docs/plans/<filename>.md
```

Fix any validation errors before presenting the plan.

### 6. Handoff

Offer:
1. Execute in this session, task by task.
2. Review the plan with a critique subagent: if the harness supports subagents,
   launch one seeded with the plan's path, the spec contract, and originating
   context to critique the plan (thinnest seam? assumptions grounded? steps
   verified not guessed? blast radius mapped? verification real?) and propose
   improvements. If subagents are unavailable, run the same critique inline via
   `verify-before-complete`.
3. Open a separate execution session, or refine the plan first.
