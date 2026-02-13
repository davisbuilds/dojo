---
name: review-pr
description: Review a GitHub pull request with preflight checks, diff analysis, and a merge recommendation.
argument-hint: "<owner/repo> <pr_number> [--quick|--deep]"
allowed-tools: [Read, Bash(gh:*), Bash(git:*), Bash(bash skills/gh-review-pr/scripts/fetch_pr.sh:*)]
---

# Review PR Command

Use this wrapper for a consistent PR-review flow.

## Behavior

1. Parse `$ARGUMENTS` into `owner/repo` and `pr_number`.
2. Run preflight checks:
- `gh auth status`
- PR exists and is accessible
3. Collect review context:

```bash
bash skills/gh-review-pr/scripts/fetch_pr.sh <owner/repo> <pr_number>
```

4. Apply blocker checks first: draft, failing CI, conflicts, closed/merged state.
5. Analyze diff and produce recommendation: `APPROVE`, `REQUEST_CHANGES`, or `COMMENT`.
6. If the workflow calls for posting a review, use `gh pr review` with a structured body.
7. Report back with key findings, recommendation, and review URL (if posted).

## Output Order

1. Findings
2. Recommendation
3. CI/mergeability status
4. Follow-up actions

## Rules

- Keep findings concrete and tied to file/line references where possible.
- Do not skip preflight checks before recommendation or review posting.

## Example Invocations

```bash
# Basic PR review
/review-pr everyinc/dojo 42

# Deep review for a risky PR
/review-pr everyinc/dojo 42 --deep

# Quick pass for small PRs
/review-pr everyinc/dojo 42 --quick
```
