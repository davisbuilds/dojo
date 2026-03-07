# SKILL Contract v1

Date: 2026-03-07
Scope: All `skills/*/SKILL.md` files in this repository.

This contract defines a deterministic checklist for skill quality. It is designed for enforcement by `skills/skill-evals/scripts/validate_skill_contract.py`.

## Required Checks (must pass)

1. `frontmatter_valid`
   - SKILL has valid frontmatter and passes `skill-creator` quick validation.

2. `description_trigger_ready`
   - Frontmatter description includes trigger-ready language (for example: `use when`, `when the user`, `triggers on`, `on-demand via`).

3. `execution_anchor_present`
   - Body includes a clear execution anchor through at least one of:
     - a workflow/process heading (`Workflow`, `Process`, `Core Workflow`, etc.)
     - commands/usage heading (`Commands`, `Usage`, `Quick Start`, etc.)
     - a numbered step sequence (`1.`, `2.`, `3.`)

## Recommended Checks (warn on fail by default)

4. `scope_anchor_present`
   - Includes `When to use`/`When to apply`/`Prerequisites` style scope section.

5. `boundaries_anchor_present`
   - Includes explicit non-goals or boundaries (`Not for`, `Skip`, `Constraints`, `Anti-patterns`, etc.).

6. `output_anchor_present`
   - Defines output contract/deliverables/summary expectations.

7. `verification_anchor_present`
   - Defines quality/verification/success criteria.

8. `resource_map_present`
   - If skill bundles resources (`scripts/`, `references/`, `assets/`, `commands/`), SKILL.md points to them clearly.

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
