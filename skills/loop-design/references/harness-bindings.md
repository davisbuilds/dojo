# Harness Bindings

One blueprint, four runtimes. The bundle (`LOOP.md`, `verify.sh`, `guard.sh`, `progress.md`, `verifier.md`) is identical; only the wiring differs. The scaffolder writes the relevant block into `BINDINGS.md`; this file is the full reference.

## Claude Code

| Cadence | Wiring |
|---|---|
| `until-done` | `/goal` with the contents of `LOOP.md` as the objective and "stop when `./verify.sh` exits 0" as the condition. A separate small model grades the stop condition. |
| `interval:<dur>` | `/loop <dur> "read LOOP.md and run exactly one iteration"`. |
| `cron:'<expr>'` | `/schedule` (routine) running the same one-iteration prompt; or a cron task. |
| beyond the laptop | GitHub Actions (below) running `claude -p` headless. |

- **Checker**: put `verifier.md` at `.claude/agents/<name>-verifier.md`. Add `isolation: worktree` so it grades on a fresh checkout.
- **Isolation**: run the maker with `--worktree` (or a subagent with `isolation: worktree`) so parallel loops never collide.
- **Lifecycle**: a Stop/PostToolUse hook can run `verify.sh` and refuse a premature "done".

## Codex

| Cadence | Wiring |
|---|---|
| scheduled | Automations tab → pick project, prompt = "read LOOP.md, run one iteration", set cadence, run on a worktree. Findings land in the Triage inbox. |
| `until-done` | `/goal` — works across turns to a verifiable stopping condition, with pause/resume. |
| reusable method | wrap the iteration prompt as a skill (`$name`); "skills define the method, automations define the schedule". |

- **Checker**: `.codex/agents/<name>-verifier.toml` (name, description, instructions from `verifier.md`, optional stronger model + higher reasoning effort).
- **Isolation**: automations run on a dedicated worktree by default.

## GitHub Actions (unattended / beyond the laptop)

- A scheduled workflow (`on: schedule: cron`) checks out the repo and runs the agent headless reading `LOOP.md`:
  - Claude Code: `claude -p "$(cat .loops/<name>/LOOP.md)"`
  - Codex: `codex exec "$(cat .loops/<name>/LOOP.md)"`
- The job runs `verify.sh`; on exit 0 it opens/labels a PR, otherwise commits progress and exits so the next run resumes.
- This is where scoped creds + spend caps matter most — use repository/environment secrets limited to staging.

## Ralph (the dumbest loop that works)

The blueprint is also a Ralph loop. The runner is *yours* — this skill does not ship one (that would duplicate `/loop` and the `ralph-wiggum` plugin) — but the wiring is:

```bash
# from inside .loops/<name>/
./verify.sh --selftest || { echo "oracle is flaky — fix it first"; exit 1; }
i=0; last=""
while :; do
  i=$((i+1)); [ "$i" -gt 20 ] && { echo "iteration cap"; break; }   # runaway fuse
  echo "iter=$i ts=$(date +%s)" > .loop_heartbeat                   # liveness
  <agent> -p "$(cat LOOP.md)"     # fresh context each pass; memory is the repo
  ./guard.sh || { echo "reward-hacking gate tripped"; break; }      # cheap gate
  ./verify.sh && break            # the oracle is the only exit
  cur="$(./verify.sh 2>&1 | grep -m1 -i fail || true)"              # circuit breaker
  [ "$cur" = "$last" ] && { echo "stuck on same failure — calling a human"; break; }
  last="$cur"
done
```

Each pass is "deterministically bad in a nondeterministic world": individually mediocre, convergent over iterations — but only when `verify.sh` is a real, *deterministic* oracle. With a weak or flaky oracle, Ralph converges confidently on garbage. Add the checker before letting it run unattended.

## Per-iteration context (headless / Ralph only)

Interactive harnesses (`/goal`, Codex automations) build each turn's context themselves via tool calls — let them. But a **headless** loop (`claude -p` / `codex exec` in a `while` or an Action) gets exactly the context you hand it, and two failure modes bite:

- Feed it the whole repo → the window fills, quality rots (context rot), and you pay for irrelevant tokens. The point of stateless iteration is lost.
- Feed it too little → it fixes blind.

The right slice is three things and nothing extra: **machine state** (`progress.md` / `.loop_state.json`), **the one open failure** being worked, and **only the files relevant to it**. Assemble the file slice deterministically from signals you already have — paths in the failing test's stack trace, plus `git diff --name-only HEAD~1` — and cap it with an explicit token budget so the slice can't grow unnoticed across iterations. Start with that dumb, explainable heuristic; reach for embeddings or a dependency graph only if it actually misses.

## Portability notes

- Keep `done_when` POSIX-runnable so `verify.sh` is identical everywhere.
- Keep `LOOP.md` instructions harness-neutral (no slash commands inside it) so the same prompt drives any runtime.
- Run `./guard.sh` before `./verify.sh` every iteration in every harness; both are POSIX shell, so the wiring is identical across runtimes.
- MCP connectors written for one harness generally work in the other; bundle them as a plugin to share a loop setup across repos.
