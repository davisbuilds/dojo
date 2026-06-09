#!/bin/bash

# PreToolUse hook: block `git push` to a protected branch unless the command
# carries an explicit override token (DOJO_ALLOW_PROTECTED_PUSH=1). Kept
# separate from the stop hook so protected branches can hold local commits
# without forcing a push.
#
# Detection is scoped to the actual push invocation. The command is split on
# shell control operators into segments, and a segment is only treated as a
# push when its git *subcommand* is `push`; branch targeting is then evaluated
# against that push's own arguments. This avoids false positives from the word
# "push" or a branch name appearing inside commit messages or unrelated
# commands -- e.g. `git commit -m "...not push"` or `git log main..feature`.
#
# Written for bash 3.2 (macOS /bin/bash): no mapfile, no `\n` in sed.

input=$(cat)

tool_name=$(echo "$input" | jq -r '.tool_name // empty')
[[ "$tool_name" == "Bash" ]] || exit 0

command=$(echo "$input" | jq -r '.tool_input.command // empty')
[[ -n "$command" ]] || exit 0

command_has_override() {
  [[ "$command" =~ (^|[[:space:]])DOJO_ALLOW_PROTECTED_PUSH=1([[:space:]]|$) ]]
}

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

# If a segment is a `git push` invocation, print its push arguments and return
# 0; otherwise return 1. Skips git global options (including the ones that
# consume the following token, e.g. `-C <dir>`) so the subcommand is found.
extract_push_args() {
  local segment="$1"
  local -a tokens
  read -ra tokens <<< "$segment"
  local n=${#tokens[@]}
  local i=0

  while (( i < n )); do
    case "${tokens[$i]}" in
      git|*/git) break ;;
    esac
    i=$((i + 1))
  done
  (( i < n )) || return 1
  i=$((i + 1))

  while (( i < n )); do
    case "${tokens[$i]}" in
      -C|-c|--git-dir|--work-tree|--namespace|--super-prefix|--exec-path) i=$((i + 2)) ;;
      -*) i=$((i + 1)) ;;
      *) break ;;
    esac
  done
  (( i < n )) || return 1
  [[ "${tokens[$i]}" == push ]] || return 1

  i=$((i + 1))
  local out=""
  while (( i < n )); do
    out="$out${tokens[$i]} "
    i=$((i + 1))
  done
  printf '%s' "$out"
  return 0
}

command_has_override && exit 0

# Split into one segment per command. tr maps each control operator to a
# newline (`||`/`&&` become two newlines -> a harmless empty segment). Parens
# are included, which also isolates $(...) command-substitution bodies.
segments_raw=$(printf '%s' "$command" | tr ';|&()' '\n\n\n\n\n')

current_branch=$(git branch --show-current 2>/dev/null)
protected_list=$(resolve_protected_branches)

while IFS= read -r segment; do
  push_args=$(extract_push_args "$segment") || continue
  # This segment is a real `git push`. Evaluate only its arguments.

  positionals=""
  pushes_all=0
  skip_next=0
  for tok in $push_args; do
    if [[ "$skip_next" == "1" ]]; then skip_next=0; continue; fi
    case "$tok" in
      --all|--mirror) pushes_all=1 ;;
      -o|--push-option|--repo|--receive-pack|--exec) skip_next=1 ;;
      -*) ;;
      *) positionals="$positionals $tok" ;;
    esac
  done

  # First positional is the remote; any later positionals are refspecs.
  set -- $positionals
  has_refspec=0
  [[ $# -gt 1 ]] && has_refspec=1

  for branch in $protected_list; do
    [[ -n "$branch" ]] || continue
    targeted=0

    idx=0
    for p in $positionals; do
      idx=$((idx + 1))
      [[ "$idx" -eq 1 ]] && continue   # skip the remote
      dst="${p##*:}"                   # refspec destination (right of last colon)
      dst="${dst#refs/heads/}"
      [[ "$dst" == "$branch" ]] && targeted=1
    done

    [[ "$pushes_all" == "1" ]] && targeted=1

    # No explicit refspec -> push sends the current branch.
    if [[ "$has_refspec" == "0" && "$current_branch" == "$branch" ]]; then
      targeted=1
    fi

    if [[ "$targeted" == "1" ]]; then
      echo "Pushes to protected branch '$branch' require explicit human approval. Re-run with DOJO_ALLOW_PROTECTED_PUSH=1 in the command once the user has approved that exact push." >&2
      exit 2
    fi
  done
done <<< "$segments_raw"

exit 0
