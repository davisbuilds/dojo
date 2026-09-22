---
name: session-retro
description: Preserve non-obvious session learnings in existing canonical project docs. Use when the user asks for a retro, says "save what we learned" or "update docs with learnings", or completed work leaves an established reference missing a consequential fact. Skip routine session endings with nothing durable to add.
skill-type: workflow
version: 2.0.0
---

# Session Retro

Preserve facts that would change how someone works in this project: a verified
operational trap, an undocumented command, a resolved design constraint, or a
correction to an existing instruction. Keep the knowledge where its next reader
will look for it.

## When To Use

- The user asks to capture learnings or invokes `/retro`.
- Completed work exposes a consequential gap in an existing project reference.

## Boundaries

- Ordinary success, generic advice, and session history are not durable learnings.
  No edit is a valid result when the docs already cover what matters.
- Use existing canonical docs. Do not create a new documentation system, promote
  a local observation into a global rule, or write harness memory as part of a retro.
  An explicit request for a new document takes precedence over this default.
- Preserve the user's scope and authority. A request to update docs authorizes
  those edits; a request to discuss or preview them does not. Do not add a second
  approval stop when the edit is already authorized.
- Keep unfinished task state in a handoff, not in evergreen reference docs.

## Workflow

Read the relevant existing docs and compare them with what the session actually
established. Distinguish a verified fact from an inference; preserve a material
uncertainty or dated observation as such rather than making it a permanent rule.

Choose the destination by the fact's owner and audience. Follow the project's
own documentation map; these are common destinations, not required paths:

| Learning | Usual home |
| --- | --- |
| Setup, commands, CI, deployment, environment quirks | Operations/runbook; README for entry-point instructions |
| System boundaries, data flow, established invariants | Architecture reference |
| Shipped behavior | Feature reference or roadmap |
| Deferred work or unresolved decision | Backlog, following its lifecycle rules |
| Agreed product direction or policy | Vision or the owning policy |
| A rule needed in most agent sessions | AGENTS.md or the harness equivalent; otherwise prefer a linked reference |

Update the most specific canonical home. Correct or replace stale text instead
of appending a conflicting note; add cross-links where readers need them without
copying the same explanation into several files. Match the surrounding format.
If no existing destination fits, say what was left uncaptured rather than
forcing it into a root instruction file.

Keep only details that help a future decision or action. Include the concrete
trigger, consequence, and workaround for a trap; retain dates or versions when
validity depends on them. Omit secrets and unnecessary private session content.

## Output

Make the authorized edits and briefly identify what changed and where. For a
preview-only request, show the proposed changes without writing. If there is
nothing worth adding, say so briefly. No required menu, learning count, or file
quota.

## Verification

Read the diff for accuracy, scope, and consistency with neighboring guidance.
Check referenced commands, paths, and links against available evidence; do not
run a mutating operation merely to document it. Apply the repo's relevant docs
checks. Do not claim a proposed remedy was verified when it was only discussed.

## Resources

- `commands/retro.md` — `/retro` entrypoint with the same scope and edit authority.
- `evals/behavioral-scenarios.md` — authored replay cases for scope and continuation;
  not measured model-performance results.

## Sibling skills

- `handoff` — preserve the current task for another session or recipient; use it
  for resumption state rather than durable project guidance.
