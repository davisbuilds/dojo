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

## Optional Frontmatter Extensions

These are dojo-specific extensions beyond the upstream `spec/agent-skills-spec.md`. They are optional; absence never fails the contract.

### `triggers`

A list of literal trigger phrases that should route to this skill (for example, the exact things a user might type or ask).

```yaml
triggers:
  - review this pr
  - code review
  - check my diff
```

Rationale: `description` carries trigger-ready *prose* (see `description_trigger_ready`), but prose is not directly testable. `triggers` makes routing intent explicit and machine-checkable, so `skills/skill-evals/scripts/run_trigger_evals.py` can assert each declared phrase self-routes to its own skill and flag collisions with other skills. When present, `triggers` must be a non-empty list of non-empty strings. Skills without `triggers` keep the description-inferred behavior unchanged.

## Generated Artifacts (single source of truth)

SKILL.md frontmatter is the source of truth. Two generation steps derive artifacts from it; both are deterministic, idempotent, and expose a `--check` mode that fails on drift:

- **Shared-fragment composition** (`scripts/gen_skill_docs.py`): expands declared shared includes into SKILL.md between `<!-- AUTO-GENERATED -->` markers. **Opt-in only** — a skill that declares no template/includes is never modified.
- **Harness sidecars** (`scripts/gen_harness_adapters.py`): emits per-skill adapter files for each target harness (`.claude/`, `.agents/`, `.agent/`, Codex) from frontmatter. Sidecars are generated artifacts and must not be hand-edited; the compliance `--check` treats hand-edits as drift.

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

10. `triggers_valid`
    - Only applies when the optional `triggers` field is present.
    - Passes when `triggers` is a non-empty list of non-empty strings; warns otherwise.
    - Absent `triggers` is `na` (not a warning).

## Status Rules

- `pass`: all required checks pass and no warnings.
- `warn`: all required checks pass, one or more recommended checks warn.
- `fail`: one or more required checks fail.

Use `--strict` to treat recommended checks as failures.
