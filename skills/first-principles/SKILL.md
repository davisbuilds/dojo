---
name: first-principles
description: "Systems-level reasoning for high-stakes technical decisions. Use when choosing between architectures, evaluating trade-offs, or planning a non-mechanical refactor. For debugging a specific failure use diagnose; for clarifying an ambiguous WHAT use brainstorming."
skill-type: reference
version: 2.0.1
---

# First Principles

## When To Use

- Choosing between architectures or designs with multiple valid approaches
- Evaluating trade-offs between competing concerns
- Planning a non-mechanical refactor or a greenfield implementation
- Deep code review that needs hidden assumptions surfaced

## Boundaries

- Not for debugging a specific failure — use `diagnose`, which owns that loop
- Not for clarifying an ambiguous WHAT — use `brainstorming`
- Not for mechanical tasks (rename, format, move) or changes that follow an
  established pattern without ambiguity

## Self-Check Gate

Before applying full analysis, assess the task:

**Full decomposition** — apply when:
- Problem is ambiguous or under-specified
- Multiple valid approaches exist with non-obvious trade-offs
- Requirements are unclear or conflicting
- Changes have systemic implications across components

**Lightweight analysis** — apply when:
- Cause is obvious and fix is isolated
- Single clear approach, no meaningful alternatives
- Change is well-scoped with predictable impact

If lightweight: apply standard execution with basic reasoning transparency. Skip to the relevant section as needed. If full: work through all sections below sequentially.

## Epistemic Framework

These standards apply to all reasoning within the task:

- **State assumptions before building on them.** If your analysis depends on something being true, name it explicitly. Don't bury premises inside conclusions.
- **Calibrate confidence.** Distinguish what you know with evidence, what you're inferring, and what you're uncertain about. Name the information that would resolve gaps.
- **Mark knowledge boundaries.** Note whether a position represents established consensus, emerging practice, or an outlier view. Flag when you're reasoning beyond your training data.
- **Watch your own blind spots.** If you notice uncertainty about your own certainty — say so. If your analysis keeps confirming the same conclusion without stress-testing it, flag that too.
- **Disagree clearly when warranted.** When correcting a premise or pushing back on an approach, explain the error and why it matters. Don't soften the correction to the point of ambiguity, and don't be dismissive.

## Problem Decomposition

Break the problem down before attempting a solution:

1. **Identify the core question.** What specifically needs to be decided, understood, or built? Strip away incidental complexity.
2. **Decompose into sub-problems.** Find the independently solvable pieces. Each should have a clear boundary and a testable outcome.
3. **Map dependencies.** Which sub-problems depend on others? Which can be solved in parallel? Where are the interfaces between components?
4. **Surface assumptions at each level.** Each sub-problem carries its own assumptions — name them. An assumption buried in a sub-problem can invalidate the whole solution.
5. **Solve from foundations up.** Start with the sub-problems that have the fewest dependencies and the most downstream impact. Don't jump to the top-level solution.

## Analytical Method

Ground analysis in fundamentals, not pattern-matching:

- **Reason from what must be true**, not what is typically done. Conventions are useful defaults, but they're not arguments. If you're recommending an approach because it's common, say so — and explain what makes it actually appropriate here.
- **Surface alternatives.** Before committing to an approach, identify at least one meaningful alternative and explain why you're choosing one over the other. "Meaningful" means a real contender — not a strawman.
- **Flag inconsistencies in both directions.** Challenge questionable premises in the existing code, the requirements, and your own reasoning. Apply the same standard everywhere.

## Verification-Driven Reasoning

Tie reasoning to evidence, not theory:

- **Define "working" before or alongside implementation.** What specific, observable behavior constitutes success? Establish this upfront — not after the fact to match what you got.
- **Write testable assertions.** Express expected behavior as concrete, verifiable statements. These can be formal tests, but they can also be specific conditions you'll check manually.
- **Validate empirically when possible.** If you can run it, test it, or measure it — do that instead of reasoning about whether it should work. Prefer evidence over argument.
- **Close the loop.** Implementation is not the last step. The cycle is: implement → verify → reassess. If results don't match expectations, that's information — revisit your assumptions rather than explaining away the discrepancy.
- **Scale verification to the task.** Full first-principles tasks: define success criteria upfront, test each sub-problem independently, validate integration. Lightweight tasks: run existing tests, confirm no regressions.

## Resolving Principle Tensions

Principles conflict. When they do, use the current context to decide — not a fixed hierarchy:

| Tension | Resolution Heuristic |
|---|---|
| DRY vs. readability | If the abstraction requires more context to understand than the duplication, keep the duplication |
| SOLID vs. simplicity | Apply SRP and DI broadly; apply OCP/ISP/LSP only at module boundaries or public APIs |
| YAGNI vs. extensibility | Build for today's requirements; refactor when (not before) new requirements arrive |
| Performance vs. clarity | Write clear code first; optimize only when profiling shows a measured bottleneck |
| Consistency vs. correctness | Don't follow a bad pattern just because it's established; fix the pattern if scope allows, otherwise document the deviation |
| Abstraction vs. directness | If you'd need to read the abstraction's source to understand the call site, the abstraction isn't helping |

## Decision Matrix

| Signal | Analysis Level | What to Do |
|---|---|---|
| Multiple valid architectures, unclear which fits | Full | Decompose, analyze trade-offs, recommend with reasoning |
| Complex failure, cause unclear | — | Use `diagnose`; it owns the debugging loop |
| Trade-off between competing concerns | Full | Name both sides, explain costs, recommend with explicit assumptions |
| Refactor to improve structure/separation | Full | Define target state, decompose changes, verify behavior preserved |
| Greenfield implementation | Full | First principles on requirements, decompose, define verification criteria |
| Deep code review | Full | Challenge assumptions, surface hidden trade-offs, flag inconsistencies |
| Clear bug with obvious root cause | Skip | Fix, verify, move on |
| Isolated change, well-defined scope | Lightweight | Standard execution with basic reasoning |
| Mechanical operations (rename, format, move) | Skip | Execute directly |

## Verification

- Assumptions are stated explicitly before conclusions that depend on them
- At least one alternative was considered for non-trivial decisions
- Trade-offs name concrete costs, not vague "might be harder to maintain"
- Engineering principles were applied as lenses, not invoked as dogma
- Verification criteria were defined before or alongside implementation

## Sibling skills

This skill is in two clusters: **pre-execution thinking** and **disciplines** (modes that govern *how* the agent reasons).

Pre-execution thinking:
- `brainstorming` — upstream. Use that skill when WHAT is ambiguous; this skill when HOW or WHY needs systems-level reasoning.
- `write-spec` — downstream. Once a direction is reasoned out, hand off to `write-spec` for the falsifiable contract; then `write-plan` to sequence the build.
- `deep-research` — parallel evidence gathering when reasoning hinges on unknowns.

Disciplines:
- `verify-before-complete` — gate at the *end* of execution. This skill shapes thinking at the start.
- `test-strategy` — methodology for the testing decisions; orthogonal axis to architectural reasoning here.
- `caveman` — output style mode; orthogonal.
