---
date: 2026-07-11
topic: plan-spec-grounding
stage: plan
status: complete
source: conversation
---

# Plan And Spec Grounding Plan

## Goal

Strengthen `write-spec` decision readiness and `write-plan` implementation
grounding so a plan is only written against a settled, falsifiable contract and
its steps are based on verified current facts. This plan realizes the scoped
conversation contract: advisory-only semantic checks, no `brainstorming` change,
and no brittle hard-fail heuristic.

## Scope

### In Scope

- Add a decision-readiness and uncertainty-triage guide to `write-spec`.
- Clarify that contract-affecting questions must close before a `write-plan`
  handoff.
- Add exact-target evidence, resolved-now, risk-triage, and test-discovery
  guidance to `write-plan`.
- Add advisory-only plan-validator output and regression coverage.
- Release both changed public workflow contracts and refresh generated artifacts.

### Out of Scope

- Changes to `brainstorming`, including its design-summary schema.
- A hard semantic validator for plan prose or a requirement to migrate historic
  plans.
- A roadmap update while the user-owned roadmap relocation is in progress.

## Assumptions And Constraints

- Advisory checks must never change a valid plan's exit status.
- Guidance must remain agent-agnostic and distinguish resolvable facts from
  irreducible future uncertainty.
- Tests belong in `tests/`: CI runs `.venv/bin/python -m pytest tests/ -q`, and
  the literal suite already collects this directory.
- Existing user changes relocating `docs/system/ROADMAP.md` must remain untouched.

## Map Before You Cut

- `validate_plan.py` currently checks only structure; the hook delegates to it,
  so advisory collection at its CLI boundary is the thinnest non-blocking seam.
- `write-spec` owns the contract-to-plan transition; its template currently says
  questions may close "before or during execution," so its handoff guidance is
  the narrow upstream seam.
- `SKILL.md` frontmatter drives release artifacts; version changes must flow
  through the existing generators rather than hand-edited outputs.

## Task Breakdown

### Task 1: Add advisory-validator regression coverage

**Objective**

Define the observable advisory behavior before changing the validator.

**Files**

- Create: `tests/test_validate_plan.py`

**Dependencies**

None

**Assumptions Verified**

- `tests/` is the repository's collected pytest root, verified in
  `.github/workflows/skill-contract-pilot.yml`; a new `tests/test_validate_plan.py`
  is discovered by the CI command.

**Implementation Steps**

1. Add valid-plan fixtures covering existing-code edits, create-only work, and
   test-file work.
2. Assert that missing grounding or discovery markers produce advisory output,
   while the CLI still exits zero for an otherwise valid plan.
3. Assert that the corresponding explicit markers suppress only their relevant
   advisories.

**Test Discovery Verified**

- `tests/test_validate_plan.py` matches pytest's collected `tests/` root; prove
  it with `.venv/bin/python -m pytest tests/test_validate_plan.py -q` and the
  full `.venv/bin/python -m pytest tests/ -q` gate.

**Verification**

- Run: `.venv/bin/python -m pytest tests/test_validate_plan.py -q`
- Expect: advisory behavior and zero-exit regression cases pass.

**Done When**

- The advisory contract is covered at the validator's observable CLI boundary.

### Task 2: Add advisory-only grounding checks to the plan validator

**Objective**

Surface likely missing plan-grounding evidence without making heuristic prose
analysis a blocking schema rule.

**Files**

- Modify: `skills/write-plan/scripts/validate_plan.py`
- Test: `tests/test_validate_plan.py`

**Dependencies**

Task 1

**Assumptions Verified**

- `skills/write-plan/scripts/validate_plan.py:main` already separates structural
  errors from CLI exit handling; adding a second advisory collection path leaves
  `has_errors` as the only non-zero condition.

**Implementation Steps**

1. Extract each task's `**Files**` block and detect existing-code `Modify:`
   entries and test-file paths from that bounded content only.
