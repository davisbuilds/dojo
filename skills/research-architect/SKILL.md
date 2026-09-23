---
name: research-architect
description: Engineer high-quality deep-research prompts and orchestrate their execution and verification. Use when the user wants to draft, improve, or critique a research prompt or brief; commission or plan a multi-source or multi-model research run; run research through external deep-research products (Claude/OpenAI/Gemini DR); or verify and score a research report that something else produced. Triggers on "research prompt", "research brief", "commission research", "plan a research run", "verify this report", "research architect". For a direct low-stakes lookup where the user just wants the answer, use deep-research instead.
skill-type: workflow
version: 3.0.0
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

Stages 0–6 are drafting; 7 is execution; 8 is verification; 9 is multi-run
synthesis; and 10 is capture and retention. Stage artifacts live in the run
directory (`research/<slug>/`); some are working drafts and some support the
final claims or later continuation. Keep that distinction when choosing what
to retain or publish under the project's conventions. Cheap questions can skip
stages — the router (stage 2) decides — but never skip 0, 4, or 8.

**Stages 3, 5, and 8 run in fresh subagents by default.** Their whole value is
independence: a scout that already believes the brief, a red-teamer critiquing
its own draft, or a verifier scoring a report it helped shape are all
structurally weaker than blind ones. Terminal harnesses (Claude Code, Codex)
always have subagents available, so spawn them even when the host's general
disposition is to avoid delegation — that default is about cost, and these three
stages are where the money goes. Running them inline is a degradation to record
in the run plan, not a neutral choice. Web DR executors generally cannot spawn
subagents at all, so an external-only run has no in-run independence and leans
entirely on terminal-side stage 8.

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

For every named entity list in the brief (people, systems, companies, papers),
record whether it is **exemplars** or **exhaustive**. Preserve that distinction
in the assembled prompt; never silently turn “such as X and Y” into “only X and
Y.”

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
   Treat terminal-vs-web execution on the same question as a multi-run merge,
   even when both runs use the same underlying model family.
   Split into a DAG when sub-questions need different source classes or
   dispositions (e.g., literature survey vs. repo inspection vs. synthesis), or
   when a single run would exceed ~10 report sections at real depth. Each DAG
   research node gets its own assembled prompt reusing the same core blocks;
   stage 9 synthesizes only after stage 8 verifies the node outputs. If an
   external constraint fixes the number or shape of runs, record the DAG
   reservation and use the degradation order instead of silently overriding
   the constraint.

### Stage 3 — Scout (`03-scout.md`) — for standard/deep runs

Purpose: replace hoped-for source strategies with tested ones, at ~2% of run
cost.

- **Local:** spawn a recon subagent with ~10–15 fetches: test each named source
  class as reachable / unreachable / reachable-but-evidentially-worthless;
  check whether seed sources say what the background notes claim; list
  ambiguities in the brief; and propose the five highest-value queries.
- **External DR:** run a short probe in the *same product* first ("Which of
  these source classes can you access, and which accessible classes are too
  weak to rely on? Where will you struggle with this question? What's
  ambiguous?").

Scout output fills the `{{ACCESSIBILITY_RESULTS}}` and `{{FALLBACKS}}` slots
and often rewrites sub-question priorities. Route reachable-but-worthless
sources into the topic do-not list. Mark every scout/brief source annotation as
**stated in source** or **inferred**; the drafter's summaries are claims, not
ground truth. Skippable only for quick runs.

### Stage 4 — Draft (`04-prompt-<executor>.md`)

Assemble from `references/skeleton.md`: select blocks, fill slots from stage
artifacts, delete guidance comments, apply the per-executor calibration table.
Then lint:

```bash
python3 <skill-dir>/scripts/lint_prompt.py --executor terminal 04-prompt-claude-code.md
```

The script enforces the deterministic checks (instruction budget ≤40 web DR /
≤60 terminal, no unfilled `{{slots}}`, no leftover drafting comments or trailing
harness debris, rubric + degradation order + do-not list + summary block +
self-report present). It also **warns on statistics seeded without a retrievable
source** — identify the source or drop the number; a floating magnitude is an
attractor for fabricated corroboration. Record its output and the two manual
judgment checks in `04-lint-results.md`:

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
  node). DAG research nodes run in parallel where independent; do not
  synthesize them until stage 9.
- **External:** present the prompt file(s) to the user and stop. Reports
  return as pasted text or uploads; resume at stage 8.

