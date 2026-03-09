---
name: template
description: Skill starter template with commented guidance for every contract section. Use when creating a new skill and you need a scaffold that passes strict contract validation. Covers frontmatter, scope, workflow, boundaries, output, verification, and resource mapping.
---

# Skill Template

Copy this file to `skills/<your-skill>/SKILL.md` and replace each section.

<!-- DELETE everything between « » after filling in. These are authoring hints. -->

## When To Use

<!-- «Scope anchor — required by contract. List 3-5 concrete situations.» -->

- «Situation where this skill adds value over general agent capability»
- «Second trigger scenario»
- «Third trigger scenario»

## Boundaries

<!-- «Non-goals — required by contract. What this skill does NOT do.» -->

- «Task type this skill should not be used for»
- «Adjacent skill or workflow that handles the excluded case»
- Do not «specific anti-pattern to avoid»

## Workflow

<!-- «Execution anchor — required by contract. Numbered steps or headed phases.» -->

1. «First step — what the agent does and with what input»
2. «Second step»
3. «Third step»
4. «Final step — what the agent produces or hands off»

## Output

<!-- «Output anchor — required by contract. What the user gets.» -->

- «Primary deliverable (file, report, code, etc.)»
- «Secondary deliverable if any»

## Verification

<!-- «Verification anchor — required by contract. How to confirm quality.» -->

- «Testable criterion for the primary output»
- «Second quality check»
- `quick_validate.py` passes on the skill directory

## Resources

<!-- «Resource map — required by contract IF the skill bundles scripts/, references/, assets/, or commands/. Delete this section if no resources exist.» -->

- `scripts/«name».sh` — «what it does»
- `references/«name».md` — «what it contains»

---

## Authoring Checklist

Use this checklist before shipping. All items are enforced by `validate_skill_contract.py --strict`:

- [ ] Frontmatter `name` is hyphen-case, matches directory name, max 64 chars
- [ ] Frontmatter `description` includes trigger language (`Use when...`, `Triggers on...`)
- [ ] Description is under 1024 chars, no angle brackets
- [ ] `When To Use` section present (scope anchor)
- [ ] `Boundaries` section present (boundaries anchor)
- [ ] Numbered steps or workflow heading present (execution anchor)
- [ ] `Output` section present (output anchor)
- [ ] `Verification` section present (verification anchor)
- [ ] `Resources` section present if skill has scripts/, references/, assets/, or commands/
- [ ] SKILL.md is under 500 lines (501-700 warns, >700 requires decomposition)
- [ ] All `«placeholder»` text replaced
- [ ] All `<!-- comments -->` removed
- [ ] Validated: `python3 skills/skill-creator/scripts/quick_validate.py <skill-path>`
- [ ] Strict pass: `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills <name> --strict`
