#!/bin/bash

# PostToolUse hook: validate implementation plan files after write/edit.
# Runs only for docs/plans/*-implementation.md and enforces the
# writing-plans schema via strict filename validation.
#
# Exit codes:
#   0 = pass / not applicable
#   2 = validation failed

input=$(cat)

file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')
if [[ -z "$file_path" ]]; then
  exit 0
fi

if [[ "$file_path" != docs/plans/*-implementation.md ]]; then
  exit 0
fi

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [[ -z "$REPO_ROOT" ]]; then
  exit 0
fi

VALIDATOR="$REPO_ROOT/skills/writing-plans/scripts/validate_plan.py"
if [[ ! -f "$VALIDATOR" ]]; then
  echo "Warning: validator not found at $VALIDATOR; skipping plan validation." >&2
  exit 0
fi

if [[ ! -f "$file_path" ]]; then
  exit 0
fi

output=$(python3 "$VALIDATOR" "$file_path" --strict-filename 2>&1)
exit_code=$?

if [[ $exit_code -ne 0 ]]; then
  echo "Implementation plan validation failed for $file_path:" >&2
  echo "$output" >&2
  exit 2
fi

exit 0
