#!/bin/bash
# Read-only publication inventory. Usage: prepare_commit.sh [repo] [base-ref]
# Reports local refs only; the caller selects/fetches the appropriate remote/base.
# Does not scan for secrets, decide authorization, or mutate Git/GitHub state.
set -euo pipefail

cd "${1:-.}"
git rev-parse --show-toplevel
branch=$(git symbolic-ref --quiet --short HEAD || true)
printf 'Branch: %s\n' "${branch:-DETACHED}"
git status --short --branch

printf '\nStaged diff:\n'
git diff --cached --stat
printf '\nUnstaged diff:\n'
git diff --stat

if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
    printf '\nNo commits yet; no commit ranges to compare.\n'
    exit 0
fi

upstream=$(git rev-parse --symbolic-full-name --abbrev-ref '@{upstream}' 2>/dev/null || true)
if [ -n "$upstream" ]; then
    printf '\nUpstream: %s\n' "$upstream"
    ahead=$(git rev-list --count "$upstream..HEAD")
    behind=$(git rev-list --count "HEAD..$upstream")
    printf 'Ahead: %s; behind: %s\n' "$ahead" "$behind"
else
    printf '\nUpstream not configured; remote publication state is unknown.\n'
fi

base_ref=${2:-}
if [ -z "$base_ref" ]; then
    printf '\nBase not supplied; PR comparison is unknown.\n'
    exit 0
fi
if ! git rev-parse --verify --end-of-options "$base_ref^{commit}" >/dev/null 2>&1; then
    printf 'Invalid base ref: %s\n' "$base_ref" >&2
    exit 1
fi
printf '\nCommits in HEAD not in %s:\n' "$base_ref"
git log --oneline "$base_ref..HEAD" --
printf '\nPR diff relative to merge base with %s:\n' "$base_ref"
git diff --stat "$base_ref...HEAD" --
