---
name: write-plan
description: 'Sequence the build: turn a settled target (a `write-spec` contract, a ticket, or a clear request) into an execution plan — task breakdown, files, ordered steps, seam selection, and verification commands. Use when WHAT is already decided and you need HOW: the file-level, dependency-ordered steps to implement it. If the target is not yet falsifiable, route back to `write-spec`.'
skill-type: workflow
---

# Write Plan

Turn a settled target into an execution plan a zero-context engineer can follow:
task breakdown, exact files, ordered steps, and verification commands. The plan is
held to a contract — its acceptance gate is the spec's end-state, not the steps it
happens to list.

## When To Use

Use this skill when:
- WHAT is already decided (a `write-spec` contract exists, or the request is clear)
  and you need HOW
- the work spans multiple files or phases and needs ordered, verifiable steps
- explicit verification gates are needed before coding

Skip this skill when:
- the target is not yet falsifiable → route back to `write-spec` first
- the change is a tiny mechanical edit
- requirements are still ambiguous → `brainstorming` first

## Input

Prefer to plan against a contract:
- If `docs/specs/YYYY-MM-DD-<topic>-spec.md` exists, plan against it and reuse its
  topic slug. `## Goal` restates/links that contract; every `Done When` traces to
  the contract's end-state.
- If no contract exists and the work is non-trivial or touches coupled code, route
  back to `write-spec` to pin the target first.
- For a small, clear, self-contained request, proceed directly.

## Start Behavior

Start with:
`I'm using the write-plan skill to sequence the build.`

If key context is missing, ask focused questions before writing:
- the target/contract and its acceptance criteria
- constraints and non-goals
- affected files or systems (if known)

## Output Path

Save the plan to:
`docs/plans/YYYY-MM-DD-<topic>-plan.md`

## Output Contract

Every plan must include YAML frontmatter and the required sections below.

### Required Frontmatter

```yaml
---
date: YYYY-MM-DD
topic: <kebab-case-topic>
stage: plan
status: draft
source: conversation
---
```

`status:` is born `draft` and follows the lifecycle `draft → in-progress →
complete` (terminal synonyms: `shipped`, `implemented`, `superseded`). Update it
honestly as the work lands so a reader — or any lifecycle tooling — can tell a
live plan from a finished one.

### Required Sections

1. `# <Title> Plan`
2. `## Goal` (restates/links the spec contract)
3. `## Scope`
4. `## Assumptions And Constraints`
5. `## Task Breakdown`
6. `## Risks And Mitigations`
7. `## Verification Matrix`
8. `## Handoff`

Add `## Map Before You Cut` (below) whenever a task touches existing or coupled
code — strongly recommended, and included in the template. Use
`assets/plan-template.md` as the default scaffold.

## Map Before You Cut

Before prescribing steps for any task that touches existing or coupled code, trace
the ground first — do not pick a mechanism blind:

1. **Trace the data/call path** the change rides on (who calls what, what state
   flows where). Read the code; don't assume.
2. **Pick the thinnest seam** that satisfies the contract — the smallest cut that
   makes the end-state true. A cleaner realization than the contract author
   imagined is allowed, as long as `Done When` still equals the contract.
3. **Record an `**Assumptions Verified**` line** per coupled task: what you
   confirmed in the code that makes the chosen seam correct (file:line, observed
   behavior). Steps stay prescriptive *because they are grounded* — verify first,
   then prescribe; don't ship guesses as steps.

See `references/seam-selection.md` for the worked checklist and a before/after.

## Task Design Rules

Each task must be independently verifiable and include:
- `### Task N: <name>`
- `**Objective**`
- `**Files**` with exact repository paths
- `**Dependencies**` (or `None`)
- `**Implementation Steps**` as ordered steps
- `**Verification**` commands with expected signals
- `**Done When**` acceptance bullets that trace to the contract

Granularity target:
- one meaningful unit of behavior per task
- usually 10-30 minutes of focused work
- avoid over-fragmented 2-minute steps unless risk demands it

## Verification Requirements

- Include at least one concrete, deterministic verification command per task.
- Include integration or end-to-end verification when applicable.
- Add negative-path verification for risky logic.
- Do not claim plan readiness until verification coverage is explicit.

If available, apply the mindset from `verify-before-complete` when checking final
plan quality.

## Plan Validation

After writing a plan, run:

```bash
python3 skills/write-plan/scripts/validate_plan.py docs/plans/<filename>.md
```

Fix all reported issues before handoff.

## Handoff

End with:
`Plan complete and saved to docs/plans/<filename>.md.`

Then offer:
1. Execute in this session, task by task.
2. **Review the plan with a critique subagent.** If the harness supports subagents
   (e.g. a Task/agent tool), launch one seeded with the plan's path, the spec
   contract, **and** the originating context, instructed to critique the *plan* —
   is the chosen seam the thinnest that satisfies the contract? are the
   `Assumptions Verified` actually grounded in code? are steps
   prescriptive-because-verified (not guesses)? is the blast radius mapped? are
   verification commands real and deterministic? are tasks over-fragmented? — and
   to propose improvements. Apply or discuss before executing. If subagents are
   unavailable, run the same critique inline via `verify-before-complete`.
3. Open a separate execution session, or refine the plan first.

## Command Wrapper

If command files are supported, use `commands/workflows/plan.md` as the canonical
`/workflows:plan` wrapper.

## Sibling skills

Pre-execution pipeline: **brainstorm → spec → plan**
(`docs/design/` → `docs/specs/` → `docs/plans/`).

- `write-spec` — upstream. Owns the falsifiable contract (the WHAT). Plan against
  it; route back if the target isn't yet falsifiable.
- `brainstorming` — further upstream. Clarifies WHAT + chosen direction when the
  request is ambiguous.
- `deep-research` — parallel. Use when steps need grounded references (library
  behavior, API contracts, current docs).
- `first-principles` — upstream for plans that hinge on a non-obvious
  architectural decision.
