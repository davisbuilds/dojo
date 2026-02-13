---
name: triage-issue
description: Triage one or more GitHub issues with labels, priority, duplicate checks, and optional assignment.
argument-hint: "<owner/repo> <issue_number>|--batch [--limit <n>] [--assign]"
allowed-tools: [Read, Bash(gh:*), Bash(git:*), Bash(bash skills/gh-triage-issues/scripts/fetch_issue.sh:*), Bash(bash skills/gh-triage-issues/scripts/list_labels.sh:*), Bash(bash skills/gh-triage-issues/scripts/find_duplicates.sh:*)]
---

# Triage Issue Command

Use this wrapper for consistent single-issue and batch triage.

## Behavior

1. Parse `$ARGUMENTS`:
- Single mode: `<owner/repo> <issue_number>`
- Batch mode: `<owner/repo> --batch [--limit <n>]`
2. Run preflight checks:
- `gh auth status`
- repo access
3. Load label catalog:

```bash
bash skills/gh-triage-issues/scripts/list_labels.sh <owner/repo>
```

4. For each issue:
- fetch issue data
- run duplicate search
- classify type and priority
- apply labels
- optionally assign owner
- optionally comment for clarification
5. Return per-issue outcome (or batch summary table).

## Rules

- Confirm before closing as duplicate.
- Keep rationale explicit for priority and labeling decisions.
- In batch mode, report blockers and skipped items clearly.

## Example Invocations

```bash
# Triage a single issue
/triage-issue everyinc/dojo 88

# Batch triage first 20 open issues
/triage-issue everyinc/dojo --batch --limit 20

# Batch triage with assignee suggestions enabled
/triage-issue everyinc/dojo --batch --limit 20 --assign
```
