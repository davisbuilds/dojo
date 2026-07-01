---
date: 2026-06-30
topic: spec-plan-skill-split
stage: plan
status: complete
source: conversation
---

# Spec/Plan Skill Split Plan

## Goal

Split the conflated `write-spec` skill into a **two-skill pipeline** that matches
the three real artifacts in the pre-execution chain, and fix the inverted
directory naming that currently muddles them:

- **`write-spec`** (repurposed → *layer 2, the contract*): states the
  mechanism-free end-state — problem, falsifiable contract, success criteria,
  evaluation — that the change must satisfy. Output: `docs/specs/<…>-spec.md`.
- **`write-plan`** (new → *layer 3, the execution*): maps that contract onto the
  thinnest seam and sequences the build — task breakdown, files, ordered steps,
  verification. Output: `docs/plans/<…>-plan.md`.
- **`brainstorming`** (*layer 1, the design*, unchanged in purpose) moves its
  output from `docs/plans/` to `docs/design/` so the directory namespace it
  vacates can hold actual implementation plans.

Net pipeline, with names that finally match their directories:
**`brainstorm` (`docs/design/`) → `spec` (`docs/specs/`) → `plan` (`docs/plans/`)**.

This makes spec-ness structural rather than an overlay: because `Files`/`Steps`
can only live in the *plan*, the *spec* is forced mechanism-free — which is the
clean fix for the seam-first failure that motivated the superseded overlay spec.

## Motivating Evidence

Two grounded findings:

1. **The rename was cosmetic.** `writing-plans → write-spec` (commit `8668562`)
   moved files but kept the artifact plan-shaped: the description still reads
   "specs (detailed implementation plans)," the required sections lead with HOW
   (`Task Breakdown → Files → Implementation Steps`), and `validate_spec.py` still
   enforces the *plan* schema (it was `validate_plan.py` pre-rename). There is no
   mechanism-free statement of the target anywhere.

2. **Conflation caused real scope churn.** The agentmonitor trace-quality reframe
   (2026-06-29) failed because a plan-shaped artifact prescribed a heavy mechanism
   up front instead of stating the end-state and letting the seam be chosen. The
   overlay spec (`2026-06-29-write-spec-seam-first-improvement-spec.md`) patched
   this by bolting a contract line onto the plan skill. The split is the clean
   version of that same fix and **supersedes** the overlay.

Product-spec influence (Gokul Rajaram's four mandatory pieces — problem, bet,
success criteria, evaluation) is adopted in **translated** form (see Task 1):
the agent's "falsifiable bet" is a **deterministic verification command**, not a
product KPI, and the metric/threshold layer is gated to work that is an actual
product/experiment bet.

## Scope

### In Scope

- Repurpose `skills/write-spec/` into the **contract** skill: new SKILL.md
  (contract sections), new `validate_spec.py` (contract schema), new
  `spec-template.md`, updated command wrapper + `agents/openai.yaml`.
- Add `skills/write-plan/` as the **execution** skill: SKILL.md (with the
  seam-first "Map Before You Cut" + `Assumptions Verified` discipline folded in),
  `validate_plan.py` (the *current* `validate_spec.py` logic, moved), template,
  command wrapper, `agents/openai.yaml`.
- Wire hooks: repoint the spec hook to the contract validator; add a parallel
  plan hook for `docs/plans/<…>-plan.md`.
- Move `brainstorming` output `docs/plans/ → docs/design/` and update its refs.
- Update all sibling cross-references to the `brainstorm → spec → plan` chain.
- Reclassify legacy `docs/specs/*-spec.md` plan-shaped files (see Task 6) and mark
  the overlay spec `superseded`.
- Regenerate `skills.json` + catalog; update `docs/system/*` and `README.md`.
- Update **and rename** the cross-repo archive script (`../ops/scripts/`) to learn
  about `docs/design/` and fit the new workflow vocabulary (Task 8) — operator has
  authorized the cross-repo change.
