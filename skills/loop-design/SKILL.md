---
name: loop-design
description: >-
  Design a reusable, verifiable autonomous loop on top of harness primitives like /loop and /goal.
  Run a go/no-go gate (is there a pass/fail oracle?), define a portable loop blueprint (goal,
  done-when command, on-disk state, maker/checker split, sandbox/credential/budget guardrails),
  then scaffold the concrete files a harness runs. Use when setting up a recurring, unattended, or
  overnight agent loop, an automation or cron task, a /loop or /goal run, a Ralph-style while-true
  loop, or when deciding whether a task SHOULD be looped at all. Agent-agnostic across Claude Code,
  Codex, and CI/GitHub Actions. On-demand via /loop-design.
skill-type: workflow
compatibility: "Requires python3 (standard library only). Scaffolds a loop bundle into the target repo under .loops/ by default. Does not execute the loop — it emits the artifacts a harness runs."
---

# Loop Design

## Overview

This skill sits one floor **above** the harness loop primitives (`/loop`, `/goal`, Codex automations, GitHub Actions, Ralph). It does not replace them and does not run the loop. It does the part the harness leaves to you:

1. Decide whether a task **should** be a loop (a go/no-go gate built on one question: is there a pass/fail oracle?).
2. Capture a **portable loop blueprint** that maps onto any harness.
3. **Scaffold** the concrete files the harness then runs: the iteration prompt, the stop-condition oracle, the on-disk state file, and a separate checker (verifier) config.

The guiding rule: `/loop` and `/goal` run the loop; this skill decides whether the loop should exist and hands the harness a verifiable, bounded, portable spec to run.

**This skill builds *closed* loops.** A closed loop is bounded: a defined goal, a deterministic oracle at the stop, scoped credentials, and a point where it hands back to you. Its opposite is an *open* (exploratory) loop that roams a goal with no fixed stop — powerful, but it burns tokens fast and, pointed at loose standards, becomes a slop machine. Start closed; only open up once the gates below are trustworthy. Everything here assumes closed.

## When To Use

Use this skill when:
- setting up a recurring, unattended, or overnight agent loop (automation, cron, `/loop`, `/goal`, Ralph)
- deciding whether a task is even loop-shaped, or should stay an interactive prompt
- you want one loop definition that runs the same way in Claude Code and Codex
- a previous loop burned tokens, declared victory early, or shipped unread code and you need guardrails
- you are about to point a scheduler at a raw prompt with no stop condition

Skip this skill when:
- the task is a single interactive turn (`write-spec` or just prompt directly)
- you want to run one end-to-end feature cycle to a PR (use `autonomous-engineering` / lfg)

## The Go/No-Go Gate (do this first)

A loop is only worth building when its progress can be checked without you. Before anything else, answer:

