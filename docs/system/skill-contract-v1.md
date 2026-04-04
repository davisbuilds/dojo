# SKILL Contract v1

Date: 2026-04-04
Scope: All `skills/*/SKILL.md` files in this repository.

This contract defines a deterministic checklist for skill quality. It is designed for enforcement by `skills/skill-evals/scripts/validate_skill_contract.py`.

## Skill Types

Skills declare a `skill-type` frontmatter field to express the structural shape they are expected to follow.

Allowed values:

- `workflow`
  - For procedural, audit, remediation, review, planning, or command-oriented skills that should define how work gets executed and what the output should contain.
- `reference`
  - For reference routers, guideline catalogs, and best-practice indexes that are primarily navigational and informational rather than procedural.

Current repo state:

- The catalog is fully typed.
- New and updated skills should continue to declare `skill-type`.
- For robustness, untyped skills still default to `workflow` behavior if one appears in the future.

## Universal Required Checks (must pass)

1. `frontmatter_valid`
   - SKILL has valid frontmatter and passes `skill-creator` quick validation.

2. `description_trigger_ready`
   - Frontmatter description includes trigger-ready language (for example: `use when`, `when the user`, `triggers on`, `on-demand via`).

3. `scope_anchor_present`
   - Includes `When to use`/`When to apply`/`Prerequisites` style scope section.

4. `boundaries_anchor_present`
   - Includes explicit non-goals or boundaries (`Not for`, `Skip`, `Constraints`, `Anti-patterns`, etc.).

5. `verification_anchor_present`
   - Defines quality/verification/success criteria.

6. `resource_map_present`
   - If skill bundles resources (`scripts/`, `references/`, `assets/`, `commands/`), SKILL.md points to them clearly.

## Type-Specific Structural Checks

### `workflow`

These checks are required for `workflow` skills and for any untyped skill that falls back to `workflow` behavior:

7. `execution_anchor_present`
   - Body includes a clear execution anchor through at least one of:
     - a workflow/process heading (`Workflow`, `Process`, `Core Workflow`, etc.)
     - commands/usage heading (`Commands`, `Usage`, `Quick Start`, etc.)
     - a numbered step sequence (`1.`, `2.`, `3.`)

8. `output_anchor_present`
   - Defines output contract/deliverables/summary expectations.

### `reference`

For `reference` skills:

- `execution_anchor_present` is not applicable.
- `output_anchor_present` is not applicable.
- Reference skills should still define scope, boundaries, verification, and resource navigation clearly.

## Recommended Checks (warn on fail by default)

9. `context_budget`
   - SKILL.md line count guidance:
     - <=500: pass
     - 501-700: warn
     - >700: warn (needs decomposition plan)

## Status Rules

- `pass`: all required checks pass and no warnings.
- `warn`: all required checks pass, one or more recommended checks warn.
- `fail`: one or more required checks fail.

Use `--strict` to treat recommended checks as failures.
