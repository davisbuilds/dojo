---
name: diagnose
description: Disciplined debugging loop for hard bugs and performance regressions. Use when the user says "diagnose this", "debug this", "this is broken/throwing/failing", reports a bug whose cause is non-obvious, or describes a performance regression. For completion-time evidence checks use verify-before-complete; for new-test methodology use test-strategy; for post-hoc code review use local-review.
skill-type: workflow
version: 2.0.0
---

# Diagnose

Investigate a specific failure using evidence that distinguishes its possible
causes. Prefer a fast, faithful reproduction when feasible. Adapt the order of
inspection, hypotheses, and probes to what is already known.

## When To Use

- A reported bug, intermittent failure, or performance regression has a
  non-obvious cause.
- The user asks to diagnose, debug, or explain why a specific behavior fails.

## Boundaries

- Determine scope from the request and conversation. Investigation-only work
  does not authorize source edits, new repo artifacts, commits, or production
  instrumentation. Use existing read-only evidence; request missing access or
  mutation authority only when it is needed for the next useful step.
- A request to fix a bug authorizes its bounded repair; do not ask again merely
  because the investigation is complete.
- General review belongs to `local-review`. Consult `test-strategy` for an
  unresolved testing choice and `verify-before-complete` for a consequential
  completion claim, without inheriting their full workflows or reports.
- Do not claim a cause is confirmed or a fix verified beyond the available
  evidence. Missing reproduction limits confidence; it does not prohibit useful
  inspection of source, traces, logs, or captured artifacts.

## Workflow

### Establish the failure and evidence

Identify the user's actual symptom, triggering conditions, and relevant recent
changes. Inspect existing tests and runtime evidence before building a new
harness. Confirm that a probe reaches the reported failure rather than a nearby
error or earlier guard.

Useful evidence includes a failing test, captured request or trace, CLI fixture,
browser flow, differential run, debugger observation, or performance profile.
For intermittent failures, preserve conditions and compare reproduction rates;
there is no universal rate threshold below which investigation must stop.

### Distinguish causes

Choose hypotheses from the evidence and test their predictions. Add alternatives
when the evidence is ambiguous or the leading explanation fails; do not invent
a fixed number. Inspecting the code may be the cheapest way to choose a useful
reproduction or probe.

Prefer probes that separate plausible causes. Keep changes controlled so their
results are interpretable. For performance work, measure the relevant path and
workload before claiming an improvement. Share consequential findings or
uncertainty; a ranked hypothesis report is optional.

If no runnable reproduction is available, continue useful read-only analysis.
State the evidence for each inference and the observation that would confirm or
reject it. If progress requires unavailable access or unauthorized changes,
report the precise gap and next useful probe rather than declaring a cause.

### Repair when authorized

Choose the smallest repair supported by the diagnosis. Where feasible, capture
the actual failure in a regression test before fixing it. The test must reach
the real bug pattern: a shallow unit seam cannot prove a multi-caller failure.
If no faithful seam is available, state the coverage gap and use the strongest
applicable check.

Re-run the original scenario after the change and the repository's relevant
checks. Reuse fresh evidence already obtained. Remove temporary instrumentation
and throwaway artifacts introduced during the investigation; preserve user
artifacts and any evidence needed for a reproducible handoff.

## Output

- **Investigation:** the cause and supporting evidence, or ranked remaining
  explanations if unresolved; confidence limits; proposed remediation and the
  next discriminating check if needed. No fix or commit is required.
- **Repair:** what changed and why, the original-scenario and regression results,
  and any residual gap. Follow repository commit policy and existing authority;
  this skill does not independently require a commit or PR.

Use the task's existing response format. Do not create a separate report or
feedback-loop file solely to satisfy this skill.

## Verification

An investigation is complete when the requested question is answered with
supporting evidence and appropriate uncertainty. If the cause remains unknown,
report an unresolved investigation and what would change that status.

A repair is verified only to the extent that checks exercise the reported
failure and affected behavior after the fix. A probable cause, plausible patch,
or passing unrelated suite is insufficient to claim the bug is fixed.

## Resources

Optional helpers for authorized artifact creation:

- `scripts/scaffold_feedback_loop.sh` — starter repro scripts for `failing-test`,
  `curl`, `cli-diff`, `playwright`, `replay`, `harness`, or `hitl`:
  `bash <skill-dir>/scripts/scaffold_feedback_loop.sh <kind> [path]`.
- `scripts/hitl-loop.template.sh` — a human-assisted loop when interaction is
  necessary. Use only if it adds useful evidence.

## Sibling Skills

- `local-review` — inspect a diff for possible defects.
- `test-strategy` — choose a faithful regression-test seam.
- `verify-before-complete` — audit evidence for a high-risk completion claim.
- `first-principles` — investigate architectural alternatives when the cause
  reveals a broader design decision; do not expand a bounded repair into one.
