---
name: workflows:brainstorm
description: Explore requirements and approaches through collaborative dialogue before planning implementation.
argument-hint: "[feature idea or problem to explore]"
---

# Brainstorm A Feature Or Improvement

This command wrapper is a Claude-style add-on for the canonical `brainstorming` skill.

Load the `brainstorming` skill and follow it exactly. This wrapper provides harness-specific orchestration only.

## Feature Description

<feature_description> #$ARGUMENTS </feature_description>

If `feature_description` is empty, ask the user for the feature/problem before proceeding.

## Flow

### 1. Assess clarity

If requirements are explicit and well-constrained, ask whether to skip brainstorming and proceed directly to planning.

### 2. Clarify intent

- Ask one question at a time.
- Prefer multiple choice where natural.
- Cover purpose, users, constraints, success criteria, edge cases.

### 3. Compare approaches

Present 2-3 options with pros/cons and your recommendation.

### 4. Capture summary

Write to `docs/design/YYYY-MM-DD-<topic>-design.md` using the template in `skills/brainstorming/SKILL.md`.

### 5. Handoff

Ask what to do next:
1. Hand off to `/workflows:spec` (write-spec) to make the direction a contract
2. Review the direction with a critique subagent (or `verify-before-complete` inline if subagents are unavailable)
3. Refine further, or stop here

Apply the conditional coordination rules from `skills/brainstorming/SKILL.md` before handoff. If another specialized skill is a better next step, recommend it with a one-sentence rationale and ask for confirmation.

Never write implementation code in this workflow.
