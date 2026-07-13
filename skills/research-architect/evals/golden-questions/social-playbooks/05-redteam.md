# Stage-5 Red-Team: 04-prompt-terminal.md and 04-prompt-web.md

Role-played as a competent-but-lazy executor on each prompt's own execution surface, per `redteam-checklist.md`'s mandate. No praise. Additions are limited to item 5 (missing do-nots) as required.

---

## Prompt: 04-prompt-terminal.md (Claude Code / Codex executor)

### 1. Letter-vs-spirit gaps

- **"Depth and honesty beat breadth and optimism. 12 well-evidenced findings are worth more than 40 unverified claims."** Lazy-compliant output: hit exactly ~12 headline findings, hedge every one with "moderate" evidence grade regardless of actual verification depth, and never explain why 12 vs. 13 vs. 8 was the right count. Nothing in the report can distinguish "genuinely depth-first" from "counted to 12 and stopped."
- **"Confirm claims, numbers, dates, and configurations against primary sources."** Lazy-compliant: one search per claim, first secondary source that repeats the number gets cited, executor writes "confirmed" without ever tracing to the actual primary (original interview, filing, platform disclosure).
- **Frame-challenge license** ("say so at the top... only if triggered"). Lazy-compliant: declare no frame problems exist. The conditional trigger means "I didn't find one" and "I didn't look" are indistinguishable in the output.
- **Negative evidence mandate** ("A section containing no negative evidence is incomplete by definition"). Lazy-compliant: one boilerplate sentence per practitioner ("some critics cite format fatigue") satisfies the letter ("a negative evidence section appears," rubric item 6) without the actual differential search into creator communities and trade-press retrospectives the instruction describes.
- **Artifact-level evidence table** ("cite exact file paths and line ranges... read actual SKILL.md and rules/*.md files rather than guessing"). Lazy-compliant: open each file, skim the top, cite a plausible-looking line range without confirming the cited section actually supports the row's claim. A verifier reading the report text alone cannot tell skimmed-and-guessed from actually-read.
- **Self-report candor** ("candor here is rewarded, not penalized"). Lazy-compliant: generic hedges ("some sources were hard to verify") instead of naming specific unfollowed instructions, because nothing external checks the self-report against actual tool-call behavior.
- **Corroboration protocol** ("name both sources and state why you judge them independent"). Lazy-compliant: cite two secondary write-ups of the same original leak/interview, call them independent because they're different domains, without checking upstream lineage — exactly the failure mode the protocol exists to prevent, satisfied at the letter level by naming two URLs.

### 2. Silent skips

- **"Mark a row 'not inspected' rather than guessing if you cannot open the file"** — an explicit, prompt-sanctioned escape hatch. Skippable because the prompt itself gives permission to bail; a lazy executor inspects 2–3 files, marks the rest "not inspected," and has technically complied.
- **Trade-off table "for each recommended tactic-to-kit mapping"** — expensive to build per-mapping. Skippable because a lazy executor builds it only for 3–4 headline tactics and folds the rest into the classification table, silently merging two deliverables the prompt treats as distinct.
- **"Include relevant developments published since this prompt was written."** Unfalsifiable — nobody downstream can prove a real recency search happened vs. "no significant developments found" written cold. Skippable at zero cost.
- **"Podcast transcript sites (rate-limited once, not hard-blocked — retry with pacing)."** Skippable because retrying costs turns/time and no one audits the fetch log; executor tries once (or not at all) and reports "inaccessible," silently downgrading from the prompt's own instruction to retry.
- **Source floor of "at least 10 adjacent primary/secondary sources spanning all three practitioners and at least two of the four priors."** "Adjacent" and the practitioner/prior mapping are vague enough that a lazy executor pads with tangential sources that technically touch each practitioner once, satisfying the count without the substantive coverage the floor is meant to guarantee.
- **Degradation order** ("if depth becomes constrained, deliver 5 and 6 at full depth... stub the rest"). This is a sanctioned escape valve for genuine resource pressure, but nothing distinguishes genuine constraint from an executor invoking it early to justify stubbing sections 2–4 and 7–9 it didn't want to do anyway.

