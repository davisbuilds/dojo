# Stage 4 — Lint Results

## Automated (`scripts/lint_prompt.py`)

**Terminal** (`04-prompt-terminal.md`), `--executor terminal`:

```
[PASS] unfilled_slots — no unfilled slots
[PASS] drafting_comments — no drafting comments
[PASS] instruction_budget — 16 instructions vs budget 60 (terminal)
[PASS] do_not_list — A7 do-not list ('Do NOT (known failure modes...)') present
[PASS] degradation_order — A8 degradation order present
[PASS] rubric_present — A9 shipped rubric / acceptance criteria present
[PASS] self_report — A10 self-report present
[PASS] summary_block — summary block tokens present
overall: pass (16/60 instructions)
```

**Web** (`04-prompt-web.md`), `--executor web`:

```
[PASS] unfilled_slots — no unfilled slots
[PASS] drafting_comments — no drafting comments
[PASS] instruction_budget — 17 instructions vs budget 40 (web)
[PASS] do_not_list — A7 do-not list ('Do NOT (known failure modes...)') present
[PASS] degradation_order — A8 degradation order present
[PASS] rubric_present — A9 shipped rubric / acceptance criteria present
[PASS] self_report — A10 self-report present
[PASS] summary_block — summary block tokens present
overall: pass (17/40 instructions)
```

Both passed clean on the first lint run — no fix/re-lint cycle was needed. See
friction log for why the instruction counts came in far under budget (15/60 and
16/40 respectively) despite assembling all 20 non-core blocks (V1–V5, D1–D5, M1–M2):
the skeleton's fixed block text is imperative-sparse by design (15 total `must/never/
always/do not/don't` markers across all 22 blocks combined, verified by grepping
`skeleton.md` directly), so nearly all instruction-budget "cost" comes from how the
drafter phrases slot content, not from block selection itself.

## Manual checks (from SKILL.md stage 4)

**[x] Every requirement checkable from report text alone.**

Re-walked both the A9 rubric (9 items, already checked individually in
`01-question.md`) and the A7 do-not list (6 topic items + 3 universal) against the
"could a verifier confirm this from the report text alone" test:

- All 9 rubric items: checkable — each maps to a scan for a specific textual feature
  (a citation+date pair, a named subsection, a tagged example, a named skill/rule in
  the handoff, an explicit verdict statement). No item requires the verifier to
  independently re-research the topic to check compliance.
- Do-not items: checkable in the weak sense that a verifier can confirm the *textual
  marker* is present (e.g., does the report cite the MrBeast leak with a hedge like
  "unverified" or does it state it flatly as fact; does it label Hormozi's own content
  as hypothesis or as evidence). "Do not conflate MrBeast's budget-dependent tactics
  with replicable ones" is the softest of the six — a verifier has to judge, not just
  pattern-match — but the judgment is bounded (does the report say anything at all
  about budget-dependency for each MrBeast tactic it recommends), so it clears the
  bar.

**[x] Do-not list is topic-specific, not generic virtue.** *(pre-red-team pass; see
post-red-team addendum below)*

All six topic items name a specific practitioner, a specific artifact (the leaked PDF,
the Flack manifesto), or a specific confusion (budget-dependent vs. replicable). None
of the six is a restatable-for-any-topic virtue like "be thorough" or "verify your
sources" — those already live in the three universal do-nots baked into the A7
template, which is the correct place for them.

## Post-red-team re-lint (after stage-5 fold-in)

Both prompts re-linted clean: **terminal 16/60, web 17/40** — identical counts to the
pre-red-team pass. The red-team's deletions (4 shared items + 1 web-only) and the
fold-in's additions (3 shared do-nots + 1 web do-not, rubric item 10, checkable
frame-check and recency rewrites) balanced out in marker terms.

**Red-team deletion applied:** the "12 findings > 40 claims" sentence, the
"quiet/unglamorous" priming line, the universal do-nots block, the "state the
reasoning... take it on faith" tail, and (web only) the "verify access at start of
run" preflight clause.

**Red-team deletion rejected:** self-report item (c) ("which instructions you could
not fully follow"). The red-team is right that it is unverifiable from report text —
but it is the sole input to the skill's stage-9 postmortem loop, i.e. the only
enforcement of a stage-0/1 process priority. Kept per the redteam-checklist's keep
rule; the unverifiability is priced in by design.

**Conflicts resolved:** bibliography curation-vs-completeness (dedup floor now set at
Weak-or-better grade); frame-challenge vs. fixed section order (section 1 is now
always present and is the designated home for reframing and, on the web run, access
divergences); depth-vs-breadth (rubric item 10 adds a per-tactic evidence floor and a
short-form register for below-floor tactics, replacing the deleted unenforceable
prose).
