---
name: research-architect
description: Engineer high-quality deep-research prompts and orchestrate their execution and verification. Use when the user wants to draft, improve, or critique a research prompt or research brief; commission or plan a multi-source, high-stakes, or multi-model research run; run research through external deep-research products (Claude/OpenAI/Gemini DR); or verify and score a research report someone or something else produced. Triggers on "research prompt", "research brief", "commission research", "plan a research run", "verify this report", "research architect". For a direct low-stakes web lookup where the user just wants the answer, use the deep-research skill instead — this skill sits upstream (prompt engineering, routing) and downstream (verification, postmortem) of execution.
skill-type: workflow
version: 1.0.0
triggers:
  - research prompt
  - research brief
  - research architect
  - commission research
  - plan a research run
  - verify this research report
compatibility: Terminal agents (Claude Code, Codex) are first-class — subagents and web fetch assumed. Web DR products supported as pluggable executors via a portable prompt artifact. Lint script requires python3.
---

# Research Architect

Execution is pluggable; this skill owns everything before and after it. It turns
a vague research desire into an engineered brief and prompt, routes execution
(local subagents, the `deep-research` skill, or an external DR product), then
verifies whatever comes back — regardless of who produced it.

**Core principle: iterate on outputs, not prompt aesthetics.** Fresh-session
critiques of prompt *text* are additive by disposition and never test anything.
Every stage below either produces a cheap testable artifact or scores a real
output.

## When To Use

- Drafting, improving, or critiquing a deep-research prompt or brief.
- Commissioning research that is multi-source, contested, high-stakes, or bound
  for an external DR product (Claude/OpenAI/Gemini) — anything where a bad
  first run is expensive.
- Planning multi-model merge runs or DAG-split research.
- Verifying or scoring a research report, wherever it came from — including
  reports pasted in from web DR products.

## Boundaries

- **Not an execution engine.** Searching, fetching, and synthesis happen in
  executor subagents, the `deep-research` skill, or external DR products.
- **Quick low-stakes lookups** ("what's the latest version of X, with sources")
  go straight to the `deep-research` skill — the pipeline overhead isn't worth
  it below multi-source stakes.
- **Never invent slot content.** Slots marked `(from stage N)` are filled from
  that stage's artifact; guessed priors or fabricated scout results poison the
  whole disconfirmation strategy.
- Prototyping/building from research findings belongs to a downstream build
  session, not here (block D5 hands off to it).

## Workflow

Stages 0–6 are drafting; 7 is execution; 8–9 are verification and memory. Each
stage writes a small artifact to the working directory (`research/<slug>/`).
These are run-scoped scratch, not deliverables — do not commit them, and stage
9 ends by cleaning them up. Cheap questions can skip stages — the router
(stage 2) decides — but never skip 0, 4, or 8.

### Stage 0 — Decision brief (`00-decision-brief.md`)

Interview the user, one question at a time, until you can fill:

- **Decision informed:** who acts, on what, by when. ("Curiosity" is a valid
  answer but say so — it changes evidence thresholds.)
- **Cost of being wrong** and staleness deadline.
- **Null result:** what a useful negative finding looks like.
- **Priors:** 3–6 bullets of what the user currently believes the answer is.
- **Surprises:** what would genuinely change their mind.

Extract answers already present in conversation before asking. Do not proceed
on guessed priors — they seed block A3 and the whole disconfirmation strategy.

### Stage 1 — Question engineering (`01-question.md`)

Produce: the core question (one sentence), sub-questions in priority order,
explicit scope in/out, a classification scheme if unlike things must be
compared, and a first-draft rubric (5–12 checkable acceptance criteria) plus
topic do-nots. Test each rubric item: could a verifier check it from the report
text alone? If not, rewrite or drop.

### Stage 2 — Route (`02-route.md`)

Three independent routing decisions:

1. **Block profile** — read `references/skeleton.md` and select:
   - *Verification-heavy* (claims about the world: markets, behavior, efficacy)
     → core + V-blocks.
   - *Design-heavy* (feeds a build/architecture decision) → core + D-blocks.
   - *Mixed* → both; keep the instruction budget by trimming per-block slots,
     not by dropping whole epistemics blocks.
