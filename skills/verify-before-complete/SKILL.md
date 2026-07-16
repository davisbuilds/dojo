---
name: verify-before-complete
description: Guard against false completion claims when the cost of being wrong is high. Use when accepting delegated or subagent work, shipping high-risk changes (auth, migrations, infra, security, broad refactors), lacking fresh verification evidence (missing, stale, or conflicting), or being explicitly asked to confirm something is really done or audit a completion claim. Skip routine low-risk changes already covered by the repo's own checks — running those checks is enough.
skill-type: reference
version: 2.0.0
---

# Verify Before Complete

## Overview

Do not claim success without fresh verification evidence.

Core principle: evidence before assertions.

This is a **circuit breaker for high-stakes completion claims**, not a ritual to
run after every chunk of work. It earns its keep when the claim is risky,
delegated, or unsupported — not when a routine change is already covered by the
repo's own checks.

## Skip When (fast exit)

If **all** of these hold, you are already done. Do not run the gate below and do
not emit a verification report:

- the change is routine and low-risk (docs, comments, formatting, a small
  isolated edit), and
- the repo's own named checks (from `AGENTS.md` / CI) cover it and you have
  fresh passing output from this session, and
- no delegated work is being accepted on trust.

Running the repo's stated checks and reporting their result *is* sufficient
here. Do not layer extra ceremony on top.

## When To Use (the circuit-breaker cases)

Engage the full gate when a completion claim carries real risk of being wrong:

- **Delegated / subagent work** you are about to accept — never treat "the
  subagent said it's done" as evidence.
- **High-risk changes** — auth, migrations, infrastructure, security, or broad
  and cross-module refactors.
- **Missing, stale, or conflicting evidence** — nothing re-run since the last
  edit, or one signal green while another is red.
- **Explicit completion audits** — you are asked to confirm something is "really
  done", to prove it passes, or to check whether it was actually verified.

## Freshness Rule

Verification must be fresh relative to the latest relevant code or config change.

If changes happened after your last check, re-run verification.

## Verification Levels

Pick a level based on change risk and blast radius.

| Level | Use When | Minimum Evidence |
| --- | --- | --- |
| `quick` | Small, isolated changes | Targeted tests or command covering edited behavior |
| `standard` | Typical feature/bug work | Targeted tests + nearby module/package checks |
| `high-risk` | Infra, migrations, auth, security, broad refactors | Full relevant suite + integration/e2e or equivalent |

## Claim Types And Required Proof

| Claim | Must Show |
| --- | --- |
| Tests pass | test command + zero-failure signal |
| Build passes | build command + exit 0 |
| Bug fixed | reproduction check now passes |
| Requirement complete | checklist coverage + proof per item |
| Delegated task complete | diff review + local verification rerun |

## Verification Gate

Before making a success claim:
1. Identify the claim you are about to make.
2. Choose verification level (`quick`, `standard`, or `high-risk`).
3. Run the relevant commands.
4. Read output and exit status.
5. Compare result to claim.
6. Report only what evidence supports.

If evidence conflicts with the claim, state actual status and blockers.

## Evidence Format

When reporting completion, include:
- command(s) run
- scope covered
- exit code
- key signal (for example, `34 passed`, `0 errors`, `build succeeded`)
- residual risk (if any)

Recommended response shape:

```text
Verification level: standard
Commands:
- pytest tests/module_x -q (exit 0, 12 passed)
- pnpm build (exit 0)
Claim supported: module X fix is verified in tested scope.
Residual risk: full e2e suite not run in this pass.
```

## If Full Verification Is Blocked

If tooling, sandbox, or time constraints block full verification:
- run the strongest available checks
- state what was not verified
- state the risk clearly
- avoid unconditional completion claims

## Delegation Rule

Delegated implementation is not complete evidence by itself.
Always verify delegated changes locally before claiming completion.

## Anti-Patterns

Do not:
- substitute confidence for evidence
- rely on stale command output
- treat lint success as build/test success
- claim global completion from partial checks
- skip reruns after new edits
- run the full gate on routine changes the repo's own checks already cover

## Output

- Verification level used (quick/standard/high-risk)
- Command(s) run with exit codes
- Scope covered and key signal (e.g. "12 passed, 0 failed")
- Residual risk or uncovered areas

## Bottom Line

Run the right checks, read the results, then claim only what the evidence proves.

## Sibling skills

One of four `reference`-typed *Disciplines* — modes that govern *how* the agent operates rather than what to build.

- `test-strategy` — testing methodology. Common upstream: this skill demands evidence; that one shapes what the evidence-producing test should look like.
- `first-principles` — reasoning methodology. Orthogonal axis (start-of-task) to the completion gate here (end-of-task).
- `caveman` — output-style mode. Orthogonal — concerned with *how the agent writes*, not *what the agent claims*.
- `diagnose` — common upstream caller; Phase 6 of the diagnose loop hands off to this gate.
