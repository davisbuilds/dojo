---
name: verify-before-complete
description: Enforce evidence-based completion claims. Use when you are about to state work is fixed, passing, done, or complete, and run verification first.
---

# Verify Before Complete

## Overview

Do not claim success without fresh verification evidence.

Core principle: evidence before assertions.

## When To Use

Use this skill when you are about to say any of the following:
- "fixed"
- "passing"
- "done"
- "ready to merge/commit"
- "requirements complete"

Apply before:
- commits
- PR creation
- task handoff
- phase completion statements

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

## Output

- Verification level used (quick/standard/high-risk)
- Command(s) run with exit codes
- Scope covered and key signal (e.g. "12 passed, 0 failed")
- Residual risk or uncovered areas

## Bottom Line

Run the right checks, read the results, then claim only what the evidence proves.
