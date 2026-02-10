#!/bin/bash

# PreToolUse hook: validate SKILL.md when Write or Edit targets one.
# Reads tool input JSON from stdin, checks if the file path is a SKILL.md,
# and runs quick_validate.py on the parent skill directory.
#
# Exit codes:
#   0 = allow (not a SKILL.md, or validation passed)
#   2 = block (validation failed)

input=$(cat)

# Extract the file path from the tool input
# Write uses "file_path", Edit uses "file_path"
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

if [[ -z "$file_path" ]]; then
  exit 0
fi

# Only validate SKILL.md files
if [[ "$(basename "$file_path")" != "SKILL.md" ]]; then
  exit 0
fi

# Determine repo root and validator path
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [[ -z "$REPO_ROOT" ]]; then
  exit 0
fi

VALIDATOR="$REPO_ROOT/skills/skill-creator/scripts/quick_validate.py"
if [[ ! -f "$VALIDATOR" ]]; then
  echo "Warning: quick_validate.py not found at $VALIDATOR — skipping validation." >&2
  exit 0
fi

# The skill directory is the parent of SKILL.md
skill_dir=$(dirname "$file_path")

# For PreToolUse, the file hasn't been written yet, so we validate the
# directory as-is. If SKILL.md doesn't exist yet (new skill), the validator
# will catch that on the PostToolUse or Stop hook instead.
if [[ ! -f "$file_path" ]]; then
  exit 0
fi

# Run validation
output=$(python3 "$VALIDATOR" "$skill_dir" 2>&1)
exit_code=$?

if [[ $exit_code -ne 0 ]]; then
  echo "SKILL.md validation failed for $(basename "$skill_dir"):" >&2
  echo "$output" >&2
  exit 2
fi

exit 0
