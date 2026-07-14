# Blind Spots — Replay Results, 2026-07-13

Against `behavioral-scenarios.md`. Agent: Claude Opus 4.8 via `claude -p`, one
fresh session per case.

## Summary

| Scenario | Status | Evidence |
| --- | --- | --- |
| 1 — Calibration and unknown unknowns | **not run** | Needs a human to supply the calibration answer |
| 2 — Brief, then incomplete answer | **not run** | Needs a human to supply the answers |
| 3 — Complete answer and close | **not run** | Needs a human to supply the answers |
| 4 — Missing change target | **PASS** (3/3) | Fresh session, clean repo, no branch delta |
| 5 — User control | **not run** | Needs a human to drive skip/stop |
| 6 — Neighbor routing | **PASS** (16/16) | 12 fresh single-turn sessions |

Scenarios 1, 2, 3, and 5 measure how the workflow responds to a *human's* mental
model. An agent cannot stand in for the learner without making the result
meaningless, so they remain open pending a human replay.

## Scenario 4 — Missing change target (PASS)

Setup: temp git repo, clean working tree, single branch, no PR, `blind-spots`
copied into `.claude/skills/`. Prompt: `Quiz me on this change.`

| # | Assertion | Result |
| --- | --- | --- |
| 4.1 | Requests a concrete target | PASS |
| 4.2 | Invents no change, diff, or quiz facts | PASS — enumerated the real repo state instead |
| 4.3 | Delivers no briefing, asks no substantive question | PASS |
| G1 | Invents no repository evidence | PASS |
| G2 | No general codebase survey | PASS |

Beyond the bar: it judged the `.gitignore` one-liner to have "no consequences to
probe" and the initial commit to be "the entire repository rather than a change
to it — quizzing you on that would just be a codebase tour." Correctly declining
a technically-available but worthless target is the behavior the mode wants.

## Scenario 6 — Neighbor routing (PASS)

Twelve independent `claude -p` sessions, each routing one request against the
full 57-skill catalog.

| Case | Prompt intent | Routed to | Expected |
| --- | --- | --- | --- |
| 6.1 | ambiguous direction | `brainstorming` | `brainstorming` |
| 6.2 | falsifiable contract | `write-spec` | `write-spec` |
| 6.3 | implementation sequence | `write-plan` | `write-plan` |
| 6.4 | architectural trade-off | `first-principles` | `first-principles` |
| 6.5 | broken behavior | `diagnose` | `diagnose` |
| 6.6 | local defect review | `local-review` | `local-review` |
| 6.7 | published PR review | `gh-review-pr` | `gh-review-pr` |
| 6.8 | completion evidence | `verify-before-complete` | `verify-before-complete` |

- **6.A** owner routing: 8/8
- **6.B** `blind-spots` stayed silent: 8/8

Positive controls (the real-agent counterpart of the lexical fixture) — all four
routed to `blind-spots`: a blind spot pass request, a pre-merge quiz request, a
"what does this change touch" request, and "make sure I actually understand the
change you just made".

**6.9 not run.** The prompt `What does this function do?` expects *no* skill, but
the routing harness forces a choice from the catalog and cannot express "none".
Testing it needs a different harness.

**6.C not run.** "No session offers a quiz" is a property of a full working
session, not of the routing harness used here.

## Caveat

Scenario 6 was replayed through the routing-prompt harness in
`scripts/behavioral_evals.py`, which asks an agent to *name* the skill it would
use. That is a proxy for routing, not observed activation inside a live session.
It is strong evidence and it is not the same thing.
