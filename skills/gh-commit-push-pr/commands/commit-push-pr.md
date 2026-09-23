---
name: commit-push-pr
description: Publish intended changes or existing commits to a GitHub PR, resuming from current repository state.
argument-hint: "[--base <branch>] [--title <title>] [--draft]"
allowed-tools: [Read, Bash(gh:*), Bash(git:*), Bash(bash skills/gh-commit-push-pr/scripts/prepare_commit.sh:*)]
---

# Commit Push PR Command

Follow `../SKILL.md` as the canonical workflow. Honor `--base`, `--title`, and
`--draft` when supplied. Existing commits need no new commit; an existing PR
should be reused. A clean worktree is not a stopping condition.

Optionally collect local state after selecting the intended base:

```bash
bash <skill-dir>/scripts/prepare_commit.sh <repo-path> <base-ref>
```

The helper is read-only and does not fetch or scan secrets. Inspect intended
changes and outgoing history, preserve unrelated work, and perform only the
requested commit/push/PR actions. Check remote state before retrying an ambiguous
failure. Use `--body-file` and the repository's PR template.

Report the resulting commit/branch or PR URL and material blockers. If merge/sync
is also requested, use `../references/merge-sync.md`; this command does not grant
that authorization by itself.
