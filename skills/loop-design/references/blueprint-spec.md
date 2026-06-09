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
  "state_file": "progress.md",
  "checker": {
    "enabled": true,
    "model": "different",
    "instructions": "Reject premature 'done', weakened tests, abstraction bloat, or dead code."
  },
  "sandbox": {
    "mode": "container",
    "creds": "staging-only / least-privilege",
    "budget": { "per_run_steps": 50, "daily_usd": 50 }
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
| `state_file` | no | On-disk memory the loop reads/writes each iteration. Default `progress.md`. |
| `checker` | no | The verifier (a separate agent/context). Strongly recommended; on by default. |
| `sandbox` | no | `mode` (container/codespace/host), `creds`, and `budget` caps. |

## The Go/No-Go Gate (why `done_when` is mandatory)

The single variable that decides whether a loop works is: **can the loop verify itself without you?** Across Willison, Anthropic, and Osmani the consensus is identical — agentic loops shine on problems with *clear success criteria where finding a solution requires trial-and-error*, and they fail without that signal.

So the gate is four questions, in order:

1. **Is there an oracle?** "Done" must be a command that exits 0. If you cannot write it, the task is not loop-shaped — keep prompting interactively. The scaffolder enforces this: no `done_when`, no bundle.
2. **Maker ≠ checker?** The model that wrote the code grades its own homework too generously. A fresh-context verifier (ideally a different model) is the only reason walking away is safe. This is the same maker/checker split `/goal` uses internally to decide its own stop condition.
3. **Scoped creds + spend caps?** An unattended loop is also an unattended mistake-maker. Narrow credentials to staging, hard-cap spend.
4. **Will you read the diffs?** A smooth loop grows the gap between code that exists and code you understand (comprehension debt) faster, not slower.

## Documented failure modes the blueprint defends against

| Failure | Cause | Blueprint defense |
|---|---|---|
| "Declare victory early" | No explicit oracle | `done_when` + `verify.sh`; agent may not self-certify |
| Weakened/deleted tests | Oracle pressure | `constraints` + checker rejects test edits |
| The last 20% (assumption propagation, abstraction bloat, dead code) | Conceptual errors compound unattended | checker reads the diff; small per-iteration increments |
| Runaway token spend | Loop left running | `budget` caps (per-run steps, daily USD) |
| Lost context between runs | Memory in conversation, not on disk | `state_file` read first every iteration |
| Exfiltration / destructive commands | YOLO auto-approve | `sandbox.mode` + scoped `creds` |

## On-disk state schema

The repo, not the conversation, is the loop's memory. Every iteration:

1. Read `state_file` and `git log --oneline -10` to recover context.
2. Do the smallest next increment; commit with a descriptive message.
3. Run the oracle. If exit 0, append a final `DONE` entry and stop.
4. Otherwise append `tried / passed / still-open` to `state_file` and end the iteration.

Git commits are the checkpoints; the state file is the human-readable summary; the oracle is the truth.

## Maker / checker pattern

- **Maker**: one iteration of the loop. Writes code, runs the oracle, updates state.
- **Checker (verifier)**: a separate agent with a clean context. Re-runs the oracle (does not trust a reported result), reads the diff for weakened tests / bloat / dead code, spot-reads the riskiest file, and returns `pass | reject` with evidence. Wire it as a Claude Code subagent (`.claude/agents/`, optionally `isolation: worktree`) or a Codex agent (`.codex/agents/*.toml`). The checker step can call `local-review` or `code-review-agents`.
