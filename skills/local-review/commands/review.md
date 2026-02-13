---
name: review
description: Run a local findings-first code review against workspace changes without posting to GitHub.
argument-hint: "[optional: --mode working|staged|branch --base <ref> --head <ref> --max-diff-lines <n> --deep]"
allowed-tools: [Read, Bash(git:*), Bash(rg:*), Bash(bash skills/local-review/scripts/collect_review_context.sh:*)]
---

# Local Review Command

Use this command to perform a `/review`-style local code review with no GitHub side effects.

## Behavior

1. Parse `$ARGUMENTS` and select mode:
- Default: `--mode working`
- If `--mode staged` is passed: review staged diff
- If `--mode branch` is passed: compare `--head` to merge-base with `--base`

2. Collect deterministic review context:

```bash
bash skills/local-review/scripts/collect_review_context.sh $ARGUMENTS
```

If no arguments are passed:

```bash
bash skills/local-review/scripts/collect_review_context.sh --mode working
```

3. Review the resulting context and any touched files as needed.

4. Return results in this exact order:
1. Findings
2. Open Questions / Assumptions
3. Change Summary
4. Residual Risks / Testing Gaps

## Findings Format

Sort by severity: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`.

Each finding must include:
- `Severity: <level>`
- `Location: <path:line>`
- `Issue: <concise problem statement>`
- `Risk: <why this matters>`
- `Recommended fix: <specific fix>`
- `Tests: <missing or required tests>`

If there are no meaningful findings, explicitly say so and still include residual risks and testing gaps.

## Rules

- Never call `gh pr review` or post to GitHub from this command.
- Prioritize concrete, evidence-backed findings over broad suggestions.
- Use deep-review scrutiny when the diff is large, risky, or user asks for deep review.

## Example Invocations

```bash
# Default working tree review
/review

# Staged-only review
/review --mode staged

# Branch review against main
/review --mode branch --base origin/main

# Branch review for a specific head
/review --mode branch --base origin/main --head feature/my-branch

# Deep review with a larger diff budget
/review --mode staged --max-diff-lines 8000 --deep
```
