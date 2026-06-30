# Brainstorming Platform Mapping

This file keeps the core `brainstorming` skill model-agnostic and moves platform specifics into an optional add-on.

## Canonical Outputs

- Design summary path: `docs/design/YYYY-MM-DD-<topic>-design.md`
- Stage marker in frontmatter: `stage: brainstorm`

## Spec Handoff Mapping

The chosen direction hands off to `write-spec` to become a falsifiable contract
(`write-plan` then sequences the build).

- Generic: "Hand off to spec the contract"
- Claude workflows: `/workflows:spec` (if available)
- Skill-driven harnesses: invoke `write-spec` (or equivalent contract skill)
- Manual fallback: create a contract in `docs/specs/`

## Questioning/Interaction Mapping

- Generic: ask one question at a time; confirm assumptions explicitly.
- Claude-specific command wrappers may use tool-native ask/question primitives.
- Harnesses without ask primitives can use normal conversational turns.

## Conditional Skill Coordination Mapping

Keep coordination intent in the canonical `SKILL.md`; keep platform invocation syntax in wrappers.

- Planning needed -> invoke planning skill or workflow command.
- CLI contract design needed -> invoke CLI design skill.
- UI/UX direction needed -> invoke frontend/design audit skill.
- Deeper architectural trade-off analysis needed -> invoke systems reasoning skill.

If a named skill is unavailable, use the closest generic fallback and continue.

## Optional Add-ons

- Claude wrapper: `skills/brainstorming/commands/workflows/brainstorm.md`

Do not place platform-specific hard requirements in `SKILL.md` unless they are universally available.
