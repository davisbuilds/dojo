# Loop: {{NAME}}

Kind: {{KIND}}. This brief describes one run; the runtime owns repetition.

## Goal and evidence

{{GOAL}}

{{EVIDENCE}}

{{KIND_GUIDANCE}}

{{CHECK}}

## Stop, pause, or escalate

{{STOP_WHEN}}

Report why work stopped: completed, run finished, inconclusive, blocked, limit
reached, or cancelled. A stop is not necessarily success. Repeated failures only
justify another attempt when new evidence or a changed approach makes it useful;
normal unchanged monitor samples are not a stall.

## Authority and execution

{{AUTHORITY}}

{{RUNTIME}}

These are instructions, not enforced permissions or budgets. This scaffold
configures no scheduler, sandbox, timeout, spend limit, or notification channel.
Do not expand authority, publish, or dispatch merely to keep the loop moving.

{{CONSTRAINTS}}

## Continuation

{{STATE}}

Before work, recover the current target/revision, relevant evidence, and remaining
budget. Inspect any in-flight operation before retrying a mutation. Preserve
operation IDs or deduplication cursors when needed. At the end of a run, retain
the latest result, unresolved uncertainty, next action, and a route to supporting
evidence. Keep a compact current checkpoint; use existing logs for history.
Do not automatically commit, revert another actor's work, or create extra logs.
