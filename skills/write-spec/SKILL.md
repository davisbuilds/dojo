---
name: write-spec
description: 'Define the target before building: write a falsifiable contract — problem, end-state, success criteria, evaluation — that states WHAT must be true, with no files or implementation steps. Use when you need to specify or align on what "done" means before sequencing work, or are handed a feature/change and must pin its acceptance criteria. Hand off to `write-plan` for the HOW.'
skill-type: workflow
version: 2.0.0
---

# Write Spec

A spec is a **contract**, not a plan. It states the target — the mechanism-free
end-state a change must satisfy — so a zero-context engineer (or a later
`write-plan` pass) can choose *how* to build it and prove *when* it is done.

The contract adopts the four pieces of a product spec, translated to the
engineering register: **problem, bet, success criteria, evaluation**. The "bet"
is not a KPI — it is a **deterministic verification command** that makes the
end-state falsifiable.

## When To Use

Use this skill when:
- you need to pin what "done" means before sequencing any work
- you are handed a feature, ticket, or change and must fix its acceptance criteria
- a brainstorm settled on a direction and it now needs a falsifiable target

Skip this skill when:
- WHAT is already falsifiable and you just need the build sequence → `write-plan`
- the change is a tiny mechanical edit
- requirements are still ambiguous → `brainstorming` first

## The Contract Discipline

State **what must be true**, never **how to build it**.

- No file paths, task breakdowns, or ordered implementation steps — those belong
  to `write-plan`. (The validator rejects them; this is structural, not advice.)
- Every contract must be **falsifiable**: name the observable behavior and the
  deterministic command/check that proves it.
- Keep mechanism out so the plan is free to pick the thinnest seam that satisfies
  the contract.

## Start Behavior

Start with:
`I'm using the write-spec skill to write the contract.`

If key context is missing, ask focused questions before writing:
- who is hurting and what they do today (the problem)
- the observable end-state that defines success
- how it will be verified (the falsifiable check)
- hard constraints and non-goals

## Decision Readiness

Before drafting, reduce preventable uncertainty without pretending every unknown
can be discovered:

1. **Resolve what is answerable now.** Read the relevant project, docs, and
   existing behavior; use research when facts are missing. Do not ask the user
   to answer a repository lookup the agent can perform.
2. **Work with the user on contract decisions.** Ask focused questions when an
   answer changes observable behavior, scope, success criteria, safety
   boundaries, or the verification claim. Resolve as many as possible before
   writing the contract.
3. **Stress-test proportionately.** For non-trivial or risky work, consider
   other consumers, bad/empty/old input, trust boundaries, dependency failure,
   and detection/containment. This is a lens, not an exhaustive checklist. Route
   high-stakes trade-offs to `first-principles` and missing evidence to
   `deep-research`.
4. **Classify what remains.** A blocking decision changes the current contract
   and must close before `write-plan`. An irreducible future uncertainty that
   does not change the contract belongs in Assumptions And Constraints with its
   signal and containment. A future choice belongs in Out of Scope, not Open
   Questions. Write `None` when all current-contract decisions are settled.

See `references/uncertainty-triage.md` for compact prompts and examples. The
spec records decisions and bounded uncertainty, not a transcript of every
question asked.

<!-- INCLUDE: risk-profile-gate -->
<!-- AUTO-GENERATED from skills/_fragments/risk-profile-gate.md — do not edit -->
## Risk Profile Gate

Classify each new artifact before drafting:

- `routine` — the default; keep the normal template and validation path lean.
- `high` — use when credentials or privilege separation, remote/destructive
  effects, cross-system state agreement, retries/concurrency/queues, executable
  untrusted input, external policy decisions, or persisted-state migration can
  make a plausible-looking artifact unsafe or infeasible.

Record `risk_profile: routine|high` and `readiness: draft|ready` separately from
delivery `status`. Legacy artifacts without these fields remain routine/draft.
For `high`, load this skill's high-risk reference and addendum; do not add those
sections to routine work. Reclassify when repository evidence reveals a trigger.
<!-- /INCLUDE: risk-profile-gate -->

## Output Path

Save the contract to:
`docs/specs/YYYY-MM-DD-<topic>-spec.md`

If a design summary exists at `docs/design/YYYY-MM-DD-<topic>-design.md`, reuse its
topic slug.

## Output Contract

Every spec must include YAML frontmatter and the required sections below.

### Required Frontmatter

```yaml
---
date: YYYY-MM-DD
topic: <kebab-case-topic>
stage: spec
status: draft
source: conversation
risk_profile: routine
readiness: draft
---
```

`status:` is born `draft` and follows the lifecycle `draft → in-progress →
complete` (terminal synonyms: `shipped`, `implemented`, `superseded`). Update it
honestly as the work lands so a reader — or any lifecycle tooling — can tell a
live contract from a finished one.

