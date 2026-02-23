---
date: 2026-02-21
topic: gemini-imagen-design
stage: implementation-plan
status: migrated
source: conversation
---

# Gemini Imagen Design Implementation Plan

## Goal

Define a single, agent-agnostic `gemini-imagen` skill design that can be implemented without relying on platform-specific paths or stale defaults.

## Scope

### In Scope

- Consolidating design decisions from prior `nano-banana-pro` and `gemini-imagegen` skills.
- Defining the final target directory and script surface.
- Defining migration cleanup requirements and acceptance checks.

### Out of Scope

- Implementing the merged skill code.
- Publishing or releasing packaged artifacts.

## Assumptions And Constraints

- Skill structure must comply with the repository skill spec.
- Script execution should remain runnable via `uv run` with inline metadata.
- Design must be model/harness-agnostic and avoid hardcoded home-directory paths.

## Task Breakdown

### Task 1: Capture overlap and gaps between source skills

**Objective**

Establish which behaviors to keep, remove, or modernize before implementation.

**Files**

- Modify: `docs/plans/2026-02-21-gemini-imagen-design-implementation.md`

**Dependencies**

None

**Implementation Steps**

1. Compare operational content from `nano-banana-pro` with reference content from `gemini-imagegen`.
2. Record missing capabilities and stale defaults.
3. Lock in required behavior parity for generate/edit/compose flows.

**Verification**

- Run: `rg -n "nano-banana-pro|gemini-imagegen|gemini-imagen" docs/plans/2026-02-21-gemini-imagen-design-implementation.md`
- Expect: references to both source skills and the merged target skill.

**Done When**

- The plan states clear keep/remove criteria for both source skills.
- The merge rationale is explicit and unambiguous.

### Task 2: Define canonical merged skill structure

**Objective**

Specify a single directory and script contract that future implementation follows.

**Files**

- Modify: `docs/plans/2026-02-21-gemini-imagen-design-implementation.md`

**Dependencies**

Task 1

**Implementation Steps**

1. Define `skills/gemini-imagen/` as the only target directory.
2. Define `scripts/generate_image.py` as the single entrypoint with three subcommands.
3. Define model, resolution, and image-format defaults.

**Verification**

- Run: `rg -n "skills/gemini-imagen|generate_image.py|generate|edit|compose" docs/plans/2026-02-21-gemini-imagen-design-implementation.md`
- Expect: all key structure and command surface elements are present.

**Done When**

- Directory and script contracts are fully specified.
- Default behavior is documented for all subcommands.

### Task 3: Define migration and cleanup actions

**Objective**

List exact repo changes needed after merged skill implementation completes.

**Files**

- Modify: `docs/plans/2026-02-21-gemini-imagen-design-implementation.md`

**Dependencies**

Task 2

**Implementation Steps**

1. Specify old skill directories to remove.
2. Specify manifest and docs updates required after merge.
3. Add acceptance checks for final repository state.

**Verification**

- Run: `rg -n "Delete|remove|skills.json|CLAUDE.md" docs/plans/2026-02-21-gemini-imagen-design-implementation.md`
- Expect: cleanup and post-merge update steps are explicitly listed.

**Done When**

- Cleanup requirements include concrete paths and expected outcomes.
- Post-merge verification checks are present.

### Task 4: Approve design for implementation handoff

**Objective**

Confirm design is actionable and ready for implementation planning.

**Files**

- Modify: `docs/plans/2026-02-21-gemini-imagen-design-implementation.md`

**Dependencies**

Tasks 1-3

**Implementation Steps**

1. Review design document for missing implementation decisions.
2. Confirm no platform-specific assumptions remain.
3. Mark the document as migration-ready for implementation planning.

**Verification**

- Run: `python3 skills/writing-plans/scripts/validate_plan.py docs/plans/2026-02-21-gemini-imagen-design-implementation.md --strict-filename`
- Expect: validator reports PASS.

**Done When**

- The document passes the writing-plans validator.
- The design can be executed without additional architectural clarification.

## Risks And Mitigations

- Risk: design omits critical implementation detail for one subcommand.
  Mitigation: require explicit behavior notes for generate, edit, and compose before handoff.
- Risk: migration leaves stale references to retired skills.
  Mitigation: include cleanup verification checks and manifest/doc updates in plan tasks.

## Verification Matrix

| Requirement | Proof command | Expected signal |
| --- | --- | --- |
| Plan follows implementation-plan schema | `python3 skills/writing-plans/scripts/validate_plan.py docs/plans/2026-02-21-gemini-imagen-design-implementation.md --strict-filename` | PASS |
| Merged skill contract is explicit | `rg -n "skills/gemini-imagen|generate_image.py" docs/plans/2026-02-21-gemini-imagen-design-implementation.md` | Contract lines found |
| Cleanup scope is explicit | `rg -n "Delete|remove|skills.json|CLAUDE.md" docs/plans/2026-02-21-gemini-imagen-design-implementation.md` | Cleanup actions found |

## Handoff

1. Execute the corresponding implementation plan in this session.
2. Open a separate execution session for implementation.
3. Refine this design plan if new constraints appear.
