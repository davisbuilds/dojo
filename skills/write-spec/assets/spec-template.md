---
date: YYYY-MM-DD
author: <agent>
topic: topic-slug
stage: spec
status: draft
source: conversation
risk_profile: routine
readiness: draft
---

# Topic Title Spec

## Problem

Who is hurting, what they do today, and why this matters now. One short paragraph,
no solution.

## Contract

When this ships, *[observable behavior]* holds, verified by `command-or-check`.

State the falsifiable end-state and name at least one deterministic verification
command. Describe *what must be true*, never *how to build it* — no file paths,
task breakdowns, or implementation steps. Pin a meaningful magnitude, floor, or
rate when mere existence, positive sign, non-emptiness, or completion could pass.

## Success Criteria

- Concrete behavior visible when it works.
- Another observable, checkable behavior.

## Evaluation

How the contract is measured.

For behavior-preserving work, define the reference behavior on ties, duplicates,
empty inputs, and other result-deciding edges; probe structural assumptions
against representative real data; include those edges in differential fixtures.

If this is a measurable product/experiment bet, set thresholds:
- Kill: signal that says stop.
- Scale: signal that says invest more.
- Graduate: signal that says it is done / promote it.

Omit the thresholds for mechanical or system specs.

## Scope

### In Scope

- Outcomes included in this contract (name results, not files).

### Out of Scope

- Outcomes explicitly excluded.

## Assumptions And Constraints

- Assumptions that shape the target.
- Constraints (technical, schedule, dependency, policy).
- For irreducible future uncertainty that does not change this contract: state
  its observable signal and containment expectation.

## Open Questions

- None — all decisions that affect this contract's scope, success criteria, and
  verification are settled before planning.

If a retained question is genuinely non-blocking, explain why it cannot change
this contract. Otherwise resolve it with the user or move the future choice to
Out of Scope before handing off to `write-plan`.

## Handoff

1. Hand off to `write-plan` to sequence the build against this contract.
2. Review the contract with a critique subagent (or `verify-before-complete`
   inline if subagents are unavailable).
3. Refine the contract before sequencing.
