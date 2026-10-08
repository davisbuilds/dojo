---
name: loop-design
description: Design bounded agent tasks, recurring monitoring, and iterative experiments. Use when setting up unattended or overnight work, scheduling repeated agent runs, defining loop stopping and recovery behavior, or deciding whether a task benefits from repetition.
skill-type: workflow
compatibility: "Guidance is harness-agnostic. Optional scaffolder requires Python 3; generated check scripts require POSIX sh. Designs loops without launching them or configuring runtime controls."
version: 2.0.0
---

# Loop Design

Make repeated agent work useful, bounded, and recoverable. Start with the user's
outcome and the actual runtime. A loop may need only a better prompt in an
existing scheduler or goal mechanism; designing one does not require a bundle,
a second agent, or a new runner.

## Choose what repeats

Distinguish the unit of work from the lifetime of the loop:

| Kind | Evidence and stopping behavior |
| --- | --- |
| Bounded task | Work toward an outcome, then stop when adequate evidence supports it. A command may cover part or all of acceptance; a judgment-based result can instead end with a supported conclusion or a reviewable proposal. |
| Recurring monitor | Each run observes a defined scope, reports meaningful change, and ends. A healthy or unchanged sample is a successful run, not a reason to disable the schedule. Define unavailable/partial data, alert deduplication, and when the schedule expires or is cancelled. |
| Iterative experiment | Compare candidates with a baseline under a bounded budget. Preserve negative and inconclusive results. Separate measurement, candidate selection, and permission to adopt or deploy. |

Combine these only when the task needs it, keeping each stopping rule clear.
Prefer a single invocation or an existing wait/notification tool when that
already resolves the task. Don't turn an unclear request into indefinite work;
resolve the missing outcome or bound the exploration.

## Set the contract at the uncertain boundaries

Reuse decisions and authorization already established. Clarify only what would
change execution:

- **Evidence:** what observation supports the outcome, from which target and
  scope? Distinguish failed acceptance from a failed command or unavailable data.
  When correctness matters, use evidence capable of contradicting the agent's
  report. A separate reviewer helps with judgment gaps; it is not mandatory for
  every run and does not establish isolation.
- **Limits:** where must this run stop, pause, or hand back? Choose relevant
  time, iteration, spend, or retry bounds and name their runtime enforcement.
  A limit reached means incomplete or inconclusive, not success. Repeated
  failure warrants retry only with a useful new approach or a known transient
  condition; an unchanged monitoring sample can be entirely normal.
- **Authority:** which reads, writes, credentials, and external effects are
  allowed? Keep evaluation criteria from being weakened merely to improve a
  result. Prompt constraints and Git diffs can reveal mistakes but cannot
  restrict a process's permissions. Use actual runtime controls where a boundary
  must hold, and verify them before relying on them unattended.
- **Continuation:** where can the next run recover current state, remaining
  budget, and in-flight operations? Reuse harness state or job records. After a
  timeout, inspect whether a mutation completed before retrying it; use operation
  IDs, idempotency, or reconciliation as the application permits.

## Fit the runtime

Inspect available scheduling, task, waiting, cancellation, and notification
capabilities before adding shell machinery. Confirm what survives an ended turn,
what actually wakes an agent, and how overlapping runs are handled. Worktrees
separate edits; they do not isolate credentials or shared services.

Read `references/harness-bindings.md` when connecting the design to a runtime.
It lists the properties to establish rather than assuming a particular slash
command exists or has identical behavior across harnesses. Report unconfigured
controls plainly. Do not infer enforcement from a budget or sandbox label in a
JSON file.

Retain a compact current checkpoint when existing state is insufficient: latest
result and evidence, unresolved uncertainty, next action, and relevant operation
references. Keep history in existing logs or linked artifacts. A fresh run
shouldn't need to reconstruct its direction from an ever-growing diary.

## Optional scaffold

Directly edit the existing runtime prompt when sufficient. If a portable brief
would help a future executor, read `references/blueprint-spec.md` and use:

```bash
python3 <skill-dir>/scripts/scaffold_loop.py --blueprint <blueprint.json> --out-dir .loops/<name>
```

Substitute the directory this skill was loaded from. The schema-2 scaffolder
writes `LOOP.md` and `blueprint.json`, with opt-in `checkpoint.md` and `check.sh`.
It refuses existing output paths and v1 blueprints. It executes no check and
installs no scheduler, checker, hooks, or controls. Migration guidance is in the
reference; preserve existing run state when changing a live loop.

## Validate and deliver

Choose evidence for the risk introduced. For a new unattended mutation, exercise
one bounded run and the relevant stopping, failure, and recovery behavior before
relying on it. Reuse applicable runtime proof for an unchanged mechanism. A
read-only monitor may need only a representative observation, an unavailable-data
case, and confirmation that the result reaches its consumer. For noisy
experiments, assess variation and comparison validity; repeating a command a
fixed number of times does not prove determinism or correctness.

Return the useful design or requested implementation, where it runs, how it
stops and resumes, and any unresolved control or evidence gap. Design work does
not authorize launch, broader credentials, deployment, or publication. Consult
`test-strategy` or `verify-before-complete` for a specific evidence gap without
inheriting their entire workflow.
