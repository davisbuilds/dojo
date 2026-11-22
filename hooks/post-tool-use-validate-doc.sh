#!/bin/bash

kind="$1"
case "$kind" in
  spec|plan) ;;
  *) echo "usage: $0 spec|plan" >&2; exit 0 ;;
esac

input=$(cat)

file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')
if [[ -z "$file_path" || ! -f "$file_path" ]]; then
  exit 0
fi

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [[ -z "$REPO_ROOT" ]]; then
  exit 0
fi
REPO_ROOT="$(cd -- "$REPO_ROOT" && pwd -P)"

# WHY: compare physical paths so a symlinked checkout or /tmp alias still matches.
file_dir="$(cd -- "$(dirname -- "$file_path")" 2>/dev/null && pwd -P)" || exit 0
relative="$file_dir/$(basename -- "$file_path")"
relative="${relative#"$REPO_ROOT"/}"

if [[ "$relative" != "docs/${kind}s/"*"-${kind}.md" ]]; then
  exit 0
fi

VALIDATOR="$REPO_ROOT/skills/write-${kind}/scripts/validate_${kind}.py"
if [[ ! -f "$VALIDATOR" ]]; then
  echo "Warning: validator not found at $VALIDATOR; skipping ${kind} validation." >&2
  exit 0
fi

output=$(bash "$REPO_ROOT/hooks/run-python.sh" "$VALIDATOR" "$REPO_ROOT/$relative" --strict-filename 2>&1)
exit_code=$?

if [[ $exit_code -ne 0 ]]; then
  echo "${kind} validation failed for $relative:" >&2
  echo "$output" >&2
  exit 2
fi

exit 0
