#!/bin/bash

input=$(cat)

file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

if [[ -z "$file_path" ]]; then
  exit 0
fi

if [[ "$(basename "$file_path")" != "SKILL.md" && "$file_path" != *"/skills/_fragments/"* && "$file_path" != "skills/_fragments/"* ]]; then
  exit 0
fi

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [[ -z "$REPO_ROOT" ]]; then
  exit 0
fi

# WHY: surface composer failures, such as a misspelled fragment, instead of
# silently leaving the composed SKILL.md stale.
COMPOSER="$REPO_ROOT/scripts/gen_skill_docs.py"
if [[ -f "$COMPOSER" ]]; then
  composer_output=$(bash "$REPO_ROOT/hooks/run-python.sh" "$COMPOSER" 2>&1)
  composer_status=$?
  if [[ "$composer_status" -ne 0 ]]; then
    echo "post-tool-use-regen-manifest: fragment composition failed:" >&2
    echo "$composer_output" >&2
  fi
fi

GENERATOR="$REPO_ROOT/scripts/generate_skills_manifest.py"
if [[ ! -f "$GENERATOR" ]]; then
  exit 0
fi

bash "$REPO_ROOT/hooks/run-python.sh" "$GENERATOR" >/dev/null 2>&1

exit 0
