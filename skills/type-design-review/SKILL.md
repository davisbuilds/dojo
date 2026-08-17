---
name: type-design-review
description: Review the design of a new or changed type — does it make illegal states unrepresentable, enforce its invariants at construction, and encapsulate its internals? Rates encapsulation, invariant expression, invariant usefulness, and enforcement. Use when introducing a new type or data model, reviewing the types added in a PR, or refactoring a type for stronger guarantees. Not general diff review (local-review).
skill-type: workflow
version: 1.0.0
---

# type-design-review

## Overview

A specialist review lens for **type design**: whether a type carries strong,
clearly expressed, well-encapsulated invariants — or leans on documentation and
caller discipline to stay valid. The guiding principle is *make illegal states
unrepresentable*: the best invariant is one the type system enforces so the
invalid case cannot be constructed at all.

This is a deliberately-invoked pass focused on the shape of the data, not the
behavior around it. Reach for it when a change introduces or reshapes a type.

## When To Use

- A change introduces a new type, domain model, struct, dataclass, enum, or
  interface.
- A PR adds several types and you want each reviewed for design quality.
- Someone is refactoring an existing type to strengthen its guarantees, and
  wants the invariants and encapsulation assessed first.
- The user asks whether a type "makes illegal states unrepresentable" or
  "enforces its invariants".

## Boundaries

- **Not general code review.** Correctness, performance, and style belong to
  `local-review`. This lens looks only at type/invariant design.
- **Not error-handling review.** Swallowed errors and fallbacks are
  `error-handling-review`.
- **Read-only.** Produce an assessment; do not edit source.
- **Pragmatism over purity.** A simpler type with fewer guarantees can beat a
  complex one that over-models. Weigh the maintenance cost of every suggestion;
  perfect is the enemy of good.

## Workflow

For each new or changed type:

1. **Identify the invariants** — implicit and explicit. Data-consistency rules,
   valid state transitions, cross-field relationships, business rules encoded in
   the type, pre/postconditions. Name them; you cannot rate what you have not
   named.
2. **Rate the four axes**, 1–10, each with a one-line justification. See
   `references/rating-rubric.md` for what each axis measures and what low vs.
   high looks like:
   - **Encapsulation** — are internals hidden; can the invariants be violated
     from outside?
   - **Invariant expression** — how clearly does the structure communicate the
     invariants; are they compile-time where possible?
   - **Invariant usefulness** — do the invariants prevent real bugs and match the
     domain, without being over- or under-restrictive?
   - **Invariant enforcement** — checked at construction; every mutation guarded;
     is it impossible to build an invalid instance?
3. **Flag anti-patterns** from `references/rating-rubric.md` (anemic models,
   exposed mutable internals, doc-only invariants, god-types, missing
   construction validation, inconsistent mutation guards).
4. **Recommend pragmatic improvements** — concrete, language-appropriate, and
   worth their complexity and breaking-change cost.

## Output Contract

One block per type, findings-oriented:

```
## Type: <TypeName>  (<path:line>)

### Invariants
- <each invariant, one line>

### Ratings
- Encapsulation: X/10 — <justification>
- Invariant expression: X/10 — <justification>
- Invariant usefulness: X/10 — <justification>
- Invariant enforcement: X/10 — <justification>

### Strengths
- <what the type does well>

### Concerns
- <specific issue, with the illegal state it permits>

### Recommended improvements
- <concrete, pragmatic change; note breaking-change/complexity cost>
```

When several types are reviewed, order blocks by lowest minimum axis rating
first (weakest design surfaced first). State explicitly when a type is
well-designed — a high score is a real result.

## Verification

- Every reviewed type cites a real `path:line`.
- Every axis rating carries a justification; every `Concern` names the concrete
  illegal state the current design permits.
- Recommendations are language-appropriate and acknowledge their cost.

## Resources

- `references/rating-rubric.md` — what each of the four axes measures (with
  low/high anchors), the anti-pattern catalog, and language-specific tools for
  making illegal states unrepresentable in TypeScript and Python.

## Sibling skills

- `local-review` — general diff review; run this lens when it flags a new type,
  or invoke it directly.
- `error-handling-review` — the failure-handling lens; orthogonal.
- `api-design` — for interface/contract shape at the API boundary rather than
  the invariants of an internal type.
