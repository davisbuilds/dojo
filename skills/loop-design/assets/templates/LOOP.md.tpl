# Loop: {{NAME}}

> Read this file at the start of every iteration. You are ONE iteration of an autonomous loop.
> The repo — not this conversation — is your memory. Read `{{STATE_FILE}}` and recent git history first.

## Goal

{{GOAL}}

## Done when (the oracle)

This loop is complete only when `verify.sh` exits 0:

```bash
./verify.sh   # runs: {{DONE_WHEN}}
```

Do not claim "done" from your own judgment. Run the oracle. It is the only source of truth.

## Constraints

{{CONSTRAINTS}}

## Each iteration

1. Read `{{STATE_FILE}}` and `git log --oneline -10` to recover context from prior runs.
2. Pick the smallest next increment toward the goal.
3. Implement it. Keep the working tree clean; commit with a descriptive message.
4. Run `./guard.sh` (cheap reward-hacking gate), then `./verify.sh` (the oracle).
   - If `guard.sh` exits non-zero, you modified a protected path — revert it and redo the work. Do not continue.
   - If `verify.sh` exits 0, append a final `DONE` entry to `{{STATE_FILE}}` and stop.
5. If not done, append `tried / passed / still-open` to `{{STATE_FILE}}` and end the iteration.
6. **Append one structured line to `.loop_log.jsonl`** so a human can diagnose the run later, e.g.
   `{"ts":<unix>,"event":"iter_end","passed":false,"failure":"<first failing check>"}`.

## Stop and call a human when

- The oracle's first failure is **identical to the previous iteration's** (you are stuck / walking in circles — do not keep retrying the same fix).
- `guard.sh` trips (protected paths changed — reward hacking).
- You hit the iteration or budget cap below.

## Guardrails

- Cadence: {{CADENCE}}.
- Sandbox: {{SANDBOX_MODE}}. Credentials: {{CREDS}}.
- Iteration cap: stop after ~{{MAX_ITER}} iterations without reaching the oracle.
- Budget: stop after ~{{BUDGET_STEPS}} steps this iteration; loop owner cap ${{BUDGET_USD}}/day.
- Never edit, delete, or skip tests to make the oracle pass. `guard.sh` and a separate checker will reject that.