2. **Execution surface** — local terminal agent (default; can clone repos,
   fetch cited URLs, spawn subagents) vs. external DR product (better at broad
   web sweeps; can't verify itself). Both is legitimate for high-stakes runs.
3. **Run shape** — single run / multi-model merge (adds M-blocks) / DAG split.
   Split into a DAG when sub-questions need different source classes or
   dispositions (e.g., literature survey vs. repo inspection vs. synthesis), or
   when a single run would exceed ~10 report sections at real depth. Each DAG
   node gets its own assembled prompt reusing the same core blocks; synthesis
   is its own node taking the others as input.

### Stage 3 — Scout (`03-scout.md`) — for standard/deep runs

Purpose: replace hoped-for source strategies with tested ones, at ~2% of run
cost.

- **Local:** spawn a recon subagent with ~10–15 fetches: test each named
  source class for reachability, check whether seed sources say what the
  background notes claim, list ambiguities in the brief, and propose the five
  highest-value queries.
- **External DR:** run a short probe in the *same product* first ("Which of
  these source classes can you access? Where will you struggle with this
  question? What's ambiguous?").

Scout output fills the `{{ACCESSIBILITY_RESULTS}}` and `{{FALLBACKS}}` slots
and often rewrites sub-question priorities. Skippable only for quick runs.

### Stage 4 — Draft (`04-prompt-<executor>.md`)

Assemble from `references/skeleton.md`: select blocks, fill slots from stage
artifacts, delete guidance comments, apply the per-executor calibration table.
Then lint:

```bash
python3 skills/research-architect/scripts/lint_prompt.py --executor terminal 04-prompt-claude-code.md
```

The script enforces the deterministic checks (instruction budget ≤40 web DR /
≤60 terminal, no unfilled `{{slots}}`, no leftover drafting comments, rubric +
degradation order + do-not list + summary block + self-report present). Two
judgment checks remain manual:

- [ ] Every requirement checkable from report text
- [ ] Do-not list is topic-specific, not generic virtue

### Stage 5 — Red-team the prompt (`05-redteam.md`)

Spawn a fresh critique subagent with the exact mandate in
`references/redteam-checklist.md` — role-play a competent-but-lazy executor,
find letter-vs-spirit gaps, and **delete at least three instructions**. The
deletion mandate is structural: it counters the additive bias that bloats
iterated prompts. Fold findings back into the draft; re-lint. One round is
usually enough — a second round only if round one found a conflict.

### Stage 6 — Run plan (`06-runplan.md`)

Record: executor(s), run shape, budget (searches/tokens/time), degradation
order, and for multi-model runs the fixed section order. For external DR, this
file doubles as the hand-back note to the user: which product, what to paste,
what to bring back.

### Stage 7 — Execute

- **Local:** hand each prompt to an executor subagent, or route through the
  `deep-research` skill (its depth router and evidence filter apply within a
  node). DAG nodes run in parallel where independent; synthesis node last.
- **External:** present the prompt file(s) to the user and stop. Reports
  return as pasted text or uploads; resume at stage 8.

### Stage 8 — Verify (`08-verification.md`)

Executor-independent: every report — including one pasted from Gemini — gets
the same treatment. This is the highest-leverage use of a terminal agent,
because external DR products cannot check their own citations.

1. **Structural pass (deterministic):** required sections present; summary
   block present; sample 10–15 citations (all, if fewer) and fetch each —
   is the URL live, and does the page actually support the claim it's
   attached to? Record hit rate.
2. **Rubric pass (judgment):** spawn a fresh critique subagent — one that has
   not seen the drafting stages — to score the report against the shipped
   rubric, item by item, with evidence quotes. Pass/fail per item, not vibes.
3. **Cross-run diff (multi-model only):** align sections; list confident
   specifics appearing in only one report — these are hallucination candidates;
   check each against a primary source before synthesis may use it.
4. **Verdict:** accept / accept-with-caveats (list them) / re-run node X with
   an amended prompt (say what changed and why).

### Stage 9 — Postmortem (`09-postmortem.md` + shared memory)

From the report's self-report (block A10 for external reports; the packet's
`self_report` field for local `deep-research` runs) plus verification results,
record: which instructions were followed, ignored, or misread; citation hit
rate; which rubric items discriminated (items that always pass are dead
weight). Then append durable lessons to two shared files (create on first
use):

- `references/postmortems.md` — dated lessons about the *skeleton and process*
  ("do-not lists beyond 8 items get ignored"; "rubric item X never fails —
  cut it").
- `references/executor-profiles.md` — per-executor quirks ("Gemini DR cannot
  reach X/Twitter"; "Codex follows file-level-evidence tables well but skips
  degradation orders").

This stage is what makes the skill compound instead of plateau. Do not skip it
after real runs.

**Cleanup (closes every run):** once durable lessons are appended, the
per-run scratch has served its purpose. Archive the keepers — the final
prompt(s), the report, and the verification verdict — then delete
`research/<slug>/`. Default archive: `docs/research/YYYY-MM-DD-<slug>-*.md`
in the repo the research serves (matching the `docs/design/` → `docs/specs/`
→ `docs/plans/` dating convention); for research that serves no repo, ask
where — personal archives often live outside any repo. If the run pauses at
stage 7 for an external DR product, tell the user the directory is disposable
once they've copied the prompt, and finish this cleanup when they return with
the report.

## Router quick reference

| Signal | Route |
|---|---|
| "Is X true / what's actually working / compare vendors" | Verification-heavy |
| "How would I build / design study / reference architecture" | Design-heavy |
| Both a market claim and a build handoff | Mixed |
| Stakes high, or topic contested | Add multi-model merge |
| Sub-questions need different source classes or dispositions | DAG split |
| Quick factual sweep, low stakes | Skip 3 and 5; consider handing straight to the `deep-research` skill |

## Output

- Per-stage artifacts in `research/<slug>/` (decision brief, question, route,
  scout, prompt(s), red-team, run plan, verification, postmortem) — run-scoped
  scratch, deleted at the end of stage 9 after keepers are archived (default:
  `docs/research/` in the repo the research serves).
- The primary deliverables: one assembled, linted prompt per executor
  (`04-prompt-<executor>.md`), and after execution a verification verdict
  (`08-verification.md`) with citation hit rate and per-rubric-item scores.
- Every report, regardless of executor, ends in the same summary block the
  `deep-research` skill emits (`key_findings` / `citations` /
  `confidence_gaps` / `next_queries`) — the interchange shape stage 8 consumes.

## Verification

- Assembled prompts pass `scripts/lint_prompt.py` for their executor before
  shipping — zero unfilled slots, zero drafting comments, budget respected.
- Stage 5 ran and deleted (not just added) instructions, or the router
  explicitly waived it as a quick run.
- Stage 8 verdicts cite evidence: citation hit rate from real fetches,
  pass/fail per rubric item with quotes — never vibes.
- After real runs, stage 9 appended at least one dated lesson or explicitly
  recorded "no new lessons."
- The run closed clean: keepers archived where the user chose, and
  `research/<slug>/` deleted — no stray artifacts left in the repo.

## Resources

- `references/skeleton.md` — composable prompt blocks, assembly rules, and
  per-executor calibration. Read at stage 2 (choose blocks) and stage 4
  (assemble).
- `references/redteam-checklist.md` — the stage-5 critique subagent's mandate.
- `scripts/lint_prompt.py` — deterministic stage-4 lint (budget, slots,
  comments, required blocks). `--json` for machine-readable output.
- `references/postmortems.md`, `references/executor-profiles.md` — shared
  memory; read at stages 2–5, append at stage 9; created on first use.
- Deferred until real runs seed them (tracked in `docs/project/BACKLOG.md`,
  do not reference as existing): `scripts/score_report.py`, `scripts/diff_runs.py`,
  `references/rubric-library.md`, `evals/golden-questions/`. Until then, perform
  scoring/diffing manually per stage 8.

## Sibling skills

- `deep-research` — the local execution backend (depth routing, search loop,
  evidence filtering). This skill sits upstream (stages 0–6) and downstream
  (stages 8–9) of it; quick low-stakes lookups should go to it directly.
- `brainstorming` / `first-principles` — upstream callers when the research
  question itself is still forming.
- `write-spec` / `write-plan` — downstream consumers when the verified report
  feeds a build (block D5's handoff target).
