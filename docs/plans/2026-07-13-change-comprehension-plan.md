---
date: 2026-07-13
topic: change-comprehension
stage: plan
status: in-progress
source: conversation
---

# Change Comprehension Plan

## Goal

Deliver the optional, non-gating human-comprehension workflow defined in
`docs/specs/2026-07-13-change-comprehension-spec.md`: a task-scoped scope mode
for proposed changes and a one-question-at-a-time quiz mode for implemented
changes, with focused routing checks and fixed behavioral acceptance scenarios.

## Scope

### In Scope

- Add one `change-comprehension` workflow skill with a concise, agent-agnostic
  runtime contract.
- Expose scope and quiz modes through explicit `/understand-change` and
  `/quiz-change` command wrappers.
- Add dedicated positive, negative, and sibling-routing fixtures plus fixed
  multi-turn behavioral scenarios.
- Register the skill and commands in the canonical feature docs and record the
  shipped capability in the roadmap.
- Regenerate the manifest, catalog, and Codex sidecar through their existing
  generators.
- Validate routing, structure, prose, generated artifacts, regression tests, and
  the fixed behavioral protocol before marking the contract complete.

### Out of Scope

- New runtime scripts, hooks, MCP servers, LSP integrations, or subagent types.
- Changes to `brainstorming`, `write-spec`, `write-plan`, `first-principles`,
  `diagnose`, `local-review`, `gh-review-pr`, or `verify-before-complete`.
- A generic codebase mapper, automatic quiz invocation, merge gating, scoring,
  persistent learner profiles, or quiz-result storage.
- Extending the repository-wide behavioral-eval runner beyond the focused skill
  fixtures required by this contract.
- Fixing the existing `skill-creator` initializer template, which currently
  omits the required release version; this implementation will replace its
  temporary scaffold immediately.
- Packaging or globally installing the skill; distribution and mirror sync need
  separate user authorization after the repository implementation is accepted.

## Assumptions And Constraints

- The approved spec has no contract-changing open questions and remains the
  acceptance authority.
- The implementation stays instruction-first. Two conversational modes do not
  justify a new executable subsystem or a large reference tree.
- `SKILL.md` is the authored source of truth. `skills.json`, the catalog page,
  and the Codex sidecar remain generated artifacts and are never hand-edited.
- New skills start at `version: 1.0.0`; because the skill does not exist on
  `origin/main`, the release checker does not require a changelog reconstruction.
- Explicit user intent is the trigger boundary. Generic explanation, planning,
  diagnosis, review, and completion requests must continue routing to their
  existing owners.
- The dedicated routing fixture is the acceptance gate for this cluster. The
  older expanded collision fixture has unrelated baseline failures and is not a
  gate for this change.
- The catalog currently contains 56 skills; successful generation adds the 57th.
- Red/green TDD applies to the focused routing fixture: freeze the cases before
  finalizing the description, demonstrate a failing positive route on the
  minimal scaffold, then author the workflow until the same command passes.
- Full conversational behavior varies across models and harnesses. Fixed inputs
  and binary assertions make that variance visible without pretending the live
  agent replay is deterministic.

## Map Before You Cut

The runtime path is metadata → selected `SKILL.md` → optional command wrapper;
there is no application code path to extend. The thinnest seam is therefore a
single workflow package with two explicit wrappers and focused eval artifacts.
Adding a generic reconnaissance engine or changing neighboring skills would
duplicate the existing stack and broaden the trigger surface.

Repository integration follows existing ownership:

1. `skills/skill-creator/scripts/init_skill.py` creates the directory scaffold;
   its template at lines 29–33 lacks the current required `version`, so the
   generated placeholder must be replaced immediately rather than validated as
   an intermediate deliverable.
2. `skills/skill-evals/scripts/run_trigger_evals.py` reads declared triggers or
   an explicit case file and accepts a selected sibling set. That is the narrow
   deterministic routing seam; no new runner is needed.
