---
name: retro
description: Preserve non-obvious session learnings in existing canonical project docs.
argument-hint: "[optional scope hint or preview-only]"
allowed-tools: [Read, Edit, Write]
---

# Retro

Use `session-retro` to capture the useful durable facts from this session.
Respect the scope in `$ARGUMENTS` and the conversation.

## Behavior

- Compare candidate learnings with the project's existing documentation.
- Update the canonical home for each fact, correcting stale guidance and avoiding
  duplicate explanations. Keep task-resumption state out of evergreen docs.
- Apply already-authorized documentation edits directly. If the user requests a
  preview or discussion, present the proposal without writing.
- Report the changes briefly, or say that no durable update is needed.

## Boundaries

Do not create new docs unless requested, write harness memory, impose a follow-up
menu, or request approval again for edits the user already authorized. Keep
uncertain or version-dependent observations qualified, and omit secrets.
