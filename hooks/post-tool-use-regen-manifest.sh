#!/bin/bash

# PostToolUse hook: regenerate skills.json after a SKILL.md is written or edited.
# Keeps the machine-readable manifest in sync with skill frontmatter.

input=$(cat)

# Extract the file path from the tool input
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

if [[ -z "$file_path" ]]; then
  exit 0
fi

# Only regenerate when a SKILL.md was modified
if [[ "$(basename "$file_path")" != "SKILL.md" ]]; then
  exit 0
fi

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [[ -z "$REPO_ROOT" ]]; then
  exit 0
fi

GENERATOR="$REPO_ROOT/scripts/generate_skills_manifest.py"
if [[ ! -f "$GENERATOR" ]]; then
  exit 0
fi

# Regenerate silently — errors are non-blocking
python3 "$GENERATOR" >/dev/null 2>&1

exit 0