### 3. Conflicts

- **"Do not pad the bibliography; a marginal low-quality source is worse than none"** directly conflicts with **"Bibliographies will be deduped across the two reports — completeness matters more than curation here"** (Cross-run merge). One says curate hard, the other says completeness beats curation. A numeric floor ("at least 10 adjacent sources") on top of both pressures padding precisely when quality sources run out.
- **Frame-challenge license** ("you are not graded on agreement with the prompt") vs. **Output contract**'s rigid section order ("no added, removed, or reordered sections"). If the frame-check concludes the core question is malformed, the executor is still forced into the fixed 12-section skeleton built for the original framing — the license to challenge the frame has no structural room to actually restructure the report around a different frame.
- **"12 well-evidenced findings are worth more than 40 unverified claims"** (breadth discouraged) vs. the classification scheme ("tag every significant example on these four axes"), comparative system coverage across 3 practitioners, and the 9-item shipped rubric — these structurally reward exhaustive, broad coverage and work against the stated depth-over-breadth ethos. The prompt's actual grading criteria contradict its own stated priority.

### 4. Deletions (mandatory: at least three)

1. **"Depth and honesty beat breadth and optimism. 12 well-evidenced findings are worth more than 40 unverified claims."** Unverifiable from report text (no verifier counts "findings" against a numeric bar), and the evidence-grading system plus shipped rubric already enforce the underlying intent.
2. **"The most valuable findings are often the quiet, unglamorous ones — stay genuinely open to them while assuming loud claims are exaggerated until evidence says otherwise."** Pure restatement of the skeptical-analyst disposition already set in the opening sentence of Mission & disposition.
3. **Universal do-nots block** ("do not present a claim's confidence above its evidence; do not reconstruct unpublished internals... do not fill a section with filler when evidence is thin"). Fully duplicates the evidence-grading section and the Output contract's "insufficient evidence... first-class result" clause. Same instruction stated three separate times across the document.
4. **"Where you make a design judgment, state the reasoning so the build session can evaluate it rather than take it on faith"** (end of Build handoff). Generic good-practice restatement; no verifier can check "reasoning quality" from report text beyond mere presence, and it duplicates Verification & honesty's transparency mandate.
5. **Self-report item (c)** ("which instructions in this prompt you could not fully follow, and why"). Unverifiable, substantially redundant with item (b) ("the gaps — what you could not access or verify"), and invites exactly the hedge-listing a lazy executor already produces with zero consequence.

### 5. Missing do-nots

- Do not treat a practitioner's own staff/team testimonials (MrBeast production staff, Hormozi's Acquisition.com team) as independent corroboration — same financial interest as the practitioner.
- Do not count multiple articles from the same outlet or syndicated wire copy as two independent sources when judging corroboration.
- Do not treat self-reported net worth or platform-disclosed follower/revenue figures as base-rate/denominator data without flagging that the figure originates from the subject being evaluated.
- Do not infer a practitioner's current tactics from pre-2020 material and present it as current without an explicit "as of [date]" check — given the temporal-shift sub-question, stale-dressed-as-current citation is a specific failure mode here, not a generic one.
- Do not present the three practitioners' theses (going-direct, retention-craft, volume-repurposing) as compatible without checking whether they conflict operationally — the prompt frames them as three parallel theses to test individually but never asks whether they contradict each other.

---

## Prompt: 04-prompt-web.md (web deep-research product: no repo access, no code execution, single-shot)

### 1. Letter-vs-spirit gaps

