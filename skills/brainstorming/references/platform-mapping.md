# Brainstorming Platform Mapping

Use the canonical skill for scope and composition. These mappings supply optional
harness syntax, not additional workflows or deliverables.

## Saved Summaries

When a durable summary is useful or requested, use
`docs/design/YYYY-MM-DD-<topic>-design.md`, `stage: brainstorm`, and a resolved
`author:` naming the producing agent. Conversation-only work needs no file.

## Conditional Coordination

Consult relevant guidance without activating a full sibling workflow. If a
material unresolved decision requires one:

- Contract definition: `write-spec` or `/workflows:spec` when available.
- Execution dependencies or rollout: `write-plan` or `/workflows:plan`.
- CLI interface decision: `create-cli`.
- Architectural trade-off: `first-principles`.

Use a manual fallback if a needed skill is unavailable. Do not create a spec or
plan solely because a platform offers that command.

## Interaction

Use the harness's question tool or ordinary conversation. Ask a single question
when later questions depend on it; group independent questions when useful.
Read existing context before asking. Continuing authorized work does not require
a new approval to switch or skip skills.

## Command Wrapper

`commands/workflows/brainstorm.md` maps this skill to the Claude-style command.