- Add an agent-agnostic **review-subagent handoff option** to each artifact skill
  (`brainstorming`, `write-spec`, `write-plan`): launch a context-seeded subagent
  to critique the just-written artifact and propose improvements, with an inline
  `verify-before-complete` fallback where subagents are unavailable.

### Out of Scope

- Changing the brainstorming *discovery method* (one-question-at-a-time) — only its
  output path, summary shape, and routing change (Task 4).
- Retro-authoring contracts for already-shipped specs.
- Any harness-adapter/manifest *format* change (the manifest auto-discovers new
  skills; no format change needed).

## Assumptions And Constraints

- Both skills are `skill-type: workflow`; SKILL.md budget is **line-based**
  (`skill-contract-v1.md` `context_budget`: ≤500 pass). Keep each lean, push depth
  to `references/`.
- `docs/plans/` currently holds only `.gitkeep` (no real impl plans yet) and is
  semantically owned by `brainstorming`. Vacating it for `write-plan` requires
  moving brainstorming first (Task 4 precedes Task 2's hook wiring for plans).
- `docs/specs/` holds 3 legacy plan-shaped files. They validate under the *plan*
  schema, not the new *contract* schema; the contract hook would fail them if
  edited. Resolve by reclassifying/superseding (Task 6), not by weakening the
  validator.
- The manifest generator (`scripts/generate_skills_manifest.py`) and catalog
  (`scripts/gen_catalog.py`) auto-discover `skills/*/SKILL.md`; a new skill dir
  self-registers on regen. Both have tests (`tests/test_*`).
- Editing any `SKILL.md`/spec triggers dojo's on-write validation + manifest-regen
  hooks; fix what they flag rather than working around.
- This spec is itself plan-shaped (authored under the old skill). It is therefore
  migrated to `docs/plans/` in Task 6 (like the other plans) so it does not fail
  the new contract validator/hook that Task 1 installs over `docs/specs/`.

## Task Breakdown

### Task 1: Repurpose `write-spec` into the contract (layer-2) skill

**Objective**

Rewrite `write-spec` so it produces a mechanism-free contract, adopting Gokul's
four pieces translated to the engineering register, with `Files`/`Steps`/`Task
Breakdown` removed (those belong to `write-plan`).

**Files**

- Modify: `skills/write-spec/SKILL.md`
- Create: `skills/write-spec/scripts/validate_spec.py` (new contract schema —
  replaces the old plan-schema validator, whose logic moves to Task 2)
- Modify: `skills/write-spec/assets/spec-template.md`
- Modify: `skills/write-spec/commands/workflows/spec.md`
- Modify: `skills/write-spec/agents/openai.yaml`

**Dependencies**

None

**Implementation Steps**

1. Rewrite SKILL.md description + body so the artifact is a *contract*, not a
   plan. Use this **locked description** (the trigger; keep it disjoint from
   `write-plan`):
   > Define the target before building: write a falsifiable contract — problem,
   > end-state, success criteria, evaluation — that states WHAT must be true, with
   > no files or implementation steps. Use when you need to specify or align on
   > what "done" means before sequencing work, or are handed a feature/change and
   > must pin its acceptance criteria. Hand off to `write-plan` for the HOW.

   New required sections (the contract schema):
   - `## Problem` — who is hurting / what they do today / why now.
   - `## Contract` — the falsifiable end-state: "when this ships, *[observable
     behavior]* holds, verified by *[deterministic command/check]*." This is the
     translated "bet": the agent's metric is a verification command, not a KPI.
   - `## Success Criteria` — concrete behaviors visible when it works.
   - `## Evaluation` — how it is measured; **kill/scale/graduate thresholds only
     when the work is an actual product/experiment bet** (gate with a one-line
     "if this is a measurable bet…"; omit for mechanical/system specs).
   - `## Scope`, `## Assumptions And Constraints`, `## Open Questions`,
     `## Handoff` (→ route to `write-plan`).
