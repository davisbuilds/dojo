# Stage 3 — Scout Pass

Real scout pass executed via this terminal session's own `WebFetch`/`WebSearch` tools
(the same reach a spawned recon subagent would have). 16 `WebFetch` calls + 7
`WebSearch` calls. Results below are what actually happened, not assumed.

## Source-class reachability grid

| Source class | Reachable? | Citable as? | Grade | Notes |
|---|---|---|---|---|
| MrBeast leaked production guide (secondary coverage) | Yes — Tubefilter, Simon Willison's blog | Yes, as *reported quotes* | **Moderate** | Cybernews (same story) returned 403. Every source that discusses the leak — including Simon Willison, a credible independent commentator — explicitly declines to confirm authenticity ("appears to have written," sourced only from a third-party tweet). No source examined independently verifies provenance. |
| MrBeast leaked guide (primary PDF / original tweet) | **No** | No | — | Original source is a tweet (`x.com/simonw/...`) → blocked (402). The PDF itself was never directly fetched by any of the three attempts. Treat the whole class as secondary-sourced only. |
| Hormozi's own published content (owned site) | Partially | — | — | `acquisition.com/blog` guess was wrong (404). Did not locate a working owned-content URL in this pass — needs a proper seed URL (YouTube channel, `alexhormozi.com`) before the real run, not another guess. |
| Hormozi content strategy (secondary/analytics coverage) | Yes | Yes | **Moderate** | Multiple independent write-ups (OutlierKit, aimaker Substack, Copyblogger, BAM) converge on the same volume/repurposing numbers (5,300 videos, 91% Shorts views, 30+ pieces per pillar) — real corroboration, though all are secondary and none audit the underlying numbers themselves. |
| Hormozi criticism / negative evidence | Yes | Yes | **Weak–Moderate** | Found real negative evidence: net worth unverified/self-reported, "guru criticizing gurus" tension, Skool Games compared to MLM-like referral structure, advice inapplicable to pre-revenue creators. Useful — do not skip this query in the real run. |
| Meservey's Substack | Yes, but **brief has the wrong name** | Yes | **Weak (as evidence)** | It's called **Flack** (formerly *Res Ipsa*), not "Rough Drafts" — no publication by that name exists in results. Landing page and the "Go Direct: The Manifesto" post are both directly fetchable. The manifesto itself is confirmed **purely argumentative — zero case studies or data**, exactly the financial-interest risk flagged in the do-not list. |
| Meservey public interviews | Yes (via secondary write-ups) | Yes | **Moderate** | Persuasion/Yascha Mounk interview, Lenny's Newsletter interview both indexed and summarized by search. Not yet fetched directly — queue for real run. |
| YouTube (video pages) | **No transcript access** | No | — | Fetching a YouTube watch page returns only nav/footer chrome, not transcript or description. This is a hard reachability wall for this terminal harness specifically. |
| YouTube (third-party transcript sites) | **No** | No | — | `youtubetotranscript.com` returned 403 on direct fetch (bot-blocked). Do not assume transcript access; rely on secondary press that paraphrases video content instead. |
| X/Twitter | **No** | No | — | Confirmed unreachable: `x.com` post returned HTTP 402 Payment Required. Matches the brief's expectation. |
| Reddit | **No, worse than "spotty"** | No | — | Both `www.reddit.com` and `old.reddit.com` are hard-blocked by this harness ("unable to fetch"). `WebSearch` for subreddit-specific threads returned **zero results** — Reddit discussion-level content is not indexed well enough to substitute. Effectively a dead source class for the terminal executor. |
| Podcast transcripts | Inconclusive | — | — | One attempt (podcosmos.com) hit HTTP 429 (rate-limited), not a hard block — worth a retry with pacing in the real run, but don't budget on it. |
| Marketing-analytics publications (Social Media Examiner) | Yes | Yes, with care | **Weak–Moderate** | Mix of practitioner analysis and sponsored/vendor content on the same page (e.g., an "AI Business Society membership" pitch alongside articles). Usable but flag per-article, not as a blanket-trusted venue. |
| Marketing-analytics publications (Tubefilter) | Yes | Yes | **Moderate** | Industry trade press; used consistently across multiple queries as the most reliable secondary source on both MrBeast retention mechanics and the leaked guide. Best available secondary venue for YouTube-creator-economy claims. |
| Academic work on platform algorithms | Yes (search), **No (PDF text)** | Search results yes; PDF no | — | `WebSearch` surfaces real arXiv/ScienceDirect papers on algorithmic amplification (2024–2025). Direct PDF fetch of one (`arxiv.org/pdf/2401.11194`) returned garbled binary — WebFetch cannot extract text from this arXiv PDF endpoint. Fetch the arXiv **abstract page** (`/abs/` not `/pdf/`) instead in the real run. |

