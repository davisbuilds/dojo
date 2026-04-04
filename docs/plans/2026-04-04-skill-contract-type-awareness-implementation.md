---
date: 2026-04-04
topic: skill-contract-type-awareness
stage: implementation-plan
status: draft
source: conversation
---

# Skill Contract Type Awareness Implementation Plan

## Goal

Introduce type-aware skill-contract validation in `dojo` so reference-style skills are not forced into workflow-only structure requirements while preserving strong deterministic checks for operational skills.

## Scope

### In Scope

- Define a minimal `skill-type` taxonomy for `dojo` skills.
- Extend the skill contract spec and validator behavior to make selected checks conditional on `skill-type`.
- Update frontmatter validation to allow `skill-type`.
- Add a phased migration path for existing skills, including `nextjs-app-router`.
- Update repo documentation so authors know when and how to declare `skill-type`.

### Out of Scope

- Rewriting every existing skill in one pass.
- Designing a large or speculative taxonomy beyond immediate validator needs.
- Changing runtime skill loading behavior outside validation and documentation.
- Broad content rewrites for reference docs that already serve users well.

## Assumptions And Constraints

- The current strict validator is useful, but it overfits workflow-style skills.
- Backward compatibility matters; missing `skill-type` should not create a repo-wide hard break without a migration path.
- `quick_validate.py` and `validate_skill_contract.py` must stay deterministic and easy to reason about.
- The first version should optimize for clarity over exhaustiveness; two or a few types are better than a sprawling taxonomy.
- CI should surface failures clearly enough that future authors understand whether they violated a universal rule or a type-specific rule.

## Task Breakdown

### Task 1: Define The Type System And Contract Rules

**Objective**

Settle the smallest viable `skill-type` model and map each validator check to required, warning, or not-applicable behavior by type.

**Files**

- Modify: `docs/system/skill-contract-v1.md`
- Review: `skills/nextjs-app-router/SKILL.md`
- Review: `skills/repo-hardening/SKILL.md`
- Review: `skills/secure-code/SKILL.md`

**Dependencies**

None

**Implementation Steps**

1. Define the initial `skill-type` values to support current skill shapes, likely starting with `workflow` and `reference`, and only adding more if the existing catalog demands it.
2. Document universal checks that apply to every skill, such as valid frontmatter, trigger-ready descriptions, scope, boundaries, verification, and resource mapping when bundled resources exist.
3. Document type-specific checks, especially that `execution_anchor_present` and `output_anchor_present` remain required for workflow-like skills but downgrade to warnings or non-required checks for reference-style skills.
4. Write an explicit migration note in the contract describing default behavior for skills that omit `skill-type` during the transition period.

**Verification**

- Review: `rg -n "execution_anchor_present|output_anchor_present|Required Checks|Recommended Checks" docs/system/skill-contract-v1.md`
- Expect: the contract clearly distinguishes universal rules from type-specific rules and explicitly names the migration behavior.

**Done When**

- The contract defines an explicit `skill-type` field and allowed initial values.
- The contract makes it obvious why `nextjs-app-router` is treated differently from workflow skills.
- Migration behavior for missing `skill-type` is written down, not implied.

### Task 2: Make Frontmatter Validation Accept Skill Types

**Objective**

Allow skill authors to declare `skill-type` without failing the quick validator, while constraining values tightly enough to prevent drift.

**Files**

- Modify: `skills/skill-creator/scripts/quick_validate.py`
- Modify: `skills/skill-creator/SKILL.md`
- Modify: `skills/skill-creator/references/skill-frontmatter-spec.md`

**Dependencies**

- Task 1

**Implementation Steps**

1. Add `skill-type` to the allowed frontmatter keys in `quick_validate.py`.
2. Validate that `skill-type`, when present, is a string and matches the allowed taxonomy from Task 1.
3. Update the authoring guidance in `skill-creator` so new skills are taught the new field and its intended use.
4. Keep the validator message crisp so authors see both the allowed key and the allowed values when they make a mistake.

**Verification**

- Run: `python3 skills/skill-creator/scripts/quick_validate.py skills/repo-hardening`
- Expect: existing workflow-style skill still validates after the frontmatter rule change.
- Run: `python3 skills/skill-creator/scripts/quick_validate.py skills/nextjs-app-router`
- Expect: the skill validates once `skill-type` is added in the migration task.

**Done When**

- `quick_validate.py` accepts the new field and rejects unknown values cleanly.
- Skill-authoring docs mention `skill-type` and when to use it.

### Task 3: Make Contract Evaluation Type-Aware

**Objective**

Update the strict validator so the required/warn behavior of checks depends on `skill-type` instead of assuming one structure fits every skill.

**Files**

- Modify: `skills/skill-evals/scripts/validate_skill_contract.py`
- Modify: `.github/workflows/skill-contract-pilot.yml`

**Dependencies**

- Task 1
- Task 2

**Implementation Steps**

1. Parse `skill-type` from frontmatter in `validate_skill_contract.py`.
2. Introduce a small rule table that maps each check to required or warning status by type instead of scattering conditionals across the evaluator.
3. Preserve sensible behavior for missing `skill-type` during migration, preferably by treating those skills as the current stricter default until they are explicitly classified, or by using a documented transitional fallback chosen in Task 1.
4. Improve report output so the evaluator can explain both the failing check and the relevant skill type when useful.
5. Ensure CI output remains understandable after the change and still uploads machine-readable artifacts.

**Verification**

