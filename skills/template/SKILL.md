---
name: template
description: Adaptable skill starter with Dojo release metadata. Use when creating a new skill and you want a minimal scaffold with optional authoring prompts.
skill-type: workflow
version: 3.0.0
---

# Skill Template

Copy this file to `skills/<your-skill>/SKILL.md` and adapt its structure. Use only
content that adds a capability, preference, or justified safeguard beyond the
agent's existing context. The sections below are optional authoring prompts, not
a contract checklist. Rename, combine, or remove them to suit the capability.
Use `reference` for primarily navigational guidance.

<!-- DELETE everything between « » after filling in. These are authoring hints. -->

## When To Use

<!-- «Selection context, if the description needs elaboration. Name the actual triggering need, without a scenario quota.» -->

- «Situation where this skill adds value over general agent capability»
- «Additional trigger scenario only if it clarifies scope»

## Boundaries

<!-- «Relevant boundaries, if needed. What this skill does NOT do.» -->

- «Task type this skill should not be used for»
- «Relevant sibling guidance, without activating its full workflow or deliverables»
- Do not «specific anti-pattern to avoid»

## Workflow

<!-- «Task guidance, if needed. State useful decision criteria; prescribe an order only when dependencies or risk require it.» -->

«Describe the decisions, capabilities, or necessary sequence that adds value.
Reuse accepted context and evidence. Do not invent steps to fill the template.»

## Output

<!-- «Result expectations, if needed. Match the user's scope; consultation can improve the existing task output without creating a separate artifact.» -->

- «Primary deliverable (file, report, code, etc.)»
- «Secondary deliverable if any»

## Verification

<!-- «Evidence, where useful. How to confirm quality.» -->

- «Testable criterion for the primary output»
- «Second quality check»
<!-- «Skill packaging checks belong to authoring below; they do not prove the user's task succeeded.» -->

## Resources

<!-- «Point to resources the executor needs, if any. Delete this section if no resources exist.» -->

- `scripts/«name».sh` — «what it does»
- `references/«name».md` — «what it contains»

---

## Authoring Checklist

Before releasing, replace placeholders and remove these authoring hints. Check
metadata, relevant script behavior, and repository-generated artifacts. Match the
version/changelog to the change. Inspect scope and useful outcomes directly;
recognized headings and passing lexical fixtures do not establish task quality.

- Metadata: `python3 skills/skill-creator/scripts/quick_validate.py <skill-path>`
- Dojo catalog: `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills <name> --strict`

These paths are relative to the Dojo checkout. Outside Dojo, use the loaded
`skill-creator` directory for its tools. Consult `skill-evals` for the evidence
appropriate to a claim; neither consultation requires a report or benchmark.
