---
name: gh-commit-push-pr
allowed-tools: Bash(git checkout:*), Bash(git add:*), Bash(git status:*), Bash(git push:*), Bash(git commit:*), Bash(git diff:*), Bash(git log:*), Bash(git branch:*), Bash(git stash:*), Bash(git remote:*), Bash(gh auth status:*), Bash(gh repo view:*), Bash(gh pr create:*), Bash(gh pr view:*)
description: "Commit intended changes, publish existing commits, and open or update a GitHub PR. Use when user asks to commit and push, create a PR, ship changes, send for review, or open a pull request. Triggers on phrases like 'commit and push', 'create a PR', 'open a pull request', 'send this for review', 'ship it', 'push and PR'."
skill-type: workflow
version: 2.0.0
---

# Commit, Push, and Open a Pull Request

Advance the requested work from its actual Git/GitHub state. A clean working
tree can still contain unpublished commits or a pushed branch needing a PR.

## When To Use

Use for commit, push, and PR requests, including already-committed work. The same
skill covers merge/sync cleanup when the user requests that continuation. A
publication request does not itself authorize merging, deployment, or review
comments to other people or services.

## Workflow

### Establish the target and remaining work

Read repository instructions and inspect the branch, index/worktree, remotes,
upstream, and intended base. Honor an explicit base, including a stacked PR's
parent; otherwise discover the repository's default branch. Fetch relevant refs
when needed for a current comparison. Do not assume `origin` is the publishing
remote in a fork, or use stale tracking refs as proof of remote state.

The optional read-only helper collects local inventory:

```bash
bash <skill-dir>/scripts/prepare_commit.sh <repo-path> <base-ref>
```

It reports worktree changes, commits relative to a supplied base, the PR diff,
and upstream divergence. It does not fetch, select a base, scan secrets, or
establish authorization. Direct Git commands are equally suitable.

| State | Next action within the request |
| --- | --- |
| Intended edits remain uncommitted | Review and commit that scope. Preserve unrelated edits and staged intent. |
| Worktree is clean; intended commits are unpublished | Inspect the outgoing commits, then push if requested. No empty commit is needed. |
| Branch is pushed; no open PR exists | Create the requested PR after checking base/head and the proposed diff. |
| Open PR already exists | Reuse it. Push requested updates; change its description if authorized and needed to reflect the final scope. |
| No intended changes remain relative to the base | Report that state or the already-merged PR; do not manufacture a commit or PR. |

For an existing PR, check its actual head repository/branch, base, and state.
`gh pr view <branch> --repo <owner/repo> --json number,url,state,baseRefName,headRefOid`
uses a positional branch argument, not `--head`. Distinguish an absent PR from
an authentication/network error. In fork or ambiguous-name cases, list candidate
PRs and verify the head repository before selecting one.

### Commit and publish only what is authorized

Create a task branch when needed to keep work off the default branch or retain
detached commits. Follow repository naming/message conventions; use
`references/conventions.md` only as a fallback. If commits on a shared/default
branch belong to other work, preserve them and isolate this task rather than
publishing them incidentally.

Inspect the proposed index and outgoing commit range, including intermediate
commits, for unintended private data or credentials. Filename patterns are hints,
not proof of either sensitivity or safety: sanitized fixtures and public keys
may be legitimate. Keep actual secrets out of publication. A later deletion does
not remove a secret from earlier commits; pause publication of affected history
and resolve it within the user's authority. Do not echo credential values.

Use the selected push remote and branch. Diagnose rejection or divergence before
retrying; do not force-push, rewrite history, or discard work as an automatic
repair. Existing authorization persists; ask only when a necessary decision or
additional permission is missing.

Before creating a PR, check again for an existing one. Use an explicit base/head,
respect draft intent and the repository template, and pass Markdown with
`--body-file` to avoid shell expansion. Lead with the concrete problem and final
behavior, then actual validation and material limits. Distinguish checks already
run from suggested checks. `references/pr-template.md` is an optional fallback.
If a create/push request times out, inspect remote state before retrying so an
ambiguous success does not produce duplicate actions.

### Merge and sync, when requested

Use `references/merge-sync.md` for review/CI checks, merge policy, and safe
branch/worktree cleanup. Opening a PR alone does not activate this phase or
queue a reviewer. Preserve existing review/merge authorization without asking
for it again.

## Boundaries

- Local review or advice-only requests do not authorize publication.
- Preserve unrelated changes, branches, and concurrent work; do not stash,
  reset, rebase, or delete them merely to make a workflow proceed.
- Sibling skills are optional sources of guidance, not mandatory preflight
  gates. Reuse relevant test evidence; this skill adds no full-suite rerun.

## Output

Report the PR URL or commit/branch for a narrower request, plus remaining blockers.

## Verification

Confirm the requested remote branch/PR reflects the intended commit and base.
Do not claim CI/review completion merely because a PR was created. For merge/sync,
confirm remote merge state and which requested checkouts actually synced.

## Resources

- `commands/commit-push-pr.md` — command entrypoint for this same workflow.
- `scripts/prepare_commit.sh` — optional read-only local inventory.
- `references/conventions.md`, `references/pr-template.md` — fallbacks where the
  repository has no convention or template.
- `references/merge-sync.md` — conditional delivery and cleanup guidance.
- `evals/behavioral-scenarios.md` — intended behavior replay cases.

## Sibling skills

- `local-review` — a local review when requested or useful for the change.
- `verify-before-complete` — resolve consequential gaps in completion evidence.
