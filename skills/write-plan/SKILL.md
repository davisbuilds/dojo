---
name: write-plan
description: 'Sequence a settled target into a grounded execution plan. Use when dependencies, rollout ordering, or verification gates need explicit planning, or a reusable implementation plan is requested. Accept clear tickets, conversations, and existing contracts; multiple files alone do not require a plan or a new spec.'
skill-type: workflow
version: 3.0.0
---

# Write Plan

Sequence work when dependencies, rollout, or handoff need explicit coordination.
A useful plan records grounded steps and proof of the accepted outcome. Its
acceptance gate is that outcome, not compliance with the proposed mechanism.

## When To Use

- The user requests an implementation plan or a reusable execution handoff.
- Dependencies, rollout ordering, or verification gates need explicit planning.

An ordinary multi-file change with clear requirements and execution order does
not require a saved plan. Consult only the relevant guidance and continue the
authorized work. A clear ticket or conversation can supply the target; no
separate `write-spec` artifact is required for routine work.

## Boundaries

Follow the user's scope and existing authority. Planning-only requests do not
authorize implementation; an implementation request does not need another
approval just because a plan was useful along the way.

Resolve decisions that change scope, acceptance, or safety before prescribing
dependent work. Consult `write-spec` for that concern when useful; do not demand
a new document merely because the work is non-trivial or coupled. Consult
siblings without inheriting their full workflows, artifacts, or handoffs, while
following higher-priority harness loading rules.

## Workflow

### Ground the target and seam

Reuse the accepted contract and evidence, linking a spec when one exists. Read
the exact source being changed and trace the relevant data/call path before
prescribing a mechanism. Find the smallest seam that satisfies the target.
For a defect class or cross-cutting property, inspect sibling/alternate paths
that could violate it; cover them or state their scope explicitly.

Resolve facts available now. Keep irreducible future uncertainty in the risks
with its signal and mitigation. For an external tool assumption that the plan
depends on, use an observed command/result rather than an unrelated repo citation.
Date runtime evidence and identify the build and entry point; recheck it when
relevant code, configuration, or runtime inputs change.

### Sequence work and proof

Group tasks by meaningful, independently verifiable behavior and actual
dependencies. Avoid invented time quotas or tiny steps that add no coordination
value. Each task should name the relevant files, intended change, acceptance,
and proof; reuse shared evidence rather than repeating its full description.

Plan checks at the seam that establishes the outcome. Include relevant failure,
compatibility, and recovery cases. For changed tests, establish runner discovery
and a command that runs the literal test path or selector; mark future execution
as planned, not observed. A green suite on each side of an interface does not
prove their integration.

Use `references/seam-selection.md` for detailed grounding, evidence-fidelity,
and non-degenerate acceptance examples when those concerns apply.

## Output

For consultation, use the task's existing plan or concise execution notes. Write
a durable plan when requested, project-required, or useful for coordination and
later execution. Use the schema below for saved plans. Do not produce duplicate
spec/plan artifacts solely to satisfy sibling routing.

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

This gate classifies a plan artifact, not whether any multi-file task must create
one. Preserve authority, privacy, migration/recovery, and behavioral verification
requirements during consultation too. Do not skip an unresolved safety decision
or downgrade a high-risk contract to avoid its readiness gates.

## Saved Plan Schema

Use `assets/plan-template.md` at `docs/plans/YYYY-MM-DD-<topic>-plan.md`, or update
the existing plan. Reuse a linked contract's topic slug when available.

Required frontmatter: `date`, resolved `author`, `topic`, `stage: plan`, `status`,
`source`, `risk_profile`, and `readiness`. New artifacts start with `status: draft`;
update delivery status as work lands. Readiness is separate from implementation
status. Legacy artifacts keep their supported schema.

Required sections:

- `# <Title> Plan`
- `## Goal` — accepted outcome or link to the contract/ticket.
- `## Scope`
- `## Assumptions And Constraints`
- `## Task Breakdown`
- `## Risks And Mitigations`
- `## Verification Matrix` — requirement, proof command, expected signal.

`## Handoff` is optional; use it for an actual next action or execution context,
not a compulsory menu. Record shared grounding once in `## Map Before You Cut`
when useful, and reference it from the affected tasks.

Each `### Task N: <name>` includes `**Objective**`, `**Files**` (exact target
paths), `**Dependencies**` (or None), `**Implementation Steps**`,
`**Verification**`, and `**Done When**`.

For existing-code tasks, record `**Assumptions Verified**` against the exact
file/symbol and observed behavior. Link shared evidence where appropriate;
neighboring examples are research context, not target verification. Use
`**Behavior Measured**` when an external tool's behavior is load-bearing and
`**Test Discovery Verified**` when tests change. Distinguish observed results
from checks that will only be executable after implementation.

For `high`, load `references/high-risk-readiness.md` and
`assets/high-risk-plan-addendum.md`. Link an existing high-risk spec with
`readiness: ready`; create or complete that contract only if it is missing or
insufficient. Trace its contract/scenario IDs to tasks and proof, preserve
capability/authority and recovery maps, evidence lifecycle, consumer closure,
and empirical stop gates for unproven security or platform assumptions.

Keep `readiness: draft` through deterministic validation, adversarial critique,
revision, and closure critique. Use a critique subagent when supported and
authorized; otherwise critique inline. Set `ready` only after blockers close.

## Verification

For a saved plan, run:

```bash
python3 <skill-dir>/scripts/validate_plan.py docs/plans/<filename>.md
```

The validator resolves `spec:` and modified-file paths from the plan's Git root.
Use `--repo-root <path>` for relocated artifacts; outside Git the fallback is the
caller's working directory.

Fix schema errors. Routine grounding, test-discovery, and weak-acceptance
advisories prompt judgment; high-risk structure, linked-spec coverage, task/file
references, and review closure remain hard gates. Validation cannot prove prose
claims or that a proposed command exercises the intended behavior.

Before declaring the plan ready, check that steps are grounded, acceptance
matches the target, and proof cannot pass on irrelevant or degenerate behavior.
For capability/measurement gates, pair the tool's answer with the user-facing
surface it claims to represent. High-risk plans also require review closure.

Report the artifact and relevant readiness limits concisely. Continue authorized
execution when appropriate; a plan-only request ends with the plan. No exact
closing phrase or optional-review menu is required.

## Resources

- `assets/plan-template.md` — saved plan scaffold.
- `references/seam-selection.md` — grounded seams, test discovery, and proof fidelity.
- `references/high-risk-readiness.md` and `assets/high-risk-plan-addendum.md` —
  conditional authority, traceability, recovery, and review requirements.
- `commands/workflows/plan.md` — explicit planning command wrapper.

## Sibling Skills

- `write-spec` — resolve a material gap in the accepted target.
- `brainstorming` — explore unsettled direction or alternatives.
- `deep-research` — gather missing external evidence.
- `first-principles` — resolve a consequential architectural choice.
