---
name: handoff
description: Create a continuation snapshot so a fresh agent can pick up ongoing work with the right intent, grounding, state, and direction. Use when handing off a task, preparing for compaction or a context reset, or requesting a session summary for later resumption. Use the available transfer surface; save a file when the recipient needs one.
skill-type: workflow
version: 2.0.0
---

# Handoff

Preserve the working context a fresh agent needs to resume where this one stops.
Treat the handoff as portable compaction: carry forward intent, decisions, state,
and direction without replaying the conversation. Link to maintained artifacts
for details the recipient can recover, and include essential context it cannot.

## When To Use

- The user requests a task handoff or a session summary for later continuation.
- Ongoing work needs to survive a context boundary or move to another agent.

## Boundaries

- Not an executive recap or a permanent project reference. The consumer is an
  agent continuing this work, possibly in another checkout or harness.
- A summary request alone does not require a repository file. Use the requested
  channel or the harness's existing handoff surface when it meets the need.
- Do not expand the task, turn suggestions into accepted decisions, or imply new
  permission to deploy, merge, send messages, or perform other external actions.
- Exclude credentials and unnecessary private content, including from quoted
  commands, logs, and user messages.

## Workflow

Use the current conversation and available artifacts to select what the next
agent needs. Preserve these details when relevant:

- **Intent and authority:** the desired outcome and completion criteria, constraints,
  accepted decisions and their consequential rationale, user corrections, authorized
  next actions, and any decision still awaiting input.
  Preserve the original objective alongside the latest steering; do not let a
  recent status question replace the task. For a delegated subtask, state its
  boundary and expected return to the parent.
- **Current state:** completed, in-progress, and remaining work; repository and
  branch; committed versus uncommitted changes; active processes or external jobs
  whose identifiers are needed to resume safely. Note concurrent ownership or
  unrelated edits the next agent must preserve.
- **Evidence:** what was checked, against which revision or artifact, the result,
  and what remains unverified. Distinguish observed output from another agent's
  report; a passing check before a later edit does not verify the later state.
- **Continuation:** the next useful action, blockers, and the paths or references
  needed to carry it out. Include a failed approach only if it prevents repetition
  or explains a decision the next executor might otherwise undo. Point to the
  applicable repo instructions, accepted spec/plan, and relevant source so the
  next agent can ground itself without restarting the investigation.

Prefer a current snapshot over a chronological transcript. Quote exact wording
only when it carries a consequential requirement; include code or error excerpts
only when the source or log will not be available to the recipient. Use paths
that resolve for that recipient and identify the repository or host when needed.

Check cheap, changeable state such as the current branch and worktree before
recording it when tools and remaining context permit. Reuse existing verification
evidence with its scope and freshness; do not rerun an entire suite solely to
write a summary. Label anything that could
not be refreshed. Give the recipient a short re-entry direction: read applicable
repo instructions and the named source/artifacts, then check branch, worktree,
and active jobs before acting. A snapshot carries context, not proof that live
state is unchanged.

When a saved artifact is requested or necessary, use the specified destination
or the project's existing convention. If neither exists, use
`docs/sessions/HANDOFF_<topic>_<YYYY-MM-DD>.md`. Update an existing same-task
handoff when appropriate; preserve unrelated content. Do not save a duplicate
file merely because the skill was consulted.

## Output

A continuation snapshot in the available transfer surface, scaled to the work
remaining. An existing harness compaction channel may already meet the need.
Omit irrelevant sections rather than filling them with "None". If saved, report
the path. No required section count, transcript, or closing menu.

## Verification

- The recipient can identify the next action and any approval or evidence still
  needed; unknowns are explicit rather than disguised as completed work.
- Claims agree with available artifacts and distinguish checked facts from reports.
- References are usable by the recipient, and the summary preserves material user
  constraints without unnecessary history or sensitive data.

## Resources

- `assets/summary-template.md` — optional starting point for an execution handoff;
  adapt or omit sections to suit the task.
- `references/examples.md` — compact and detailed executor handoffs.
- `evals/behavioral-scenarios.md` — authored replay cases for scope and continuation;
  not measured model-performance results.

## Sibling skills

- `session-retro` — maintain durable project knowledge in its canonical docs;
  completing a handoff does not automatically require a retro.