2. Explicitly forbid mechanism in the spec: "No file paths, task breakdowns, or
   ordered implementation steps — those belong to `write-plan`. State *what must be
   true*, not *how to build it*."
3. Write the new `validate_spec.py` enforcing the contract schema (frontmatter
   `stage: spec`; the new required headings; a `Contract` section that contains at
   least one verification command). Reuse the parsing helpers from the old script.
4. Rewrite `spec-template.md` to the contract scaffold; update the command wrapper
   and `agents/openai.yaml` to describe contract authoring and the `→ write-plan`
   handoff.
5. Add a **review-subagent option** to the `## Handoff` numbered list (agent-
   agnostic, with fallback): "If the harness supports subagents (e.g. a Task/agent
   tool), launch a critique subagent seeded with the spec's path **and** the
   originating goal/context, instructed to critique the *contract* — is the
   end-state falsifiable? did any mechanism (files/steps) leak in? are success
   criteria concrete? is the evaluation gate right? is the problem real? — and to
   propose concrete improvements. Apply or discuss before handing off. If
   subagents are unavailable, run the same critique inline via
   `verify-before-complete`." Mirror the option into the command wrapper's flow.

**Verification**

- Run: `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict`
- Run: `python3 skills/write-spec/scripts/validate_spec.py skills/write-spec/assets/spec-template.md`
- Run: `rg -n "subagent" skills/write-spec/SKILL.md`
- Expect: write-spec passes the contract; the template validates against the new
  schema; the review-subagent handoff option is present; SKILL.md line count ≤500.

**Done When**

- `write-spec` produces a mechanism-free contract with the translated Gokul
  sections, contains no `Task Breakdown`/`Files`/`Steps` guidance, and its Handoff
  offers a context-seeded review-subagent option with an inline fallback.

### Task 2: Create the `write-plan` (layer-3) execution skill

**Objective**

Add a sibling skill that consumes a spec (or a settled request) and produces the
execution plan, carrying the seam-first discipline from the superseded overlay.

**Files**

- Create: `skills/write-plan/SKILL.md`
- Create: `skills/write-plan/scripts/validate_plan.py` (the **current**
  `write-spec/scripts/validate_spec.py` logic, moved + renamed)
- Create: `skills/write-plan/assets/plan-template.md`
- Create: `skills/write-plan/commands/workflows/plan.md`
- Create: `skills/write-plan/agents/openai.yaml`
- Create: `skills/write-plan/references/seam-selection.md`

**Dependencies**

Task 1 (the spec contract is the input the plan is held to)

**Implementation Steps**

1. Author SKILL.md (`skill-type: workflow`). Use this **locked description** (the
   trigger; keep it disjoint from `write-spec`):
   > Sequence the build: turn a settled target (a `write-spec` contract, a ticket,
   > or a clear request) into an execution plan — task breakdown, files, ordered
   > steps, seam selection, and verification commands. Use when WHAT is already
   > decided and you need HOW: the file-level, dependency-ordered steps to
   > implement it. If the target is not yet falsifiable, route back to `write-spec`.

   Required sections keep the execution schema: `## Goal` (restates/links the spec
   contract), `## Scope`,
   `## Assumptions And Constraints`, `## Task Breakdown` (per-task `Objective` /
   `Files` / `Dependencies` / `Implementation Steps` / `Verification` /
   `Done When`), `## Risks And Mitigations`, `## Verification Matrix`,
   `## Handoff`. Output path `docs/plans/YYYY-MM-DD-<topic>-plan.md`,
   `stage: plan`.
