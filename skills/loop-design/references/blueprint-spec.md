# Loop Blueprint Spec

The blueprint is the portable, harness-agnostic definition of one loop. It is the thing you design; the scaffolder turns it into files a harness runs.

## Schema

```json
{
  "name": "auth-test-fixer",
  "goal": "All tests under test/auth pass and the linter is clean.",
  "done_when": "pytest test/auth -q && ruff check .",
  "cadence": "until-done",
  "harness": "claude-code",
  "constraints": [
    "Never edit, delete, or skip tests to make the oracle pass.",
    "Keep each iteration's diff under ~200 lines."
  ],
  "protected_paths": ["test/", "tests/"],
  "state_file": "progress.md",
  "checker": {
    "enabled": true,
    "model": "different",
    "instructions": "Reject premature 'done', weakened tests, abstraction bloat, or dead code."
  },
  "sandbox": {
    "mode": "container",
    "creds": "staging-only / least-privilege",
    "network": "none",
    "budget": { "max_iterations": 20, "per_run_steps": 50, "daily_usd": 50 }
  }
}
```

### Fields

| Field | Required | Meaning |
|---|---|---|
| `name` | yes | Slug for the loop; names the bundle dir and artifacts. |
| `goal` | yes | One sentence a fresh agent can act on. |
| `done_when` | **yes** | The oracle: a shell command that exits 0 only when the goal is met. No field matters more. |
| `cadence` | no | `until-done`, `interval:<dur>`, `cron:'<expr>'`, or `on-demand`. Default `until-done`. |
| `harness` | no | `claude-code`, `codex`, `github-actions`, `ralph`, or `all`. Default `claude-code`. |
| `constraints` | no | Hard rules the maker must not violate. Always include the "don't weaken tests" rule. |
| `protected_paths` | no | Paths the maker must not touch — the cheap reward-hacking gate (`guard.sh`). Defaults to `test/`, `tests/`. Harmless if absent. |
| `state_file` | no | On-disk memory the loop reads/writes each iteration. Default `progress.md`. |
| `checker` | no | The verifier (a separate agent/context). Strongly recommended; on by default. |
| `sandbox` | no | `mode` (container/codespace/host), `creds`, `network` (`none` for prompt-injection defense), and `budget` caps (`max_iterations`, `per_run_steps`, `daily_usd`). |

## The Go/No-Go Gate (why `done_when` is mandatory)

The single variable that decides whether a loop works is: **can the loop verify itself without you?** Across Willison, Anthropic, and Osmani the consensus is identical — agentic loops shine on problems with *clear success criteria where finding a solution requires trial-and-error*, and they fail without that signal.

So the gate is five questions, in order:

1. **Is there an oracle?** "Done" must be a command that exits 0. If you cannot write it, the task is not loop-shaped — keep prompting interactively. The scaffolder enforces this: no `done_when`, no bundle.
2. **Is the oracle deterministic?** Run it ~10× on one unchanged state; every run must agree (`./verify.sh --selftest`). A flaky oracle is worse than none — it breaks the stop condition both ways: the loop "fixes" what isn't broken, or stops on what is. If it flakes, fix the oracle (quarantine the flaky test, pin the seed, stub the clock/network) *before* building the loop. This is the step almost everyone skips.
3. **Maker ≠ checker?** The model that wrote the code grades its own homework too generously — its own output is a high-probability continuation, so it systematically overrates correctness. A fresh-context verifier (ideally a different model) is the only reason walking away is safe. This is the same maker/checker split `/goal` uses internally to decide its own stop condition.
4. **Scoped creds + spend caps?** An unattended loop is also an unattended mistake-maker. Narrow credentials to staging, hard-cap spend, and (in container mode) cut outbound network (`--network none`) — the blast-radius defense if untrusted task text or code carries a prompt injection.
5. **Will you read the diffs?** A smooth loop grows the gap between code that exists and code you understand (comprehension debt) faster, not slower.

## Documented failure modes the blueprint defends against