3. `scripts/generate_skills_manifest.py:58-94` enumerates every
   `skills/*/SKILL.md`, including version and triggers.
4. `scripts/gen_harness_adapters.py:171-189` derives the missing Codex sidecar
   from frontmatter, while `scripts/gen_catalog.py:83-90` renders the manifest
   into the searchable catalog.
5. `docs/system/FEATURES.md:45-59` owns the development-workflow inventory and
   `docs/system/FEATURES.md:134-151` owns the command list.
6. `docs/project/ROADMAP.md:20-49` owns shipped highlights; its line 94 catalog
   count is stale and should become 57 when this skill lands.

## Task Breakdown

### Task 1: Author the workflow package through focused red/green evals

**Objective**

Create the complete instruction-first skill, explicit command wrappers, and
fixed acceptance fixtures without changing neighboring workflow contracts.

**Files**

- Create: `skills/change-comprehension/SKILL.md`
- Create: `skills/change-comprehension/commands/understand-change.md`
- Create: `skills/change-comprehension/commands/quiz-change.md`
- Test: `skills/change-comprehension/evals/trigger-cases.json`
- Test: `skills/change-comprehension/evals/behavioral-scenarios.md`
- Modify: `docs/specs/2026-07-13-change-comprehension-spec.md`
- Modify: `docs/plans/2026-07-13-change-comprehension-plan.md`

**Dependencies**

None

**Assumptions Verified**

- `docs/specs/2026-07-13-change-comprehension-spec.md:5` and
  `docs/plans/2026-07-13-change-comprehension-plan.md:5` both begin at
  `status: draft`; they must move together when implementation actually starts.

**Research Context**

- `docs/specs/2026-07-13-change-comprehension-spec.md:22-38` defines the two-mode,
  non-scored contract and its verification gate.
- `docs/specs/2026-07-13-change-comprehension-spec.md:58-111` separates scope,
  quiz, and sibling-routing behavior.
- `skills/brainstorming/SKILL.md:45-60` demonstrates one-question-at-a-time user
  interaction; this skill reuses the interaction discipline but not
  brainstorming's decision responsibility.
- `skills/local-review/SKILL.md:14-59` demonstrates explicit target selection and
  a read-only workflow boundary; change comprehension consumes evidence without
  adopting review findings.
- `skills/verify-before-complete/SKILL.md:47-65` keeps proof of completion
  separate from explanatory confidence.

**Implementation Steps**

1. Change the spec and plan to `status: in-progress` before creating the skill;
   keep both in that state through any failed implementation or verification
   gate.
2. Run
   `python3 skills/skill-creator/scripts/init_skill.py change-comprehension --path skills`
   to create the canonical scaffold. Immediately replace the TODO template with
   valid frontmatter containing `name: change-comprehension`,
   `skill-type: workflow`, `version: 1.0.0`, a trigger-ready description, and a
   small set of literal scope/quiz trigger phrases.
3. Before finalizing the description or body, add the dedicated trigger fixture.
   Include positive scope and quiz prompts and negative controls for
   `brainstorming`, `write-spec`, `write-plan`, `first-principles`, `diagnose`,
   `local-review`, `gh-review-pr`, `verify-before-complete`, and generic
   non-interactive code explanation.
4. Run the focused trigger command against the minimal valid scaffold and record
   a non-zero result for at least one positive change-comprehension case. This is
   the red signal; do not weaken negative controls to obtain green.
5. Add the fixed behavioral scenario protocol from the spec. For each scenario,
   include the repository/change context, literal user turns, expected assistant
   turn boundaries, and binary assertions. Cover scope evidence conflict,
   incomplete and “I don't know” answers, a complete answer and natural close,
   missing change target, skip/stop control, no-artifact default, and sibling
   routing.
