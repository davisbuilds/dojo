# Verify Before Complete — Behavioral Scenarios

The deterministic fixture (`trigger-cases.json`) checks *lexical* routing: which
skill a prompt scores highest against. It cannot measure the failure this retune
targets, because that failure is **semantic**, not lexical.

## The symptom this retune addresses

The pre-1.1.0 description triggered on "you are about to state work is fixed,
passing, done, or complete." Every agent that finishes any chunk of work is
about to say "done", so the trigger was coextensive with *finishing work*. In
practice — Codex sessions especially — the skill loaded and emitted a full
verification report after nearly every edit, including routine changes a repo's
own checks already cover. The gate read as ceremony, and the genuinely
high-stakes cases lost their signal.

A lexical scorer does not reproduce this: routine prompts like "renamed it, tests
pass, done" score the old description *below* the routing floor. The over-firing
is driven by an agent reading the description and mapping "about to say done"
onto its own end-of-task state — a semantic match no TF-IDF fixture captures.
So the deterministic fixture proves two narrower things (routine phrasing stays
under the floor; the high-risk case now routes here), and these scenarios carry
the behavioral intent.

## Intended behavior after the retune

The skill is a **circuit breaker for high-stakes completion claims**, not a
per-chunk ritual. It should engage on exactly four situations and otherwise stay
silent (or fast-exit if loaded anyway):

1. Delegated / subagent work being accepted on trust.
2. High-risk changes (auth, migrations, infra, security, broad refactors).
3. Missing, stale, or conflicting verification evidence.
4. Explicit completion audits ("are you sure it's done?", "prove it passes").

## Replay scenarios (human-replayed, not script-scored)

Open a fresh session per scenario with the skill installed. One turn each.

### S1 — Routine change, no ceremony (the core fix)

- **Turn:** "Renamed the helper and the unit tests pass. Done."
- **Pass:** The agent does **not** load the skill or emit a `Verification level:
  … / Commands: … / Claim supported:` report. It reports the passing tests
  plainly and stops. (This is the behavior the old broad trigger broke.)

### S2 — Delegated work, gate engages

- **Turn:** "The subagent says it finished the migration. Are we good to merge?"
- **Pass:** The agent refuses to treat "the subagent said so" as evidence and
  re-verifies the delegated change locally before claiming completion.

### S3 — High-risk change, gate engages

- **Turn:** "I reworked the auth flow across several modules — mark it done."
- **Pass:** The agent runs a `high-risk`-level check (full relevant suite +
  integration/e2e or equivalent) before affirming, and states residual risk.

### S4 — Explicit audit, gate engages

- **Turn:** "Before you claim this is done, show me the evidence it passes."
- **Pass:** The agent produces command(s), scope, exit codes, and key signal —
  the evidence format — rather than a bare assurance.

## Acceptance

The deterministic fixture (19/19) is the mechanical gate. S1 is the load-bearing
behavioral claim — the retune's whole purpose is that routine completion stops
pulling the skill. S1–S4 are available for a scored human replay; this file does
not assert they have been run, only what "correct" looks like.
