# Change Comprehension — Behavioral Scenarios

Frozen conversational acceptance for the `change-comprehension` skill, per
`docs/specs/2026-07-13-change-comprehension-spec.md`.

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

Two global assertions apply to every scenario and are not repeated below:

- **G1** — No response invents repository evidence. Every file, line, symbol, or
  behavior cited exists.
- **G2** — No response expands into a general codebase survey.

On failure: revise the **minimum** instruction needed, then replay the *same*
frozen scenario from a *new* session. Do not edit the scenario to fit the
behavior.

## Scenario 1 — Scope boundary and evidence

**Setup.** A repository where the user's approved intent conflicts with current
behavior, and one boundary is genuinely unresolved. Reference setup: a service
whose retry logic currently swallows a specific error class, an approved request
to surface that error to the caller, and no evidence in the repo of whether the
upstream queue retries the call.

**Turns.**

- **User:** `Before we implement this, help me understand the scope of the proposed change — we want that swallowed error surfaced to the caller.`

**Assertions.**

| # | Assertion |
|---|---|
| 1.1 | Separates current behavior (repository evidence) from proposed intent (the user's request), so a reader can tell which is which |
| 1.2 | Names the conflict between the two explicitly rather than silently adopting either |
| 1.3 | Marks the unresolved boundary as unknown, and does not assert a retry behavior the repo does not show |
| 1.4 | Explains a bounded entry point and call path, not every path in the system |
| 1.5 | Prescribes **no** architecture choice, **no** acceptance criteria, and **no** task sequence |
| 1.6 | Writes no file |

## Scenario 2 — Incomplete quiz answer

**Setup.** An implemented, identifiable change (working tree, branch, or commit)
with some verification evidence — at least one test covering it.

**Turns.**

- **User:** `Quiz me on this change before I merge it.`
- **User:** *(after the assistant's first substantive question)* `I think it changes how the retry path handles errors, but I'm not sure what the tests actually cover.`
- **User:** *(after the assistant's next question)* `I don't know.`

**Assertions.**

| # | Assertion |
|---|---|
| 2.1 | Reads the actual change before asking any substantive question |
| 2.2 | Proposes a bounded topic set (or accepts a user-specified depth) before quizzing |
| 2.3 | Each active quiz turn contains **at most one** substantive question |
| 2.4 | After asking, it **stops and waits** — it does not answer, hint, or reveal in the same turn |
| 2.5 | After the partial answer, it names what was correct, then corrects or extends with concrete repository evidence (file, line, or symbol) |
| 2.6 | After `I don't know`, it teaches the answer with evidence and does not judge, score, or express disappointment |
| 2.7 | Continues within the proposed topic set rather than expanding scope |

## Scenario 3 — Complete answer and close

**Setup.** The same change as Scenario 2.

**Turns.**

- **User:** `Quiz me on this change.`
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
| 4.3 | Asks no substantive quiz question |

## Scenario 5 — User control

**Setup.** The same change as Scenario 2, with a quiz already underway and a
proposed topic set the user has seen.

**Turns.**

- **User:** `Quiz me on this change.`
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
| 6.B | `change-comprehension` does not activate in any of the nine sessions |
| 6.C | No session offers or volunteers a quiz |

## Recording Results

Record one row per assertion: scenario, assertion id, pass/fail, and a one-line
note on any failure. Live agents are not deterministic — if an assertion fails
intermittently across replays, record that honestly as variance rather than
rounding it to a pass.
