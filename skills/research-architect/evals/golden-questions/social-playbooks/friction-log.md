# Friction Log — research-architect pressure test

Written live during stages 1–4 of a real drafting run (topic: social-media guru
tactics vs. survivorship theater, feeding the `viral` skill kit). Blunt by design —
this feeds the skill's postmortem, not a polished review.

## Stage 1 — Question engineering

- The stage description is generous on "classification scheme if unlike things must be
  compared" but the skeleton's V5 block and the stage-1 instructions don't cross-
  reference each other explicitly — I had to infer that the stage-1 classification
  scheme *is* what fills V5's `{{CLASSIFICATION_AXES}}` slot later. Worked fine once
  inferred, but a one-line pointer ("this becomes V5" / "this becomes D3's table
  columns") in either doc would save a re-read.
- No friction on the rubric itself — the "checkable from report text alone" test is a
  genuinely sharp filter and caught one item I almost wrote ("tactics are properly
  contextualized," dropped for being unfalsifiable) before it made the draft.

## Stage 2 — Route

- **Real gap:** the router's three decisions (block profile / execution surface / run
  shape) are presented as independent, but they interact in ways the skill doesn't
  flag. Choosing "mixed" (V + D) profile plus "both executors" (which I read as a de
  facto merge run, triggering M-blocks) produces a 20-block assembly before any
  content is written. The skill never states what a "large" assembly looks like or
  when to reconsider the profile choice — I had to reason it out from first principles
  (grep the skeleton's own baseline instruction density) rather than get guidance from
  the process.
- **Ambiguous:** M-blocks are written entirely in "multiple models" language
  ("merged with reports from other models"). My run has two *executor classes*
  (terminal vs. web), not two models in the usual sense. The mechanism (fixed section
  order + cross-run diff on confident specifics) clearly still applies, and stage 8's
  own text ("Cross-run diff (multi-model only)") uses "multi-model" to mean exactly
  this. But nothing in the skeleton or SKILL.md says explicitly "terminal-vs-web on the
  same question counts as multi-model for M-block purposes" — I made a judgment call
  and documented it, but a fresh drafter without that instinct could easily skip
  M-blocks here and lose the cross-run diff capability stage 8 wants to use.
- **Real tension, not fully resolved:** the DAG-split threshold ("~10 report sections
  at real depth") and this task's explicit instruction to produce exactly two prompt
  files pull in opposite directions once the section count is estimated at 10–12. The
  skill offers no guidance on how to weigh an external scoping constraint (here: the
  orchestrator's own instructions) against its own DAG heuristic. I documented the
  tension and made a call, but this is exactly the kind of thing that should be an
  explicit stage-2 decision point ("if the run shape is constrained externally, note
  the DAG reservation and lean on degradation order instead") rather than something I
  had to invent language for.

## Stage 3 — Scout

- **The skeleton assumes scout results are mostly binary (reachable/not)** but a
  meaningful fraction of what I found was neither — "reachable but the primary source
  itself is unverifiable" (MrBeast leak), "reachable but zero-evidence" (Meservey's
  manifesto), "reachable once then rate-limited" (podcast transcripts). The
  `{{ACCESSIBILITY_RESULTS}}` / `{{FALLBACKS}}` slots handle reachable-vs-not cleanly
  but have no natural home for "reachable-but-worthless-as-evidence," which is a
  distinct and important finding here. I ended up folding it into the do-not list
  instead (correct destination, but the stage-3 template doesn't point you there).
- **A real, valuable catch this pass forced:** the decision brief itself named the
  wrong source ("Rough Drafts" instead of "Flack"). Nothing in the skill flags "seed
  sources named in the decision brief are themselves hypotheses to verify at scout
  time," even though A4 says exactly this about *background notes* in the assembled
  prompt. The brief is upstream of the prompt and gets the same treatment implicitly,
  but stage 3's own instructions don't say "check the brief's named sources actually
  exist" as a distinct checklist item — I did it because it's an obvious thing to test
  once you start fetching, not because the process told me to.
- Reddit and X/Twitter being unreachable matched the task's own prediction, so no
  friction there — the brief primed me correctly.

## Stage 4 — Draft & lint

- **Budget anxiety was misplaced, and the skill doesn't warn you either way.** Going
  into assembly with 20 non-core blocks selected (all of V1–V5, D1–D5, M1–M2), I
  expected to fight the 40-instruction web budget hard. In practice the skeleton's
  fixed block text carries only 15 imperative markers total across all 22 blocks
  combined — the budget pressure, when it exists, comes almost entirely from how a
  drafter phrases slot fills, not from block count. Both prompts landed at 16/60 and
  17/40 on the first attempt with zero trimming. This is good news about the
  skeleton's design (blocks are lean by default) but the SKILL.md's own framing
  ("Over budget → rank instructions by 'what breaks if dropped' and cut") primed me to
  expect a fight that never came. A short note ("most assemblies land well under
  budget; the ceiling matters mainly for drafters who over-phrase slots with must/
  never") would calibrate expectations better.
- **Lint script false-negative risk, not observed but worth flagging:** the
  `instruction_budget` regex counts literal `must|never|always|do not|don't`. A
  drafter could trivially write "should never" style softened imperatives or bulleted
  requirement lists with no marker words at all and dodge the count while still adding
  real cognitive load for the executor. Didn't happen here (I wasn't trying to game
  it), but the counting method is a proxy for "instruction density," not the thing
  itself, and the skill doesn't say so anywhere near the lint step.
- **No false pass/fail observed.** Both lints ran clean on the first pass; the
  required-block regexes (do-not list, degradation order, rubric, self-report, summary
  tokens) all correctly found their targets even though I wrote the section headers
  slightly differently from the skeleton's own headers (e.g. "Output contract" vs. the
  skeleton's own heading text) — the regexes are appropriately loose on wording and
  strict on substance, which is the right trade-off.
- **D3 in a non-software research topic worked, but needed real adaptation** — the
  block's default table (Concept | Repo/source | File/module | Function/class/config)
  is clearly software-shaped. It mapped cleanly onto "validated tactic | viral repo |
  skill/rule file | SKILL.md section | fit/gap" once I made that translation myself,
  but the skeleton gives zero guidance that D3 is reusable this way for a
  build-handoff-shaped (not literally code-shaped) research question. This is
  probably D3's single best non-obvious use case and it's undocumented.
- **The two manual lint checks have no artifact home.** SKILL.md lists them as
  stage-4 checklist items but never says where the result should be recorded — I had
  to invent `04-lint-results.md` as a destination. A named artifact (or an instruction
  to append to the route file) would remove that ambiguity.

## Net assessment

The skeleton held up well under a genuinely heavy, high-stakes, mixed-profile,
two-executor assembly — no block felt like it didn't earn its place, and the lint
script did its deterministic job with no false positives/negatives observed. The real
friction was all at the seams between stages (2→4 M-block interpretation, 3→4 "low-
evidence-but-reachable" handling, the missing artifact home for manual checks) rather
than inside any single block's content.

## Stage 5–6 — Red-team fold-in and run plan (completed by the orchestrator)

Provenance note: the executor subagent hit a session usage limit before starting the
fold-in; the orchestrating session completed stages 5→6 itself. The interruption cost
zero work — every completed stage was already checkpointed to disk, which is the
strongest live validation yet of the artifact-per-stage design.

- **Executor Write calls left a literal `</content>` trailer line in every artifact
  it created — including both shippable prompts — and `lint_prompt.py` has no check
  for it.** Slots and HTML comments are caught; stray harness/tool artifacts are not.
  Candidate lint addition: flag lines matching common tool-wrapper debris
  (`</content>`, XML-ish trailers) in assembled prompts.
- **The redteam-checklist processing rules worked as written.** The deletion-vs-keep
  call was clear exactly once it mattered: red-team proposed deleting self-report
  item (c), which is the postmortem's only input — the "unless a deletion would
  remove the only enforcement of a stage-0/1 priority" clause fit precisely and the
  rejection was easy to justify. The other four deletions applied cleanly.
- **The red-team's structural findings forced rubric changes, not prose changes** —
  the depth-vs-breadth conflict could only be resolved by adding an enforceable
  rubric item (per-tactic evidence floor + short-form register) and deleting the
  aspirational prose. Supports the skill's core thesis: quality lives in checkable
  criteria, not disposition language.
- **Marker-count blindness confirmed from the other direction:** the fold-in deleted
  5 instruction-bearing passages and added ~6 new requirements, and the lint counts
  did not move (16/60, 17/40 before and after). The budget counter is insensitive to
  real instruction-density changes in both directions.
- **Minor:** the red-team's "no additions except do-nots" mandate and the drafter's
  duty to make requirements checkable are in mild tension — several fixes (frame-check
  always-present, recency check, rubric item 10) are additions in form even though
  they replace deleted unenforceable text. The checklist could say explicitly that
  rewrite-to-checkable may add text where it deletes intent-duplicating prose.
