---
date: YYYY-MM-DD
topic: topic-slug
stage: plan
status: draft
source: conversation
---

# Topic Title Plan

## Goal

One sentence describing what this plan delivers. Link the contract it realizes:
`docs/specs/YYYY-MM-DD-<topic>-spec.md` (every `Done When` traces to its end-state).

## Scope

### In Scope

- What is included in this implementation pass.

### Out of Scope

- What is explicitly excluded for this pass.

## Assumptions And Constraints

- Assumptions that shape the approach.
- Constraints (technical, schedule, dependency, policy).

## Map Before You Cut

For tasks touching existing or coupled code, trace the ground before prescribing:

- Data/call path the change rides on (who calls what, what state flows where).
- The thinnest seam that satisfies the contract.
- `**Assumptions Verified**`: what you confirmed in the code (file:line, observed
  behavior) that makes the chosen seam correct.

Omit only when every task is greenfield/self-contained.

## Task Breakdown

### Task 1: Name

**Objective**

Describe the concrete outcome of this task.

**Files**

- Create: `path/to/new.file`
- Modify: `path/to/existing.file`
- Test: `tests/path/to/test.file`

**Dependencies**

None

**Implementation Steps**

1. Step with a concrete, grounded action.
2. Step with a concrete, grounded action.

**Verification**

- Run: `command`
- Expect: observable pass signal

**Done When**

- Acceptance criterion that traces to the contract's end-state.

## Risks And Mitigations

- Risk: short description.
  Mitigation: concrete prevention or fallback.

## Verification Matrix

| Requirement | Proof command | Expected signal |
| --- | --- | --- |
| Requirement description | `command` | Deterministic pass signal |

## Handoff

1. Execute in this session, task by task.
2. Review the plan with a critique subagent (or `verify-before-complete` inline
   if subagents are unavailable).
3. Open a separate execution session, or refine this plan first.
