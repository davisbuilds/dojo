#!/bin/bash

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [[ -z "$REPO_ROOT" ]]; then
  exit 0
fi

AUDIT="$REPO_ROOT/skills/skill-standardizer/scripts/audit.py"
NOTIFIER="$REPO_ROOT/hooks/skill_drift_state.py"
STATE="$REPO_ROOT/.skill-standardizer/drift-state.json"

if [[ ! -f "$AUDIT" || ! -f "$NOTIFIER" ]]; then
  exit 0
fi

report="$(bash "$REPO_ROOT/hooks/run-python.sh" "$AUDIT" --global-policy prefer-primary-link --format json 2>/dev/null)"
[[ -z "$report" ]] && exit 0

printf '%s' "$report" | bash "$REPO_ROOT/hooks/run-python.sh" "$NOTIFIER" --state "$STATE" 2>/dev/null

exit 0
