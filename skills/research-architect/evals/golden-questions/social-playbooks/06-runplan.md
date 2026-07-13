# Stage 6 — Run Plan (proposal; stage 7 execution not yet approved)

## Executors and run shape

Two-run merge (M-blocks active in both prompts, fixed 12-section order):

1. **Terminal run** — a local executor subagent in this environment, given
   `04-prompt-terminal.md`. It has what the web run lacks: local `viral` checkout
   for the artifact-evidence table, and per-URL fetching for corroboration lineage.
2. **Web DR run** — `04-prompt-web.md` pasted into **Gemini Deep Research**
   (recommended) or OpenAI Deep Research as the alternate.

**Why Gemini DR:** the scout showed this topic lives in Google-indexed trade press,
Substacks, and YouTube-adjacent secondary coverage — breadth of index matters more
here than reasoning depth, and the terminal run already covers the
depth/verification side. Per the skeleton's calibration table both web products have
the same known limits (X unreachable, Reddit spotty), which the prompt's fallbacks
already handle. No executor-profiles.md history exists yet to override this
reasoning — this run seeds it.

## Budgets

- **Terminal:** deep tier per the `deep-research` skill's routing (20–80 searches,
  4–8 tracks); soft cap ~90 minutes wall-clock; degradation order applies if the
  budget bites (sections 5 and 6 at full depth first).
- **Web DR:** one full run of the product's default deep-research budget; no re-runs
  without a stage-8 verdict first.
- **Verification reserve (stage 8):** ~15 citation fetches per report + one fresh
  rubric-scoring subagent per report + the cross-run diff. Do not spend this budget
  on extending research.

## Degradation order (restated from both prompts)

Sections 5 (priors evaluation) and 6 (confounds analysis) at full depth; all other
sections may be stubbed with one explicit paragraph each. Uniform shallowness is the
worst outcome.

## Fixed section order (both reports, for the stage-8 cross-run diff)

(1) Frame-check (always present) · (2) MrBeast case study · (3) Hormozi case study ·
(4) Meservey case study · (5) Priors evaluation · (6) Confounds analysis ·
(7) Platform-transfer analysis · (8) Temporal-change analysis · (9) Classification
synthesis table · (10) Build handoff · (11) Self-report · (12) Summary block.

## Hand-back note (web run)

- Paste the full contents of `04-prompt-web.md` into the chosen product as a single
  message; no preamble needed — the prompt is self-contained.
- Bring back: the complete report text including the annotated bibliography and the
  final `key_findings / citations / confidence_gaps / next_queries` summary block.
  Export/copy the whole thing — partial pastes break the section-aligned diff.
- Note which product and date you ran it; that goes in `executor-profiles.md` at
  stage 9.
- The `research/social-playbooks/` directory must survive until stage 9 completes;
  after that, keepers move to `docs/research/` in this repo and the directory is
  deleted.

## Stage 8 preview (what happens when reports return)

Structural pass (sections present, ~15 citation fetches per report with claim-support
checks), rubric pass (fresh subagent scores all 10 items per report, pass/fail with
quotes), cross-run diff (confident specifics appearing in only one report are
hallucination candidates — checked against primary sources before the merge may use
them), then a verdict: accept / accept-with-caveats / re-run with amended prompt.
