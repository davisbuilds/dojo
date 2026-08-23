# Executor profiles — per-executor quirks and routing facts

Observed behavior of specific executors, appended at stage 10. Read at stages
2–4 to calibrate prompts and at stage 3 to seed scout expectations. Date every
entry — access and behavior drift.

## Index

- [Claude Code terminal harness](#claude-code-terminal-harness-webfetchwebsearch--as-of-2026-07-12)
- [Sonnet terminal executor](#sonnet-subagent-as-pipelineresearch-executor--as-of-2026-07-12)
- [Gemini Deep Research](#gemini-deep-research-web--as-of-2026-07-12-one-full-run--verification)
- [Claude Opus 5 web DR](#claude-opus-5-as-external-web-dr-executor--as-of-2026-08-22)
- [GPT-5.6-sol web DR](#gpt-56-sol-as-external-web-dr-executor--as-of-2026-08-22)
- [Gemini Flash 3.7 web DR](#gemini-flash-37-as-external-web-dr-executor--as-of-2026-08-22)

## Claude Code terminal harness (WebFetch/WebSearch) — as of 2026-07-12

- X/Twitter: 402 on direct fetch. Reddit: hard-blocked on both `www` and
  `old`, and search does not surface subreddit content as a substitute.
- YouTube: video pages return nav chrome only; third-party transcript sites
  403. Retention/transcript-level claims must route through secondary press.
- arXiv: `/abs/` pages extract fine; `/pdf/` text extraction fails.
- Podcast transcript sites: rate-limited but not hard-blocked — retry with
  pacing.

## Sonnet subagent as pipeline/research executor — as of 2026-07-12

- Write calls can leave a literal `</content>` trailer line at the end of
  created files — including shippable prompt artifacts. Instruct explicitly
  ("file must end with X, no wrapper tags") and lint for it.
- Followed a fixed 12-section output contract and degradation order
  faithfully; self-report candor was high (it surfaced a factual error in the
  commissioning prompt itself). Instruction-following on the do-not list held
  under a 300-line report.

### Sonnet 5 `general-purpose` as terminal DR executor — as of 2026-07-23

- **Strong on infrastructure/artifact tasks.** Cloned 5 repos, ran 6 read-only
  API probes, wrote the report to the exact requested path, honored the
  read-only/no-trades safety constraint, and produced a 759-line report on the
  full section contract. Followed clone-and-cite-paths (D3 terminal clause) as
  intended — the whole reason to route repo-inspection to a terminal executor.
- **Mutates cited numbers and mischaracterizes sources — verify every citation.**
  Reported a paper as "1.2B trades, finds longshot bias"; the actual paper
  (arXiv 2602.19520) is 292M trades about underconfidence/compression. Same
  numeric-drift failure class as Gemini DR (2026-07-12). Do not ship its
  quantitative or source-attribution claims without a Stage-8 fetch.
- **Candid self-report includes what it cloned/probed vs. only read about** when
  the prompt asks for it (self-report item added in the terminal prompt) — makes
  the postmortem's "actually verified vs. paraphrased" split cheap.

## Gemini Deep Research (web) — as of 2026-07-12 (one full run + verification)

- Reaches and cites Reddit directly — inverse of the terminal harness. Do not
  copy terminal accessibility notes into Gemini prompts as ground truth.
- **Numeric claims require independent verification before use** — first run
  shipped two refuted load-bearing numbers: a source's "$40k over six months"
  became "$40k/month" (~6x inflation, feeding a headline verdict), and a
  per-impression ad-rate stat with no trace in the public record. Verification
  (stage 8) is not optional for this executor.
- Leaks SEO-adjacent and AI-generated sources (Grokipedia, personality-analysis
  and motivation blogs) into the bibliography despite a do-not list and source
  priorities, and cites them unhedged. Add an explicit source blacklist line.
- Corroboration protocol followed procedurally, not substantively: pairs
  "independent" sources that share an upstream origin (e.g., a derivative blog
  cited as independent of the post it derives from). Spell out the lineage
  check with an example.
- Artifact-level (D3) evidence: raw.githubusercontent fetches genuinely fail
  (probe-confirmed access failure, not laziness) — every table row came back
  "not inspected." Either drop D3 for this executor or expect an empty table.
- Honors structural section contracts (used the always-present frame-check
  substantively, rejecting the framing with argument) but not intra-section
  analytical structures (skipped a required two-bucket temporal split).
- Report formatting: appends its own numbered "Works cited" list and can embed
  base64 image data at the end of the export; strip before downstream
  processing. Citation markers are superscript numbers that survive export as
  bare digits mid-sentence.

## Claude Opus 5 as external web DR executor — as of 2026-08-22

- **Best primary sourcing and A10 candor of the three-run comparison.** It
  admitted search-budget exhaustion and an unopenable dataset rather than
  claiming full compliance.
- **Strongest on operational specifics:** quota-exhaustion behavior, dated
  incident history, and vendor-conceded negatives.
- **Observed failures:** artifact-metadata date drift; selective enumeration
  favoring its own vendor; and Recommendations/Caveats appended beyond a fixed
  section contract. Restate structural compliance in the rubric for merge runs.
- Export carried no retrievable claim-to-URL mapping, so the citation worksheet
  must classify it as opaque and require manual mapping or a better export.

## GPT-5.6-sol as external web DR executor — as of 2026-08-22

- **Most methodologically skeptical of the three.** It downgraded the strongest
  benchmark with six stated reasons, caught a model mismatch in the compaction
  probe, and refused unsupported comparative rankings.
- Parses an attached brief into an extracted-requirements table, providing a
  useful compliance signal. Numeric confidence was calibrated, and it volunteered
  the desk-research-only limitation.
- **Observed failures:** artifact-metadata drift, verbosity, missing top-level
  sections, and opaque `citeturn...` markers after export. Obtain a link-preserving
  export or map citations manually before scoring.

## Gemini Flash 3.7 as external web DR executor — as of 2026-08-22

- **Highest surface polish, lowest reliability in this comparison.** All three
  refuted claims were its: an inverted compaction result, doubled task count, and
  a real benchmark imported from an unrelated domain with the magnitude changed.
- Confidence was anti-correlated with accuracy: it rated the most-wrong section
  High and omitted A10(c).
- Structural/export failures extended the 2026-07-12 profile: invalid requested
  summary shape, appended Works cited list, ambiguous bare-digit markers, and a
  broken base64 image reference.
- **Routing:** do not use this executor alone for verification-heavy questions.
  It can serve as an adjudicative run only when Stage 8 independently verifies
  every claim used downstream.