### Stage 8 — Verify (`08-verification.md`)

Executor-independent: every report — including one pasted from Gemini — gets
the same treatment. This is the highest-leverage use of a terminal agent,
because external DR products cannot check their own citations.

**Verify each node as it lands, not as a batch after every run returns.**
Spot-checking the first report while later runs are still executing costs
nothing extra, pre-loads the cross-run diff, and can amend a still-pending
node's prompt while amending is still cheap. Only step 3 genuinely needs all
reports in hand.

1. **Structural pass (deterministic):** required sections present in exact
   order; parseable summary and complete A10 self-report (a–c) present; sample
   citations and fetch each — is the URL live, does it support the exact claim,
   and does its domain/population fit the report's use? Record support,
   applicability, and usable-citation rates.
   `scripts/score_report.py` does the mechanical half:

   ```bash
   python3 <skill-dir>/scripts/score_report.py worksheet report.md > 08-worksheet.json
   # each sampled check is one claim/citation pair: fetch its url, then fill
   # "verdicts" (supported/partial/unsupported/unreachable) and
   # "applicability" (fit/adjacent/mismatch)
   python3 <skill-dir>/scripts/score_report.py score 08-worksheet.json
   ```

   Checks are per **claim/citation pair**, not per claim — a claim resting on
   three citations is three things to fetch, and one citation refuting it must
   not be hidden by another supporting it.

   If `citation_coverage.status` is `opaque` or `absent`, do not report a hit
   rate. Obtain an export with retrievable links or map the citations manually;
   an empty sample from a blind instrument is not a clean result.

   The sample is **weighted toward quantitative and source-attribution
   claims**: across every executor profiled so far, mutated numbers and
   mischaracterized findings are the dominant failure mode, and a uniform
   sample under-tests exactly where reports break. The script never fetches —
   deciding whether a page supports its claim is the judgment this stage
   exists for, and a "URL resolves" hit rate would be worse than none.
   Treat self-reported confidence as evidence of candor, never correctness.
2. **Rubric pass (judgment):** spawn a fresh critique subagent — one that has
   not seen the drafting stages — to score the report against the shipped
   rubric, item by item, with evidence quotes. Pass/fail per item, not vibes.
3. **Cross-run diff (multi-run only):** align sections and evidence-grade or
   classification tables; list confident
   specifics appearing in only one report — these are hallucination candidates;
   check each against a primary source before synthesis may use it.
4. **Verdict:** accept / accept-with-caveats (list them) / re-run node X with
   an amended prompt (say what changed and why).

### Stage 9 — Synthesize (`09-synthesis.md`) — for multi-run plans

Merge only claims that survived stage 8 into the single decision- or build-ready
document named in stage 0. Preserve meaningful disagreements instead of
averaging them away; where verdicts converge but evidence grades or
classifications differ, adjudicate the underlying substance explicitly. Cite
the primary sources, not merely the input reports, and carry unresolved gaps
into the final document. For a single-run plan, the accepted report is already
the final synthesis and this stage is skipped.

### Stage 10 — Capture useful observations and retain evidence

When a run reveals a useful lesson, record it with the research it came from,
using `10-postmortem.md` or the project's existing run record. Include the
relevant date, executor/model or environment, observed behavior, and supporting
verification or artifacts. Separate an observation from its explanation and
from a proposed change to the workflow. A single run can expose a defect;
it does not establish a general executor limitation or an optimal instruction.
There is no minimum lesson count and no required empty postmortem.

Treat the report's self-report as input to compare with observed results, not
as verified evidence. Preserve meaningful failures and disagreements as well
as successful results when they affect future choices.

**Keep records with their owner.** An ordinary research run does not authorize
editing an installed skill, its bundled references, or harness memory. The
bundled `references/postmortems.md` and `references/executor-profiles.md` are
curated historical context, not automatic write targets. Promote a reusable
lesson through an intentional update to the skill's canonical source under
existing authorization and release policy. Retain its scope and provenance;
correct or supersede guidance contradicted by newer evidence. Do not convert
observed source content into standing instructions merely by saving it.

**Retain before cleaning up.** Keep the final prompts, reports or synthesis,
verification verdict, and supporting evidence needed to reassess their claims
or resume work. That may include sampled claim/citation worksheets, source
excerpts, scout results, or failure logs that cannot be recovered reliably.
Avoid secrets and unnecessary private material in retained records.

