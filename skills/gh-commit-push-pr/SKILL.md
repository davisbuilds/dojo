---
name: gh-commit-push-pr
allowed-tools: Bash(git checkout:*), Bash(git add:*), Bash(git status:*), Bash(git push:*), Bash(git commit:*), Bash(git diff:*), Bash(git log:*), Bash(git branch:*), Bash(git stash:*), Bash(git remote:*), Bash(gh auth status:*), Bash(gh repo view:*), Bash(gh pr create:*), Bash(gh pr view:*)
description: "Commit staged changes, push branch, and open a GitHub PR. Use when user asks to commit and push, create a PR, ship changes, send for review, or open a pull request. Triggers on phrases like 'commit and push', 'create a PR', 'open a pull request', 'send this for review', 'ship it', 'push and PR'."
---

# Commit, Push, and Open a Pull Request

## Context

Gather state before acting:

- Current branch: !`git branch --show-current`
- Current git status: !`git status`
- Staged and unstaged changes: !`git diff HEAD`

## Workflow

### Step 1: Pre-flight Checks

Before doing anything, verify:

- **Changes exist**: If `git status` shows nothing to commit (clean working tree), stop and tell the user. Do not create empty commits.
- **Not in detached HEAD**: If HEAD is detached, create a branch first.
- **Not on main/master with intent to push directly**: If on main or master, always create a new branch before committing.
- **GitHub CLI auth is ready**: Run `gh auth status`. If not authenticated, stop and ask user to authenticate first.
- **Determine base branch**: Prefer `gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'` over assumptions.

### Step 2: Create Branch (if needed)

If on main/master or detached HEAD, create a feature branch:

- Convention: `<type>/<short-description>` where type is one of: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `ci`
- Examples: `feat/add-user-search`, `fix/null-pointer-on-login`, `docs/update-readme`
- Use `git checkout -b <branch-name>` to create and switch

### Step 3: Stage and Commit

Stage changes if not already staged, then commit:

- **Commit message format**: Start with a verb in imperative mood (Add, Fix, Update, Remove, Refactor)
- **First line**: Concise summary, max ~72 characters
- **Body** (if changes warrant it): Blank line after summary, then explain *why* not *what*
- Reference issues if applicable: `Fixes #123` or `Closes #456`
- Do NOT commit files that look like secrets (`.env`, `credentials.json`, `*.pem`, `*.key`)

### Step 4: Push

Push the branch to origin:

```
git push -u origin <branch-name>
```

**If push fails**:
- **Authentication error**: Tell the user to check their git credentials or `gh auth status`
- **Rejected (non-fast-forward)**: The remote branch has diverged. Tell the user — do not force push
- **Remote not found**: Check with `git remote -v` and report
- **Network error**: Retry once after a brief pause. If it fails again, report the error

### Step 5: Create Pull Request

Create a PR using `gh pr create`:

```
gh pr create --base "<base-branch>" --head "<branch-name>" --title "<imperative summary>" --body-file "<path>"
```

PR body structure:
- **Summary**: 1-3 bullet points describing what changed and why
- **Test plan**: How to verify the changes work (commands to run, things to check)

If the repo has a PR template, `gh pr create` will use it automatically. Do not override templates.

Before creating, check if PR already exists for this branch:

```
gh pr view --head "<branch-name>" --json url --jq '.url'
```

If that returns a URL, report it and do not create a duplicate PR.

When generating PR body text, NEVER inline complex markdown in `--body` if it may contain shell-sensitive characters (especially backticks). Use a body file:

```
tmp_pr_body="$(mktemp)"
cat > "$tmp_pr_body" <<'EOF'
## Summary
- <what changed and why>

## Test plan
- [ ] <how to verify>
EOF

gh pr create --base "<base-branch>" --head "<branch-name>" --title "<title>" --body-file "$tmp_pr_body"
rm -f "$tmp_pr_body"
```

If `gh pr create` fails, handle by error pattern:
- **`error connecting to api.github.com` / network denied**: retry once; if sandbox/network restrictions apply, rerun with escalated network permissions.
- **`A pull request already exists`**: run `gh pr view --head "<branch-name>" --json url --jq '.url'` and report existing URL.
- **`not logged into any GitHub hosts`**: stop and ask user to run `gh auth login`.
- **`No commits between`**: branch has no diff against base; report and stop.
- **`permission denied`/`command not found` lines caused by PR body text**: this usually means shell interpolation from unescaped markdown; rerun using `--body-file`.
- **Validation/base errors**: re-check base branch via `gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'` and retry with explicit `--base`.

### Step 6: Report Back

After all steps complete, report:
- Branch name
- Commit message summary
- PR URL
- Any warnings (e.g., large diff, binary files, files that look sensitive)

## Edge Cases

| Situation | Action |
|-----------|--------|
| No changes to commit | Stop. Tell the user there's nothing to commit. |
| Already on a feature branch | Use it. Don't create a new one. |
| Existing PR for this branch | Tell the user a PR already exists. Show the URL with `gh pr view`. |
| Merge conflicts on push | Do not force push. Tell the user to pull and resolve. |
| Uncommitted changes + staged changes | Commit only what's staged. Warn about unstaged changes. |
| Binary files in diff | Warn the user. Include them only if intentional. |
| Sensitive-looking files (.env, keys) | Do NOT stage or commit. Warn the user. |

## Tool Call Strategy

You MUST call multiple tools in a single response when the calls are independent. For example, `git add` and `git status` can be parallel. But `git commit` must follow `git add`, and `git push` must follow `git commit`. Chain dependent operations sequentially.
