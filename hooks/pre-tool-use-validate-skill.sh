#!/bin/bash

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [[ -z "$REPO_ROOT" ]]; then
  exit 0
fi

VALIDATOR="$REPO_ROOT/hooks/validate_skill_payload.py"
if [[ ! -f "$VALIDATOR" ]]; then
  echo "Warning: validate_skill_payload.py not found at $VALIDATOR — skipping validation." >&2
  exit 0
fi

bash "$REPO_ROOT/hooks/run-python.sh" "$VALIDATOR"
