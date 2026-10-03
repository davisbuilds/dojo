---
name: local-review
description: Review code changes for actionable defects without posting to GitHub. Use for local, staged, branch, or commit reviews, including focused reviews of error handling, fallbacks, types, and invariants. Trace affected callers and contracts; return concise, evidence-backed findings.
skill-type: workflow
version: 2.0.0
---

# Local Review

Find defects the author would fix, and explain them well enough to act on.
Review the actual change independently of its implementation narrative. A useful
review can have no findings; neither volume nor an elaborate report proves depth.

## When To Use

- Reviewing uncommitted changes, a branch, a commit, or an explicitly named scope.
- Investigating failure handling or type invariants within a requested review.

## Boundaries

Review is read-only: do not edit source, commit, push, or post comments unless the
user separately authorizes those actions. Safe focused checks may produce
ordinary temporary/build artifacts; do not run destructive or externally mutating
probes just to validate a suspicion.

For a change review, findings must be introduced or newly exposed by that change.
Read unchanged callers, dependencies, tests, configuration, and contracts when
needed to prove the effect. This is an evidence boundary, not a restriction to
reading changed lines. An explicitly requested broader audit can include existing
defects; label them accordingly rather than presenting them as regressions.

Honor a request for the harness's native reviewer when available. A native
`/review` command is not this skill's command wrapper. See
`references/review-basis.md` for the inspected Codex implementation and limits.
Do not automatically launch a second reviewer or claim an inline self-review is
independent. Consultation adds no separate approval or delivery gate.

## Workflow

### Establish the target

Read applicable repository instructions and resolve the requested comparison.
Use the existing diff or the optional bundled collector:

```bash
bash <skill-dir>/scripts/collect_review_context.sh --mode working
bash <skill-dir>/scripts/collect_review_context.sh --mode staged
bash <skill-dir>/scripts/collect_review_context.sh --mode branch --base origin/main
```

Working mode includes tracked changes relative to HEAD and untracked files;
before the first commit it compares against the empty tree. Staged mode reads
the index. Branch mode compares the selected head with its
merge-base, defaulting to `origin/main` with a reported local-main fallback.
For a specific commit, inspect its actual parent comparison with Git. Resolve
ambiguous merge-commit targets rather than guessing which parent the user means.

Review the named revision, not whichever bytes happen to be checked out. In
staged or non-checked-out revisions, read corresponding blobs for supporting
code. Check whether the base ref is stale when that could change the comparison;
do not silently substitute a different target. Ask only if context cannot resolve
an ambiguity that affects the result.

The collector is a starting point, not complete evidence. If output truncates,
use `--deep`, `--max-diff-lines`, or scoped Git reads to cover the omitted change.
A larger output budget does not itself make a review deeper. Inspect relevant
untracked files and deleted behavior; scale investigation to consequences and
uncertainty rather than a file-count threshold.

### Investigate candidate defects

Follow the changed behavior through inputs, consumers, state transitions, and
failure paths. After a changed field, condition, key, or contract, ask what else
must agree: sibling queries, writers/readers, filtering and grouping, UI/API,
configuration, migration, generated output, and installed/runtime consumers.
Search the relevant parallel sites instead of assuming the edited path is alone.

For each candidate, establish the trigger, resulting behavior, and violated
contract or user impact. Inspect the old behavior and look for evidence that
would invalidate the finding: upstream validation, intentional compatibility
changes, handling in a caller, or an existing regression test. A runnable minimal
probe can resolve uncertainty, but a demonstrable code path can be sufficient;
do not require a new test for every comment or run every suite by default.

Use a specialist reference only when the changed behavior warrants it:

- `references/error-handling.md` — success-shaped failures, retries, cancellation,
  propagation, cleanup, and useful diagnostics.
- `references/type-invariants.md` — construction, mutation, decoding, aliases,
  representable states, and consumer assumptions.

Report a candidate when it is concrete, actionable, materially affects behavior
or maintenance, and has evidence for the affected scenario. Do not require proof
that a user has already encountered it. Do not flag speculative callers, optional
refactors, missing tests alone, style preferences, or a stricter engineering
standard than this project needs. An intended change can still contain a defect
in its implementation or break a promised contract; explain that distinction.

Continue across the requested change after the first finding. Deduplicate one
root cause/remedy rather than emitting the same issue for each affected line.
Keep independent defects separate. An unresolved suspicion belongs in a brief
question or limitation if consequential, not disguised as a finding.

## Output

Findings first, ordered by impact. Default to a compact title and one paragraph:

`[P2] Preserve failed-fetch state instead of caching an empty result — path:line`

Explain the input or condition, the causal path, and the concrete consequence.
Name the affected consumer when that establishes the bug. Give the fix direction
when useful without prescribing an unnecessary redesign. Anchor to the smallest
useful changed span; supporting evidence may be elsewhere. Cite an applicable
repository rule when it materially establishes a non-obvious requirement.

Use the consumer's priority scheme when supplied; otherwise:

- **P0:** unconditional critical failure requiring immediate action.
- **P1:** serious defect requiring urgent correction; state relevant conditions.
- **P2:** ordinary actionable defect.
- **P3:** lower-impact but worthwhile correction, not a cosmetic preference.

Severity follows consequence and reachability, not a syntax pattern or the
presence of a catch block. No finding quota, numeric confidence score, per-type
rating, mandatory patch, or fixed set of closing sections. Preserve an explicit
machine-output contract if a caller requires one.

If no qualifying issues are found, say so. Briefly state material scope or
verification limits, including tests not run when relevant. Do not equate a clean
review with proof of correctness, and do not imply full coverage after reading
only part of the target.

## Verification

Before returning, check each finding against the reviewed revision, its trigger,
impact, and relevant counterevidence. Distinguish executed checks from source
reasoning. Remove unsupported claims and duplicate findings, not legitimate
issues merely to keep the report short.

## Resources

- `scripts/collect_review_context.sh` — optional Git context collector.
- `commands/review.md` — wrapper for harnesses that expose command files.
- `references/error-handling.md` and `references/type-invariants.md` — optional lenses.
- `references/review-basis.md` — upstream basis, native-review distinction, evaluation limits.
- `evals/trigger-cases.json` — lexical routing probes, not measured agent selection.
- `evals/behavioral-scenarios.md` — replay cases for finding quality and scope;
  authored acceptance cases, not measured model-performance results.
