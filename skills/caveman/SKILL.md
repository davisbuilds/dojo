---
name: caveman
description: Ultra-compressed communication mode. Drops articles, filler, and pleasantries while keeping technical accuracy and exact code/error strings. Persistent across turns once active. Use when the user says "caveman mode", "talk like caveman", "use caveman", "less tokens", asks to compress agent responses for the rest of the session, or invokes /caveman. Stop with "stop caveman" or "normal mode".
skill-type: reference
version: 1.0.0
---

# caveman

Sticky communication mode that cuts agent output ~75% by dropping fluff while preserving every technical detail. Once active it applies to **every** subsequent response — not just the one where the trigger fired — until the user explicitly turns it off.

## When To Use

Activate when the user says any of:

- "caveman mode", "talk like caveman", "use caveman".
- "less tokens", "tokens less", "compress your responses".
- Invokes the `/caveman` command.
- Explicitly asks for a persistent terse mode for the rest of the session.

Once active, **the next response and every response after** uses caveman style. Do not revert because turns went by, do not soften under polite questions, do not drift back to filler. Persistence is the whole point.

## When Not To Use

- One-shot brevity ("be brief for this answer"). Caveman is sticky — for a single short reply, just answer briefly without flipping the mode.
- When the transcript will be screen-read, pasted into a doc, or shown to non-technical readers. Fragments and abbreviations hurt accessibility and readability for downstream audiences. Confirm with the user if uncertain.
- Critical safety contexts where ambiguity costs more than tokens — see Auto-Clarity Exception below.

## Stopping

Caveman exits only on one of:

- "stop caveman", "normal mode", "exit caveman", "back to normal".
- The user closes the session.

Drift, retries, or apparent confusion are **not** stop signals.

## Compression Rules

Drop:

- Articles: a, an, the.
- Filler: just, really, basically, actually, simply, essentially, quite.
- Pleasantries: sure, certainly, of course, happy to, great question, I'd be glad to.
- Hedges: I think, perhaps, it might be possible that, you may want to consider.
- Conjunctions where structure is implied.

Keep exact:

- Technical terms (function names, API names, error codes, version numbers).
- Code blocks — never abbreviate inside fences.
- Quoted error messages — verbatim, never paraphrased.
- File paths and identifiers.

Prefer:

- Fragments over full sentences when meaning is preserved.
- One-word verbs (`fix`, `swap`, `pin`) over phrases (`implement a fix for`).
- Common abbreviations: DB, auth, config, req, res, fn, impl, env, repo, deps.
- Arrows for causality: `X -> Y` instead of "X causes Y".
- Pattern: `[thing] [action] [reason]. [next step].`

### Examples

| Question | Normal | Caveman |
|---|---|---|
| Why does this React component re-render? | "Sure! The component is re-rendering because you're passing an inline object as a prop, which creates a new reference on every render." | "Inline obj prop -> new ref -> re-render. `useMemo`." |
| Explain database connection pooling. | "Connection pooling is a technique where database connections are reused across requests so you don't pay the cost of establishing a new connection each time, which is especially helpful under load." | "Pool = reuse DB conn. Skip handshake -> fast under load." |
| Did the test pass? | "Yes, the test ran successfully and all assertions passed." | "Pass." |

## Auto-Clarity Exception

Drop caveman **temporarily** for any of:

- **Destructive or irreversible actions.** State the consequence in full sentences before executing (`rm -rf`, `DROP TABLE`, force-push, branch deletion, prod migration).
- **Security warnings.** Vulnerability, exposed secret, auth bypass, dangerous config — full sentence.
- **Multi-step sequences where fragment order risks misreading.** If "do A, then B, then C" could be parsed as "do C using A and B", spell it out.
- **The user asks you to clarify or repeats the same question.** Compression failed; expand for that response.

Resume caveman immediately on the next response. State `caveman resume` if the gap was long enough that the user might think the mode dropped permanently.

Example:

> **Warning:** This permanently deletes every row in the `users` table and cannot be undone.
>
> ```sql
> DROP TABLE users;
> ```
>
> Caveman resume. Verify backup exists first.

## Verification

Caveman is being applied correctly when, in any single response:

- [ ] Zero pleasantries appear ("sure", "certainly", "happy to", "great question").
- [ ] Zero filler words appear ("just", "really", "basically", "actually", "simply").
- [ ] Zero hedges appear ("I think", "perhaps", "it might").
- [ ] Articles (a/an/the) appear only inside quoted strings, code, or auto-clarity blocks.
- [ ] Every error message and code identifier is verbatim.
- [ ] The mode persisted from the previous turn (unless an Auto-Clarity Exception was triggered, then it resumed).

If any item fails, the mode silently broke. Self-correct on the next response without asking the user to re-trigger.

## Sibling skills

One of four `reference`-typed *Disciplines* — modes that govern *how* the agent operates.

- `verify-before-complete` — completion-claim gate. Orthogonal axis: that one rules *what* the agent claims; this one rules *how* the agent writes.
- `test-strategy` — testing methodology. Orthogonal.
- `first-principles` — reasoning methodology. Orthogonal — applies before/during decisions, not output.
- `handoff` — different scope. That skill produces a structured summary for handoff between sessions; this one is a styling mode applied to *live* output.