2. Add the `## Map Before You Cut` section (from the overlay spec): for tasks
   touching existing/coupled code, trace the data/call path, pick the thinnest
   seam that satisfies the spec's contract, and record an `**Assumptions
   Verified**` line. Acceptance gate is `Done When` = the spec contract, so a
   cleaner realization is allowed. Steps stay prescriptive *because grounded*
   (verify-first-then-prescribe; not "treat steps as hypotheses").
3. Port the plan validator: move the existing `validate_spec.py` body to
   `validate_plan.py`, switch expected `stage` to `plan` and the strict-filename
   suffix to `-plan.md`.
4. Write `plan-template.md`, the `/workflows:plan` command wrapper, and
   `agents/openai.yaml`. Add `references/seam-selection.md` (the worked
   data-path/seam checklist + the anonymized agentmonitor before/after).
5. Cross-link: `write-plan` consumes a `docs/specs/<topic>-spec.md` if present,
   else asks for the target; routes back to `write-spec` if no contract exists for
   non-trivial coupled work.
6. Add the same **review-subagent option** to `## Handoff` (and the command
   wrapper), with a *plan-focused* critique brief: seed the subagent with the
   plan's path + the spec contract + originating context, and have it check — is
   the chosen seam the thinnest that satisfies the contract? are `Assumptions
   Verified` actually grounded in code? are steps prescriptive-because-verified
   (not guesses)? is the blast radius mapped? are verification commands real and
   deterministic? are tasks over-fragmented? — then propose improvements. Inline
   `verify-before-complete` fallback when subagents are unavailable.

**Verification**

- Run: `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict`
- Run: `python3 skills/write-plan/scripts/validate_plan.py skills/write-plan/assets/plan-template.md`
- Run: `rg -n "subagent" skills/write-plan/SKILL.md`
- Expect: write-plan passes the contract; the plan template validates; the
  review-subagent option is present; manifest regen lists `write-plan`.

**Done When**

- `write-plan` exists, produces a seam-aware execution plan from a spec contract,
  its validator enforces the plan schema on `docs/plans/*-plan.md`, and its Handoff
  offers a context-seeded review-subagent option with an inline fallback.

### Task 3: Wire the validation hooks for both layers

**Objective**

Make the on-write hooks enforce the contract schema on `docs/specs/` and the plan
schema on `docs/plans/`.

**Files**

- Modify: `hooks/post-tool-use-validate-spec.sh`
- Create: `hooks/post-tool-use-validate-plan.sh`
- Modify: hook registration (`.claude/settings.json` or equivalent — confirm where
  `post-tool-use-validate-spec.sh` is registered before editing)

**Dependencies**

Task 1, Task 2

**Implementation Steps**

1. Confirm how the existing spec hook is registered (grep settings for
   `post-tool-use-validate-spec`); mirror that registration for the new plan hook.
2. Leave the spec hook keyed to `docs/specs/*-spec.md` but pointing at the new
   contract `validate_spec.py` (path unchanged; behavior changed by Task 1).
3. Create the plan hook as a copy keyed to `docs/plans/*-plan.md`, invoking
   `skills/write-plan/scripts/validate_plan.py --strict-filename`, same exit-code
   contract (0 pass / 2 fail).

**Verification**

- Run the spec hook against a valid new-schema spec and the plan hook against the
  plan template via stdin JSON (`{"tool_input":{"file_path":"…"}}`).
- Expect: exit 0 on valid files; exit 2 on a schema-mismatched file.

**Done When**

- Editing a `docs/specs/*-spec.md` validates the contract schema and editing a
  `docs/plans/*-plan.md` validates the plan schema, both via hooks.

### Task 4: Relocate and reshape brainstorming into a clean spec *feeder*

**Objective**

Vacate `docs/plans/` (so `write-plan` can own it) **and** reshape brainstorming's
output so it feeds the contract layer without overlapping it. Keep the discovery
*method* (one-question-at-a-time) untouched; change only the output path, the
summary shape, and the handoff. Depth rationale: a path-only move would leave
brainstorming emitting a proto-spec (it already has a `Success Criteria` section)
that duplicates and pre-empts `write-spec`'s contract — the pipeline composes
cleanly only if brainstorming stops at *direction* and `write-spec` owns
*falsifiability*.

