---
name: template
description: Skill starter template with commented guidance for every contract section. Use when creating a new skill and you need a scaffold that passes strict contract validation.
skill-type: workflow
version: 2.0.0
---

# Skill Template

Copy this file to `skills/<your-skill>/SKILL.md` and adapt its structure. Use only
content that adds a capability, preference, or justified safeguard beyond the
agent's existing context. Anchors make a skill navigable; they do not require a
fixed process, a document, or a handoff. Use `reference` for guidance that needs
no workflow or output section.

<!-- DELETE everything between « » after filling in. These are authoring hints. -->

## When To Use

<!-- «Scope anchor — required by contract. Name the actual triggering need, without a scenario quota.» -->

- «Situation where this skill adds value over general agent capability»
- «Additional trigger scenario only if it clarifies scope»

## Boundaries

<!-- «Non-goals — required by contract. What this skill does NOT do.» -->

- «Task type this skill should not be used for»
- «Relevant sibling guidance, without activating its full workflow or deliverables»
- Do not «specific anti-pattern to avoid»

## Workflow

<!-- «Execution anchor for workflow skills. State useful decision criteria; prescribe an order only when dependencies or risk require it.» -->

«Describe the decisions, capabilities, or necessary sequence that adds value.
Reuse accepted context and evidence. Do not invent steps to fill the template.»

## Output

<!-- «Output anchor for workflow skills. Match the user's scope; consultation can improve the existing task output without creating a separate artifact.» -->

- «Primary deliverable (file, report, code, etc.)»
- «Secondary deliverable if any»

## Verification

<!-- «Verification anchor — required by contract. How to confirm quality.» -->

- «Testable criterion for the primary output»
- «Second quality check»
<!-- «Skill packaging checks belong to authoring below; they do not prove the user's task succeeded.» -->

## Resources

<!-- «Resource map — required by contract IF the skill bundles scripts/, references/, assets/, or commands/. Delete this section if no resources exist.» -->

- `scripts/«name».sh` — «what it does»
- `references/«name».md` — «what it contains»

---

## Authoring Checklist

Use the relevant authoring checks before shipping. The strict contract validates
structural anchors; manual review judges value, scope, and process proportionality:

- [ ] Frontmatter `name` is hyphen-case, matches directory name, max 64 chars
- [ ] Frontmatter `description` includes trigger language (`Use when...`, `Triggers on...`)
- [ ] Description is under 1024 chars, no angle brackets
- [ ] `When To Use` section present (scope anchor)
- [ ] `Boundaries` section present (boundaries anchor)
- [ ] Workflow skills have an execution anchor; reference skills need no invented process
- [ ] Workflow skills explain the output; a separate artifact is required only when useful
- [ ] `Verification` section present (verification anchor)
- [ ] `Resources` section present if skill has scripts/, references/, assets/, or commands/
- [ ] Context and resource placement meet the current skill contract; unnecessary instructions are removed
- [ ] Mandatory instructions protect an actual requirement, not a preferred ritual
- [ ] Sibling consultation preserves task scope; formats and artifacts have real consumers
- [ ] All `«placeholder»` text replaced
- [ ] All `<!-- comments -->` removed
- [ ] Validated: `python3 skills/skill-creator/scripts/quick_validate.py <skill-path>`
- [ ] Strict pass: `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills <name> --strict`

## Sibling skills

Part of the skill-management toolchain.

- `skill-creator` — guided authoring path. Use that skill when you want full guidance; use this template when you just need a contract-passing shell.
- `skill-evals` — runs the strict validator referenced in the checklist above.
- `audit-skill` — security audit before publishing/installing.