1. **Is there an oracle?** Can "done" be expressed as a command that exits 0 (tests, lint, type-check, a metric threshold)? **If no → stop. This is not a loop. Keep prompting interactively.**
2. **Is that oracle deterministic?** Run it ~10× on one unchanged state — same exit code every time? A flaky oracle is *worse* than none: it breaks the stop condition in both directions (the loop fixes what isn't broken, or stops on what is). **If flaky → fix the oracle first, then build the loop.** (`./verify.sh --selftest` does this check.)
3. **Is the maker graded by something other than itself?** If no → the blueprint must add a fresh-context checker.
4. **Are credentials scoped and spend capped?** If no → do not let it run unattended.
5. **Will the diffs actually be read?** If no → the loop is buying comprehension debt at interest.

Gate 1 is hard. The scaffolder refuses to emit a bundle without a `done_when` command, by design. See `references/blueprint-spec.md` for the full rationale and failure modes.

## Workflow

1. **Gate.** Run the five go/no-go questions above. If gate 1 fails, report why this should not be a loop and stop.
2. **Draft the blueprint.** Fill the schema in `references/blueprint-spec.md`: `name`, `goal`, `done_when` (the oracle), `constraints`, `protected_paths` (the cheap reward-hacking gate), `cadence`, `harness`, `checker`, and `sandbox` (mode / creds / budget). Reuse `test-strategy` to design the oracle and `verify-before-complete` for stop semantics.
   - **Estimate the cost before launch.** Run the task by hand once and note the tokens/steps for one iteration; the upper bound is roughly `max_iterations × per-iteration cost` (stateless keeps this ~linear, not quadratic). If that number is alarming, lower `max_iterations` or split the task — don't launch and hope.
3. **Scaffold the bundle.** Run the scaffolder to write the loop files:

   ```bash
   python3 skills/loop-design/scripts/scaffold_loop.py --blueprint <blueprint.json> --out-dir .loops/<name>
   ```

   Or pass the essentials directly with `--name`, `--goal`, `--done-when`, `--harness`. The script writes `LOOP.md`, `verify.sh`, `guard.sh`, `progress.md`, `verifier.md`, `BINDINGS.md`, and a normalized `blueprint.json`.
4. **Bind to the harness.** Wire the bundle into the chosen harness using `BINDINGS.md` (generated) and `references/harness-bindings.md`. Put the checker in `.claude/agents/` or `.codex/agents/*.toml`.
5. **Dry-run once, attended.** First confirm the oracle is deterministic: `./verify.sh --selftest`. Then run a single iteration with you watching. Confirm `verify.sh` reports done correctly, `guard.sh` trips when you deliberately edit a protected path, and the checker actually rejects a bad result. Only then let it run unattended.
6. **Hand off.** Point out the budget caps and where state lives. The loop owner reads diffs; the loop does not get to self-certify.

## Boundaries

- Not a loop runtime. It does not re-invoke on a cadence or spawn a grader model — `/loop`, `/goal`, automations, and CI do that. This emits what they run.
- Not a single-feature workflow. `autonomous-engineering` (lfg/slfg) runs one plan→implement→review→PR cycle; this designs the recurring/unattended loop around such work.
- Not a test designer. Use `test-strategy` to build the oracle; this skill only requires that one exists.
- Do not name the generated command or any artifact `/loop` or `/goal` — those collide with harness primitives.
- Do not scaffold a loop with no `done_when`. A loop without an oracle is an unsupervised process with your credentials.

## Output

- A loop bundle under `.loops/<name>/` (or a chosen path):
  - `LOOP.md` — the iteration prompt the agent reads every cycle (memory-on-disk, oracle, constraints, guardrails)
  - `verify.sh` — the stop-condition oracle (exit 0 == done); the single source of truth for completion. `--selftest` checks it for flakiness.
  - `guard.sh` — the cheap, always-on reward-hacking gate (fails if a protected path changed); run before the oracle each iteration
  - `progress.md` — the on-disk state file (with a machine-readable `.loop_log.jsonl` companion for diagnosis)
  - `verifier.md` — a separate-context checker config (maker ≠ checker)
  - `BINDINGS.md` — concrete wiring for the chosen harness
  - `blueprint.json` — the normalized, portable loop definition
- A go/no-go verdict when a task is judged not loop-shaped, with the reason.

## Verification

- Gate 1 is enforced: `scaffold_loop.py` exits non-zero with a clear message when no `done_when` is provided.
- The generated `verify.sh` is executable and runs the exact `done_when` command; `./verify.sh --selftest` confirms it is deterministic before the loop runs.
- `guard.sh` exits non-zero when a protected path is modified, added, or deleted (tracked or untracked).
- An attended dry-run shows `verify.sh` exits 0 only when the goal is genuinely met, and the checker rejects a deliberately weakened result.
- `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills loop-design --strict` passes.

## Resources

- `references/blueprint-spec.md` — the blueprint schema, the go/no-go gate rationale, guardrails (sandbox/creds/budget), the on-disk state schema, the reward-hacking gate vs. judge, the observability/circuit-breaker contract, and the maker/checker pattern.
- `references/harness-bindings.md` — how one blueprint maps to Claude Code, Codex, GitHub Actions, and Ralph.
- `scripts/scaffold_loop.py` — emits the loop bundle from a blueprint; enforces the oracle gate.
- `assets/templates/` — the `LOOP.md`, `verify.sh`, `guard.sh`, `progress.md`, and `verifier.md` templates the scaffolder fills.
- `commands/loop-design.md` — the `/loop-design` command wrapper.

## Sibling skills

- `test-strategy` — designs the oracle (tests) that the loop verifies against.
- `verify-before-complete` — the evidence-based "done" semantics the oracle enforces.
- `local-review` / `code-review-agents` — what the checker (verifier) step calls.
- `handoff` — the state-on-disk pattern this skill applies to the loop's `progress.md`.
- `autonomous-engineering` — runs one feature cycle; this designs the loop around recurring work.
