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
topic slug. Confirm it has no unresolved question that changes scope, success
criteria, or verification; route those back to `/workflows:spec`. If no contract
exists and the work is non-trivial or touches coupled code, ask whether to switch
to `/workflows:spec` first.

If the spec is high-risk, require `readiness: ready` before planning.

### 2. Map Before You Cut

For tasks touching existing/coupled code, trace the data/call path, pick the
thinnest seam that satisfies the contract, and record `Assumptions Verified` in
each existing-code task against its exact target file/symbol. Resolve current
lookups before steps; risks are only irreducible future uncertainty.

### 3. Draft Plan

Use `skills/write-plan/assets/plan-template.md` as the scaffold. Each `Done When`
must trace to the contract's end-state. Replace `author: <agent>` with the
producing agent's most specific available model or harness identifier; never
leave the placeholder unresolved.

Classify `risk_profile` using the canonical gate. For `high`, add the linked spec
to frontmatter, load `references/high-risk-readiness.md`, append
`assets/high-risk-plan-addendum.md`, and keep `readiness: draft` through critique
closure. Keep routine plans lean.

### 4. Save Plan

Write the plan to:
`docs/plans/YYYY-MM-DD-<topic>-plan.md`

### 5. Validate Plan

Run:

```bash
python3 skills/write-plan/scripts/validate_plan.py docs/plans/<filename>.md
```

Fix any validation errors before presenting the plan.
Treat grounding and test-discovery messages as advisories: they are a prompt to
read the code, not a verdict on prose. High-risk structure, linked-spec coverage,
task references, modified-file existence, and readiness closure are hard gates.

### 6. Handoff

For `risk_profile: high`, run adversarial critique, revise blocking findings,
run closure critique, and set `readiness: ready` only when none remain. Use a
critique subagent when supported and authorized; otherwise critique inline.

Then offer:
1. Execute in this session, task by task.
2. Review or refine a routine plan first.
3. Open a separate execution session.