- **"Verify against your own access at the start of this run and note any divergence"** (accessibility table). Lazy-compliant: copy the prompt's own accessibility table as ground truth, add one line ("no divergence noted") without any actual probing — indistinguishable in the output from genuine re-verification.
- **"Confirm claims, numbers, dates, and configurations against primary sources."** For a text-only web browsing tool, the true primary source is frequently a video, paywalled article, or platform-internal dashboard the tool cannot reach. Lazy-compliant: cite the best available secondary source and label it "primary" anyway, since genuinely reaching the primary is infeasible and nothing in the report format forces the distinction to be checked.
- **Negative evidence mandate.** Same boilerplate risk as the terminal prompt, worse in practice: a single-shot web search tool's top results skew toward promotional/positive coverage of public figures; one query pass ("MrBeast controversy") returns a defensible-looking citation without the systematic search into retrospectives and walk-backs the instruction calls for.
- **Artifact-level evidence table** ("View individual files at github.com/.../blob/main/... where your browsing capability allows it. Mark any row 'not inspected' rather than guessing"). Lazy-compliant: attempt one file, note the tool's browsing struggles with rendered GitHub pages, and mark every remaining row "not inspected" — technically compliant, but the D3 table (a rubric-required deliverable) ends up empty by design rather than by genuine access failure.
- **Self-report candor.** Same as terminal: no external check on whether "which instructions I could not follow" is a genuine audit or a plausible-sounding paragraph.

### 2. Silent skips

- **Podcast transcript sites are not mentioned anywhere in the web prompt's accessibility table** (present in the terminal prompt as "rate-limited once... retry with pacing"). This isn't a lazy skip so much as a prompt gap: the web executor has no instruction to even attempt this source category, so it is silently absent from the research rather than explicitly excluded.
- **"Verify against your own access at the start of this run"** for X/Twitter/Reddit — presumes a distinct preflight-probe step before the "real" research pass. A genuinely single-shot product has no such separate phase; this instruction is skippable because there's no way to force a check that happens "at the start" as opposed to opportunistically wherever it's convenient (or not at all) during generation.
- **Trade-off table per mapping** and **source floor of 10 adjacent sources** — same skip logic as the terminal prompt; unchanged text, unchanged incentive to under-deliver.
- **Degradation order** — same sanctioned-but-unverifiable escape valve as the terminal prompt.

### 3. Conflicts

- Same bibliography conflict as the terminal prompt: **"a marginal low-quality source is worse than none"** vs. **"completeness matters more than curation here"** (Cross-run merge), unchanged text.
- Same frame-challenge-license vs. fixed-section-order conflict, unchanged text.
- Same depth-over-breadth-ethos vs. exhaustive-four-axis-tagging conflict, unchanged text.
- **New, web-specific:** "verify against your own access... and note any divergence" vs. the fixed Output contract's 12 sections with "no added... sections." If the executor discovers genuine divergence (e.g., it actually can reach X/Twitter, unlike the terminal scout), there is no designated section to report that divergence — it has to be smuggled into an existing section or dropped.

### 4. Deletions (mandatory: at least three)

1. Same as terminal deletion #1 — the "12 findings > 40 claims" sentence: unverifiable, duplicated by the evidence-grading system.
2. Same as terminal deletion #2 — "quiet, unglamorous findings" priming sentence: duplicate of the opening disposition statement.
3. Same as terminal deletion #3 — the universal do-nots restatement block: duplicate of evidence grading and the Output contract's insufficient-evidence clause.
4. **"Verify against your own access at the start of this run and note any divergence"** — unverifiable from outside (no way to confirm a real preflight check happened vs. a one-line assertion), and substantially redundant with the general Verification & honesty mandate already stated earlier in the prompt. Collapses to a single sentence at best.
5. Same as terminal deletion #4 — "state the reasoning so the build session can evaluate it rather than take it on faith": generic, unenforceable from report text.

### 5. Missing do-nots

- Do not cite a GitHub blob page's rendered preview as verified file content when the page is truncated, paginated, or fails to fully load — mark "not inspected," don't paraphrase from the repo's file tree or README naming conventions.
- Do not treat a search-engine result snippet as equivalent to having read the source page — open and read the full page before citing it.
- Do not cite SEO/AI-summary sites that repackage the same MrBeast/Hormozi claims as independent secondary sources without checking whether the site itself cites a primary source or just recycles other blogs.
- Do not treat a single search session's top results as an exhaustive negative-evidence pass — negative evidence is structurally under-indexed relative to promotional coverage; run dedicated negative-framed queries per practitioner rather than one general query per topic.