### Required Sections

1. `# <Title> Spec`
2. `## Problem` — who is hurting, what they do today, why now.
3. `## Contract` — the falsifiable end-state: "when this ships, *[observable
   behavior]* holds, verified by *[deterministic command/check]*." Name at least
   one verification command (an inline `` `code` `` span). This is the translated
   bet: the metric is a command, not a KPI.
4. `## Success Criteria` — concrete behaviors visible when it works.
5. `## Evaluation` — how it is measured. Add kill/scale/graduate thresholds
   **only when the work is an actual product or experiment bet** (gate with a
   one-line "if this is a measurable bet…"); omit them for mechanical/system specs.
6. `## Scope` — in/out of scope (still mechanism-free: name outcomes, not files).
7. `## Assumptions And Constraints`
8. `## Open Questions` — `None` when ready to plan. Any retained question must
   be non-blocking and state why it cannot change the current contract.
9. `## Handoff` — route to `write-plan` for the HOW.

Use `assets/spec-template.md` as the default scaffold.

For `risk_profile: high`, also use `assets/high-risk-spec-addendum.md` and follow
`references/high-risk-contract.md`. High-risk contracts add stable success
criterion and evaluation-scenario IDs, observable authority/safety outcomes, and
a readiness review while remaining mechanism-free.

## Verification Requirements

- The `## Contract` must name at least one concrete verification command or check.
- Prefer deterministic checks (a command with an observable pass/fail signal) over
  prose assertions.
- Confirm the stated check can prove the contract's outcome. Test-file placement
  and runner discovery are plan-level details; `write-plan` verifies those when
  tests change.
- Do not claim the contract is ready until the end-state is falsifiable.
- For high-risk contracts, do not set `readiness: ready` or announce completion
  until deterministic validation passes, adversarial critique findings are
  revised, and a closure critique confirms no blocking finding remains.

If available, apply the mindset from `verify-before-complete` when checking final
contract quality.

## Conditional Coordination

Route to another skill only when needed:
- requirements unclear: use `brainstorming`
- architectural trade-off dominates risk: use `first-principles`
- evidence/prior art needed for the contract: use `deep-research`
- ready to sequence the build with no contract-affecting question open: hand off
  to `write-plan`

If a named skill is unavailable, continue with manual fallback in this skill.

## Spec Validation

After writing a contract, run:

```bash
python3 skills/write-spec/scripts/validate_spec.py docs/specs/<filename>.md
```

Fix all reported issues before handoff. The validator fails the contract if any
plan-shaped content (task breakdowns, file lists, implementation steps) leaked
in. For high-risk contracts it also enforces the conditional addendum, stable ID
classes, and structural review closure. Decision readiness and semantic safety
remain human/agent reasoning gates, not brittle prose heuristics.

## Handoff

End with:
`Contract complete and saved to docs/specs/<filename>.md.`

Use that completion line immediately for routine contracts after validation. For
high-risk contracts, keep `readiness: draft` through deterministic validation,
adversarial critique, revision, and closure critique; use the completion line
only after `readiness: ready` validates.

Before offering a plan handoff, confirm that `Open Questions` is `None` or that
any retained item is explicitly non-blocking. Return to decision readiness if it
would change scope, success criteria, or verification.

For high-risk contracts, run the required critic described in
`references/high-risk-contract.md` before handoff. Use a critique subagent when
the harness supports and authorizes one; otherwise run the same critique inline.
For routine contracts, critique remains optional.

Then offer:
1. Hand off to `write-plan` to sequence the build against this contract.
2. Review or refine a routine contract before sequencing.

## Command Wrapper

If command files are supported, use `commands/workflows/spec.md` as the canonical
`/workflows:spec` wrapper.

## Resources

- `references/uncertainty-triage.md` — classify uncertainty, work through
  proportionate unknown-unknown lenses, and keep contracts ready for planning.
- `references/high-risk-contract.md` — conditional authority, invariant,
  scenario-ID, and critique-closure protocol.
- `assets/high-risk-spec-addendum.md` — conditional scaffold for high-risk
  contracts; do not copy it into routine specs.

## Sibling skills

Pre-execution pipeline: **brainstorm → spec → plan**
(`docs/design/` → `docs/specs/` → `docs/plans/`).

- `brainstorming` — upstream. Clarifies WHAT + chosen direction; come here to make
  that direction a falsifiable contract.
- `write-plan` — downstream. Sequences the build (tasks, files, steps) against
  this contract. Hand off once the target is falsifiable.
- `first-principles` — upstream for high-stakes contracts that hinge on a
  non-obvious architectural decision.
- `deep-research` — parallel. Use when the contract needs evidence (library
  behavior, prior art, current docs).
