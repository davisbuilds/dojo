---
name: fix-issue
description: Execute an end-to-end GitHub issue fix workflow from issue intake through PR creation.
argument-hint: "<owner/repo> <issue_number> [--no-pr]"
allowed-tools: [Read, Bash(gh:*), Bash(git:*), Bash(bash skills/gh-fix-issue/scripts/fetch_issue.sh:*)]
---

# Fix Issue Command

Use this wrapper to run the `gh-fix-issue` workflow with consistent guardrails.

## Behavior

1. Parse `$ARGUMENTS` into `owner/repo` and `issue_number`.
2. Run preflight checks:
- `gh auth status`
- issue exists and is open (or confirm if closed)
3. Fetch issue context:

```bash
bash skills/gh-fix-issue/scripts/fetch_issue.sh <owner/repo> <issue_number>
```

4. Ensure repository is available locally (clone if needed).
5. Create or select a feature branch.
6. Implement fix and run relevant tests.
7. Commit with issue reference.
8. Unless `--no-pr` is set, push and create PR linked to the issue.
9. Report back with branch, commit summary, PR URL, and outstanding risks.

## Output Order

1. Plan
2. Code/test results
3. PR status and URL
4. Follow-ups

## Rules

- Avoid opening duplicate PRs for the same branch.
- Do not claim completion without test evidence (or explicit testing gap notes).

## Example Invocations

```bash
# Fix an issue end-to-end (includes PR)
/fix-issue everyinc/dojo 314

# Fix locally but skip PR creation
/fix-issue everyinc/dojo 314 --no-pr
```