6. Author a concise `SKILL.md` with: mode selection; shared grounding and
   confidence rules; a scope workflow that distinguishes current behavior from
   proposed intent; a quiz workflow that proposes a bounded topic set, asks at
   most one substantive question per active quiz turn, waits, teaches with
   evidence, and closes with a non-scored recap; explicit boundaries; output and
   verification contracts; resource pointers; and sibling handoffs.
7. Add `/understand-change` as the canonical scope wrapper and `/quiz-change` as
   the canonical quiz wrapper. Each wrapper loads the same skill, supplies its
   mode and user arguments, preserves chat-only/no-write defaults, and delegates
   all behavior to `SKILL.md` rather than duplicating the full workflow. Keep the
   wrappers directly under `commands/`: unlike the nested brainstorm/spec/plan
   wrappers, these are independent entrypoints rather than one staged pipeline.
8. Re-run the exact focused trigger command until every positive and negative
   assertion passes. Then run the full-catalog declared-trigger check so the new
   literal triggers do not tie or beat another skill.
9. Replay each behavioral scenario in its own new chat session with no prior
   conversation beyond repository instructions, explicit skill invocation, and
   the frozen scenario context. A human evaluator drives the user turns verbatim;
   the skill-under-test agent produces only assistant turns. Record binary
   pass/fail per assertion, revise only the minimum instructions needed for a
   failure, and replay the same frozen scenario from another new session.
10. Remove every TODO or scaffold explanation and confirm the final skill and
   wrappers contain no harness-specific behavior beyond the optional command
   metadata.

**Verification**

- Run:
  `python3 skills/skill-creator/scripts/quick_validate.py skills/change-comprehension`
- Expect: `Skill is valid!` and exit 0.
- Run:
  `python3 skills/skill-evals/scripts/run_trigger_evals.py --cases skills/change-comprehension/evals/trigger-cases.json --skills-root skills --skills change-comprehension,brainstorming,write-spec,write-plan,first-principles,diagnose,local-review,gh-review-pr,verify-before-complete --pretty`
- Expect: every focused assertion passes and exit 0.
- Run:
  `python3 skills/skill-evals/scripts/run_trigger_evals.py --from-triggers --skills-root skills --pretty`
- Expect: every declared trigger self-routes without a collision and exit 0.
- Run:
  `python3 scripts/slop_scan.py skills/change-comprehension/SKILL.md skills/change-comprehension/commands/understand-change.md skills/change-comprehension/commands/quiz-change.md`
- Expect: `No slop detected.` and exit 0.
- Run: replay the fixed cases in
  `skills/change-comprehension/evals/behavioral-scenarios.md`.
- Expect: every binary assertion passes; no transcript leaks an answer early,
  asks multiple substantive questions, invents evidence, writes an artifact,
  scores the user, or gives a merge verdict.

**Test Discovery Verified**

- Runner/discovery evidence:
  `skills/skill-evals/scripts/run_trigger_evals.py` accepts an explicit `--cases`
  file and evaluates only the named `--skills` set; the behavioral protocol is a
  literal replay artifact rather than a pytest-discovered test.
- Literal proof:
  `python3 skills/skill-evals/scripts/run_trigger_evals.py --cases skills/change-comprehension/evals/trigger-cases.json --skills-root skills --skills change-comprehension,brainstorming,write-spec,write-plan,first-principles,diagnose,local-review,gh-review-pr,verify-before-complete --pretty`
  runs the exact routing fixture. Every scenario heading in
  `skills/change-comprehension/evals/behavioral-scenarios.md` is replayed directly
  against its frozen turns and assertions.

**Done When**

- Both modes are independently invokable and satisfy the spec's chat behavior.
- Scope output remains explanatory and task-bounded rather than plan-shaped.
- Quiz output is adaptive, evidence-backed, user-controlled, one-question-at-a-
  time, and non-gating.
- Focused and declared-trigger evals pass without weakening sibling boundaries.
- Every fixed behavioral assertion passes on replay.

