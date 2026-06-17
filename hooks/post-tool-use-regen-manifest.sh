#!/bin/bash

# PostToolUse hook: after a SKILL.md (or a shared fragment) is written or edited,
# expand opt-in fragment composition and regenerate skills.json so the composed
# docs and machine-readable manifest stay in sync with skill frontmatter.

input=$(cat)

# Extract the file path from the tool input
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

if [[ -z "$file_path" ]]; then
  exit 0
fi

# Trigger on SKILL.md edits or shared-fragment edits (skills/_fragments/*)
if [[ "$(basename "$file_path")" != "SKILL.md" && "$file_path" != *"/skills/_fragments/"* && "$file_path" != "skills/_fragments/"* ]]; then
  exit 0
fi

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [[ -z "$REPO_ROOT" ]]; then
  exit 0
fi

# Expand opt-in fragment composition first (idempotent; no-op if nothing opted in).
# Surface composer failures (e.g. a missing/misspelled fragment) instead of
# silently leaving the composed SKILL.md stale.
COMPOSER="$REPO_ROOT/scripts/gen_skill_docs.py"
if [[ -f "$COMPOSER" ]]; then
  composer_output=$(python3 "$COMPOSER" 2>&1)
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

# Regenerate silently — errors are non-blocking
python3 "$GENERATOR" >/dev/null 2>&1

# Regenerate the browseable catalog from the refreshed manifest (non-blocking)
CATALOG="$REPO_ROOT/scripts/gen_catalog.py"
if [[ -f "$CATALOG" ]]; then
  python3 "$CATALOG" >/dev/null 2>&1
fi

exit 0