**Files**

- Modify: `skills/brainstorming/SKILL.md` (output path, summary template, routing)
- Modify: `skills/brainstorming/commands/workflows/brainstorm.md`
- Modify: `skills/brainstorming/references/platform-mapping.md`
- Create: `docs/design/.gitkeep`
- Modify: `rules/doc-hygiene.md`, `README.md`,
  `skills/code-review-agents/agents/review/code-simplicity-reviewer.md` (refs to
  `docs/plans` as the brainstorm dir)

**Dependencies**

None (can land before Task 2; must land before the plan hook treats `docs/plans/`
as impl-plans)

**Implementation Steps**

1. Change every brainstorming output reference `docs/plans/…-plan.md` →
   `docs/design/…-design.md`. Keep `stage: brainstorm` (nothing keys off a `design`
   stage value; avoid a gratuitous cross-repo archive-tooling change).
2. Reshape the design-summary template to be a *feeder, not a proto-spec*:
   `## Problem / Context`, `## Options Considered` (with trade-offs),
   `## Chosen Direction` (+ rationale), `## Open Questions`, `## Constraints`.
   Replace the current `## Success Criteria` with `## What Good Looks Like`
   (directional, not falsifiable) and add a one-line note: "These harden into a
   falsifiable contract in `write-spec` — do not finalize metrics here."
3. Update routing/handoff: brainstorming hands to **`write-spec`** to turn the
   chosen direction into a contract; only then `write-plan` for execution. Drop the
   old "Proceed to planning" / direct-`write-spec`-as-plan language.
4. Add `docs/design/.gitkeep`; sweep remaining `docs/plans` references that mean
   "brainstorm output" (README, rules, the reviewer agent) to `docs/design`.
5. For pipeline consistency, add the same agent-agnostic **review-subagent option**
   to brainstorming's handoff, with a *design-focused* brief: critique the chosen
   direction — are alternatives fairly weighed? is the direction the simplest that
   meets the need? are open questions actually open? — before routing to
   `write-spec`. Inline fallback when subagents are unavailable.

**Verification**

- Run: `rg -n "docs/plans" skills/brainstorming README.md rules/ | rg -v "impl|execution"`
- Run: `rg -n "Success Criteria" skills/brainstorming/SKILL.md`
- Run: `rg -n "subagent" skills/brainstorming/SKILL.md`
- Expect: no brainstorming-output refs to `docs/plans/`; no falsifiable-criteria
  section left in the design summary (it lives in `write-spec` now).

**Done When**

- Brainstorming writes a direction-level design summary to `docs/design/`, hands
  to `write-spec`, and `docs/plans/` is free for `write-plan`.

### Task 5: Update sibling cross-references to the new chain

**Objective**

Make every skill that points at the old `write-spec` describe the correct
`brainstorm → spec → plan` roles, using one consistent vocabulary so triggers stay
disjoint.

**Shared vocabulary** (apply verbatim where each skill links the chain):
- `brainstorming` — clarify WHAT + chosen direction (`docs/design/`).
- `write-spec` — make the target falsifiable: the **contract** (`docs/specs/`).
- `write-plan` — sequence the build: tasks, files, steps (`docs/plans/`).

**Files**

- Modify: `skills/first-principles/SKILL.md` — reasoning feeds the **contract**;
  change "hand off to author the executable plan" → "hand off to `write-spec` for
  the contract; then `write-plan` to execute."
- Modify: `skills/deep-research/SKILL.md` — research grounds **both**: evidence for
  the contract (`write-spec`) and references for steps (`write-plan`). Change
  "common caller when a plan needs grounded references" to name both.
