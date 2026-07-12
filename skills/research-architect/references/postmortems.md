# Postmortems — skeleton and process lessons

Dated, durable lessons about the skeleton and pipeline, appended at stage 9 of
real runs. Read during stages 2–5 of new runs. Keep entries short; link the
run's friction log for detail.

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
