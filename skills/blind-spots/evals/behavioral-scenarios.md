# Blind Spots — Behavioral Scenarios

Frozen conversational acceptance for the `blind-spots` skill, per
`docs/specs/2026-07-13-blind-spots-spec.md`.

The deterministic trigger fixture (`trigger-cases.json`) checks *routing* by
lexical overlap. It says nothing about how the skill behaves once it is running.
These scenarios are the behavioral half, and they are **replayed by a human**,
not by a script — no runner in this repository can drive a multi-turn
conversation and judge it.

## Replay Protocol

For **each** scenario, independently:

1. Open a **new session** with no prior conversation beyond repository
   instructions. Never replay two scenarios in one session — state leaks.
2. Invoke the skill explicitly (`/understand-change`, `/quiz-change`, or by name).
3. Feed the **User** turns **verbatim, in order**. Send one, wait for the
   assistant to finish, then send the next. Never paraphrase, never merge turns,
   never answer a question the scenario does not answer.
4. Mark each assertion **pass** or **fail**. An assertion is binary; "mostly" is
   a fail.
5. A scenario passes only when **every** assertion passes. The suite passes only
   when every scenario passes.

Three global assertions apply to every scenario and are not repeated below:

- **G1** — No response invents repository evidence. Every file, line, symbol, or
  behavior cited exists.
- **G2** — No response expands into a general codebase survey.
- **G3** — Depth matches the expertise the user declared. A user who says they
  know the codebase gets no fundamentals lecture.

On failure: revise the **minimum** instruction needed, then replay the *same*
frozen scenario from a *new* session. Do not edit the scenario to fit the
behavior.

## Scenario 1 — Calibration and unknown unknowns

**Setup.** A repository where the user's approved intent conflicts with current
behavior, and one boundary is genuinely unresolved. Reference setup: a service
whose retry logic currently swallows a specific error class, an approved request
to surface that error to the caller, and no evidence in the repo of whether the
upstream queue retries the call.

**Turns.**

- **User:** `Do a blind spot pass on this before we build it — we want that swallowed error surfaced to the caller.`
- **User:** *(in reply to the calibration question)* `I know this service well but I've never touched the queue side of it.`

**Assertions.**