2. Emit an advisory when a task modifying existing code lacks
   `**Assumptions Verified**`, and another when a task adding/changing tests
   lacks `**Test Discovery Verified**`.
3. Document the heuristic's deliberately limited signal and ensure advisories
   print while an otherwise valid invocation exits zero.

**Test Discovery Verified**

- The Task 1 `tests/test_validate_plan.py` discovery proof covers the same test
  file that this task changes; run it directly after the validator edit.

**Verification**

- Run: `.venv/bin/python -m pytest tests/test_validate_plan.py -q`
- Expect: each advisory condition is observable and cannot fail a valid plan.

**Done When**

- The validator nudges missing grounding/discovery evidence without claiming it
  can judge the truth of free prose.

### Task 3: Strengthen the `write-plan` workflow and template

**Objective**

Make target-specific evidence, resolve-now discipline, irreducible-risk triage,
and test discovery part of a plan author's normal workflow.

**Files**

- Modify: `skills/write-plan/SKILL.md`
- Modify: `skills/write-plan/assets/plan-template.md`
- Modify: `skills/write-plan/references/seam-selection.md`
- Modify: `skills/write-plan/commands/workflows/plan.md`

**Dependencies**

Task 2

**Assumptions Verified**

- The canonical skill, template, seam reference, and command wrapper each
  independently instruct planners today; all four must agree to avoid a wrapper
  or scaffold silently restoring the old behavior.

**Implementation Steps**

1. Require existing-code tasks to cite the exact edited file/symbol in
   `**Assumptions Verified**`; label cross-file precedents as research context.
2. State that create-only tasks do not need an invented target-file citation;
   they may carry labeled research context when useful.
3. Require current, answerable questions to be resolved before steps are written;
   limit risks to irreducible future uncertainty with a signal and mitigation.
4. Require test-changing tasks to record runner discovery evidence and a command
   that runs the literal new test.
5. Explain the validator's advisory scope and have the wrapper reject a source
   spec whose contract-affecting questions remain open.

**Verification**

- Run: `.venv/bin/python -m pytest tests/test_validate_plan.py -q`
- Run: `python3 skills/write-plan/scripts/validate_plan.py docs/plans --strict-filename`
- Expect: advisory regression tests pass; historic plans remain structurally
  valid, with any heuristic messages non-blocking.

**Done When**

- New plans distinguish verified target facts, research context, resolvable
  questions, irreducible risk, and test-discovery proof.

### Task 4: Add `write-spec` decision readiness and uncertainty triage

**Objective**

Help agents and users settle contract-affecting decisions before planning while
handling unknown unknowns proportionately rather than with a pretend-complete
checklist.

**Files**

- Modify: `skills/write-spec/SKILL.md`
- Modify: `skills/write-spec/assets/spec-template.md`
- Modify: `skills/write-spec/commands/workflows/spec.md`
- Create: `skills/write-spec/references/uncertainty-triage.md`

**Dependencies**

Task 3

**Assumptions Verified**

- `write-spec` owns the mechanism-free contract and the handoff to
  `write-plan`; its current `Open Questions` template permits decisions to close
  during execution, making the template and handoff the smallest correction seam.

**Implementation Steps**

1. Add a short decision-readiness pass: inspect what can be answered locally,
   ask the user only contract-changing questions, and classify what remains.
2. Define blocking decisions, irreducible future uncertainty, and deferred
   future choices; only the middle category remains in the current contract.
3. Add proportionate unknown-unknown lenses for relevant work—other consumers,
   bad input/boundaries, dependencies/failure, and detection/containment—and
   route high-stakes analysis or missing evidence to existing sibling skills.
4. Require a settled contract before handoff; retain an explicit `None` form for
   a contract with no open questions.
5. Keep the template and wrapper aligned and route depth to the new reference.

**Verification**

