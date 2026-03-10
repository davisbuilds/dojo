#!/bin/bash

# PreToolUse hook: block pushes to protected branches unless the command
# carries an explicit override token. This is intentionally separate from the
# stop hook so protected branches can keep local commits without forcing a push.

input=$(cat)

tool_name=$(echo "$input" | jq -r '.tool_name // empty')
if [[ "$tool_name" != "Bash" ]]; then
  exit 0
fi

command=$(echo "$input" | jq -r '.tool_input.command // empty')
if [[ -z "$command" ]]; then
  exit 0
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

command_has_override() {
  [[ "$command" =~ (^|[[:space:]])DOJO_ALLOW_PROTECTED_PUSH=1([[:space:]]|$) ]]
}

command_looks_like_git_push() {
  [[ "$command" =~ (^|[[:space:]])git([[:space:]]+[^;&|()]+)*[[:space:]]+push([[:space:]]|$) ]]
}

command_targets_branch() {
  local branch="$1"

  [[ "$command" =~ (^|[[:space:]])$branch([[:space:]]|$) ]] && return 0
  [[ "$command" =~ :$branch([[:space:]]|$) ]] && return 0
  [[ "$command" =~ refs/heads/$branch([[:space:]]|$) ]] && return 0

  return 1
}

command_pushes_current_branch() {
  [[ "$command" =~ (^|[[:space:]])git([[:space:]]+[^;&|()]+)*[[:space:]]+push([[:space:]]|$) ]] && return 0
  [[ "$command" =~ (^|[[:space:]])git([[:space:]]+[^;&|()]+)*[[:space:]]+push([[:space:]]+--[^[:space:]]+)*[[:space:]]+origin([[:space:]]|$) ]] && return 0
  [[ "$command" =~ (^|[[:space:]])git([[:space:]]+[^;&|()]+)*[[:space:]]+push([[:space:]]+--[^[:space:]]+)*[[:space:]]+[^[:space:]]+[[:space:]]*$ ]] && return 0
  [[ "$command" =~ (^|[[:space:]])git([[:space:]]+[^;&|()]+)*[[:space:]]+push([[:space:]]|$).*--all([[:space:]]|$) ]] && return 0
  [[ "$command" =~ (^|[[:space:]])git([[:space:]]+[^;&|()]+)*[[:space:]]+push([[:space:]]|$).*--mirror([[:space:]]|$) ]] && return 0

  return 1
}

if ! command_looks_like_git_push; then
  exit 0
fi

if command_has_override; then
  exit 0
fi

current_branch=$(git branch --show-current 2>/dev/null)

while IFS= read -r protected_branch; do
  [[ -n "$protected_branch" ]] || continue

  if command_targets_branch "$protected_branch"; then
    echo "Pushes to protected branch '$protected_branch' require explicit human approval. Re-run with DOJO_ALLOW_PROTECTED_PUSH=1 in the command once the user has approved that exact push." >&2
    exit 2
  fi

  if [[ "$current_branch" == "$protected_branch" ]] && command_pushes_current_branch; then
    echo "The current branch '$protected_branch' is protected. Re-run the push with DOJO_ALLOW_PROTECTED_PUSH=1 only after explicit user approval." >&2
    exit 2
  fi
done < <(resolve_protected_branches)

exit 0