| # | Assertion |
|---|---|
| 1.1 | Opens by asking what the user already knows, before explaining anything |
| 1.2 | Honors the declared expertise — explains the queue side, does not re-explain the service the user said they know |
| 1.3 | Separates current behavior (repository evidence) from proposed intent (the user's request) |
| 1.4 | Names the conflict between the two explicitly rather than silently adopting either |
| 1.5 | Surfaces at least one **unknown unknown** — something the user did not ask about and would not have thought to ask |
| 1.6 | Marks the unresolved queue-retry boundary as unknowable from the repo, and asserts no retry behavior |
| 1.7 | Prescribes **no** architecture choice, **no** acceptance criteria, and **no** task sequence |
| 1.8 | Writes no file |

## Scenario 2 — Brief, then incomplete answer

**Setup.** An implemented, identifiable change (working tree, branch, or commit)
with some verification evidence — at least one test covering it.

**Turns.**

- **User:** `Quiz me on this change before I merge it.`
- **User:** *(in reply to the calibration question)* `I know the codebase well, but I wasn't watching closely while you worked.`
- **User:** *(after the assistant's first substantive question)* `I think it changes how the retry path handles errors, but I'm not sure what the tests actually cover.`
- **User:** *(after the assistant's next question)* `I don't know.`

**Assertions.**

| # | Assertion |
|---|---|
| 2.1 | Reads the actual change before asking any substantive question |
| 2.2 | **Briefs the user before quizzing** — what changed, why, where it plugs in, what the tests cover |
| 2.3 | The briefing does **not** pre-answer the quiz: it does not spell out the failure modes, the limits of the tests, or the residual risks |
| 2.4 | Proposes a bounded topic set before quizzing |
| 2.5 | Each active quiz turn contains **at most one** substantive question |
| 2.6 | After asking, it **stops and waits** — it does not answer, hint, or reveal in the same turn |
| 2.7 | Questions probe consequences (why this seam, what breaks, what the tests miss), not contents the briefing already stated |
| 2.8 | After the partial answer, it names what was correct, then corrects or extends with concrete repository evidence (file, line, or symbol) |
| 2.9 | After `I don't know`, it teaches the answer with evidence and does not judge, score, or express disappointment |

## Scenario 3 — Complete answer and close

**Setup.** The same change as Scenario 2.

**Turns.**

- **User:** `Quiz me on this change.`
- **User:** *(in reply to the calibration question)* `Senior engineer, I know this codebase.`
- **User:** *(after each question, until the topic set is covered)* A complete, correct answer covering intent, the seam, and what the tests do and do not prove. Supply a genuinely complete answer each time; do not withhold.

**Assertions.**

| # | Assertion |
|---|---|
| 3.1 | Recognizes the complete answer and does not re-ask the same ground |
| 3.2 | Closes once the proposed topic set is covered — it does not invent extra questions to prolong the quiz |
| 3.3 | Ends with a concise recap naming strengths and anything worth revisiting |
| 3.4 | The recap contains **no** numeric score, **no** pass/fail label, **no** claim the implementation is correct, and **no** merge verdict |
| 3.5 | Writes no file |

## Scenario 4 — Missing change target

**Setup.** A clean repository: no working-tree changes, no staged changes, no
branch delta, no pull request under discussion.

**Turns.**

- **User:** `Quiz me on this change.`

**Assertions.**

| # | Assertion |
|---|---|
| 4.1 | Reports that it cannot identify a change target and asks for a concrete one (diff, commit, branch, or PR) |
| 4.2 | Invents no change, no diff, and no quiz facts |
| 4.3 | Delivers no briefing and asks no substantive quiz question |

## Scenario 5 — User control

**Setup.** The same change as Scenario 2, with a quiz already underway and a
proposed topic set the user has seen.

**Turns.**

- **User:** `Quiz me on this change.`
- **User:** *(in reply to the calibration question)* `I know this area.`
- **User:** *(after the first question)* `Skip the failure-modes topic, I don't care about it right now.`
- **User:** *(after the assistant's next turn)* `Actually, let's stop here.`

**Assertions.**

| # | Assertion |
|---|---|
| 5.1 | Drops the skipped topic and does not return to it |
| 5.2 | Stops immediately when asked, without one more question |
| 5.3 | Treats neither the skip nor the stop as a failure — no scolding, no score, no "you didn't finish" |
| 5.4 | Writes no file |

## Scenario 6 — Neighbor routing

**Setup.** Any repository. Each prompt goes in its **own** new session — nine
sessions, not one.

**Turns.** One per session, verbatim:

| # | Prompt | Expected owner |
|---|---|---|
| 6.1 | `I'm not sure what we should build here. Let's talk through the options and trade-offs.` | `brainstorming` |
| 6.2 | `Pin the falsifiable contract and acceptance criteria for this feature.` | `write-spec` |
| 6.3 | `Sequence the implementation into ordered tasks with files and steps.` | `write-plan` |
| 6.4 | `Which architecture should we pick? Reason from first principles about the trade-offs.` | `first-principles` |
| 6.5 | `This endpoint throws intermittently in production. Find the root cause.` | `diagnose` |
| 6.6 | `Review my staged diff and give me severity-ranked findings.` | `local-review` |
| 6.7 | `Review pull request 42 on GitHub and post a merge recommendation.` | `gh-review-pr` |
| 6.8 | `Before you claim this is done, show me the evidence that it passes.` | `verify-before-complete` |
| 6.9 | `What does this function do?` | none — a plain answer |

**Assertions.**

| # | Assertion |
|---|---|
| 6.A | Each prompt is handled by its expected owner (or, for 6.9, answered directly) |
| 6.B | `blind-spots` does not activate in any of the nine sessions |
| 6.C | No session offers or volunteers a quiz or a blind spot pass |

## Recording Results

Record one row per assertion: scenario, assertion id, pass/fail, and a one-line
note on any failure. Live agents are not deterministic — if an assertion fails
intermittently across replays, record that honestly as variance rather than
rounding it to a pass.
