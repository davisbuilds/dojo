# Stage 2 — Route

## 1. Block profile: Mixed

The question has two genuinely different payloads and neither can be dropped:

- **Verification-heavy** — sub-questions 1, 2, 4, 5, 6 make falsifiable claims about
  the world ("did MrBeast/Hormozi/Meservey actually do X, and does it generalize").
  → include **V1–V5** in full.
- **Design-heavy** — sub-question 7 and the decision-informed statement ("findings get
  encoded into the `viral` skill kit... map validated tactics to specific skills/rules")
  is a build handoff, not just a finding. → include **D1–D5** in full.

I considered dropping D3 (artifact-level evidence) as software-shaped and not
obviously fitting a marketing-research report, but the `viral` repo is a real,
public, inspectable artifact (`github.com/davisbuilds/viral`) and rubric item 7
requires the handoff to name specific existing skill/rule files, not describe them
generically. D3's table shape — Concept | Repo/source | File/module |
Function/class/config | Notes & divergence — maps directly onto: validated tactic |
`viral` repo | skill or rule file path | specific SKILL.md section/instruction |
fit vs. gap. Adapted this way, D3 is the mechanism that keeps the build handoff (D5)
honest instead of hand-wavy — dropping it would have let the report recommend "update
hook-engine" without ever citing what hook-engine currently says. Kept.

D4 (trade-offs & maturity) is justified by the brief's own stated cost-of-being-wrong:
"encoding survivorship theater into reusable skills poisons every future draft at
scale." A maturity ladder per proposed change (validated-enough-to-encode-now vs.
needs-more-evidence vs. do-not-encode) is the concrete mechanism against that risk.
Kept.

**Result: all of A1–A10, V1–V5, D1–D5 selected — 20 blocks before per-executor
trimming.** This is a genuinely heavy assembly; see friction log.

## 2. Execution surface: both (given at stage 0)

Terminal agent and one web DR product, per the stage-0 routing input. This is not a
redundant re-run of the same question — it is functionally a **two-model merge**:
same core question, same rubric, two different reach profiles (terminal can clone/
inspect the `viral` repo directly and hit local files; web DR sweeps broader public
web surface but cannot touch the filesystem). Stage 8's cross-run diff becomes
directly usable here: any confident specific naming a MrBeast/Hormozi/Meservey tactic
that shows up in only one report is a hallucination candidate to check before the
build handoff trusts it.

**Decision: treat this as a merge run.** Include **M1 (fixed structure) and M2
(bibliography retention)** in both prompts so the two reports align section-for-section
at stage 8, even though "multi-model merge" in the skill's usual sense means multiple
LLM vendors on the same run shape rather than terminal-vs-web. The mechanism (fixed
section order, cross-diff on confident specifics) applies identically here, so I'm
using it as designed rather than treating "merge blocks" as vendor-count-gated.

## 3. Run shape: single run per executor, not a DAG — with a documented reservation

Estimated section count at real depth: framing, three practitioner case studies (each
carrying tactic inventory + evidence grading + negative evidence + classification),
priors evaluation (4 subsections), confounds analysis, platform-transfer analysis,
temporal-change analysis, classification synthesis, build handoff, summary block —
this lands at **10–11 sections**, right at the skeleton's stated DAG-split threshold
("or when a single run would exceed ~10 report sections at real depth").

The three practitioners plausibly warrant three DAG nodes (different source classes:
MrBeast leans YouTube/Reddit/leaked-doc forums, Hormozi leans his own
YouTube/podcast/X, Meservey leans Substack/X/interview transcripts) plus a synthesis
node. **I did not split into a DAG** because the task explicitly scopes stage 4 to
producing exactly two prompt files (`04-prompt-terminal.md`, `04-prompt-web.md`), which
reads as a single-run-per-executor mandate, and because splitting would 4x the prompt
count (4 nodes × 2 executors) beyond what this pressure test asked to produce. Instead
I lean harder on the degradation order (A8) — full depth on the priors evaluation and
confounds analysis (the sections that actually adjudicate the brief's disconfirmation
goal), stubbed depth allowed on exhaustive per-platform tactic cataloging.

**Reservation for stage 9:** if verification shows uniform shallowness across the three
practitioner case studies (the failure mode the skeleton warns is worst), that's the
signal to re-run as a DAG next time, not to add more instructions to a single prompt.

## What the skeleton made easy vs. awkward

- **Easy:** the V-block set mapped almost one-to-one onto this topic without
  modification — V3 (negative evidence) and V4 (corroboration protocol) practically
  write the do-not list themselves once you know Meservey and Hormozi have financial
  interests in their own theses.
- **Awkward:** nothing in the skeleton flags when a "mixed" profile plus a merge run
  produces 20 candidate blocks against a 40-instruction web budget. The guidance says
  "trim per-block slots, not whole blocks," which is right in principle but gives no
  guidance on which slots survive trimming when the arithmetic doesn't work — see
  friction log.
- **Awkward:** the merge-block section (M1/M2) is framed entirely around
  "multiple models" in the prose, but the actual trigger condition (reports will be
  diffed section-for-section) applies just as well to two different executor classes
  on the same question. Had to reinterpret rather than follow literally.
