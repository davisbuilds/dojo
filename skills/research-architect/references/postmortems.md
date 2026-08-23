# Postmortems — skeleton and process lessons

Dated, durable lessons about the skeleton and pipeline, appended at stage 10 of
real runs. Read during stages 2–5 of new runs. Keep entries short; link the
run's friction log for detail.

## Index

- [2026-08-22 — coding-harnesses](#2026-08-22--coding-harnesses-3-run-web-dr-merge-opus-5-gpt-56-sol-gemini-flash-37)
- [2026-07-23 — predmarket-alpha](#2026-07-23--predmarket-alpha-mixed-profile-terminal--web-dr-verification-mid-run)
- [2026-07-12 — social-playbooks](#2026-07-12--social-playbooks-first-live-run-mixed-profile-terminal--gemini-dr)

## 2026-07-12 — social-playbooks (first live run; mixed profile, terminal + Gemini DR)

- **Frame-check must be unconditional.** The original A5/A8 wording ("only if
  triggered") makes "didn't look" indistinguishable from "no challenge found."
  The rewrite — section 1 always present, stating either the challenge or
  "frame verified" plus what was checked — was used substantively on first
  contact: the web executor rejected the three-parallel-theses framing
  outright, and the terminal executor independently flagged the same asymmetry.
  Convergent frame-challenge across executors is high-value signal; design for
  it, don't merely permit it.
- **The per-tactic evidence floor discriminated on first use** (rubric item:
  ≥2 independent sources with lineage, ≥1 negative data point, dated as-of
  check; below-floor tactics demoted to a short-form register). It caught a
  full profile shipping on one independent source the same day it was added.
  First confirmed candidate for a future rubric-library.
- **Red-team deletion mandate works on lint-clean prompts.** Five legitimate
  deletions found in prompts that had passed every deterministic check. The
  deletion-vs-keep rule resolved its first hard case cleanly (self-report
  item (c): unverifiable, but kept as the postmortem loop's only input).
  Structural conflicts (depth-vs-breadth) could only be fixed in the rubric,
  not the prose — quality lives in checkable criteria.
- **The drafter's own seed-source annotations need A4's stated-vs-inferred
  discipline.** The prompt asserted a source "flags authenticity as
  unconfirmed" when he merely never confirms it; the executor caught it and
  verification confirmed the prompt was wrong. Scout notes are claims too.
- **Scout results are tri-state, not binary**: reachable / unreachable /
  reachable-but-evidentially-worthless. The third state was load-bearing
  (leaked-guide provenance, zero-data manifesto) and its correct destination
  is the do-not list, which the stage-3 instructions should say.
- **Checkpoint-per-stage earned its cost**: the executor subagent died
  mid-pipeline (session limit) and the interruption cost zero work — the
  orchestrator resumed from artifacts alone.
- **Instruction-budget counts are a weak proxy.** A maximal 22-block assembly
  landed at ~40% of the web budget; a fold-in that deleted 5 passages and
  added ~6 requirements moved the count by 0–1. Do not treat the lint number
  as instruction density; the budget matters mainly for slot phrasing.
- **Multi-run plans need synthesis as a formal step.** The pipeline verifies
  and diffs reports but had no named stage/artifact for merging them into the
  single build-ready document the decision consumer actually wants; this run
  added it ad hoc after stage 8.
- **Executor-independent verification is the load-bearing stage — confirmed.**
  A polished, authoritative-reading web DR report failed verification at 43%
  fully-supported citations with two refuted headline numbers; the terminal
  report on the same question verified at ~93%. Nothing in the web report's
  surface distinguished it. The cross-run diff adjudicated all five
  spot-checked one-report-only claims correctly (three terminal claims
  confirmed, two web claims refuted).
- **Convergent verdicts can mask divergent substance.** Both reports reached
  "small-and-boring durable core," but rated the identical tactic differently
  underneath (Strong/validated vs. Moderate/not-yet-validated). Diff the
  classification tables and evidence grades, not just the verdicts.
- **Seed lists anchor; say they are not a ceiling.** When priority platforms
  (X, Reddit) are unreachable, the fallback framing ("these named sources are
  the floor") reads as a boundary and narrows the search universe. A6 should
  explicitly license expansion into any reachable high-grade source class
  (court/registry records, earnings data, platform transparency reports,
  academic work, practitioner interviews) beyond the named seeds.

## 2026-07-23 — predmarket-alpha (mixed profile, terminal + web DR; verification mid-run)

- **Fresh subagents for stages 3/5/8 are the design, and the orchestrator must
  actually spawn them.** This run ran scout, red-team, and the first Stage-8
  pass inline (host harness defaulted to "don't spawn unless asked"), which
  silently forfeits the independence the red-team and rubric passes depend on —
  a self-red-team is structurally weaker than a blind one. In terminal harnesses
  (Claude Code, Codex) subagents are always available; the workflow should
  *encourage* fresh independent subagents for 3/5/8 rather than read as if they
  might be unavailable. Caveat worth stating in-skill: web DR executors usually
  cannot spawn subagents, so an external-only run loses all in-run independence
  and must lean entirely on the terminal-side Stage 8.
- **Never seed a paraphrased statistic; it is an attractor for fabrication.**
  A5/A6 carried a scout finding as "at least one large-N study reportedly finds
  no general longshot bias." The executor "confirmed" it by inventing a
  precise-but-wrong matching citation (claimed 1.2B trades / "finds bias"; the
  actual paper, arXiv 2602.19520, is 292M trades about *underconfidence /
  compression toward 50%*). Sharpen A4/A6: seed either a fully-identified source
  (name + arXiv/SSRN id, framed as a verify-this target) or no number at all —
  a floating "a study found X" invites a hallucinated match.
- **Executor-independent verification load-bearing — reconfirmed.** A single
  spot-check of the terminal report's two weakest-sourced (SSRN-403) claims
  confirmed one against the primary source (arXiv 2605.00864: 173 games, 7
  executable single-market episodes) and caught the miscite above. Consistent
  with the 2026-07-12 finding.
- **Verify each node as it lands, not batched.** Running the Stage-8 structural
  spot-check on the first-returning report while the second run was still going
  paid off immediately and pre-loaded the cross-run diff. Stage 8's framing as a
  post-all-runs batch step could note this.
- **Source-priority ranking optimizes reliability, not edge-relevance — a real
  bias for "find what's working" questions.** The A6 ordering (peer-reviewed
  papers co-top) and V1 evidence grades both rank *verifiability*. For an
  alpha-hunting question that structurally over-weights academic efficiency
  findings — high-reliability but lagging, aggregate, and selection-biased
  (efficiency is publishable; a live edge is not) — tilting the verdict toward
  "no edge / arbitraged away." On-chain ground truth and inspected working code
  were correctly co-top here, which saved it. See BACKLOG: A6/V-block needs an
  explicit edge-relevance × recency axis distinct from reliability.

## 2026-08-22 — coding-harnesses (3-run web DR merge: Opus 5, GPT-5.6-sol, Gemini Flash 3.7)

- **Cross-domain citation misapplication is distinct from fabrication.** One
  report used BankerVerifierBench's real RewardKit/Gandalf results as coding-
  harness economics even though the benchmark evaluates agent-as-judge graders
  on investment-banking deliverables; it also changed the headline magnitude.
  Existence and lineage checks both passed. Detection required asking what the
  source measures and on what population. Acted on in A4 and Stage 8.
- **A named-but-unopenable artifact attracts fabricated detail.** Two reports
  admitted they could not ingest the same benchmark ZIP, then confidently gave
  contradictory file counts, row counts, and update dates. Extend the unreachable-
  source rule to artifact contents and metadata. Acted on in A6.
- **The citation worksheet itself needed a positive-control check.** On the raw
  exports, it found zero claim/citation pairs in the Claude and OpenAI reports;
  Gemini's numbered references required bibliography resolution. An empty sample
  from an opaque export is not evidence of clean citations. Acted on in
  `score_report.py` with direct/resolvable/opaque/absent coverage classification.
- **M1 caught the highest-severity claim on first pass.** The cross-domain
  benchmark appeared in exactly one report. Treating one-report confident
  specifics as hallucination candidates is now 3-for-3 as the highest-yield
  verification step.
- **The third run's marginal value was adjudicative, not additive.** Runs two and
  three added little coverage but resolved which earlier claim to believe. Keep
  this as a budgeting heuristic for verification-heavy work, not a mandatory run
  count.
- **Watch for incumbent-flattering selectivity when executor and subject share a
  vendor.** The Claude executor named only two of four compaction-probe retainers,
  making its own tool look more unique. Recount exhaustive primary-source lists
  during Stage 8 when vendor alignment can influence selection.
- **Self-reported confidence was anti-correlated with accuracy in the weakest
  run.** Gemini rated its most-wrong section High and omitted A10(c). Confidence
  is not verification; missing A10(c) is itself a structural failure.
- **Section-contract drift degraded merge alignment in two of three runs.** One
  report added sections; another omitted required top-level sections, and Gemini's
  summary was not valid in the requested interchange shape. For merge runs, put
  exact structure and summary/self-report presence into A9, not only A8/M1.
- **Rubric discrimination:** benchmark metadata (model/version/date/attempt
  policy or unusable) caught the weakest run. The status-tag item was nearly
  unfailable because "no recent source found" carried no search-evidence cost;
  the Stage-5 red-team predicted this. Costless escape hatches are dead weight.
