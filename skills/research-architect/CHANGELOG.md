## 2.2.2 - 2026-08-14

- Anchor runnable script commands to <skill-dir> so they resolve outside a dojo checkout

## 2.2.1 - 2026-07-31

- Trim mechanism from the description (777 -> 622 chars) while restoring the full trigger list and the external deep-research-product use case, both of which an earlier pass in this session dropped by accident. Routing is unchanged from 2.2.0.

## 2.2.0 - 2026-07-24

- Add scripts/score_report.py: worksheet extracts claims and citations from a report and samples claim/citation pairs to verify (weighted toward quantitative and source-attribution claims); score computes the citation hit rate from filled-in verdicts, excluding unreachable URLs from the denominator. One check per pair, so a claim's refuting citation is never masked by a supporting one. Never fetches -- judging page support stays with the verifying agent.

## 2.1.1 - 2026-07-24

- Lint warns on statistics seeded into the background with no retrievable source (name + arXiv/DOI/SSRN/URL), scoped to the seed/background region so numbers the report is asked to produce are untouched.

## 2.1.0 - 2026-07-24

Acts on the 2026-07-23 predmarket-alpha postmortem. Net-zero on shipped
instruction count: three additions offset by three deletions.

- **A6 ranks sources on two axes** — reliability (is the claim true) and
  edge-relevance × recency (does it still hold) — replacing the single
  verifiability ordering that biased "what's working now" questions toward
  "already arbitraged away". Adds `LAG_WARNING`; V5 gains `EDGE_TAG`; V1 states
  that a grade is about the past and never substitutes for an as-of date.
- **Seed sources must carry a stable identifier.** A4 now instructs the executor
  to report an unsourced number as unsourced rather than hunting a source that
  matches it — a floating statistic is an attractor for fabricated corroboration.
- **Stages 3, 5, and 8 default to fresh subagents**, explicitly overriding host
  dispositions against delegation; running them inline is a recorded degradation.
  Notes that web DR executors cannot spawn subagents, so external-only runs have
  no in-run independence.
- **Stage 8 verifies each node as it lands** instead of batching after all runs,
  and weights the citation sample toward quantitative and source-attribution
  claims — the dominant failure mode across every executor profiled so far.
- Deletions: A6's bibliography-padding rule (contradicted M2 on multi-run
  assemblies), A7's confidence-above-evidence clause (V1 carries it), and A7's
  thin-section filler clause (A8 carries it, tied to scoring). D2 loses a
  redundant "do not over-reconstruct" tail.

## 2.0.0 - 2026-07-12

- Promote verified multi-run synthesis to formal stage 9 and renumber
  postmortem/cleanup to stage 10.
- Harden the first live-run seams: multi-executor merge routing, tri-state
  scouting, exemplar-vs-exhaustive scope, stated-vs-inferred drafter notes,
  constrained run shapes, named lint results, and non-code D3 adaptation.
- Make frame checking unconditional and clarify that seed sources are a floor,
  not a ceiling.
- Expand prompt linting to catch trailing harness debris and bullet-initial
  imperative requirements.