- Modify: `skills/api-design/SKILL.md` — the API contract feeds `write-spec`;
  multi-file execution goes to `write-plan` (today it says `write-spec` for "spans
  files or phases," which is now the plan's job).
- Modify: `skills/loop-design/SKILL.md` — "single interactive turn" example should
  reference `write-plan` (sequencing) or a direct prompt, not `write-spec`.
- Modify: `skills/brainstorming/SKILL.md` — routing already handled in Task 4;
  confirm it uses the shared vocabulary.
- Modify: `skills/skill-evals/assets/trigger-collision-cases-expanded.json`
- Note: `skills/autonomous-engineering/` does **not** reference `write-spec` by
  name (only its README says "implementation plan"); update that README line to
  "spec (contract) then plan (execution)" but expect no SKILL.md change.

**Dependencies**

Task 1, Task 2

**Implementation Steps**

1. Apply the shared vocabulary to each file above; fix every line that conflates
   "spec" with "executable/implementation plan."
2. Add a trigger-collision case distinguishing `write-spec` (WHAT/contract,
   "define the target / acceptance / what done means") from `write-plan`
   (HOW/sequencing, "break into tasks / files / order the build") so the
   descriptions stay disjoint and the agent routes correctly.

**Verification**

- Run: `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict`
- Run any skill-evals trigger test that exists for collision cases.
- Run: `rg -ni "write-spec.*(executable|implementation) plan" skills/`
- Expect: contract passes; no skill still calls `write-spec` "an implementation
  plan"; the new collision case present.

**Done When**

- All sibling references use the shared `brainstorm → spec → plan` vocabulary with
  disjoint triggers, and a collision case guards the spec/plan boundary.

### Task 6: Reclassify legacy specs and supersede the overlay

**Objective**

Leave `docs/specs/` holding only contract-shaped files and `docs/plans/` holding
plan-shaped files, without weakening either validator.

**Files**

- Move: `docs/specs/2026-06-16-authoring-multiharness-pipeline-spec.md` and
  `docs/specs/2026-06-28-api-design-skill-spec.md` → `docs/plans/…-plan.md`
  (these are plan-shaped; verify each is not already terminal/archived first)
- Move: `docs/specs/2026-06-30-spec-plan-skill-split-spec.md` (this doc — it is
  plan-shaped) → `docs/plans/2026-06-30-spec-plan-skill-split-plan.md`
- Modify: `docs/specs/2026-06-29-write-spec-seam-first-improvement-spec.md`
  (set `status: superseded`, add a pointer to this plan)

**Dependencies**

Task 2 (plan validator must exist), Task 3 (plan hook)

**Implementation Steps**

1. Migrate the two legacy plan-shaped specs
   (`2026-06-16-authoring-multiharness-pipeline-spec.md`,
   `2026-06-28-api-design-skill-spec.md`): confirm each has `Task Breakdown`,
   `git mv` to `docs/plans/<date>-<topic>-plan.md`, switch frontmatter
   `stage: spec → plan`, rename the title suffix `Spec → Plan`, and update any
   in-repo references to the old paths (`rg -l <old-filename>`).
2. Migrate **this** split plan the same way (it is plan-shaped, so it belongs in
   `docs/plans/` and would otherwise fail the new contract validator/hook in
   `docs/specs/`): `git mv` to `docs/plans/2026-06-30-spec-plan-skill-split-plan.md`,
   `stage: spec → plan`, title `Spec → Plan`, set `status: in-progress` during
   execution and `complete` at the end. Do this **after** Task 2's plan validator
   exists so the moved file validates immediately.
3. Set the overlay spec `status: superseded` with a one-line link to the moved
   plan; the renamed archive script (Task 8) sweeps it on the next pass.

**Verification**

- Run: `python3 skills/write-plan/scripts/validate_plan.py docs/plans/*-plan.md`
- Run: `python3 skills/write-spec/scripts/validate_spec.py docs/specs/*-spec.md`
  (after migration, only `superseded` overlay artifacts may remain; no plan-shaped
  file should be left in `docs/specs/` to trip the contract validator/hook)
- Expect: migrated files validate as plans; `docs/specs/` clean of stray plans.

**Done When**

- `docs/specs/` holds only contract-shaped files, all plan-shaped docs (legacy +
  this split plan) live in `docs/plans/` and validate, and the overlay is
  `superseded`.

### Task 7: Update reference docs and regenerate manifests

**Objective**

Bring `docs/system/*`, `README.md`, `skills.json`, and the catalog in line with
the split.

**Files**

- Modify: `docs/system/ARCHITECTURE.md`, `docs/system/FEATURES.md`,
  `docs/system/OPERATIONS.md`, `docs/system/ROADMAP.md`, `README.md`
- Regenerate: `skills.json`, `docs/catalog/index.html`

**Dependencies**

Tasks 1–6

**Implementation Steps**

1. Document the `brainstorm → spec → plan` pipeline and the three directories in
   ARCHITECTURE; add `write-plan` to FEATURES; update OPERATIONS commands; add a
   ROADMAP entry closing the seam-first finding and noting the cross-repo archive
   follow-up.
2. Regenerate the manifest and catalog:
   `python3 scripts/generate_skills_manifest.py` and
   `python3 scripts/gen_catalog.py` (or rely on hooks; verify output changed).

**Verification**

- Run: `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict`
- Run: `python3 -m pytest tests/test_generate_skills_manifest.py tests/test_gen_catalog.py`
- Run: `rg -n "write-spec" docs/system README.md | rg -i "implementation plan"`
- Expect: contract passes; manifest/catalog tests pass; no doc still equates spec
  with implementation plan.

**Done When**

- Reference docs describe the split; `skills.json` lists `write-spec` (contract)
  and `write-plan` (execution); catalog regenerated.

### Task 8: Update and rename the cross-repo archive script (final step)

**Objective**

Teach the lifecycle-archive script about `docs/design/` and rename it to fit the
`design → spec → plan` workflow, since "archive_plans" no longer describes what it
does. **Cross-repo** (`~/Dev/ops`, a separate git repo) — run last, commit
separately in that repo.

**Files**

- Rename + modify: `../ops/scripts/archive_plans.py` → `../ops/scripts/archive_docs.py`
- Modify (parent workspace refs): `~/Dev/AGENTS.md`,
  `~/Dev/ops/agent-docs/capabilities/plan-archiving.md` (rename/retitle as
  `docs-archiving.md` if cheap), and any `rg -l archive_plans ~/Dev` hits.

**Dependencies**

Tasks 1–7 (run after dojo changes land so the script is updated against the final
directory layout)

**Implementation Steps**

1. Add `"design"` to the script's `STATUS_DIRS` (currently
   `("plans", "specs", "review")`) so design summaries archive on terminal status.
   Note: brainstorming summaries carry `stage: brainstorm` but **no `status:`**
   today — decide and document one of: (a) give design summaries a status
   lifecycle, or (b) archive `design/` by age like `sessions/`. Recommend (a) for
   consistency; implement whichever, but make the script's behavior explicit, not
   accidental (a statusless doc currently reports as TRIAGE, never moves).
