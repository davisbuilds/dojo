# Executor profiles — per-executor quirks and routing facts

Observed behavior of specific executors, appended at stage 9. Read at stages
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

## Gemini Deep Research (web) — as of 2026-07-12 (first run; entries preliminary until more runs)

- Reaches and cites Reddit directly — inverse of the terminal harness. Do not
  copy terminal accessibility notes into Gemini prompts as ground truth.
- Leaks SEO-adjacent and AI-generated sources (Grokipedia, personality-analysis
  and motivation blogs) into the bibliography despite a do-not list and source
  priorities. Consider an explicit source blacklist line for this executor.
- Used the always-present frame-check substantively (rejected the prompt's
  framing with argument) — honors structural sections, not just content asks.
- Report formatting: appends its own numbered "Works cited" list and can embed
  base64 image data at the end of the export; strip before downstream
  processing. Citation markers are superscript numbers that survive export as
  bare digits mid-sentence.