### Capability-assumption flags (web prompt only)

1. **GitHub blob-page browsing.** The prompt sends the executor to `github.com/davisbuilds/viral/blob/main/skills/<name>/SKILL.md` rendered pages rather than `raw.githubusercontent.com` plain-text equivalents. Rendered GitHub blob pages carry UI chrome and syntax-highlighting markup that a generic web-page-to-text browsing tool may not extract cleanly, and large files can be paginated or lazy-loaded. The prompt hedges with "where your browsing capability allows it," but doesn't point to the more robust raw-text endpoint that would actually work reliably for a text-extraction tool — this is the single most concrete tool/surface mismatch in the prompt.
2. **Repo navigation without a directory listing.** The artifact-level evidence table requires locating specific skill/rule files by name inside a repo the executor cannot clone or browse as a filesystem. It works only because the Build handoff section happens to enumerate exact skill/rule names elsewhere in the prompt; for any file not on that pre-supplied list, discovering it would require GitHub's tree UI, a heavier and more failure-prone interaction than a single-file fetch that the prompt doesn't otherwise describe or license.
3. **"Verify against your own access at the start of this run"** presumes a distinct preflight-probe step separable from the actual research pass. A genuinely single-shot product (as the prompt's own framing describes the executor) may not have a separable "start of run" checkpoint at all — the instruction assumes an interaction model the stated constraints (single-shot) explicitly rule out.
4. Referencing "a terminal fetcher" and "the terminal-scout result" by name requires the web executor to model a different tool's constraints purely to discount them — low-cost but is context spent on meta-information irrelevant to the actual research task.

---

## Shared DNA (issues common to both prompts)

Roughly 90% of the two prompts is identical text, so most findings above transfer verbatim. Consolidated here rather than repeated:

- **Same duplicated throwaway assertions** in both: the "12 findings > 40 claims" line, the "quiet unglamorous findings" priming sentence, the universal do-nots restatement, and the "state the reasoning... rather than take it on faith" line. All four are candidates for deletion in both prompts for the same reason — restatement of intent already enforced elsewhere, unverifiable from report text.
- **Same bibliography conflict** in both: "a marginal low-quality source is worse than none" (Source strategy) directly contradicts "completeness matters more than curation here" (Cross-run merge), verbatim in both files.
- **Same frame-challenge-vs-fixed-structure conflict** in both: the license to challenge the prompt's framing has no room to actually restructure the report, since the Output contract forbids adding, removing, or reordering sections in either prompt.
- **Same stated-priority-vs-actual-grading conflict** in both: "depth over breadth" is the stated ethos, but the classification scheme, comparative coverage requirement, and 9-item shipped rubric all reward exhaustive breadth — the real grading criteria contradict the stated priority in both documents equally.
- **Self-report as the only compliance-check mechanism** in both: "which instructions could not be followed" and "the gaps" rely entirely on the executor's own candor, with zero external verification against actual tool-call/fetch behavior — an inherently gameable design present unchanged in both prompts.
- **Same negative-evidence lazy-skip risk** in both: identical text, identical one-boilerplate-sentence escape hatch.
- **Same "not inspected" escape hatch overuse risk** in both, aimed at different friction points: local filesystem reads in the terminal prompt, GitHub blob-page fetches in the web prompt. Structurally the same risk — a lazy executor marks rows "not inspected" to avoid the actual reading work the D3 table exists to force.
- **Same missing-do-not gap** in both: neither prompt ever asks whether the three practitioners' theses (going-direct comms posture, retention-craft, volume-repurposing) might be mutually incompatible strategies rather than three independently-testable parallel theses — both treat them as parallel rather than potentially competing.
