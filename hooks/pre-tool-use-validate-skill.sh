#!/bin/bash

# PreToolUse hook: validate SKILL.md when Write or Edit targets one.
#
# Delegates to hooks/validate_skill_payload.py, which validates the content the
# tool call *would produce* rather than the content already on disk. Validating
# the on-disk file deadlocks: an invalid SKILL.md blocks the very edit that would
# repair it.
#
# Exit codes:
#   0 = allow (not a SKILL.md, or the projected content is valid)
#   2 = block (the projected content would be an invalid SKILL.md)

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [[ -z "$REPO_ROOT" ]]; then
  exit 0
fi

VALIDATOR="$REPO_ROOT/hooks/validate_skill_payload.py"
if [[ ! -f "$VALIDATOR" ]]; then
  echo "Warning: validate_skill_payload.py not found at $VALIDATOR — skipping validation." >&2
  exit 0
fi

python3 "$VALIDATOR"
