# Executor profiles — per-executor quirks and routing facts

Observed behavior of specific executors, appended at stage 10. Read at stages
2–4 to calibrate prompts and at stage 3 to seed scout expectations. Date every
entry — access and behavior drift.

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
