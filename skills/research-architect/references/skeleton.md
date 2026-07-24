# Research Prompt Skeleton — Composable Blocks

This file is the invariant DNA of a high-quality deep-research prompt. Assemble a
prompt by selecting blocks, filling `{{SLOTS}}`, and deleting the HTML comments
(they are drafting guidance, never shipped to the executor).

## Assembly rules

1. **Core blocks (A1–A10) are always included**, in order.
2. **Verification blocks (V1–V5)** go in when the question makes claims about the
   world that could be wrong (markets, behavior, efficacy, "what's actually
   working"). Insert after A5.
3. **Design blocks (D1–D5)** go in when the deliverable feeds a build or decision
   about how to construct something (architecture studies, tooling surveys,
   reference designs). Insert after A5, or interleaved with V-blocks for mixed
   questions.
4. **Merge blocks (M1–M2)** go in only for multi-run plans (multiple
   models/executors whose reports will be diffed and synthesized). Two executor
   classes on the same question — for example terminal and web DR — count even
   if they share a model family.
5. **Instruction budget.** Count the imperative requirements in the assembled
   prompt (explicit must/never/always clauses plus bullet-initial imperative
   verbs are approximate signals). Target **≤ 40 for web DR products, ≤ 60 for
   terminal agents**. Most fixed-block assemblies land well below the ceiling;
   slot phrasing is usually where density grows. Over budget → rank instructions
   by "what breaks if this is dropped" and cut from the bottom.
   An instruction that merely restates good general practice ("be thorough",
   "cite sources") is dead weight — the epistemics blocks already carry that
   load with specifics. Cut it.
6. **Every requirement must be checkable.** If you cannot imagine a verifier
   confirming compliance from the report text alone, rewrite the requirement
   until you can, or delete it. ("Be skeptical" → uncheckable. "Every income
   claim carries an evidence grade and a date" → checkable.)
7. The slots marked `(from stage N)` are filled from that pipeline stage's
   artifact — do not invent their content while drafting.

---

## A. Core blocks (always)

### A1 — Mission & disposition

> You are a {{DISPOSITION — e.g., "skeptical, intellectually curious research
> analyst with a nose for hype" / "rigorous systems engineer doing a design
> study"}}. Your job: {{ONE_SENTENCE_MISSION}}.
>
> Depth and honesty beat breadth and optimism. {{N_DEEP}} well-evidenced
> findings are worth more than {{N_SHALLOW}} unverified claims. The most
> valuable findings are often the quiet, unglamorous ones — stay genuinely open
> to them while assuming loud claims are exaggerated until evidence says
> otherwise.

<!-- Keep the disposition specific to the question. A generic "expert
researcher" persona adds nothing; a disposition that encodes the likely failure
mode of the topic (hype, vendor marketing, academic overclaiming) does real
work. -->

### A2 — Decision context & core question

> **The decision this research informs:** {{DECISION — who will act, on what,
> by when}} (from stage 0)
>
> **Core question:** {{CORE_QUESTION}}
>
> **Sub-questions, in priority order:** {{SUBQUESTIONS}} (from stage 1)
>
> **A useful null result looks like:** {{NULL_RESULT — e.g., "the celebrated
> method mostly doesn't work; say so plainly and show the reasoning"}}. A
> well-evidenced negative answer is a success, not a failure, of this research.

<!-- The decision context is what lets the executor prioritize when it hits its
compute budget. Without it, every sub-question looks equally important and you
get uniform shallowness. -->

### A3 — Priors & surprise register

> **My current beliefs (attack these):** {{PRIORS — 3-6 bullets of what the
> requester currently thinks the answer is}} (from stage 0)
>
> **What would genuinely surprise me:** {{SURPRISES}} (from stage 0)
>
> Treat the priors as targets for disconfirmation, not as conclusions to
> confirm. If the evidence supports a prior, say so and show why; if it breaks
> one, lead with that.

### A4 — Verification & honesty

> Any background notes, summaries, seed material, or drafter/scout annotations
> provided in this prompt are
> **hypotheses to verify, not ground truth**. Confirm claims, numbers, dates,
> and configurations against primary sources. Explicitly distinguish "reported
> in the primary source" from "my inference." Where public material does not
> support a detail, say so and present plausible hypotheses separately, labeled
> as such. Do not invent specifics to appear complete: "unverified / not
> public" is always a better answer than a fabricated one. Where this prompt
> gives a number without naming a retrievable source, do not go looking for a
> source that matches it — report it as unsourced and move on.

### A5 — Required frame check

> **Begin the report with a frame check.** State either (a) the framing problem
> — the question is malformed, a stated tension is not the real tension, or an
> important consideration is missing — or (b) "frame verified" plus one sentence
> naming what you checked. If the framing is wrong, say so before answering the
> question as posed. You are not graded on agreement with the prompt.

<!-- Stage 6's SECTION_ORDER must place the frame check first. Making the
section unconditional distinguishes "checked and found no issue" from "did not
check." -->

### A6 — Source strategy

> **Seed sources (vetted; start here):** {{SEED_SOURCES — each carrying a
> stable identifier: URL, arXiv/DOI/SSRN id, or repo path}}
>
> **Rank sources on two independent axes; a source can be high on one and low
> on the other:**
>
> - **Reliability** — how likely the claim is true. {{RELIABILITY_ORDER — e.g.,
>   primary papers > official repos/blogs > practitioner communities >
>   secondary analysis; name the specific venues that matter for this topic}}
> - **Edge-relevance × recency** — how likely the claim still describes the
>   present. {{EDGE_ORDER — e.g., live telemetry/on-chain data and inspected
>   working code > dated practitioner reports > aggregate published findings}}
>
> {{LAG_WARNING — include for "what is actually working now" questions, e.g.,
> "published efficiency results are lagging and selection-biased — an efficient
> market is publishable, a live edge is not — so treat them as evidence about
> the past, never as evidence that the edge is gone today"}}
>
> **Scout status — reachable / unreachable / reachable-but-evidentially-worthless:**
> {{ACCESSIBILITY_RESULTS}} (from stage 3)
>
> **Fallbacks:** where a priority source class is inaccessible, use
> {{FALLBACKS}} instead — never silently substitute low-grade sources (SEO
> listicles, content farms) for inaccessible high-grade ones. An unreachable
> but valuable source class belongs under research gaps, not implied coverage.
>
> The named seeds and source classes are a starting floor, **not a ceiling**.
> Expand into any reachable source class that meets the evidence standard,
> including high-grade classes the prompt did not anticipate.
>
> {{SOURCE_FLOOR — optional: minimum coverage, e.g., "all seed sources plus ≥10
> adjacent primary sources spanning X, Y, Z"}}

<!-- The accessibility slot is mandatory when a scout pass ran. This is the
single most common silent failure of DR products: the prompt names Reddit/X/HN,
the agent can't reach them, and it substitutes listicles without saying so.
Move reachable-but-evidentially-worthless sources into A7's do-not list.

Deleted here: "do not pad the bibliography; a marginal low-quality source is
worse than none." It contradicted M2 ("completeness matters more than curation")
on multi-run assemblies, and the evidence standard above already excludes weak
sources. If you assemble without M-blocks and the topic invites padding, the
do-not list is the place for it.

Two axes, because one ranking cannot carry both jobs. Collapsing them ranks
sources by verifiability alone, which systematically over-weights rigorous but
lagging evidence — fine for "is X true", quietly biasing for "what is working
now" (2026-07-23 postmortem). Rank discovery on edge-relevance, belief on
reliability.

SEED_SOURCES entries must be identified, never paraphrased statistics. A
floating "a large study reportedly found X" is an attractor: the executor
fabricates a precise citation that matches the number (2026-07-23: a real
292M-trade paper was "confirmed" as 1.2B trades with the opposite finding).
Seed the identified source as a verify-this target, or omit the number. -->

### A7 — Do-not list

> **Do NOT (known failure modes for this topic):**
> {{TOPIC_DO_NOTS — 4-8 items, each a concrete error an executor plausibly
> makes on THIS topic, e.g., "do not treat k-anonymity as equivalent to formal
> DP", "do not conflate gross revenue with owner income"}} (from stages 1 & 5)
>
> And universally: do not reconstruct unpublished internals of any organization
> beyond what public sources support.

<!-- Topic do-nots are the highest-value-per-token content in the prompt. Write
them by asking: "if a competent-but-lazy executor ran this, what would it get
wrong?" The red-team stage (stage 5) exists to expand this list.

Two deletions from the universal tail. "Do not present a claim's confidence
above its evidence" — V1 carries it with specifics ("never present a claim above
its grade"). "Do not fill a section with filler when evidence is thin" — A8
carries it and ties it to scoring, which this did not. Add either back when you
assemble without the block that replaced it; with that block they are duplicates,
and duplicates spend budget without adding enforcement. -->

### A8 — Output contract

> **Report structure — use this exact section order:**
> {{SECTION_ORDER}} (from stage 6)
>
> **Degradation order:** if depth becomes constrained, deliver sections
> {{PRIORITY_SECTIONS}} at full depth and explicitly stub the rest with one
> paragraph each stating what a full treatment would cover. Uniform
> shallowness across all sections is the worst outcome.
>
> A section honestly marked **"insufficient evidence — intentionally short"**
> is a first-class result and will be scored as compliant. A section padded
> with confident filler will be scored as a failure.
>
> End the report with a machine-parseable summary block:
> `key_findings` / `citations` / `confidence_gaps` / `next_queries`.

<!-- The final summary block matches the deep-research skill's output contract
so stage 8 verification consumes every report — local or external — through one
shape. -->

### A9 — Shipped rubric

> **This report will be scored against the following acceptance criteria by a
> separate verification pass.** Meeting them is the definition of done:
> {{RUBRIC — 5-12 checkable criteria}} (from stages 1 & 4)

<!-- Telling the executor the rubric is deliberate: it converts vague quality
prose into targets. Every rubric item must be checkable from the report text
plus its citations. Examples of good items: "every quantitative claim carries a
date and an evidence grade"; "each recommended approach names at least one
failed or negative example"; "every repo claim cites a file path or is marked
'not inspected'". -->

### A10 — Self-report

> Close with a short **self-report**: (a) your confidence in each major
> conclusion (high/medium/low with one-line reasons), (b) the gaps — what you
> could not access or verify, (c) **which instructions in this prompt you could
> not fully follow, and why.** The self-report is used to improve future
> prompts; candor here is rewarded, not penalized.

<!-- (c) is the postmortem's raw material. Executors will admit dropped
instructions when explicitly told it's safe to. -->

---

## V. Verification blocks (claims about the world)

### V1 — Evidence grading

> Grade every major claim; never present a claim above its grade. Prefer ranges
> over precise numbers unless independently corroborated.
>
> - **Strong** — {{STRONG_DEF — transaction/registry data, regulatory filings,
>   audited or longitudinal third-party corroboration}}
> - **Moderate** — {{MODERATE_DEF — repeated consistent evidence over time from
>   the same primary actor}}
> - **Weak** — {{WEAK_DEF — one-off screenshot, anonymous claim, uncorroborated
>   interview}}
> - **Marketing/noise** — claim attached to a sales funnel for the claim itself
>   (course, affiliate link, paid community, lead magnet). Treat as noise
>   unless independently verified.
>
> A grade says the claim *was* true, not that it *still* holds. Currency is the
> separate axis A6 ranks and V2 dates — a Strong finding about a closed window
> is Strong and irrelevant. Never let a grade substitute for an as-of date.

### V2 — Claim hygiene

> Every quantitative claim carries: **(1) a date** (when the number was true,
> not when you found it), **(2) its evidence grade**, and **(3) precise units —
> never conflate {{QUANTITY_CONFUSIONS — e.g., "gross revenue / net profit /
> owner income / MRR / valuation" or "throughput / latency / cost per unit"}}.**
> Where any denominator or base-rate data exists (marketplace stats, registry
> counts, platform disclosures), report it — adjudicating anecdotes without
> base rates is astrology.

### V3 — Negative evidence mandate

> Actively search for failures, churn, saturation, retractions, bans, policy
> changes, and practitioners saying "this no longer works." For every visible
> winner, ask how many attempted the same thing and failed silently — and go
> look where the failures live ({{FAILURE_VENUES}}). **A section containing no
> negative evidence is incomplete by definition.**

### V4 — Corroboration protocol

> "Independently corroborated" means: two or more sources that do not share an
> upstream origin (not two articles citing the same press release, not two
> accounts run by the same operator) and do not share a financial interest in
> the claim. When you assert corroboration, name both sources and state why you
> judge them independent. Watch for the recursive-grift tell: the claimant's
> real income is selling instruction in the method.

### V5 — Classification scheme

> Tag every significant example on these axes: {{CLASSIFICATION_AXES}} (from
> stage 1). Apply the scheme consistently — the point is to make unlike things
> comparable and to expose category errors ({{CATEGORY_ERROR_EXAMPLE — e.g.,
> "'AI-necessary' vs 'AI-cosmetic' exposes most fake AI businesses"}}).
>
> {{EDGE_TAG — include when the question asks what currently works: tag each
> example live / decaying / historical with the as-of evidence behind the tag,
> so a well-evidenced dead example cannot read as a live one}}

---

## D. Design blocks (build-oriented deliverables)

### D1 — Comparative system coverage

> Cover these systems/approaches comparatively: {{SYSTEMS_LIST}}. Note where
> designs converge (likely fundamentals) and where they diverge (likely open
> trade-offs). Include relevant systems published since this prompt was
> written.

### D2 — Stated-vs-inferred reconstruction

> When reconstructing any architecture or pipeline, mark every stage as
> **stated in sources** or **inferred**. For systems with unpublished
> internals, separate published facts from plausible-but-unconfirmed design
> patterns.

### D3 — Artifact-level evidence

> For implementation references (repos, libraries, configs), provide
> **artifact-level evidence, not README-level paraphrase**, using this table:
>
> | Concept | Repo/source | File/module | Function/class/config | Notes & divergence |
>
> If you cannot inspect at that level, mark rows "not inspected" rather than
> guessing. {{TERMINAL_ONLY — for terminal agents: clone and inspect the
> repos; cite paths and line ranges}}

<!-- For non-code build handoffs, adapt the columns to the destination artifact
rather than dropping D3. Example: Concept | Source | Skill/rule file | Section |
Fit/gap. The invariant is artifact-level traceability, not software vocabulary. -->

### D4 — Trade-offs & maturity levels

> For each recommended design, provide an explicit trade-off table
> ({{TRADEOFF_DIMENSIONS — e.g., capability, cost, complexity, guarantee
> strength}}) and classify every recommendation by maturity level, stating what
> is safe, unsafe, missing, and required to advance at each:
> {{MATURITY_LADDER — e.g., toy prototype → internal demo → research-grade →
> production over sensitive data}}.

### D5 — Build handoff

> This report feeds a downstream build session. Close the main body with a
> concrete, opinionated **handoff**: {{HANDOFF_CONTENTS — e.g., MVP scope,
> recommended stack, components to fork/borrow, first milestones, licensing,
> top risks to design around}}. Where you make a design judgment, state the
> reasoning so the build session can evaluate it rather than take it on faith.

---

## M. Merge blocks (multi-run plans only)

### M1 — Fixed structure for cross-run merge

> This report will be merged with reports from other runs/executors, including
> terminal-vs-web runs on the same question. Use the **exact
> section order in the output contract** with no added, removed, or reordered
> sections, so reports align section-for-section. Confident specifics that
> appear in only one model's report will be treated as hallucination candidates
> and checked against primary sources.

### M2 — Bibliography retention

> Provide a complete annotated bibliography (one-line credibility note per
> source; flag claims resting only on secondary sources). Bibliographies are
> deduped across runs — completeness matters more than curation here.

---

## Per-executor calibration

Apply after assembly, before shipping:

| Executor | Adjustments |
|---|---|
| **Claude Code / Codex (terminal)** | Full budget (≤60 instructions). Include D3 terminal clause (clone repos, cite paths). May reference local files and request intermediate artifacts on disk. Can be given the DAG plan directly and told to spawn subagents per node. |
| **Claude Research (web)** | ≤40 instructions. No repo cloning — D3 rows default to "not inspected" unless web-viewable. Strip DAG language; single-run framing. |
| **OpenAI / Gemini DR (web)** | ≤40 instructions. Known tendency to paraphrase repos at README level — if D3 included, state the "not inspected" rule twice (once in D3, once in the do-not list). Verify source-class access via scout probe in the same product first; X/Twitter usually unreachable, Reddit spotty. |

Record new executor quirks in `executor-profiles.md` as postmortems reveal them.