## Five highest-value queries for the real run

1. `MrBeast average view percentage retention data case study` — chase quantified, dated
   retention claims beyond the leaked-guide narrative and vague "he obsesses over
   retention" restatements.
2. `Alex Hormozi content volume backlash burnout diminishing returns` — deliberately
   hunt negative evidence on the volume/repurposing thesis before crediting it (V3
   mandate); scout found the criticism angle exists but hasn't chased the
   volume-specific failure mode yet.
3. `Lulu Cheng Meservey Rostra client outcome case study` OR `"going direct" measured
   result` — the manifesto itself supplied zero evidence; this query tests whether
   evidence exists anywhere else before crediting the thesis at more than "argued, not
   shown."
4. `MrBeast video underperformed flop format failure` — a documented platform/format
   failure per practitioner is a rubric item (item 3); none surfaced yet for MrBeast.
5. `content repurposing effectiveness study Tubular Rival IQ analytics` — test whether
   any analytics-firm (not guru-adjacent) data exists on repurposing ROI, to get past
   secondary paraphrase of Hormozi's own claimed numbers.

## Ambiguities in the brief this pass surfaced

- **Wrong Substack name.** The brief says "Meservey's Substack (Rough Drafts)"; her
  actual publication is **Flack** (formerly *Res Ipsa*). No publication called "Rough
  Drafts" was found. Corrected in the prompt's seed-sources slot.
- **"MrBeast leaked production guide... verify what's actually accessible"** — verified:
  accessible only as secondary-sourced quotes, never as a directly-fetchable primary
  document, and every commentator who discusses it declines to confirm authenticity.
  The prompt must not let either executor treat this class as more certain than
  "leaked, stylistically consistent, formally unverified."
- **No working seed URL for Hormozi's owned content** was found in this pass
  (`acquisition.com/blog` 404s). Flagged as a research gap rather than guessed.

## Sub-question priority changes this scout pass forces

- **Sub-question 2 (independent corroboration) moves from priority-2 to load-bearing
  everywhere**, not just its own subsection: two of the three practitioners' flagship
  source material (Meservey's manifesto, the MrBeast leak) turn out to be either
  overtly interest-conflicted-and-evidence-free or provenance-unconfirmed. Every claim
  drawn from either has to carry that caveat inline, not just in a dedicated
  corroboration subsection.
- **Reddit drops out of the source-priority list** for the terminal executor — it is
  not "spotty," it is unreachable, and search does not substitute. (Flagged as an
  executor-specific finding — a web DR product may have different Reddit reach; stage 8
  should compare.)
- **YouTube-native evidence (retention graphs, transcripts) is downgraded** from an
  assumed-accessible source to a confirmed-inaccessible one for this executor; secondary
  press that already paraphrases the video content (Tubefilter, analytics blogs) becomes
  the load-bearing fallback rather than a backup.

## Fills for the A6 slots

**`{{ACCESSIBILITY_RESULTS}}`:** Reachable and citable: Tubefilter, Simon Willison's
blog, Flack (getflack.com), Social Media Examiner, general marketing-analytics
write-ups (OutlierKit, aimaker, Copyblogger), arXiv abstract pages. Reachable but
low-evidence: the MrBeast leaked-guide primary document (secondary-only, unverified
provenance) and Meservey's manifesto (argumentative, zero case studies). Confirmed
unreachable for this executor: X/Twitter (402), Reddit (hard-blocked, zero search
substitute), YouTube transcripts/captions (nav-only page, transcript sites 403).
Inconclusive: podcast transcript sites (rate-limited, not hard-blocked — retry with
pacing).

**`{{FALLBACKS}}`:** Where X/Twitter or Reddit would be the natural source, use
secondary trade press (Tubefilter) and marketing-analytics write-ups that already
quote or paraphrase the primary platform content, and say explicitly that the primary
platform post was not independently viewed. Where YouTube transcript-level detail
would be the natural source, use secondary coverage that paraphrases the video and
mark retention-graph-level specifics as "reported, not independently observed." Do not
substitute SEO listicles for any of the above — Tubefilter and named analytics
write-ups are the floor.