- Run: `python3 skills/write-spec/scripts/validate_spec.py docs/specs --strict-filename`
- Run: `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills write-spec --strict`
- Expect: existing specs remain valid and the enhanced public workflow passes
  its strict contract checks.

**Done When**

- `write-spec` converts resolvable uncertainty into decisions before planning and
  records only bounded, non-contract-changing uncertainty for the current work.

### Task 5: Release, regenerate, and record the shipped backlog work

**Objective**

Publish coherent, versioned skill changes and leave the future-only backlog
accurate without touching the concurrent roadmap relocation.

**Files**

- Create: `skills/write-plan/CHANGELOG.md`
- Create: `skills/write-spec/CHANGELOG.md`
- Modify: `skills/write-plan/SKILL.md`
- Modify: `skills/write-spec/SKILL.md`
- Modify: `skills.json`
- Modify: `docs/catalog/index.html`
- Modify: `docs/project/BACKLOG.md`

**Dependencies**

Tasks 3 and 4

**Assumptions Verified**

- Release validation treats all skill contents except generated adapters and a
  changelog as release-relevant; workflow-contract changes require SemVer and a
  matching in-skill changelog entry.

**Implementation Steps**

1. Apply the appropriate workflow-contract version increases and changelog
   entries for both skills.
2. Regenerate manifest/catalog artifacts through repository generators.
3. Remove the three now-shipped `write-plan` items from the future-only backlog.
4. Leave the user-owned roadmap deletion/addition unchanged and report that
   exclusion explicitly.

**Verification**

- Run: `.venv/bin/python -m pytest tests/ -q`
- Run: `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict`
- Run: `python3 skills/skill-evals/scripts/check_skill_versions.py --base origin/main`
- Run: `python3 scripts/generate_skills_manifest.py --check`
- Run: `python3 scripts/gen_harness_adapters.py --check --skip-symlinks`
- Run: `python3 scripts/gen_catalog.py --check`
- Run: `git diff --check`
- Expect: tests and contract/release/generated checks pass, and the diff has no
  whitespace errors.

**Done When**

- Both skills are released with their generated inventory in sync, and the
  completed backlog notes are gone without overwriting user-owned work.

## Risks And Mitigations

- Risk: heuristics misclassify free-form plans.
  Mitigation: inspect bounded `Files` blocks only and keep messages advisory.
- Risk: "unknown unknown" guidance becomes ceremony.
  Mitigation: make lenses proportionate and route depth to a short reference.
- Risk: scope/verification decisions still leak from specs into plans.
  Mitigation: make the contract-handoff readiness rule explicit in both skills.
- Risk: concurrent roadmap relocation is overwritten.
  Mitigation: do not edit either user-owned roadmap path in this work.

## Verification Matrix

| Requirement | Proof command | Expected signal |
| --- | --- | --- |
| Advisory grounding stays non-blocking | `.venv/bin/python -m pytest tests/test_validate_plan.py -q` | advisory cases pass and valid CLI invocation exits zero |
| Historic plans remain schema-valid | `python3 skills/write-plan/scripts/validate_plan.py docs/plans --strict-filename` | all existing plans pass structural validation |
| Specs still validate | `python3 skills/write-spec/scripts/validate_spec.py docs/specs --strict-filename` | all stored specs pass |
| New test is discovered | `.venv/bin/python -m pytest tests/test_validate_plan.py -q` | collected test file runs |
| Public skill releases are coherent | `python3 skills/skill-evals/scripts/check_skill_versions.py --base origin/main` | both changed skills have valid versions/changelogs |
| Generated artifacts are current | `python3 scripts/generate_skills_manifest.py --check && python3 scripts/gen_catalog.py --check` | no manifest or catalog drift |

## Handoff

1. Execute Tasks 1–5 in this session, then mark this plan complete.
2. Review the completed diff inline against the grounding and decision-readiness
   requirements; subagent review is intentionally unavailable in this session.
3. Commit the complete implementation as coherent workflow-improvement work;
   do not push unless requested.
