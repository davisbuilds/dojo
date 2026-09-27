# Git History and Branch Hygiene

Merge settings verified: September 27, 2026

## Repository Merge Settings

Configured on GitHub repository `davisbuilds/dojo`:

- `allow_squash_merge`: `false`
- `allow_merge_commit`: `true`
- `allow_rebase_merge`: `true`
- `delete_branch_on_merge`: `true`
- `merge_commit_title`: `PR_TITLE`
- `merge_commit_message`: `PR_BODY`

Result:

- PR branches retain their full commit history when merged.
- `main` receives either a merge commit (preserving the PR boundary) or rebased commits (linear history), depending on which strategy the merger picks for that PR.
- Squash merging is disabled — full per-commit history is preserved.
- Merged remote branches are auto-deleted.

## Merge Strategy

Merge commits and rebase merges are both allowed; squash merges are disabled.

- **Default — merge commit.** Preserves the PR as a discoverable boundary in `main`'s history. Best when the PR contains multiple meaningful commits worth keeping addressable individually.
- **Rebase merge.** Use when the PR's commits are clean and the linear history reads better without an extra merge node. Avoid if the PR's commits are noisy (WIP, fixups) — clean them up locally first.
- **Authoring expectation.** Because squash is gone, individual PR commits land in `main`. Keep PR commit messages tidy: meaningful subjects, no WIP markers, no fixup chains. Squash or reword locally before opening the PR if needed.

## CI Gates

GitHub Actions runs regression, strict skill-contract, version, and generated-file
checks in [the workflow](../../.github/workflows/skill-contract-pilot.yml).
[Operations](../system/OPERATIONS.md) owns the corresponding local commands.
Hooks provide earlier feedback; they do not replace CI.

## Verify Remote Policy

Merge settings above were queried on the stated date. Repository visibility or an
old API error does not establish current branch protection. Inspect the current
settings when changing delivery policy:

```bash
gh api repos/davisbuilds/dojo
gh api repos/davisbuilds/dojo/branches/main/protection
gh api repos/davisbuilds/dojo/rules/branches/main
```

A failed protection query is unresolved evidence, not proof that protections are
absent. Follow the project checks and review policy regardless.

## Recommended Ongoing Hygiene

1. Create short-lived feature branches from `main`.
2. Open PRs early; keep them focused.
3. Tidy your PR commit history *before* merging — reword/squash locally so what lands on `main` reads cleanly.
4. Pick **Create a merge commit** by default; pick **Rebase and merge** when linear history is materially better.
5. Periodically prune local branches:

```bash
git fetch --prune
git branch --merged main | grep -v ' main$' | xargs -n 1 git branch -d
```
