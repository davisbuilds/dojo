---
name: write-spec
description: Create robust, execution-ready specs (detailed implementation plans) with explicit scope, task sequencing, dependencies, and verification commands. Use when planning non-trivial implementation work before coding, or when asked for an implementation plan.
skill-type: workflow
---

# Write Spec

Create specs that are executable, auditable, and easy for a zero-context engineer to follow.

## When To Use

Use this skill when:
- requirements are clear enough to sequence implementation
- the work spans multiple files or phases
- explicit verification gates are needed before coding

Skip this skill when:
- the change is a tiny mechanical edit
- the user asks for immediate implementation and scope is trivial
- requirements are still ambiguous (route to `brainstorming` first)

## Start Behavior

Start with:
`I'm using the write-spec skill to create a robust spec.`

If key context is missing, ask focused questions before writing:
- goal and non-goals
- constraints
- acceptance criteria
- affected files or systems (if known)

## Output Path

Save spec to:
`docs/specs/YYYY-MM-DD-<topic>-spec.md`

If a brainstorm summary exists at `docs/plans/YYYY-MM-DD-<topic>-plan.md`, reuse its topic slug.

## Output Contract

Every spec must include YAML frontmatter and the required sections below.

### Required Frontmatter

```yaml
---
date: YYYY-MM-DD
topic: <kebab-case-topic>
stage: spec
status: draft
source: conversation
---
```

`status:` is born `draft` and follows the lifecycle `draft → in-progress →
complete` (terminal synonyms: `shipped`, `implemented`, `superseded`). Update it
honestly as the work lands — completed specs are swept out of `docs/plans/` and
`docs/specs/` into a gitignored `docs/archive/<category>/` by
`ops/scripts/archive_plans.py`, which keys off this field. A spec left at the
wrong `status` is either archived prematurely or lingers in the tracked tree.

### Required Sections

1. `# <Title> Spec`
2. `## Goal`
3. `## Scope`
4. `## Assumptions And Constraints`
5. `## Task Breakdown`
6. `## Risks And Mitigations`
7. `## Verification Matrix`
8. `## Handoff`

Use `assets/spec-template.md` as the default scaffold.

## Task Design Rules

Each task must be independently verifiable and include:
- `### Task N: <name>`
- `**Objective**`
- `**Files**` with exact repository paths
- `**Dependencies**` (or `None`)
- `**Implementation Steps**` as ordered steps
- `**Verification**` commands with expected signals
- `**Done When**` acceptance bullets

Granularity target:
- one meaningful unit of behavior per task
- usually 10-30 minutes of focused work
- avoid over-fragmented 2-minute steps unless risk demands it

## Verification Requirements

- Include at least one concrete verification command per task.
- Include integration or end-to-end verification when applicable.
- Add negative-path verification for risky logic.
- Do not claim spec readiness until verification coverage is explicit.

If available, apply the mindset from `verify-before-complete` when checking final spec quality.

## Conditional Coordination

Route to another skill only when needed:
- requirements unclear: use `brainstorming`
- architectural trade-off dominates risk: use `first-principles`
- CLI contract design is central: use `create-cli`
- user asks for autonomous execution after the spec: use `autonomous-engineering` or manual execution

If a named skill is unavailable, continue with manual fallback in this skill.

## Spec Validation

After writing a spec, run:

```bash
python3 skills/write-spec/scripts/validate_spec.py docs/specs/<filename>.md
```

Fix all reported issues before handoff.

## Handoff

End with:
`Spec complete and saved to docs/specs/<filename>.md.`

Then offer:
1. Execute in this session, task by task.
2. Open a separate execution session.
3. Refine the spec before implementation.

## Command Wrapper

If command files are supported, use `commands/workflows/spec.md` as the canonical `/workflows:spec` wrapper.

## Sibling skills

Pre-execution thinking pipeline: **brainstorm → reason → research → spec**.

- `brainstorming` — upstream. Use when WHAT is ambiguous; come here once direction is clear and HOW needs structuring.
- `first-principles` — upstream for high-stakes specs. Use it when the spec hinges on a non-obvious architectural decision.
- `deep-research` — parallel. Use when the spec needs evidence (library behavior, prior art, current docs).