### Task 2: Register the workflow and commands in canonical docs

**Objective**

Make the authored capability discoverable in the maintained feature inventory
and record its shipped role without duplicating runtime instructions.

**Files**

- Modify: `docs/system/FEATURES.md`
- Modify: `docs/project/ROADMAP.md`

**Dependencies**

Task 1

**Assumptions Verified**

- `docs/system/FEATURES.md:45-59` is the canonical Development Workflows table,
  and lines 134–151 are the explicit command-wrapper inventory.
- `docs/project/ROADMAP.md:20-49` records shipped skill capabilities. Its summary
  row at line 11 says 56 curated skills, while line 94 still says 54; both should
  report 57 after this addition rather than preserving conflicting live counts.
- `README.md:205-207` deliberately points readers to `FEATURES.md` for the full
  command list, so repeating both commands in README would create a second home
  for the same fact.

**Implementation Steps**

1. Add `change-comprehension` to Development Workflows with a one-line purpose
   centered on optional human scope understanding and pre-merge self-quizzing.
2. Add `/understand-change` and `/quiz-change` to the command-wrapper list with
   distinct scope and quiz descriptions.
3. Add one shipped roadmap highlight describing the human-comprehension gap,
   the two modes, non-gating boundary, and focused behavioral/routing evaluation.
4. Update both live roadmap catalog counts—56 at line 11 and stale 54 at line
   94—to 57. Leave the older approximate resource-distribution breakdown labeled
   as approximate rather than pretending it was recomputed.

**Verification**

- Run:
  `rg -n 'change-comprehension|understand-change|quiz-change|57 skills' docs/system/FEATURES.md docs/project/ROADMAP.md`
- Expect: one workflow entry, two command entries, one roadmap highlight, and the
  updated catalog count; no duplicate README command listing.
- Run:
  `python3 scripts/slop_scan.py docs/system/FEATURES.md docs/project/ROADMAP.md`
- Expect: `No slop detected.` and exit 0.

**Done When**

- The canonical feature docs make the skill and both explicit entrypoints
  discoverable.
- The roadmap accurately records the shipped capability and resulting catalog
  size without copying runtime instructions.

### Task 3: Regenerate the inventory, catalog, and harness sidecar

**Objective**

Derive every machine-facing artifact from the new canonical frontmatter and
confirm the generation pipeline remains idempotent.

**Files**

- Create: `skills/change-comprehension/agents/openai.yaml`
- Modify: `skills.json`
- Modify: `docs/catalog/index.html`

**Dependencies**

Task 1 (functional dependency). Execute after Task 2 so the documentation and
generated integration can land as one coherent commit.

**Assumptions Verified**

- `scripts/generate_skills_manifest.py:58-94` enumerates every direct skill
  directory and copies `name`, `description`, `version`, and optional triggers
  from `SKILL.md`.
- `scripts/gen_harness_adapters.py:171-189` creates or refreshes generated Codex
  sidecars while preserving hand-authored ones.
- `scripts/gen_catalog.py:83-90` derives the searchable catalog payload from
  `skills.json`; direct HTML edits would be overwritten.

**Implementation Steps**

1. Run `python3 scripts/generate_skills_manifest.py` after the final frontmatter
   is green; do not hand-edit `skills.json` even if an edit hook already updated
   it.
2. Run `python3 scripts/gen_harness_adapters.py --skip-symlinks` to create the
   committed Codex sidecar without mutating local harness symlink topology.
3. Run `python3 scripts/gen_catalog.py` after the manifest so the catalog embeds
   the same 57-skill inventory and trigger metadata.
4. Re-run every generator in check mode to prove the outputs are idempotent and
   no generated artifact is missing or stale.

**Verification**

- Run: `jq -e '.skills | length == 57' skills.json`
- Expect: exit 0.
- Run:
  `jq -e '.skills[] | select(.name == "change-comprehension" and .version == "1.0.0")' skills.json`
