# Changelog

## 2.0.0 - 2026-10-07

- Distinguish bounded tasks, recurring monitoring, and experiments; use evidence
  and stopping rules appropriate to each, with existing runtime capabilities first.
- Make scaffolding, separate reviewers, checkpoints, and check scripts conditional.
  Replace accumulating progress logs with an optional compact current checkpoint.
- Introduce blueprint schema 2 and a smaller optional scaffold; reject v1 input
  with migration guidance and refuse overwriting existing bundles.
- Remove generated guards, verifier/bindings files, repeated-command self-tests,
  and hardcoded harness recipes. Separate declared controls from actual enforcement.
- Run optional evidence commands once in an explicit working directory, preserving
  their output and status without equating a successful command with loop completion.
- Remove the command wrapper's stale repository-relative permission prefixes.

## 1.0.4 - 2026-08-14

- Anchor runnable script commands to <skill-dir> so they resolve outside a dojo checkout

## 1.0.3 - 2026-08-01

- Trim the internal go/no-go-gate and blueprint-then-scaffold procedure from the description; triggers unchanged.


## 1.0.2 - 2026-07-31

- Remove references to skills retired on 2026-07-31 (`gh-fix-issue`,
  `gh-review-pr`, `gh-triage-issues`, `code-review-agents`,
  `autonomous-engineering`, `self-improve`, `vercel-react-native-skills`).
  Sibling sections and routing text only; no behavior change.

## 1.0.1 - 2026-07-31

- Trim the description from 632 to 520 chars by removing the loop-blueprint component list. Trigger surface unchanged.
