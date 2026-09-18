---
name: write-spec
description: 'Define what done means before building: observable outcomes, acceptance criteria, and how to verify them. Use when material target decisions remain unresolved or a durable specification is requested or needed for coordination. Reuse an accepted ticket, conversation, or contract when it already defines the target.'
skill-type: workflow
version: 3.0.0
---

# Write Spec

Define what must be true and how to check it. Use a durable specification when
it helps consumers agree on or retain that contract. Thinking through acceptance
does not by itself require publishing a spec file.

## When To Use

- Material scope, behavior, or acceptance decisions remain unresolved.
- The user requests a specification, or coordination needs a durable contract.

An accepted ticket, conversation, or existing document can already supply the
contract. If it is clear and sufficient, reuse it and continue the authorized
task. Neither multi-file work nor consulting this skill requires a new spec.

## Boundaries

Follow the requested scope. Specification-only work does not authorize code
changes. During an implementation request, resolve the missing decisions without
inheriting a document pipeline or additional permission checkpoints.

Consult relevant sibling sections without activating their whole workflows.
Escalate for an unresolved material decision or evidence gap, not domain overlap.
Follow higher-priority harness loading rules.

## Workflow

1. **Resolve current uncertainty.** Read relevant source, docs, and behavior.
   Ask the user only about choices that change the contract and cannot be
   inferred from existing intent. Separate blocking decisions from irreducible
   future uncertainty; record the latter's signal and containment. Use
   `references/uncertainty-triage.md` when that distinction is difficult.
2. **State the outcome and proof.** Tie acceptance to observable behavior and
   checks that can fail for the defect in question. Pin a meaningful floor or
   non-degenerate case when empty/trivial output could pass. An existing check
   can be reused; a second template does not add evidence.
3. **Check relevant failure modes.** Consider affected consumers, old or malformed
   inputs, permissions, partial failure, and recovery proportionately. For
   behavior-preserving work, define the reference behavior on ties, duplicates,
   empty inputs, and other result-deciding edges; probe assumptions against
   representative data and include those edges in differential checks.
4. **Capture only what needs persistence.** Amend an existing contract or create
   the requested artifact. Resolve contract-changing questions before planning
   or implementation; identify remaining non-blocking uncertainty honestly.

## Output

For consultation, integrate decisions and acceptance evidence into the current
task. No separate file is required. For a durable spec, use the contract schema
below and link existing decisions/evidence rather than restating them at length.
A formal spec states WHAT; implementation files and ordered tasks belong in an
execution plan when one is needed.

<!-- INCLUDE: risk-profile-gate -->
<!-- AUTO-GENERATED from skills/_fragments/risk-profile-gate.md — do not edit -->
## Risk Profile Gate

Classify each new artifact before drafting:

- `routine` — the default; keep the normal template and validation path lean.
- `high` — use when credentials or privilege separation, remote/destructive
  effects, cross-system state agreement, retries/concurrency/queues, executable
  untrusted input, external policy decisions, or persisted-state migration can
  make a plausible-looking artifact unsafe or infeasible.

Record `risk_profile: routine|high` and `readiness: draft|ready` separately from
delivery `status`. Legacy artifacts without these fields remain routine/draft.
For `high`, load this skill's high-risk reference and addendum; do not add those
sections to routine work. Reclassify when repository evidence reveals a trigger.
<!-- /INCLUDE: risk-profile-gate -->

This gate classifies a new or revised spec artifact; it does not require one
merely because guidance was consulted. Regardless of artifact choice, unresolved
authority, privacy, migration/recovery, or verification concerns must be resolved
before the dependent action. Do not downgrade an existing high-risk contract to
avoid its readiness requirements.

## Saved Contract Schema

Use `assets/spec-template.md` for a new artifact at
`docs/specs/YYYY-MM-DD-<topic>-spec.md`, or update the existing contract. Reuse the
topic slug of a related design summary when available.

Required frontmatter: `date`, resolved `author`, `topic`, `stage: spec`,
`status`, `source`, `risk_profile`, and `readiness`. New artifacts start with
`status: draft`; update delivery status as work lands. `readiness` describes
whether the contract is ready for use, separately from implementation status.
Legacy artifacts keep their supported schema.

Required sections:

- `# <Title> Spec`
- `## Problem` — the need and relevant context.
- `## Contract` — observable end-state and at least one concrete verification
  command/check in an inline code span.
- `## Success Criteria` — the behaviors that establish success.
- `## Evaluation` — proof appropriate to those criteria. Product/experiment
  thresholds belong here only when the work is actually a measurable bet.
- `## Scope` — included and excluded outcomes.
- `## Assumptions And Constraints` — relevant limits and bounded uncertainty.
- `## Open Questions` — None, or explicitly non-blocking with the reason.

`## Handoff` is optional. If useful, state the actual next action or consumer;
there is no required menu. Do not add task breakdowns, file lists, or ordered
implementation steps to a formal contract.

For `high`, load `references/high-risk-contract.md` and
`assets/high-risk-spec-addendum.md`: retain authority/safety outcomes, stable
criterion/scenario IDs, and negative/recovery/concurrency/legacy scenarios.
Keep `readiness: draft` through validation, adversarial critique, revision, and
closure critique. Set it to `ready` only after blocking findings are closed.
Use a critique subagent when supported and authorized; otherwise critique inline.

## Verification

For a saved spec, run:

```bash
python3 <skill-dir>/scripts/validate_spec.py docs/specs/<filename>.md
```

Fix schema errors. Weak-acceptance advisories are prompts for judgment, not
schema failures. Validation proves structure, not that the proposed check proves
the outcome or the authority/recovery model is sound.

Before calling the target ready, confirm acceptance is falsifiable and no open
decision changes scope, success criteria, or verification. High-risk artifacts
also require the review closure described above. Report only supported readiness
and relevant remaining questions; no exact completion phrase is required.

## Resources

- `assets/spec-template.md` — saved contract scaffold.
- `references/uncertainty-triage.md` — unresolved-decision guidance.
- `references/high-risk-contract.md` and `assets/high-risk-spec-addendum.md` —
  conditional safety, traceability, and review protocol.
- `commands/workflows/spec.md` — explicit specification command wrapper.

## Sibling Skills

- `brainstorming` — explore genuinely unsettled direction.
- `write-plan` — sequence dependencies or rollout when an execution plan is needed;
  a complete contract does not automatically require a planning workflow.
- `first-principles` — resolve material architectural trade-offs.
- `deep-research` — gather missing external evidence.