- Expect: exactly one matching manifest entry with the authored trigger list.
- Run:
  `python3 scripts/generate_skills_manifest.py --check && python3 scripts/gen_harness_adapters.py --check --skip-symlinks && python3 scripts/gen_catalog.py --check`
- Expect: all three report up-to-date state and exit 0.

**Done When**

- The runtime inventory, Codex adapter, and catalog all expose the same canonical
  skill intent and version.
- A second generation pass produces no diff.

### Task 4: Run the full gate and close the lifecycle docs

**Objective**

Prove the complete branch satisfies the skill contract and repository CI surface,
then mark the spec and plan complete only on fresh evidence.

**Files**

- Modify: `docs/specs/2026-07-13-change-comprehension-spec.md`
- Modify: `docs/plans/2026-07-13-change-comprehension-plan.md`

**Dependencies**

Tasks 1–3

**Assumptions Verified**

- `docs/specs/2026-07-13-change-comprehension-spec.md:5` is `status: draft` and
  remains the acceptance contract.
- `docs/plans/2026-07-13-change-comprehension-plan.md:5` starts as
  `status: draft`; lifecycle status is not evidence and must advance only after
  the corresponding work begins or passes.
- `.github/workflows/skill-contract-pilot.yml:61-105` defines the current CI
  surface: pytest, strict contract checks, version checks, generated-artifact
  checks, and the prose scan.

**Implementation Steps**

1. Confirm the spec and plan have remained `status: in-progress` since Task 1;
   do not repair a missed lifecycle transition retroactively without noting it.
2. Re-run Task 1's focused routing checks on the final authored content, not on
   cached earlier output. Replay each behavioral scenario with the same protocol:
   one new session per scenario, human-driven frozen user turns, and only the
   skill-under-test agent producing assistant turns.
3. Run the repository regression suite, strict skill contract, skill-version
   check, all generated-artifact checks, prose scan, spec validator, plan
   validator, and whitespace check.
4. Review the final diff to confirm only the new skill, its focused evals,
   generated outputs, canonical docs, and lifecycle artifacts changed.
5. Change both statuses to `complete` only after every required check passes and
   residual live-agent variance is reported honestly. Re-run the spec/plan
   validators after the status edit.
6. Commit coherent chunks in order: Task 1's evals/workflow; Tasks 2–3 together
   as docs/generated integration; then Task 4's lifecycle closure. Do not push or
   globally sync the skill without a new explicit user request.

**Verification**

- Run: `python -m pytest tests/ -q`
- Expect: all repository tests pass.
- Run:
  `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict`
- Expect: all 57 skills pass strict validation.
- Run:
  `python3 skills/skill-evals/scripts/check_skill_versions.py --base origin/main`
- Expect: the new `1.0.0` skill passes without requiring a historical changelog;
  no existing skill has an unbumped release-relevant change.
- Run:
  `python3 scripts/gen_skill_docs.py --check && python3 scripts/generate_skills_manifest.py --check && python3 scripts/gen_harness_adapters.py --check --skip-symlinks && python3 scripts/gen_catalog.py --check`
- Expect: all generated artifacts are current.
- Run: `python3 scripts/slop_scan.py`
- Expect: `No slop detected.` and exit 0.
- Run:
  `python3 skills/write-spec/scripts/validate_spec.py --strict-filename docs/specs/2026-07-13-change-comprehension-spec.md`
- Expect: spec passes.
- Run:
  `python3 skills/write-plan/scripts/validate_plan.py --strict-filename docs/plans/2026-07-13-change-comprehension-plan.md`
- Expect: plan passes with no grounding or test-discovery advisories.
- Run: `git diff --check`
- Expect: exit 0 with no whitespace errors.
- Run: `git status --short --branch`
- Expect: only intentional commits remain and no uncommitted generated drift is
  present before handoff.