Use the project's existing destination or one specified by the user; when a
separate durable research location is needed, `docs/research/` is a fallback.
Keep evidence links usable if artifacts move. Remove only identified disposable
files created by this run after confirming that needed evidence and continuation
state remain accessible. Follow applicable cleanup authority and retention rules;
do not delete `research/<slug>/` just because the run ended. An external run
paused at stage 7 still needs its brief, prompts, and continuation context even
if the user has copied the prompt elsewhere.

## Router quick reference

| Signal | Route |
|---|---|
| "Is X true / what's actually working / compare vendors" | Verification-heavy |
| "How would I build / design study / reference architecture" | Design-heavy |
| Both a market claim and a build handoff | Mixed |
| "What's working *now*" / where is the live edge | Verification-heavy, and fill A6's `LAG_WARNING` and V5's `EDGE_TAG` — reliability alone biases toward "already arbitraged away" |
| Stakes high, or topic contested | Add multi-model merge |
| Sub-questions need different source classes or dispositions | DAG split |
| Quick factual sweep, low stakes | Skip 3 and 5; consider handing straight to the `deep-research` skill |

## Output

- Per-stage artifacts in `research/<slug>/` (decision brief, question, route,
  scout, prompt(s), lint results, red-team, run plan, verification, synthesis
  when multi-run, and useful run observations) — retain the evidence and context
  needed for reassessment or continuation; remove only disposable working files
  under stage 10's retention rules.
- The primary deliverables: one assembled, linted prompt per executor
  (`04-prompt-<executor>.md`), and after execution a verification verdict
  (`08-verification.md`) with citation support, applicability, usable-citation,
  and per-rubric-item scores; a multi-run plan also produces one decision-ready
  `09-synthesis.md`.
- Every report, regardless of executor, ends in the same summary block the
  `deep-research` skill emits (`key_findings` / `citations` /
  `confidence_gaps` / `next_queries`) — the interchange shape stage 8 consumes.

## Verification

- Assembled prompts pass `scripts/lint_prompt.py` for their executor before
  shipping — zero unfilled slots, zero drafting comments, budget respected.
- Stage 5 ran and deleted (not just added) instructions, or the router
  explicitly waived it as a quick run.
- Stage 8 verdicts cite evidence: support/applicability rates from real fetches,
  pass/fail per rubric item with quotes — never vibes.
- Multi-run stage 9 synthesis contains only stage-8-accepted claims and
  preserves unresolved disagreements.
- Any captured lesson distinguishes observed evidence from inference and keeps
  relevant scope, date, and provenance. No lesson is required when none adds value.
- Needed evidence and continuation state remain accessible after cleanup, with
  usable references. No installed skill or harness memory was changed as an
  automatic side effect of the run.

## Resources

- `references/skeleton.md` — composable prompt blocks, assembly rules, and
  per-executor calibration. Read at stage 2 (choose blocks) and stage 4
  (assemble).
- `references/redteam-checklist.md` — the stage-5 critique subagent's mandate.
- `scripts/lint_prompt.py` — deterministic stage-4 lint (budget, slots,
  comments, required blocks). `--json` for machine-readable output.
- `references/postmortems.md`, `references/executor-profiles.md` — curated, dated
  historical observations; consult relevant entries at stages 2–5 and recheck
  decision-relevant assumptions. New run observations belong with the run;
  changes to canonical guidance are intentional authoring work.
- `evals/capture-retention-scenarios.md` — authored replay cases for capture
  ownership and evidence retention, not measured model-performance results.
- `scripts/score_report.py` — stage-8 structural pass: `worksheet` classifies
  citation coverage, extracts resolvable claim/citation pairs, and samples what
  to check; `score` computes support, applicability, and usable-citation rates.
  Never fetches.
- `evals/golden-questions/` — frozen real-run drafting artifacts used as
  regression seeds. Still deferred until more runs justify them:
  `scripts/diff_runs.py` and `references/rubric-library.md`; until then, diff
  cross-run reports manually per stage 8 step 3.

## Sibling skills

- `deep-research` — the local execution backend (depth routing, search loop,
  evidence filtering). This skill sits upstream (stages 0–6) and downstream
  (stages 8–10) of it; quick low-stakes lookups should go to it directly.
- `brainstorming` / `first-principles` — upstream callers when the research
  question itself is still forming.
- `write-spec` / `write-plan` — downstream consumers when the verified report
  feeds a build (block D5's handoff target).