2. `git mv` the script to `archive_docs.py`; update its module docstring/usage to
   the `design/specs/plans/sessions` vocabulary.
3. Update every reference: `~/Dev/AGENTS.md` (the lifecycle/`ops/scripts` mention),
   the capability doc, and any other `rg -l archive_plans ~/Dev` hits.
4. Commit in the `~/Dev/ops` repo separately (cross-repo; do not mix with the dojo
   commit).

**Verification**

- Run: `python3 ../ops/scripts/archive_docs.py --root ~/Dev dojo` (dry-run default)
- Run: `rg -l "archive_plans" ~/Dev` (excluding archives)
- Expect: dry-run lists `design/`, `specs/`, `plans/` candidates without moving;
  no stale `archive_plans` references remain.

**Done When**

- The script is renamed, recognizes `docs/design/`, parent-workspace references are
  updated, and the change is committed in `~/Dev/ops`.

## Risks And Mitigations

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Trigger collision: agent can't tell `write-spec` from `write-plan` | High | High | Disjoint descriptions (WHAT/contract vs HOW/sequencing); add a trigger-collision eval case (Task 5); `write-plan` consumes a spec, `write-spec` forbids steps. |
| Cross-repo archive tooling unaware of `docs/design/` + split | High | Med | Handled in Task 8 (operator-authorized): add `design` to `STATUS_DIRS`, rename to `archive_docs.py`, commit separately in `~/Dev/ops`. |
| Design summaries lack a `status:` so never auto-archive | Med | Low | Task 8 step 1 forces an explicit decision (status lifecycle vs age-based) rather than silent TRIAGE. |
| Legacy `docs/specs` plan files break the new contract hook | Med | Med | Reclassify them to `docs/plans/` (Task 6); supersede the overlay; never weaken the validator. |
| Scope creep: full pipeline rewrite balloons | Med | Med | Brainstorming method unchanged (only path/routing); plan schema is the *existing* validator moved, not rewritten. |
| Gokul product framing imposes ceremony on mechanical specs | Med | Med | Gate Evaluation/thresholds behind "is this a measurable bet?"; only Problem + Contract + Success are universal. |
| Two skills double the maintenance + drift surface | Med | Low | Shared validator helpers; run skill-standardizer after landing; CI sync check. |
| This spec self-references during migration | Low | Low | Explicitly excluded from Task 6; archived on completion. |