| Failure | Cause | Blueprint defense |
|---|---|---|
| "Declare victory early" | No explicit oracle | `done_when` + `verify.sh`; agent may not self-certify |
| Flaky stop condition (stops on red / loops on green) | Non-deterministic oracle | `verify.sh --selftest`; gate question 2 |
| Weakened/deleted tests (reward hacking) | Oracle pressure | `protected_paths` + `guard.sh` (cheap, always-on) **plus** checker; not the prompt constraint alone |
| The last 20% (assumption propagation, abstraction bloat, dead code) | Conceptual errors compound unattended | checker reads the diff; small per-iteration increments |
| Runaway token spend | Loop left running | `budget` caps (`max_iterations`, per-run steps, daily USD) |
| Stuck / random walk (spins, never converges) | No progress detection | repeat-detector: same first failure twice → stop for a human (see Observability) |
| Lost context between runs | Memory in conversation, not on disk | `state_file` read first every iteration |
| Silent death | Iteration hangs / context fills | heartbeat marker + structured log (see Observability) |
| Exfiltration / destructive commands | YOLO auto-approve | `sandbox.mode` + scoped `creds` + `network: none` |

## Reward hacking: the cheap gate vs. the judge

The model will try to fool the oracle — not from malice but from optimization. If the only goal is a green check, the cheapest path to green is often breaking the check, not fixing the code: delete an assert, mock the logic, hardcode the expected value. Defend in three layers, cheapest first:

1. **The prompt constraint** ("never weaken the tests"). The *weakest* layer — the maker talks itself past it under pressure. Necessary, not sufficient.
2. **`guard.sh` — a deterministic gate the maker does not control.** It fails the iteration if any `protected_paths` entry changed (tracked edit/delete or new untracked file, via `git status --porcelain`). Near-free, always-on, runs before the oracle. This is the layer that actually holds, because the maker cannot satisfy the goal by editing what it is forbidden to touch.
3. **The judge (checker).** A different-model agent that reads the diff for *substance* — did the oracle go green because the code was fixed, not because its checks were gutted? Expensive (a second model per turn), so reserve it for that judgement and keep the deterministic gate always on.

Keep the cheap gate on by default and spend the judge where a second opinion is worth paying for.

## Observability and circuit breakers

A loop running unattended is also a loop *failing* unattended. Budget caps stop a runaway but tell you nothing about *why* a loop died. Make every iteration leave a trace so a human can diagnose it in the morning:

- **Structured log.** Each iteration appends one JSON line to `.loop_log.jsonl` (`ts`, `iter`, `event`, and the first failing check). After a dead loop you grep this and see the shape immediately.
- **Heartbeat.** Write `iter=<n> ts=<unix>` to a liveness file at the top of each iteration. A stale heartbeat with no new events is a *silent death* (a hung step or a context that filled).
- **Repeat-detector (circuit breaker).** If the oracle's first failure is identical to the previous iteration's, the loop is stuck / walking in circles. Stop and call a human rather than burning the budget retrying the same fix. Budget caps do not catch this — only progress detection does.

The four ways loops die map onto these signals: **runaway** (many iterations, no green → iteration/budget cap), **silent death** (heartbeat stops → liveness marker), **random walk / stuck** (failure repeats or churns, never converges → repeat-detector + a real fixpoint oracle), and **understanding debt** (repo grows past what you've read — invisible in any log; the only defense is your discipline to read the diffs).

The skill bakes the per-iteration log line, the stop-when-stuck rule, and the heartbeat reminder into `LOOP.md`. The *enforcement* (counting iterations, killing on a stale heartbeat) lives in the runner you wire up — `/loop`, `/goal`, an Action, or a Ralph `while` — not in this skill, which is not a runtime.

## On-disk state schema

The repo, not the conversation, is the loop's memory. Every iteration:

1. Read `state_file` and `git log --oneline -10` to recover context.
2. Do the smallest next increment; commit with a descriptive message.
3. Run the oracle. If exit 0, append a final `DONE` entry and stop.
4. Otherwise append `tried / passed / still-open` to `state_file` and end the iteration.

Git commits are the checkpoints; the state file is the human-readable summary; the oracle is the truth.

## Maker / checker pattern

- **Maker**: one iteration of the loop. Writes code, runs `guard.sh` then the oracle, updates state.
- **Checker (verifier)**: a separate agent with a clean context. Re-runs `guard.sh` and the oracle (does not trust a reported result), reads the diff for weakened tests / bloat / dead code, spot-reads the riskiest file, and returns `pass | reject` with evidence. Wire it as a Claude Code subagent (`.claude/agents/`, optionally `isolation: worktree`) or a Codex agent (`.codex/agents/*.toml`). The checker step can call `local-review` or `code-review-agents`.
