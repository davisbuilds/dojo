# Merge, Sync, and Cleanup

Use only for an authorized merge/sync or post-merge cleanup request. Preserve
repository merge policy, including history requirements and stacked PR bases.

- Verify the intended PR head, required CI, and applicable review requirements,
  including unresolved review threads. A requested review still pending is not
  a clean review. Inspect threads from the first review poll; a top-level review
  summary is not a substitute. Resolve material findings before merging.
  Tie approval/checks to the relevant head; after changes, run affected checks
  and follow the repository's re-review requirements. Do not request repeated
  review passes solely as ceremony.
- Merge with the permitted strategy. Where supported, require the expected head
  (for example, `gh pr merge <number> --match-head-commit <sha>` plus the chosen
  merge strategy) so a concurrent push cannot silently change what is merged.
  Inspect dependent stacked PRs before merging/deleting their base; retarget
  them to the intended surviving base as needed within the authorized scope.
- Confirm the remote merged state, then fetch the relevant remote. Fast-forward
  clean intended checkouts. Leave dirty/diverged checkouts and unpublished
  commits intact unless their preservation/integration is already authorized;
  report the precise blocker instead of resetting or stashing automatically.
- Before deleting a local branch or worktree, establish that its work is merged
  or preserved and that it contains no later unpublished commits or needed
  untracked/ignored artifacts. A missing remote branch is not proof. Ancestry
  works for preserved history; squash/rebase merges require checking the PR's
  reviewed head and resulting changes instead.
- Inspect attached worktrees before branch deletion. Remove only a verified
  disposable, inactive worktree before its branch; do not force-remove dirty or
  concurrently used worktrees. Prune stale remote-tracking refs as appropriate.

Report the merge and sync result, naming any checkout or cleanup left pending.
Cross-machine updates and global skill distribution need their own applicable
scope; a local cleanup instruction does not authorize editing every clone.
