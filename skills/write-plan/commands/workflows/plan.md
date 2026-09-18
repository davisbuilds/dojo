---
name: workflows:plan
description: Turn a settled target (a write-spec contract, ticket, or clear request) into a seam-aware execution plan with task breakdown, files, ordered steps, and verification.
argument-hint: "[contract path, ticket, or clear request]"
---

# Plan The Build

This command requests a durable execution plan using the canonical `write-plan`
skill. Load it and use the conversation and `#$ARGUMENTS` as input. A clear ticket,
conversation, or existing contract can establish the target.

## Flow

- Resolve material scope/acceptance decisions before prescribing dependent
  work. Do not require another spec solely because work is non-trivial or coupled.
- Trace the relevant source and seam; reuse existing decisions and evidence.
  Sequence actual dependencies and relevant verification using the canonical
  skill's grounding guidance.
- Save the requested plan at `docs/plans/YYYY-MM-DD-<topic>-plan.md` or update
  the existing plan. Use `assets/plan-template.md`, resolved author metadata,
  and the canonical risk classification.
- For `high`, link a ready high-risk spec, consult the high-risk reference and
  addendum, preserve traceability/authority/recovery/empirical gates, and complete
  validation and critique closure before setting `readiness: ready`. Reuse the
  existing high-risk contract; do not downgrade it to avoid these requirements.
- Run `python3 <skill-dir>/scripts/validate_plan.py docs/plans/<filename>.md`.
  The validator resolves paths from the target plan's Git root; use `--repo-root`
  for relocated artifacts. Fix schema errors and assess advisories on their merits.

Report the plan and meaningful readiness limits. A handoff section is optional;
there is no compulsory review menu or exact closing phrase. A plan-only request
ends with the plan. Continue implementation when already authorized, without
asking again merely because planning is complete.
