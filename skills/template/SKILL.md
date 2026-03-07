---
name: template
description: Skill starter template. Use when creating a new skill and you need a minimal scaffold with trigger language, workflow steps, and output expectations.
---

# Skill Template

## When To Use

Use this template when bootstrapping a new skill directory and drafting first-pass instructions.

## Workflow

1. Replace frontmatter name/description with the target skill.
2. Add core instructions for scope, execution, and boundaries.
3. Add `scripts/`, `references/`, and `assets/` only if needed.
4. Validate with `python3 skills/skill-creator/scripts/quick_validate.py <skill-path>`.

## Boundaries

- This template is a starting point; do not ship it unmodified as a real skill
- Do not add resource folders unless the skill genuinely needs them

## Output Contract

- A valid `SKILL.md` with trigger-ready description
- Lean instructions with clear execution anchors
- Optional resource folders only where justified

## Verification

- `quick_validate.py` passes on the generated skill directory
- Frontmatter name matches directory name
- Description includes trigger-ready language
