---
date: YYYY-MM-DD
author: <agent>
topic: topic-slug
stage: plan
status: draft
source: conversation
risk_profile: routine
readiness: draft
---

# Topic Title Plan

## Goal

State the accepted outcome and link its contract or ticket when available. A
clear conversation can supply the target for routine work; do not create a new
spec solely for this link. Every `Done When` traces to that accepted outcome.
High-risk plans link a ready high-risk spec as required by the addendum.

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
- Every sibling, alternate, upstream/downstream, error, and ported path that must
  preserve the same property; give each a `Done When` or explicit out-of-scope note.
- Resolve current questions by reading/grepping before writing steps. A risk is
  an irreducible future uncertainty, not a lookup deferred to execution.
- For each task that edits existing code, add `**Assumptions Verified**` in that
  task: cite the exact target file/symbol and observed behavior. Label any
  neighboring precedent as `Research Context`, not target verification. Reuse
  shared evidence with links instead of duplicating it in every task.

Use this section for shared grounding; omit it when the task blocks already
contain the relevant evidence or the work is self-contained.

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

**Assumptions Verified**

- Required when `**Files**` includes `Modify:`: `path/to/existing.file:line`
  contains the observed behavior that makes this exact cut correct.
- For create-only work, omit this marker or label useful cross-file precedent as
  `Research Context`; do not invent a target-file citation.

**Implementation Steps**

1. Step with a concrete, grounded action.
2. Step with a concrete, grounded action.

**Verification**

- Run: `command`
- Expect: observable pass signal

**Test Discovery Verified**

Include only when this task creates or changes tests:

- Runner/discovery evidence: `package.json`, `pyproject.toml`, or equivalent
  includes the new test path.
- Name the command that runs the literal new test or exact selector. Distinguish
  observed discovery evidence from execution planned after the file exists.

**Done When**

- Acceptance criterion that traces to the contract's end-state and pins a
  meaningful magnitude, floor, rate, or non-degeneracy bound when needed.

## Risks And Mitigations

- Risk: irreducible future uncertainty (not a repository lookup that can be
  resolved now).
  Signal: how the uncertainty is observed.
  Mitigation: concrete prevention, containment, or fallback.

## Verification Matrix

| Requirement | Proof command | Expected signal |
| --- | --- | --- |
| Requirement description | `command` | Deterministic pass signal |

## Handoff

Optional: omit this section if there is no useful handoff. Otherwise state the
actual next action, consumer, or execution context, reusing existing authority.
No numbered menu or additional workflow is required.
