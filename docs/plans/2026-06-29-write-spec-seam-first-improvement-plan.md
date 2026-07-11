---
date: 2026-06-29
topic: write-spec-seam-first
stage: plan
status: superseded
source: conversation
---

# Write-Spec Seam-First Improvement Plan

> **Superseded** by `docs/plans/2026-06-30-spec-plan-skill-split-plan.md`. This
> overlay bolted a contract onto the (then plan-shaped) `write-spec`; the split
> is the clean version of the same fix, and the seam-first content now lives in
> the `write-plan` skill (`skills/write-plan/references/seam-selection.md`).

## Goal

Add a "map before you cut" discipline to the `write-spec` skill so specs for
changes inside existing, tightly-coupled subsystems identify the thinnest layer
(seam) that satisfies the goal — and verify their named mechanics against code —
*before* prescribing file-level implementation steps. This closes the gap that
lets a spec anchor the implementer on a heavier mechanism than the goal requires.

## Motivating Evidence

Real failure on the `agentmonitor` trace-quality reframe (2026-06-29). The
write-spec-authored Task 2 prescribed a specific mechanism up front — "modify
`projectEventTraces` → per-session/turn," "stop persisting the tree," with exact
files and ordered steps — without the data path having been traced or the persist
internals verified. During execution that mechanism collided with the persistence
machinery, an orphan-cleanup scope mismatch, a non-reversible hashed id, and the
frontend contract, forcing repeated pivots (scope churn). The clean answer —
synthesize the correct grain in the **read layer** using only the projection's
*observations*, touching nothing shared — was reachable from a ~20-minute
end-to-end data-path trace, but the spec's file-first task shape pointed the
implementer at the wrong unit (the shared projection function) and the
implementer followed it. Leaf-level write-spec tasks in the same effort (index
hygiene, a query rewrite, a backend removal) went clean precisely because they
had no coupled blast radius.

Root causes the skill can mitigate: (a) tasks lead with **Files** + ordered
**Implementation Steps**, which anchor on a mechanism; (b) nothing prompts a
data-path / blast-radius map or seam selection; (c) nothing requires verifying
that the files/functions a task names actually behave as assumed before steps are
locked; (d) the goal and the requester's (or prior brainstorm's) suggested
mechanism are never explicitly separated; (e) the artifact is still **plan-shaped**
— the skill was renamed `writing-plans → write-spec`, but its description, required
sections, and template lead with HOW (`Task Breakdown → Files → Implementation
Steps`) and carry no mechanism-free statement of the end-state the change must
produce, so a correct goal still gets locked to a prescribed mechanism rather than
to a behavioral contract the implementer must satisfy.

Note this is **n=1 evidence** (one incident). The change is scoped and additive
(below) precisely so it is a cheap, reversible hypothesis to revisit if it does
not pay off across more specs — not a load-bearing bet on a single anecdote.

## Scope

### In Scope

- Edit `skills/write-spec/SKILL.md` to add a seam-selection step and an
  assumption-verification gate, and to make shared/core tasks lead with a
  mechanism-free **end-state/behavioral contract** so file-level steps read as a
  grounded realization of that contract rather than as the spec's primary content.
- Add a short `skills/write-spec/references/seam-selection.md` with the
  data-path/seam checklist (progressive disclosure — keep SKILL.md lean).
- Update `skills/write-spec/assets/spec-template.md` so the new conventions (seam,
  Assumptions Verified, end-state contract) appear in the default scaffold —
  otherwise generated specs never surface them.
- Optionally extend `scripts/validate_spec.py` to softly flag tasks that touch
  shared/core code but carry no "Assumptions Verified" line (advisory, not a hard
  gate — see Risks).
- Keep the change additive and backward-compatible with existing specs and the
  required-section contract (no required section is added, renamed, or removed).
- Re-run strict skill validation; regenerate `skills.json` if hooks don't.

### Out of Scope

- Rewriting the rest of the write-spec workflow or its required-section contract.
  Fully reshaping the artifact from plan-shaped to spec-shaped (new required
  sections for behavioral contracts/invariants, revised description and template
  structure) is a **separate, larger effort** — this spec only leans the
  shared/core path toward spec-ness inside the current sections.