- Run: `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict --skill nextjs-app-router`
- Expect: `nextjs-app-router` fails only on checks still intended to apply to its declared type, or passes once the migration task is complete.
- Run: `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict --skill repo-hardening`
- Expect: `repo-hardening` still passes as a workflow-style skill.
- Run: `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict`
- Expect: output clearly identifies any remaining unclassified or noncompliant skills.

**Done When**

- The validator has a deterministic type-to-rules mapping.
- Reference skills are no longer forced to invent workflow sections just to satisfy the contract.
- Workflow skills still receive strong structural enforcement.

### Task 4: Backfill Skill Types And Fix Immediate Failures

**Objective**

Classify the current skill catalog incrementally, starting with the skills already blocked by the uniform contract and a small representative sample across categories.

**Files**

- Modify: `skills/nextjs-app-router/SKILL.md`
- Modify: `skills/repo-hardening/SKILL.md`
- Modify: `skills/secure-code/SKILL.md`
- Modify: `skills/writing-plans/SKILL.md`
- Modify: `skills/*/SKILL.md` as needed for the first migration slice

**Dependencies**

- Task 2
- Task 3

**Implementation Steps**

1. Add `skill-type` to `nextjs-app-router` as the first reference-skill migration and confirm it behaves correctly under strict validation.
2. Add `skill-type` to a small set of workflow-style skills to validate the positive path for the new rules.
3. If any existing skill no longer fits the intended taxonomy cleanly, either reclassify it or split the taxonomy only when a concrete mismatch exists.
4. Leave a clear queue for the remaining catalog rather than forcing a giant one-shot backfill.

**Verification**

- Run: `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict --skill nextjs-app-router --skill repo-hardening --skill secure-code --skill writing-plans`
- Expect: the representative sample validates under the new type-aware contract.
- Run: `rg -n "^skill-type:" skills/*/SKILL.md`
- Expect: the first migration slice is visibly classified.

**Done When**

- `nextjs-app-router` no longer fails for workflow-only expectations that do not fit its purpose.
- At least one reference skill and multiple workflow skills are classified and passing.
- The remaining migration backlog is explicit and bounded.

### Task 5: Document The Authoring And Migration Model

**Objective**

Make the new model discoverable so future skill authors apply the contract correctly without reverse-engineering validator code.

**Files**

- Modify: `README.md`
- Modify: `AGENTS.md`
- Modify: `docs/system/FEATURES.md`
- Modify: `docs/system/skill-contract-v1.md`
- Modify: `skills/skill-creator/SKILL.md`

**Dependencies**

- Task 1
- Task 2
- Task 3

**Implementation Steps**

1. Update the human-facing docs where skill-authoring norms are described so `skill-type` and type-aware validation are visible.
2. Add a short migration note describing how existing untyped skills will be treated until fully backfilled.
3. Keep the guidance concise: what the types are, when to use them, and which validator expectations differ.
4. Ensure the docs point authors back to the contract spec instead of duplicating long rule tables everywhere.

**Verification**

- Run: `rg -n "skill-type|type-aware|reference skill|workflow skill" README.md AGENTS.md docs/system/FEATURES.md docs/system/skill-contract-v1.md skills/skill-creator/SKILL.md`
- Expect: the new model is documented in the contract and discoverable from author-facing docs.

**Done When**

- A new contributor can understand the type system without reading validator internals.
- The contract spec remains the canonical source of truth.

## Risks And Mitigations

- Risk: The taxonomy becomes too broad too early.
  Mitigation: start with the smallest viable set, likely `workflow` and `reference`, and expand only when a real skill cannot be classified cleanly.
- Risk: Missing `skill-type` creates confusing mixed behavior during migration.
  Mitigation: document one explicit default behavior in the contract and reflect it in validator output.
- Risk: Validator logic becomes harder to maintain once checks are conditional.
  Mitigation: centralize type-to-check policy in a small rule table instead of duplicating branching logic per check.
- Risk: Authors game the contract by labeling weak workflow skills as `reference`.
  Mitigation: keep trigger, scope, boundaries, verification, and resource-map requirements universal, and document type intent in authoring guidance.
- Risk: The migration stalls after fixing only `nextjs-app-router`.
  Mitigation: require a first representative batch of typed skills and leave a visible backlog for the rest.

## Verification Matrix

| Requirement | Proof command | Expected signal |
| --- | --- | --- |
| Contract documents type-aware rules | `rg -n "skill-type|Required Checks|Recommended Checks|reference|workflow" docs/system/skill-contract-v1.md` | Spec shows explicit type system and conditional rule descriptions |
| Frontmatter validator accepts the new field | `python3 skills/skill-creator/scripts/quick_validate.py skills/repo-hardening` | Command exits 0 and prints `Skill is valid!` |
| Reference skill validates under new model | `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict --skill nextjs-app-router` | Output no longer fails solely because workflow/output anchors are absent for a reference skill |
| Workflow skill still validates under strict rules | `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict --skill repo-hardening` | Output remains passing for workflow-oriented structure |
| Representative migration slice is visible | `rg -n "^skill-type:" skills/*/SKILL.md` | Typed skills appear in the expected first migration set |
| Full repo contract run stays understandable | `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict` | Report clearly distinguishes remaining migration work from true structural regressions |

## Handoff

1. Implement Task 1 through Task 3 first so the taxonomy, frontmatter, and validator behavior move together.
2. Use Task 4 to migrate `nextjs-app-router` immediately and classify a small representative batch before widening the backfill.
3. Finish with Task 5 so the new model is documented before more authors start creating or editing skills.

Plan complete and saved to docs/plans/2026-04-04-skill-contract-type-awareness-implementation.md.
