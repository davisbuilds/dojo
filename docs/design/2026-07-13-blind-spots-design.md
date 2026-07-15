---
date: 2026-07-13
topic: blind-spots
stage: brainstorm
---

# Blind Spots

## Problem / Context

Dojo already helps an agent resolve uncertainty before implementation: `write-spec`
triages contract-affecting unknowns, `write-plan` maps the existing code before
choosing a seam, and the research, diagnosis, review, and verification skills
cover their specialized evidence needs. A broad `map-unknowns` skill aimed at the
agent would substantially duplicate those responsibilities and risk becoming an
always-triggered reconnaissance checklist.

The less-covered problem is human comprehension debt. When an agent scopes and
implements a change, the user can reach a merge-ready diff without developing a
durable mental model of what changed, why the selected seam works, or where the
remaining risks sit. The user wants an optional, conversational way to understand
scope before work and test their own understanding after implementation.

## Options Considered

- **Extend existing planning and review skills**: Add human-comprehension prompts
  to `write-plan`, `local-review`, or PR workflows. This adds little catalog
  surface, but scatters one concern across skills whose contracts currently focus
  on agent grounding, defect detection, and delivery evidence.
- **Create one human-centered blind-spots skill**: Give one skill two
  independently invokable modes: a pre-implementation scope briefing and a
  post-implementation quiz. This creates a distinct responsibility and preserves
  the existing pipeline boundaries, at the cost of a skill that can appear at two
  points in the change lifecycle.
- **Create separate mapping and quiz skills**: Keep each temporal phase narrow.
  This produces the cleanest individual workflows, but adds two small catalog
  entries with shared context and makes the user choose between concepts that are
  both serving the same comprehension goal.

## Chosen Direction

Create a human-centered `blind-spots` workflow skill with two modes that
can be invoked independently.

**Scope mode** helps the user understand a proposed change before implementation.
It provides a task-bounded mental model: relevant entry points and boundaries,
important data or call paths, likely blast radius, and consequential unknowns. It
does not produce a specification or implementation plan and should reuse existing
artifacts when they exist.

**Quiz mode** runs after implementation, normally before merge. It reads the
actual diff and available verification evidence, then quizzes the user one
question at a time. Questions emphasize intent, the changed seam, data flow,
failure modes, what tests establish, and residual risk. After each answer, the
agent corrects or extends the user's model with concrete repository evidence
before continuing.

The workflow is optional and non-gating. It does not score the user or issue a
merge-readiness verdict. Its default output stays in the chat session and ends
with a concise recap of what the user understood well and what may be worth
revisiting. A durable artifact is created only when explicitly requested.

## What Good Looks Like

- A user can ask what a proposed change touches and receive a bounded explanation
  that makes the important system relationships legible without becoming a plan.
- A user can request a pre-merge quiz and reason about the actual implemented
  behavior rather than answer trivia about filenames or syntax.
- Corrections are educational, evidence-backed, and safe for an honest “I don't
  know” response.
- The skill strengthens human ownership without duplicating code review,
  verification, specification, or planning.
- Invocation is deliberate enough that ordinary implementation work does not
  acquire an unsolicited teaching ritual.

## Open Questions

- Whether `blind-spots` is the final public name or a clearer user-facing
  name emerges during specification.
- Which explicit command wrappers best expose scope and quiz modes across
  harnesses.
- Whether quiz depth should be inferred from change risk or selected explicitly
  by the user.
- What minimum repository evidence each mode must gather when no spec or plan
  exists.

## Constraints

- Keep the workflow task-scoped; do not attempt to map an entire codebase.
- Keep it human-centered; agent uncertainty remains owned by the existing
  brainstorming, specification, planning, research, and diagnosis workflows.
- Do not replace `local-review`, `gh-review-pr`, or `verify-before-complete`, and
  do not infer correctness from the user's answers.
- Keep quizzes non-gating, non-scored, adaptive, and conversational, with one
  question at a time.
- Prefer explicit invocation initially to minimize trigger collisions and avoid
  unsolicited quizzes.
- Avoid persistent repository artifacts by default.