**Done When**

- Every structural, routing, behavioral, generated, regression, prose, and
  lifecycle check supports the spec's end state.
- The spec and plan are marked complete only after fresh final evidence.
- The branch is ready for user-directed review or publication, with no push or
  global sync performed implicitly.

## Risks And Mitigations

- Risk: live models or harnesses vary in how strictly they preserve quiz state
  and one-question pacing despite identical instructions.
  Signal: a frozen behavioral scenario passes in one supported harness/model and
  fails in another, or loses the bounded topic set after a long exchange.
  Mitigation: keep turn invariants explicit and compact, replay the same fixed
  scenarios on the supported target harness, and report residual variance rather
  than adding a false deterministic claim.
- Risk: some repositories or version-control systems cannot expose the requested
  change target through the available tools.
  Signal: quiz mode cannot resolve a working tree, commit, branch, or pull-request
  diff from local or user-supplied evidence.
  Mitigation: require the agent to ask for a concrete target or supplied diff and
  begin no substantive quiz until evidence exists.
- Risk: explicit command wrappers are unavailable in a consuming harness.
  Signal: `/understand-change` or `/quiz-change` is not surfaced even though the
  skill catalog is available.
  Mitigation: keep both intents trigger-ready in canonical frontmatter and make
  the wrappers optional adapters, not the only invocation path.

## Verification Matrix

| Requirement | Proof command | Expected signal |
| --- | --- | --- |
| Valid workflow package | `python3 skills/skill-creator/scripts/quick_validate.py skills/change-comprehension` | `Skill is valid!` |
| Strict dojo contract | `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict` | 57 skills pass |
| Focused sibling routing | `python3 skills/skill-evals/scripts/run_trigger_evals.py --cases skills/change-comprehension/evals/trigger-cases.json --skills-root skills --skills change-comprehension,brainstorming,write-spec,write-plan,first-principles,diagnose,local-review,gh-review-pr,verify-before-complete --pretty` | All focused assertions pass |
| Declared triggers avoid collisions | `python3 skills/skill-evals/scripts/run_trigger_evals.py --from-triggers --skills-root skills --pretty` | No tie or collision |
| Fixed conversational contract | Replay `skills/change-comprehension/evals/behavioral-scenarios.md` | Every binary assertion passes |
| Manifest contains the new release | `jq -e '.skills | length == 57' skills.json` | Exit 0 |
| Generated artifacts are current | `python3 scripts/gen_skill_docs.py --check && python3 scripts/generate_skills_manifest.py --check && python3 scripts/gen_harness_adapters.py --check --skip-symlinks && python3 scripts/gen_catalog.py --check` | All checks exit 0 |
| Existing repository behavior is preserved | `python -m pytest tests/ -q` | Full suite passes |
| New-skill release policy holds | `python3 skills/skill-evals/scripts/check_skill_versions.py --base origin/main` | Version check passes |
| Authored prose remains clean | `python3 scripts/slop_scan.py` | No slop detected |
| Contract remains valid | `python3 skills/write-spec/scripts/validate_spec.py --strict-filename docs/specs/2026-07-13-change-comprehension-spec.md` | Spec passes |
| Plan remains grounded | `python3 skills/write-plan/scripts/validate_plan.py --strict-filename docs/plans/2026-07-13-change-comprehension-plan.md` | Plan passes with no advisories |
| Working tree hygiene | `git diff --check` | Exit 0 |

## Handoff

1. Execute this plan in the current feature branch, task by task, setting the
   plan and spec to `in-progress` before implementation.
2. Review this plan with a headless Claude Sonnet 5 high-effort critique seeded
   with AGENTS.md, the design, spec, plan, relevant skill contracts, and exact
   repository seams; apply justified corrections before execution.
3. Open a separate execution session or refine the plan further if the critique
   exposes a contract-changing issue.
