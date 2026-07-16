---
name: diagnose
description: Disciplined debugging loop for hard bugs and performance regressions — build a deterministic pass/fail signal first, then reproduce, hypothesise, instrument, fix, regression-test. Use when the user says "diagnose this", "debug this", "this is broken/throwing/failing", reports a bug whose cause is non-obvious, or describes a performance regression. For completion-time evidence checks use verify-before-complete; for new-test methodology use test-strategy; for post-hoc code review use local-review.
skill-type: workflow
version: 1.0.1
---

# Diagnose

A disciplined six-phase loop for hard bugs and performance regressions. The whole skill is built around one move: **construct a fast, deterministic, agent-runnable pass/fail signal *before* hypothesising about the cause.** With the loop, the bug is 90% fixed; without it, no amount of code-staring will save you.

## When To Use

- The user says "diagnose this", "debug this", "figure out why X is broken/throwing/failing/slow".
- The user reports a bug and the cause is not obvious from the stack trace.
- Output is wrong or non-deterministic, and you can't yet point at the offending line.
- A performance regression appeared and you need to localise the cause.
- An intermittent / flaky failure shows up in CI or production logs.

Skip phases only when explicitly justified (e.g. "the trace already names the cause; jump to Phase 5").

## Not For

- **Gating a completion claim.** Use `verify-before-complete` — that skill is about *evidence before claiming done*, not active debugging.
- **Designing new test coverage.** Use `test-strategy` for TDD methodology and test-shape decisions.
- **Reviewing code that *might* have bugs.** Use `local-review` or `code-review-agents` for findings-first inspection.
- **Bugs where you cannot construct any programmatic feedback signal.** Stop and explicitly say so; ask the user for an environment, a captured artifact, or permission to add temporary instrumentation. Do *not* hypothesise blind.

## Core Workflow

### Phase 1 — Build a feedback loop

**This is the skill.** Everything else is mechanical. Spend disproportionate effort here. Be aggressive, be creative, refuse to give up.

Ways to construct one — try in roughly this order, escalating only when the cheaper options don't fit:

1. **Failing test** at whatever seam reaches the bug (unit / integration / e2e).
2. **Curl or HTTP script** against a running dev server.
3. **CLI invocation** with a fixture input, diffing stdout against a known-good snapshot.
4. **Headless browser script** (Playwright / Puppeteer) — drives the UI, asserts on DOM / console / network.
5. **Replay a captured trace.** Save the real network request / payload / event log to disk; replay through the code path in isolation.
6. **Throwaway harness.** Spin up a minimal subset of the system (one service, mocked deps) that exercises the bug code path with a single function call.
7. **Property / fuzz loop.** For "sometimes wrong output", run 1000 random inputs and look for the failure mode.
8. **Bisection harness.** If the bug appeared between two known states (commit, dataset, version), automate "boot at state X, check, repeat" so `git bisect run` works.
9. **Differential loop.** Run the same input through old-version vs new-version and diff outputs.
10. **Human-in-the-loop bash script.** Last resort. If a human must click, drive them with `scripts/hitl-loop.template.sh` so the loop is still structured. Captured output feeds back to you.

The script `scripts/scaffold_feedback_loop.sh <kind>` writes a starter template for kinds 1–6 and 10 directly into the working tree — fill in the bug specifics and run.

**Iterate on the loop itself.** Treat it as a product:

- Faster? (Cache setup, skip unrelated init, narrow the test scope.)
- Sharper? (Assert on the specific symptom, not "didn't crash".)
- More deterministic? (Pin time, seed RNG, isolate filesystem, freeze network.)

A 30-second flaky loop is barely better than no loop. A 2-second deterministic loop is a debugging superpower.

**Non-deterministic bugs.** The goal is not a clean repro but a *higher reproduction rate*. Loop the trigger 100×, parallelise, add stress, narrow timing windows, inject sleeps. A 50% flake is debuggable; 1% is not.

**When you genuinely cannot build a loop.** Stop. List what you tried. Ask the user for: (a) access to whatever environment reproduces it, (b) a captured artifact (HAR, log dump, core dump, screen recording with timestamps), or (c) permission to add temporary production instrumentation. Do **not** proceed without a loop.

Do not advance to Phase 2 until you have a loop you believe in.

### Phase 2 — Reproduce

Run the loop. Watch the bug appear. Confirm:

- [ ] The loop produces the failure mode the **user** described — not a different failure that happens to be nearby. Wrong bug → wrong fix.
- [ ] The failure is reproducible across multiple runs (or, for non-deterministic bugs, at a high enough rate to debug against — see Phase 1).
- [ ] You have captured the exact symptom (error message, wrong output, slow timing) so later phases can verify the fix actually addresses it.

### Phase 3 — Hypothesise

Generate **3–5 ranked hypotheses** before testing any of them. Single-hypothesis generation anchors on the first plausible idea.

Each hypothesis must be **falsifiable** — state the prediction it makes:

