---
name: first-principles
description: "Guide agent into first-principles, systems-thinking reasoning for high-stakes technical tasks. Use when making architectural or design decisions, evaluating trade-offs between competing approaches, performing deep code review, debugging complex or unclear failures, planning non-mechanical refactors, or starting greenfield implementations. Triggers on: 'what approach should I take', 'help me decide', 'evaluate trade-offs', 'design review', 'why is this failing', 'architect', 'first principles', 'think through this', 'compare approaches', 'root cause', 'how should I structure this'."
---

## When To Use

- Making architectural or design decisions with multiple valid approaches
- Debugging complex failures where root cause is unclear or intermittent
- Evaluating trade-offs between competing concerns (performance vs. readability, etc.)
- Planning non-mechanical refactors or greenfield implementations
- Deep code review that needs to surface hidden assumptions and trade-offs

## Boundaries

- Not for mechanical tasks (rename, format, move files) that need no analysis
- Not for clear bugs with obvious root causes and isolated fixes
- Skip full decomposition when a single approach is clearly correct and well-scoped
- Do not apply to routine code changes that follow established patterns without ambiguity

## Output

- Problem decomposition with identified sub-problems, dependencies, and assumptions
- Trade-off analysis naming alternatives with explicit costs and recommendations
- Decision matrix mapping signals to analysis level (full, lightweight, skip)
- Verification criteria defined before or alongside implementation

# First Principles

## Self-Check Gate

Before applying full analysis, assess the task:

**Full decomposition** — apply when:
- Problem is ambiguous or under-specified
- Multiple valid approaches exist with non-obvious trade-offs
- Requirements are unclear or conflicting
- Changes have systemic implications across components
- Failure mode is unclear or intermittent

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
- **Show the reasoning, not just the conclusion.** Make logical steps explicit. If there's a leap, acknowledge it.
- **Surface alternatives.** Before committing to an approach, identify at least one meaningful alternative and explain why you're choosing one over the other. "Meaningful" means a real contender — not a strawman.
- **Distinguish correlation from causation.** Especially in debugging: the fact that a change preceded a failure doesn't mean it caused it.
- **Flag inconsistencies in both directions.** Challenge questionable premises in the existing code, the requirements, and your own reasoning. Apply the same standard everywhere.

## Verification-Driven Reasoning

Tie reasoning to evidence, not theory:

- **Define "working" before or alongside implementation.** What specific, observable behavior constitutes success? Establish this upfront — not after the fact to match what you got.
- **Write testable assertions.** Express expected behavior as concrete, verifiable statements. These can be formal tests, but they can also be specific conditions you'll check manually.
- **Validate empirically when possible.** If you can run it, test it, or measure it — do that instead of reasoning about whether it should work. Prefer evidence over argument.
- **Close the loop.** Implementation is not the last step. The cycle is: implement → verify → reassess. If results don't match expectations, that's information — revisit your assumptions rather than explaining away the discrepancy.
- **Scale verification to the task.** Full first-principles tasks: define success criteria upfront, test each sub-problem independently, validate integration. Lightweight tasks: run existing tests, confirm no regressions.

## Engineering Principles

Apply these as lenses during analysis — not as rules to follow mechanically, but as forces to weigh:

- **YAGNI (You Aren't Gonna Need It).** Default stance. Don't build for hypothetical future requirements. The cost of removing speculative code later is almost always lower than the cost of maintaining it now. Only add complexity when a concrete, current need demands it.
- **KISS (Keep It Simple).** Prefer the simplest solution that satisfies current requirements. Complexity is a cost — justify every layer of indirection, every abstraction, every configuration option.
- **Separation of Concerns.** Each module, function, or component should have one reason to change. When concerns are tangled, changes cascade unpredictably.
- **DRY (Don't Repeat Yourself) — with judgment.** Eliminate duplication of *knowledge* (business rules, invariants, data definitions). But do not DRY away *incidental similarity* — two blocks of code that happen to look alike but serve different purposes should stay separate. Three similar lines are better than a premature abstraction.
- **SOLID — selectively.** Single Responsibility and Dependency Inversion are almost always worth applying. Open/Closed and Interface Segregation matter at API boundaries. Liskov Substitution matters when inheritance is in play. Don't force all five onto every class.
- **Composition over inheritance.** Prefer composing small, focused pieces over deep inheritance hierarchies. Inheritance couples subclasses to implementation details of parents.

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

## Trade-Off Awareness for Code

When writing or modifying code:

- **Surface competing approaches before committing.** Name the trade-offs: readability vs. performance, simplicity vs. extensibility, short-term speed vs. long-term maintenance.
- **Explain strategy before writing code.** State the approach, the constraints that shaped it, and what alternatives you considered.
- **Flag deviations from conventions.** If you're doing something non-standard, explain why. If you're following convention, no justification needed.
- **Acknowledge knowledge limits.** For technologies or APIs that may have evolved beyond your training data, say so and suggest where to verify.

## Decision Matrix

| Signal | Analysis Level | What to Do |
|---|---|---|
| Multiple valid architectures, unclear which fits | Full | Decompose, analyze trade-offs, recommend with reasoning |
| Complex failure, cause unclear | Full | Decompose the system, isolate variables, verify hypotheses empirically |
| Trade-off between competing concerns | Full | Name both sides, explain costs, recommend with explicit assumptions |
| Refactor to improve structure/separation | Full | Define target state, decompose changes, verify behavior preserved |
| Greenfield implementation | Full | First principles on requirements, decompose, define verification criteria |
| Deep code review | Full | Challenge assumptions, surface hidden trade-offs, flag inconsistencies |
| Clear bug with obvious root cause | Lightweight | Fix, verify, move on |
| Isolated change, well-defined scope | Lightweight | Standard execution with basic reasoning |
| Mechanical operations (rename, format, move) | Skip | Execute directly |

## Verification

- Assumptions are stated explicitly before conclusions that depend on them
- At least one alternative was considered for non-trivial decisions
- Trade-offs name concrete costs, not vague "might be harder to maintain"
- Engineering principles were applied as lenses, not invoked as dogma
- Verification criteria were defined before or alongside implementation
