---
name: local-review
description: Perform local code reviews on workspace changes without posting to GitHub. Use for requests like /review, review this diff, audit staged changes, or check branch changes. Collects git context and produces findings-first reports with severity, file line references, risks, and test gaps.
---

# local-review

## Overview

Run a disciplined local code review on git changes with no GitHub side effects. Use this skill when the user wants a `/review`-style assessment of local diffs.

## Scope

- In scope: local diff review (`working`, `staged`, or `branch` compare), risk analysis, and action-focused findings.
- Out of scope: posting PR reviews to GitHub. Use `gh-review-pr` for that.

## Workflow

1. Select review target.
- Working tree changes: `--mode working` (default)
- Staged changes only: `--mode staged`
- Branch changes against a base: `--mode branch --base <ref> [--head <ref>]`

2. Collect deterministic context.

```bash
bash scripts/collect_review_context.sh --mode working
```

or

```bash
bash scripts/collect_review_context.sh --mode staged
```

or

```bash
bash scripts/collect_review_context.sh --mode branch --base origin/main
```

3. Analyze for:
- correctness and regressions
- security and data integrity
- performance and scalability
- maintainability and readability
- API or contract compatibility
- test coverage gaps

4. Produce response in the exact output contract below.

## Output Contract

Always present sections in this order:

1. Findings
- Findings must come first.
- Order by severity: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`.
- Include file and line when available.
- Use this structure for each finding:
  - `Severity: <level>`
  - `Location: <path:line>`
  - `Issue: <concise problem statement>`
  - `Risk: <why this matters>`
  - `Recommended fix: <specific fix>`
  - `Tests: <missing or required tests>`

2. Open Questions / Assumptions
- List unknowns that affect confidence.

3. Change Summary
- Keep short. This is secondary to findings.

4. Residual Risks / Testing Gaps
- Explicitly call out what was not verified.

If there are no meaningful findings, state that explicitly and still include residual risks and test gaps.

## Review Depth

- Quick review: small changes and low-risk files.
- Deep review: large diff, sensitive areas (auth, migrations, payments, infra), or user request.
- Trigger deep review automatically when diff is very large (for example, over 20 files or over 500 changed lines).

## Commands

```bash
# Default: review working tree changes
bash scripts/collect_review_context.sh

# Review only staged changes
bash scripts/collect_review_context.sh --mode staged

# Review branch changes vs base
bash scripts/collect_review_context.sh --mode branch --base origin/main
```

## Command Wrapper

If the harness supports command files, use `commands/review.md` as the canonical `/review` wrapper for this skill.

## Notes

- Prefer precise, evidence-backed findings over broad advice.
- Do not make GitHub review API calls in this skill.
