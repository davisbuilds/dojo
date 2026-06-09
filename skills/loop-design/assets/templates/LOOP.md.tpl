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
4. Run `./verify.sh`. If it exits 0, append a final `DONE` entry to `{{STATE_FILE}}` and stop.
5. If not done, append `tried / passed / still-open` to `{{STATE_FILE}}` and end the iteration.

## Guardrails

- Cadence: {{CADENCE}}.
- Sandbox: {{SANDBOX_MODE}}. Credentials: {{CREDS}}.
- Budget: stop after ~{{BUDGET_STEPS}} steps this iteration; loop owner cap ${{BUDGET_USD}}/day.
- Never edit, delete, or skip tests to make the oracle pass. A separate checker will reject that.
