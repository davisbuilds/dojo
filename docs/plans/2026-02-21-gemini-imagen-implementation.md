---
date: 2026-02-21
topic: gemini-imagen
stage: implementation-plan
status: migrated
source: conversation
---

# Gemini Imagen Implementation Plan

## Goal

Merge `nano-banana-pro` and `gemini-imagegen` into a single, agent-agnostic `gemini-imagen` skill with one executable script and one canonical SKILL document.

## Scope

### In Scope

- Build `skills/gemini-imagen/scripts/generate_image.py` with `generate`, `edit`, and `compose` subcommands.
- Create canonical `skills/gemini-imagen/SKILL.md`.
- Remove superseded skill folders.
- Update catalog documentation and manifest outputs.

### Out of Scope

- Multi-provider abstraction beyond Gemini.
- Non-image modalities and hosted runtime workflows.

## Assumptions And Constraints

- Runtime target is Python 3.10+.
- Dependencies are declared in PEP 723 script metadata.
- Output should be compatible across harnesses that can run local scripts.

## Task Breakdown

### Task 1: Create unified image script

**Objective**

Implement a single script entrypoint that supports generate/edit/compose and shared argument handling.

**Files**

- Create: `skills/gemini-imagen/scripts/generate_image.py`

**Dependencies**

None

**Implementation Steps**

1. Create the script with PEP 723 metadata (`google-genai`, `pillow`).
2. Implement `generate`, `edit`, and `compose` subcommands via `argparse` subparsers.
3. Implement shared helpers for API key resolution, config building, and format-aware image save.
4. Implement edit-resolution autodetection and compose input count validation.

**Verification**

- Run: `uv run skills/gemini-imagen/scripts/generate_image.py generate --help`
- Expect: help output includes required generate flags.
- Run: `uv run skills/gemini-imagen/scripts/generate_image.py edit --help`
- Expect: help output includes `--input-image`.
- Run: `uv run skills/gemini-imagen/scripts/generate_image.py compose --help`
- Expect: help output includes `--input-images`.

**Done When**

- All three subcommands parse and expose expected options.
- Script exits with non-zero status when no image is returned.

### Task 2: Create canonical skill documentation

**Objective**

Publish one SKILL.md that combines operational workflow guidance and reference-quality API notes.

**Files**

- Create: `skills/gemini-imagen/SKILL.md`

**Dependencies**

Task 1

**Implementation Steps**

1. Add valid frontmatter (`name`, `description`).
2. Document usage examples for generate/edit/compose invocation.
3. Document defaults, API key precedence, aspect ratios, and resolution guidance.
4. Document preflight checks, prompt templates, and common failure handling.

**Verification**

- Run: `python3 skills/skill-creator/scripts/quick_validate.py skills/gemini-imagen`
- Expect: `Skill is valid!`

**Done When**

- SKILL.md is validator-compliant.
- Script usage and behavior expectations are fully documented.

### Task 3: Remove superseded skills

**Objective**

Eliminate overlapping legacy skills after replacement is in place.

**Files**

- Delete: `skills/nano-banana-pro/`
- Delete: `skills/gemini-imagegen/`

**Dependencies**

Tasks 1-2

**Implementation Steps**

1. Remove `skills/nano-banana-pro/`.
2. Remove `skills/gemini-imagegen/`.
3. Regenerate or confirm manifest updates.

**Verification**

- Run: `ls skills/nano-banana-pro 2>&1`
- Expect: `No such file or directory`.
- Run: `ls skills/gemini-imagegen 2>&1`
- Expect: `No such file or directory`.
- Run: `python3 scripts/generate_skills_manifest.py`
- Expect: manifest regenerates successfully.

**Done When**

- Legacy skill directories no longer exist.
- `skills.json` contains `gemini-imagen` and excludes removed skills.

### Task 4: Update repo documentation and manifest references

**Objective**

Ensure user-facing docs and machine-readable catalog reflect the merged skill.

**Files**

- Modify: `CLAUDE.md`
- Modify: `skills.json`

**Dependencies**

Task 3

**Implementation Steps**

1. Update skills tables to include `skills/gemini-imagen/`.
2. Remove stale references to removed skills.
3. Regenerate `skills.json` after SKILL changes.

**Verification**

- Run: `rg -n "gemini-imagen|nano-banana-pro|gemini-imagegen" CLAUDE.md skills.json`
- Expect: `gemini-imagen` present; old skills absent.

**Done When**

- Documentation and manifest reflect only the new merged skill.

### Task 5: Final validation and publish readiness check

**Objective**

Confirm merged skill structure is complete and operational before final handoff.

**Files**

- Modify: `docs/plans/2026-02-21-gemini-imagen-implementation.md`

**Dependencies**

Tasks 1-4

**Implementation Steps**

1. Verify final folder layout and executable script presence.
2. Re-run parser help checks for all subcommands.
3. Validate this plan document under the new writing-plans schema.

**Verification**

- Run: `ls skills/gemini-imagen/`
- Expect: includes `SKILL.md` and `scripts/`.
- Run: `ls skills/gemini-imagen/scripts/`
- Expect: includes `generate_image.py`.
- Run: `python3 skills/writing-plans/scripts/validate_plan.py docs/plans/2026-02-21-gemini-imagen-implementation.md --strict-filename`
- Expect: PASS.

**Done When**

- Skill directory is complete and script is discoverable.
- Plan validates under the current writing-plans contract.

## Risks And Mitigations

- Risk: behavioral regressions during merge remove useful features.
  Mitigation: explicit task coverage for generate/edit/compose parity and docs validation.
- Risk: stale references remain in docs/manifest.
  Mitigation: grep-based checks and manifest regeneration step.

## Verification Matrix

| Requirement | Proof command | Expected signal |
| --- | --- | --- |
| Implementation plan schema compliance | `python3 skills/writing-plans/scripts/validate_plan.py docs/plans/2026-02-21-gemini-imagen-implementation.md --strict-filename` | PASS |
| Skill docs are valid | `python3 skills/skill-creator/scripts/quick_validate.py skills/gemini-imagen` | `Skill is valid!` |
| Legacy skills removed | `ls skills/nano-banana-pro 2>&1 && ls skills/gemini-imagegen 2>&1` | Both report missing directories |
| Merged skill is discoverable | `rg -n "gemini-imagen" skills.json` | At least one manifest entry |

## Handoff

1. Execute implementation tasks in this session.
2. Open a separate execution session for implementation.
3. Refine task details before coding.