> Format: "If `<X>` is the cause, then `<changing Y>` will make the bug disappear / `<changing Z>` will make it worse."

If you can't state the prediction, the hypothesis is a vibe — discard or sharpen it.

**Show the ranked list to the user before testing.** Domain knowledge often re-ranks instantly ("we just deployed a change to #3"), or rules out hypotheses they've already checked. Cheap checkpoint, big time saver. Don't block on it — proceed with your ranking if the user is AFK.

### Phase 4 — Instrument

Each probe must map to a specific Phase-3 prediction. **Change one variable at a time.**

Tool preference:

1. **Debugger / REPL inspection** if the env supports it. One breakpoint beats ten logs.
2. **Targeted logs** at the boundaries that distinguish hypotheses.
3. Never "log everything and grep".

**Tag every debug log** with a unique prefix, e.g. `[DEBUG-a4f2]`. Cleanup at the end becomes a single grep. Untagged logs survive; tagged logs die.

**Performance branch.** For perf regressions, logs are usually wrong. Establish a baseline measurement (timing harness, `performance.now()`, profiler, query plan), then bisect. Measure first, fix second.

### Phase 5 — Fix and regression-test

Write the regression test **before the fix** — but only if there is a **correct seam** for it.

A correct seam exercises the **real bug pattern** as it occurs at the call site. If the only available seam is too shallow (single-caller test for a multi-caller bug, unit test that can't replicate the chain), a test there gives false confidence.

**If no correct seam exists, that itself is the finding.** Note it. The architecture is preventing the bug from being locked down. Flag for Phase 6.

If a correct seam exists:

1. Turn the minimised repro into a failing test at that seam.
2. Watch it fail.
3. Apply the fix.
4. Watch it pass.
5. Re-run the Phase 1 feedback loop against the original (un-minimised) scenario.

### Phase 6 — Cleanup and post-mortem

Required before declaring done:

- [ ] Original repro no longer reproduces (re-run the Phase 1 loop).
- [ ] Regression test passes (or absence of seam is documented).
- [ ] All `[DEBUG-...]` instrumentation removed (`grep` the prefix).
- [ ] Throwaway harnesses deleted (or moved to a clearly-marked debug location).
- [ ] The hypothesis that turned out correct is stated in the commit / PR message — so the next debugger learns.

Then ask: **what would have prevented this bug?** If the answer involves architectural change (no good test seam, tangled callers, hidden coupling), record the specifics for a follow-up architecture review. Make the recommendation **after** the fix, not before — you have more information now than when you started.

## Output Contract

A diagnosis run produces:

1. **A feedback-loop artifact** — a script, test, or harness that produces a fast, deterministic pass/fail signal for the bug. Lives in the repo (or is explicitly marked as throwaway).
2. **A ranked hypothesis list** — 3–5 falsifiable hypotheses with predictions, written down before any was tested.
3. **A fix** — the smallest change that makes the loop pass.
4. **A regression test** — at the correct seam, or an explicit note that no correct seam exists.
5. **A commit / PR message** stating the correct hypothesis (so the next debugger learns).
6. **Optional architecture finding** — surfaced only if Phase 6 turns up structural prevention.

## Verification

Diagnosis is complete only when all of:

- [ ] The original repro no longer reproduces under the Phase 1 loop.
- [ ] If a correct seam existed, a regression test exists and passes; otherwise the seam-absence is documented.
- [ ] All `[DEBUG-...]` tagged instrumentation has been removed (`grep` returns no hits).
- [ ] Throwaway harnesses are deleted or marked.
- [ ] The commit / PR message names the hypothesis that turned out correct.

If any item is unchecked, diagnosis is not done — even if "the bug seems fixed".

## Resources

### `scripts/scaffold_feedback_loop.sh`

Writes a starter template for the most common Phase 1 loop kinds:

```bash
bash skills/diagnose/scripts/scaffold_feedback_loop.sh <kind> [path]
```

`<kind>` is one of: `failing-test` · `curl` · `cli-diff` · `playwright` · `replay` · `harness` · `hitl`.

Output is a single file at `path` (default `./repro.<ext>`) you fill in with bug specifics, then run. The template includes the speed / sharpness / determinism checklist as comments.

### `scripts/hitl-loop.template.sh`

Standalone human-in-the-loop reproduction loop. Copy, edit the `step` and `capture` calls, and run. The agent runs the script; the user follows prompts in their terminal; captured values are echoed as `KEY=VALUE` for the agent to parse.

## Sibling skills

- `verify-before-complete` — the *gate* before claiming done; Phase 6 verification feeds it.
- `test-strategy` — methodology for the regression test you write in Phase 5 (real deps over mocks, behavior-based assertions).
- `local-review` / `code-review-agents` — when the question is "is this code correct?" rather than "why is *this specific* failure happening?"
- `first-principles` — when the bug is actually a design flaw and Phase 6 surfaces architectural prevention work.
