---
name: gh-fix-issue
description: "Fetch and fix GitHub issues using the gh CLI. Use when user asks to fix, resolve, or work on a GitHub issue by number or URL. Handles the full workflow from fetching issue details, cloning repo if needed, understanding context, implementing fixes, and creating PRs. Triggers on phrases like 'fix issue #N', 'resolve issue', 'work on github.com/.../issues/N', 'help with issue N in repo', 'close out issue'."
---

# gh-fix-issue

Fix GitHub issues end-to-end using the gh CLI.

## Prerequisites

- `gh` CLI installed (`apt install gh` if missing)
- Authentication already configured (`gh auth status` to verify)

## Workflow

### 1. Parse Input

Extract from user request:

- **repo**: `owner/repo` format (from URL or explicit)
- **issue_number**: numeric issue ID

If user provides URL like `github.com/owner/repo/issues/123`, extract both.

### 2. Fetch Issue Details

```bash
bash scripts/fetch_issue.sh <owner/repo> <issue_number>
```

This returns: title, description, labels, comments, and linked PRs.

### 3. Clone Repo (if needed)

Check if repo exists locally. If not:

```bash
gh repo clone <owner/repo>
cd <repo-name>
```

If already cloned, ensure you're on the default branch and pull latest:

```bash
git checkout main && git pull  # or master
```

### 4. Create Feature Branch

Derive branch name from issue context:

- Use issue number and brief slug from title
- Examples: `fix/42-null-pointer-exception`, `feat/108-add-dark-mode`

```bash
git checkout -b <branch-name>
```

### 5. Analyze & Plan

Before coding:

1. Read files referenced in the issue
2. Search codebase for relevant code (`grep`, `find`, or language-specific tools)
3. Understand the root cause or feature scope
4. State your plan before implementing

### 6. Implement Fix

Make changes. Follow existing code style and conventions in the repo.

### 7. Test

If the repo has tests:

```bash
# Detect and run appropriate test command
npm test | pytest | go test ./... | cargo test | etc.
```

If no tests exist, verify manually or suggest adding test coverage.

### 8. Commit

Write commit message based on the change:

- Reference issue number
- Be specific about what changed
- Follow repo conventions if apparent (conventional commits, etc.)

```bash
git add -A
git commit -m "<type>: <description>

Fixes #<issue_number>"
```

### 9. Push & Create PR

```bash
git push -u origin <branch-name>

gh pr create \
  --title "<descriptive title>" \
  --body "## Summary
<what this PR does>

## Changes
<bullet points of changes>

Fixes #<issue_number>" \
  --repo <owner/repo>
```

The PR title and body should reflect the actual fix, not just copy the issue title.

### 10. Report Back

Provide user with:

- Link to created PR
- Summary of changes made
- Any concerns or follow-up items

## Edge Cases

**Issue already has a linked PR**: Note this and ask user how to proceed.

**Issue is closed**: Inform user and confirm they want to proceed.

**Repo requires fork**: Use `gh repo fork` then push to fork.

**CI failures after PR**: Review logs with `gh pr checks` and iterate.
