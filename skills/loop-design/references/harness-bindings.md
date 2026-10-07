# Bind a Loop to the Available Runtime

Read this when moving from a loop design to execution. Harness features change;
inspect the current tool descriptions, local help, or official documentation for
the actual surface. A similarly named slash command, desktop automation, and
headless invocation may have different lifetimes and permissions.

## Prefer the existing mechanism

- **Bounded task:** use an available goal/task mechanism if it supports the
  required limits, interruption, and continuation. Otherwise a single bounded
  invocation may suffice. A shell loop is not required to keep an agent working.
- **Recurring monitor:** prefer an existing scheduler or notification/wait
  interface. Specify one observation per run, overlap policy, expiry or
  cancellation, and where results arrive. Don't assume an ended turn will wake
  when a detached shell command exits.
- **Experiment:** use the project's existing experiment runner when available.
  Keep baseline identity, candidate measurements, and trial limits there; let
  the agent reason about candidates without handing it implicit deployment
  authority.

For Claude Code, Codex, CI, or a custom runner, establish these properties only
to the extent the task depends on them:

| Property | What to establish |
| --- | --- |
| Invocation | Exact working directory, loaded instructions, inputs, and target checkout/service. A generated brief is not necessarily auto-loaded. |
| Lifecycle | What starts a run; what ends it; whether work survives disconnection or an ended turn; what cancellation actually terminates, including child operations. |
| Limits | Where time, iteration, retry, or spend limits are enforced. A prompt asking an agent to stop is a soft limit. |
| Authority | Actual credentials and allowed filesystem, network, and external effects. A worktree does not isolate the host user or shared services. |
| Concurrency | Whether the next run skips, queues, or reconciles with an active run. Use the runtime's locking where shared mutation matters. |
| Recovery | Durable checkpoint or job reference; what a retry can safely repeat; how to inspect ambiguous completion. |
| Delivery | Destination for results/failures and whether it can notify or resume the intended consumer. |

A fresh reviewer needs the actual changed state and relevant evidence. A separate
checkout may omit uncommitted work; a different model does not automatically
provide independent evidence or narrower authority. Configure a reviewer only
where it resolves a judgment or verification gap.

## If a shell runner is necessary

Use a bounded runner with explicit command failure, timeout, and cancellation
handling. Evaluate a check once per intended observation and retain its result;
rerunning it to extract an error can change state, repeat cost, or contradict
the original observation. Distinguish accepted work, unfinished work, unavailable
evidence, budget exhaustion, and cancellation. Avoid an unbounded `while true`
whose only exit is a passing command.

Check scripts and the optional scaffold are not a runner. They do not install
hooks, suppress permissions, restrict credentials, enforce budgets, publish
results, commit changes, or launch agents. Reuse the user's existing authority
within scope, and keep actions beyond that scope pending the actual decision.

## Confirm the connection

For new consequential unattended work, exercise a bounded run and relevant
failure/recovery behavior in a suitable environment. Confirm the runner actually
loads the chosen instructions and that observed results reach the intended
consumer. Reuse current evidence for unchanged runtime guarantees rather than
re-proving every property on every prompt edit. Report any unresolved limit or
delivery question before describing a loop as ready to leave unattended.
