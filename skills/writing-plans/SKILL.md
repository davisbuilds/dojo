---
name: writing-plans
description: Create robust, execution-ready implementation plans with explicit scope, task sequencing, dependencies, and verification commands before coding.
---

# Writing Plans

Create implementation plans that are executable, auditable, and easy for a zero-context engineer to follow.

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
`I'm using the writing-plans skill to create a robust implementation plan.`

If key context is missing, ask focused questions before writing:
- goal and non-goals
- constraints
- acceptance criteria
- affected files or systems (if known)

## Output Path

Save plan to:
`docs/plans/YYYY-MM-DD-<topic>-implementation.md`

If a brainstorm summary exists at `docs/plans/YYYY-MM-DD-<topic>-plan.md`, reuse its topic slug.

## Output Contract

Every implementation plan must include YAML frontmatter and the required sections below.

### Required Frontmatter

```yaml
---
date: YYYY-MM-DD
topic: <kebab-case-topic>
stage: implementation-plan
status: draft
source: conversation
---
```

### Required Sections

1. `# <Title> Implementation Plan`
2. `## Goal`
3. `## Scope`
4. `## Assumptions And Constraints`
5. `## Task Breakdown`
6. `## Risks And Mitigations`
7. `## Verification Matrix`
8. `## Handoff`

Use `assets/implementation-plan-template.md` as the default scaffold.

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
- Do not claim plan readiness until verification coverage is explicit.

If available, apply the mindset from `verification-before-completion` when checking final plan quality.

## Conditional Coordination

Route to another skill only when needed:
- requirements unclear: use `brainstorming`
- architectural trade-off dominates risk: use `first-principles`
- CLI contract design is central: use `create-cli`
- user asks for autonomous execution after planning: use `autonomous-engineering` or manual execution

If a named skill is unavailable, continue with manual fallback in this skill.

## Plan Validation

After writing a plan, run:

```bash
python3 skills/writing-plans/scripts/validate_plan.py docs/plans/<filename>.md
```

Fix all reported issues before handoff.

## Handoff

End with:
`Plan complete and saved to docs/plans/<filename>.md.`

Then offer:
1. Execute in this session, task by task.
2. Open a separate execution session.
3. Refine the plan before implementation.

## Command Wrapper

If command files are supported, use `commands/workflows/plan.md` as the canonical `/workflows:plan` wrapper.