## Verification Matrix

| Requirement | Proof command | Expected signal |
| --- | --- | --- |
| Both skills pass the contract | `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict` | write-spec + write-plan pass |
| Spec is contract-shaped (no plan content) | `rg -n "Task Breakdown\|Implementation Steps" skills/write-spec/SKILL.md skills/write-spec/assets/spec-template.md` | no matches |
| Spec template validates as a contract | `python3 skills/write-spec/scripts/validate_spec.py skills/write-spec/assets/spec-template.md` | `PASS` |
| Plan template validates as a plan | `python3 skills/write-plan/scripts/validate_plan.py skills/write-plan/assets/plan-template.md` | `PASS` |
| Brainstorming vacated `docs/plans` | `rg -n "docs/plans" skills/brainstorming` | no matches |
| New skill registered | `rg -n '"write-plan"' skills.json` | present |
| Manifest/catalog tests pass | `python3 -m pytest tests/test_generate_skills_manifest.py tests/test_gen_catalog.py` | pass |
| No doc equates spec with impl plan | `rg -ni "spec.*implementation plan" docs/system README.md` | no matches |
| Review-subagent handoff option present | `rg -ln "subagent" skills/write-spec/SKILL.md skills/write-plan/SKILL.md skills/brainstorming/SKILL.md` | all three match |

## Handoff

- Execute in a separate session. Suggested order: Task 1 → Task 4 → Task 2 →
  Task 3 → Task 5 → Task 6 → Task 7 → Task 8. Run strict contract validation after
  each skill task; regenerate `skills.json` + catalog if hooks don't.
- After landing, run `skill-standardizer` to sync the global harness copies of
  `write-spec`/`write-plan`/`brainstorming`.
- Task 8 is **cross-repo** (`~/Dev/ops`): run it last and commit it separately in
  that repo, not in the dojo commit.
- The superseded overlay is
  `docs/specs/2026-06-29-write-spec-seam-first-improvement-spec.md`; its seam-first
  content now lives in `write-plan`.

### Next Steps

1. Confirm the directory scheme (`docs/design` / `docs/specs` / `docs/plans`) and
   the contract schema (translated Gokul sections) before execution.
2. Execute Tasks 1–7 in a separate session (dojo), then Task 8 in `~/Dev/ops`.
3. Run `skill-standardizer` to sync global skill copies.
