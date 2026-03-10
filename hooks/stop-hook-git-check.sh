#!/bin/bash

# Read the JSON input from stdin
input=$(cat)

# Check if stop hook is already active (recursion prevention)
stop_hook_active=$(echo "$input" | jq -r '.stop_hook_active')
if [[ "$stop_hook_active" = "true" ]]; then
  exit 0
fi

# Check if we're in a git repository - bail if not
if ! git rev-parse --git-dir >/dev/null 2>&1; then
  exit 0
fi

# Check for uncommitted changes (both staged and unstaged)
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "There are uncommitted changes in the repository. Please commit and push these changes to the remote branch." >&2
  exit 2
fi

# Check for untracked files that might be important
untracked_files=$(git ls-files --others --exclude-standard)
if [[ -n "$untracked_files" ]]; then
  echo "There are untracked files in the repository. Please commit and push these changes to the remote branch." >&2
  exit 2
fi

resolve_protected_branches() {
  local configured default_branch

  configured="${DOJO_PROTECTED_BRANCHES:-main}"
  default_branch=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null)
  default_branch=${default_branch#origin/}

  if [[ -n "$default_branch" && " $configured " != *" $default_branch "* ]]; then
    configured="$configured $default_branch"
  fi

  printf '%s\n' "$configured" | tr ' ' '\n' | awk 'NF' | sort -u
}

is_protected_branch() {
  local branch="$1"
  local protected

  while IFS= read -r protected; do
    [[ -n "$protected" ]] || continue
    if [[ "$branch" == "$protected" ]]; then
      return 0
    fi
  done < <(resolve_protected_branches)

  return 1
}

resolve_compare_ref() {
  local default_ref protected

  default_ref=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null)
  if [[ -n "$default_ref" ]]; then
    printf '%s\n' "$default_ref"
    return 0
  fi

  while IFS= read -r protected; do
    [[ -n "$protected" ]] || continue
    if git show-ref --verify --quiet "refs/remotes/origin/$protected"; then
      printf 'origin/%s\n' "$protected"
      return 0
    fi
  done < <(resolve_protected_branches)

  return 1
}

current_branch=$(git branch --show-current)
if [[ -n "$current_branch" ]]; then
  if upstream=$(git rev-parse --abbrev-ref '@{u}' 2>/dev/null); then
    # Branch has an upstream tracking ref - compare against it
    unpushed=$(git rev-list '@{u}..HEAD' --count 2>/dev/null) || unpushed=0
    if [[ "$unpushed" -gt 0 ]]; then
      if is_protected_branch "$current_branch"; then
        echo "Branch '$current_branch' has $unpushed unpushed commit(s), but protected branches are allowed to stay local at session stop. Any push to '$current_branch' still requires an explicit DOJO_ALLOW_PROTECTED_PUSH=1 override." >&2
      else
        echo "There are $unpushed unpushed commit(s) on branch '$current_branch' (tracking $upstream). Please push these changes to the remote repository." >&2
        exit 2
      fi
    fi
  else
    # No upstream configured - compare against default branch
    compare_ref=$(resolve_compare_ref)
    if [[ -n "$compare_ref" ]]; then
      unpushed=$(git rev-list "$compare_ref..HEAD" --count 2>/dev/null) || unpushed=0
      if [[ "$unpushed" -gt 0 ]]; then
        if is_protected_branch "$current_branch"; then
          echo "Branch '$current_branch' has $unpushed unpushed commit(s) and no upstream tracking branch, but protected branches are allowed to stay local at session stop. Any push to '$current_branch' still requires an explicit DOJO_ALLOW_PROTECTED_PUSH=1 override." >&2
        else
          echo "Branch '$current_branch' has $unpushed unpushed commit(s) and no upstream tracking branch. Please push these changes to the remote repository." >&2
          exit 2
        fi
      fi
    elif ! is_protected_branch "$current_branch"; then
      echo "Branch '$current_branch' has no upstream tracking branch and no default remote branch could be resolved. Push it or set an upstream before ending the session." >&2
      exit 2
    fi
  fi
fi

exit 0
