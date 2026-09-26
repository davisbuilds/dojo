---
name: verify-before-complete
description: Guard against false completion claims when the cost of being wrong is high. Use when accepting delegated or subagent work, shipping high-risk changes (auth, migrations, infra, security, broad refactors), lacking fresh verification evidence (missing, stale, or conflicting), or being explicitly asked to confirm something is really done or audit a completion claim. Skip routine low-risk changes already covered by the repo's own checks — running those checks is enough.
skill-type: reference
version: 3.0.0
---

# Verify Before Complete

Check whether the evidence supports the consequential claim being made. The
useful work is closing a proof gap; loading this skill does not create one.

## When To Use

Use for consequential completion decisions, acceptance of delegated work,
conflicting or missing evidence, and explicit completion audits. Routine work
with adequate project checks needs no extra gate or verification report.

## Match Evidence to the Claim

Start with the result the user needs and the evidence already available. Check
its scope, revision, relevant configuration/environment, and actual outcome.
Freshness means those inputs still support this claim, not that the current
agent personally ran the command in this session.

| Claim | Evidence that matters |
| --- | --- |
| A bug is fixed | The relevant reproduction or regression check exercises the failure and now passes. |
| A requirement is complete | Its observable outcome is covered; build/lint success alone cannot establish behavior. |
| A deployment or runtime boundary works | Evidence from that runtime and boundary, not only source or generated configuration. |
| Delegated work is ready | Inspect the change and its test/run evidence; a completion message alone is insufficient. |

Reuse inspectable CI results, test artifacts, and delegated evidence when they
cover the actual change and environment. Rerun or add checks when evidence is
missing, unverifiable, relevant inputs changed, signals conflict, or a material
failure mode remains uncovered. An unrelated documentation edit does not by
itself invalidate a runtime test; a configuration change affecting that runtime
can invalidate it even with identical code.

Choose checks that can distinguish success from the plausible failure. Expand
coverage for compatibility, recovery, authority, or integration risks that the
existing evidence does not address. Follow required project checks; neither an
arbitrary risk label nor running every available suite substitutes for coverage
of the actual risk.

## Boundaries

- An audit request authorizes investigation, not an unrequested fix or release.
  Reuse existing authorization; ask only for a genuinely missing decision or
  permission needed by the next action.
- Run risky probes in an authorized isolated environment. If required evidence
  cannot be obtained safely, report the unresolved claim and what would resolve
  it; do not test destructively against valuable state.
- Do not automatically add tests, commission reviewers, or invoke sibling
  workflows merely because this skill was consulted.

## Output

Report the supported result and any material limit in the task's normal answer.
Provide a command, artifact, or CI reference when it helps the user assess the
claim or they request proof. A separate report, level label, command transcript,
and repeated exit-code table are unnecessary unless a consumer requires them.

## Verification

Before declaring completion, resolve contradictory evidence or narrow the claim
to what is established. Distinguish passed, failed, skipped, and not checked.
If required verification is blocked, the affected claim remains unverified.

## Resources

- `evals/behavioral-scenarios.md` — replay cases for evidence reuse, missing proof,
  scope boundaries, and avoiding routine ceremony; not live evaluation results.
- `evals/trigger-cases.json` — deterministic lexical routing fixtures.

## Sibling skills

- `test-strategy` — designing a check when the evidence gap requires one.
- `diagnose` — investigating a failure whose cause remains unclear.
- `first-principles` — examining a consequential decision's assumptions.

Consult only what helps the current task; these pointers add no deliverables.