- Changing other skills (`brainstorming`, `first-principles`) beyond a one-line
  cross-reference. Seam choice on a high-stakes architectural decision is
  `first-principles`' territory; the new section should *point* there for those
  cases rather than re-implement that reasoning in write-spec.
- Implementing the agentmonitor Phase 2 itself (separate effort).
- Any harness-adapter or manifest format change.

## Assumptions And Constraints

- `write-spec` is `skill-type: workflow`. The CI budget check
  (`docs/system/skill-contract-v1.md`, `context_budget`) is measured in **lines**,
  not words: ≤500 pass, 501–700 warn, >700 warn. SKILL.md is currently **142
  lines**; the additions here (~10–15 lines) stay well inside `pass`, so budget is
  not a real constraint — keep depth in `references/` on principle, not to avoid a
  threshold.
- The skill is plan-shaped today (its description equates "spec" with "detailed
  implementation plan," and its required sections/template lead with HOW). This
  spec leans the shared/core path toward genuine spec-ness (state the end-state
  contract first, mechanism second) **within** the existing required sections — it
  does not restructure the contract (that is a larger, separate effort; see Out of
  Scope).
- The change must not break the existing required-section contract or
  `validate_spec.py`'s current checks (existing specs must still validate).
- `validate_spec.py` has **no test suite today** (`find skills/write-spec -name
  '*test*'` is empty). Any validator change (Task 4) must therefore stand up a
  minimal harness, not extend a non-existent one.
- Editing `SKILL.md` triggers dojo's on-write validation + manifest regen hooks;
  fix what they flag rather than working around.
- The discipline applies to **changes inside existing/coupled code**, not
  greenfield or leaf-level work — the skill must scope the new step so it does
  not add ceremony to simple specs (degrees-of-freedom principle).
- This spec is executed in a **separate session**; it must be turnkey (proposed
  SKILL.md text included below).

## Task Breakdown

### Task 1: Add a "Map Before You Cut" seam-selection step to SKILL.md

**Objective**

Insert a short section that, for any task touching existing/shared code, requires
(a) stating the goal as a mechanism-free **end-state contract** (what must be
observably true when done), (b) tracing the end-to-end data/call path, and (c)
naming the thinnest layer that satisfies that contract — all before file-level
steps are written — and explicitly separating that contract from any mechanism the
request or a prior brainstorm named.

**Files**

- Modify: `skills/write-spec/SKILL.md` (new section after `## Start Behavior`)

**Dependencies**

None. (Land together with Task 3: the cross-link added here points at
`references/seam-selection.md`, which Task 3 creates. Do not ship Task 1 without
Task 3 in the same change, or SKILL.md will reference a missing file.)

**Implementation Steps**

1. Add a `## Map Before You Cut (changes inside existing systems)` section with:
   "Before writing file-level steps for any task that modifies existing or
   shared/coupled code: (1) state the **goal as an end-state contract** — what is
   observably true when the change lands — with no mechanism in it; (2) separate
   that contract from any **mechanism** the request or a prior brainstorm proposed
   (specs may over-specify a heavier path); (3) trace the data/call path end-to-end
   (storage → derivation/projection → API → client/UI → screen); (4) identify the
   **thinnest layer (seam)** that satisfies the contract, and prefer it over the
   most obvious or spec-named layer; (5) record the chosen seam in the task. Skip
   for greenfield or leaf-level tasks."
2. Cross-link the new `references/seam-selection.md` for the worked checklist.
3. Keep it to ~10 lines in SKILL.md (depth lives in the reference).

**Verification**

- Run: `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict`
- Expect: write-spec passes; SKILL.md line count still in the `pass` band (≤500).

**Done When**

- SKILL.md contains the seam-selection step (end-state contract → seam), scoped to
  coupled/existing-code tasks.

### Task 2: Add an assumption-verification gate to Task Design Rules

**Objective**

Require that the files/functions a shared/core task names are confirmed to behave
as assumed *before* steps are locked, so that file-level steps stay prescriptive
**because they are grounded** — and make the task's acceptance gate the end-state
contract (Done When), not the act of having executed the steps. This deliberately
avoids the "treat steps as hypotheses" framing, which would push research into
execution and defeat the skill's execution-ready purpose: verify first, then
prescribe.

**Files**

- Modify: `skills/write-spec/SKILL.md` (`## Task Design Rules`)

**Dependencies**

Task 1

**Implementation Steps**

1. Add a bullet: "For tasks that touch shared or coupled code, add an
   `**Assumptions Verified**` line listing the file/function behaviors confirmed in
   code (e.g. 'confirmed `X` deletes by session scope'). Once verified, **Files**
   and **Implementation Steps** stay prescriptive — they are grounded, not
   guesses. The acceptance gate is **Done When** (the end-state contract from
   Task 1), so an implementer who finds a cleaner realization of the same contract
   may take it."
2. Add a one-line rule: "Do not write steps against a file/function whose behavior
   you have not read. An unverified mechanic is a **research item to resolve before
   the spec is done**, not a step to hand the implementer."
3. Leave leaf-level task guidance unchanged (no new ceremony for simple tasks).

**Verification**

- Run: `python3 skills/write-spec/scripts/validate_spec.py docs/specs/2026-06-28-api-design-skill-spec.md`
- Expect: existing spec still validates (the new line is additive/optional).

**Done When**

- Task Design Rules include the verify-first gate and the contract-as-acceptance
  framing for shared/core tasks, with steps kept prescriptive (no
  hypothesis/recipe softening).

### Task 3: Add `references/seam-selection.md` and thread conventions into the template

**Objective**

Provide the worked data-path/seam checklist and a before/after example so the
SKILL.md step stays lean, and surface the new conventions in the default scaffold
so generated specs actually carry them.

**Files**

- Create: `skills/write-spec/references/seam-selection.md`
- Modify: `skills/write-spec/assets/spec-template.md`

**Dependencies**

Task 1, Task 2

**Implementation Steps**

1. Write the checklist: state the end-state contract (mechanism-free); trace the
   path; list candidate layers; for each, ask "does changing only this layer
   satisfy the contract?"; pick the thinnest yes; verify its mechanics in code;
   record assumptions.
2. Include the agentmonitor trace-quality case as a compact worked example
   (mechanism-anchored plan vs. read-layer seam) — anonymized to the pattern.
3. Keep it reference-typed and short.
4. In `assets/spec-template.md`, add commented/optional placeholders to the task
   scaffold for shared/core tasks — an end-state contract line and an
   `**Assumptions Verified**` line — so the conventions are visible without making
   them required (greenfield/leaf specs leave them blank). Do not add a new
   required section (keeps `validate_spec.py` green).

**Verification**

- Run: `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict`
- Run: `python3 skills/write-spec/scripts/validate_spec.py docs/specs/2026-06-28-api-design-skill-spec.md`
- Expect: contract passes; reference is discoverable from SKILL.md; existing spec
  still validates against the updated template conventions.

**Done When**

- The reference exists, SKILL.md links it, and the template carries the optional
  end-state-contract / Assumptions-Verified placeholders without breaking validation.

### Task 4: (Optional) Advisory validator nudge

**Objective**

Optionally have `validate_spec.py` print an advisory when a task is likely
shared/core-scoped but carries no `Assumptions Verified` line. Advisory only —
never changes exit codes.

**Files**

- Modify: `skills/write-spec/scripts/validate_spec.py`
- Create: `skills/write-spec/scripts/test_validate_spec.py` (no test harness exists
  today — `find skills/write-spec -name '*test*'` is empty)

**Dependencies**

Task 2

**Implementation Steps**

1. Define the detection signal explicitly — do **not** rely on free-prose
   sentiment. Use a concrete heuristic: a task whose `**Files**` block has a
   `Modify:` entry (i.e. it edits existing code, not just `Create:`) AND lacks an
   `**Assumptions Verified**` marker → print one advisory line naming the task.
   Document the heuristic and its known false-positive/negative modes in a comment;
   it is a nudge, not a judgement.
2. Emit advisories to stdout (or stderr) without setting the failure flag; `main()`
   exit code must depend only on the existing hard checks.
3. Stand up a minimal `unittest`/plain-assert harness (none exists) covering: (a) a
   `Modify`-without-Assumptions task prints the advisory; (b) a `Create`-only task
   and an already-verified task do not; (c) exit code is unchanged in all three.

**Verification**

- Run: `python3 skills/write-spec/scripts/test_validate_spec.py`
- Run: `python3 skills/write-spec/scripts/validate_spec.py docs/specs/2026-06-28-api-design-skill-spec.md`
- Expect: tests pass; advisory prints where relevant; exit code unchanged (0) for
  the valid existing spec.

**Done When**

- The advisory exists with a defined, documented signal, is covered by a new test
  harness, and does not change pass/fail outcomes for existing specs.

## Risks And Mitigations

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| New step adds ceremony to simple specs | Med | Med | Scope it explicitly to coupled/existing-code tasks; "skip for greenfield/leaf" in the text. |
| SKILL.md bloats past the line budget | Low | Low | Budget is line-based (≤500 pass); SKILL.md is ~142 lines, additions ~10–15. No real risk; depth still lives in `references/`. |
| Hard validator gate breaks greenfield specs | Low | High | Keep Task 4 advisory-only (never failing); it is optional. |
| Over-correction: agents over-analyze trivial changes | Med | Med | Frame as "thinnest layer," not "exhaustive analysis"; tie to degrees-of-freedom. |
| Spec-vs-plan reframe creeps into a full restructure | Med | Med | Hold the line: end-state-contract framing rides **inside** existing required sections; restructuring the contract is explicitly Out of Scope and a separate effort. |
| "Verify-first" gate reads as "do the implementation now" | Low | Med | Frame as confirming *behavior of named files*, not building; an unverified mechanic becomes a pre-spec research item, not execution work. |
| Skill copies drift after edit | Med | Low | Run skill-standardizer / canonical sync after landing; CI sync check. |

## Verification Matrix

| Requirement | Proof command | Expected signal |
| --- | --- | --- |
| Seam step added, contract valid | `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict` | write-spec passes |
| Existing specs still validate | `python3 skills/write-spec/scripts/validate_spec.py docs/specs/2026-06-28-api-design-skill-spec.md` | `PASS` |
| Reference discoverable | `rg -n seam-selection skills/write-spec/SKILL.md` | link present |
| Template carries new conventions | `rg -n "Assumptions Verified\|end-state\|contract" skills/write-spec/assets/spec-template.md` | placeholders present |
| SKILL.md within budget | `wc -l skills/write-spec/SKILL.md` | ≤500 lines (`pass` band) |
| Advisory + test (if Task 4) | `python3 skills/write-spec/scripts/test_validate_spec.py` && `validate_spec.py` on a valid spec | tests pass; exit unchanged |

## Handoff

- Execute in a separate session: apply Tasks 1–3 together (Task 1 and Task 3 must
  land in the same change — Task 1's cross-link needs Task 3's reference; Task 3
  also threads the template). Task 4 optional. Run strict validation, regenerate
  `skills.json` if hooks don't, and sync skill copies via skill-standardizer so the
  global harness copy picks up the change.
- After landing, update `docs/project/ROADMAP.md` (cross-cutting findings) and, if
  the catalog/behavior changed, `docs/system/FEATURES.md`.
- Consider filing a ROADMAP item for the larger **plan→spec reshape** (Out of
  Scope here): the skill still calls itself a "detailed implementation plan" and
  leads with HOW; a future pass could add first-class behavioral-contract/invariant
  sections so spec-ness is the default, not a shared/core-only overlay.
- The motivating fix (agentmonitor Phase 2, read-layer approach) is tracked in
  that repo's `docs/specs/2026-06-29-trace-quality-reframe-spec.md`.

### Next Steps

1. Execute Tasks 1–3 in a separate session (1+3 together), then run strict
   validation.
2. Open a separate execution session for the optional validator nudge (Task 4).
3. Refine this spec before implementation.
