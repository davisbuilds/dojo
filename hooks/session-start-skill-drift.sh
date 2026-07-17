#!/bin/bash

# SessionStart hook: warn once when installed global skill copies have diverged
# from canonical. Informational only (never blocks), and debounced by
# hooks/skill_drift_state.py so it speaks only when the drifted set changes —
# not on every session while the same drift persists.

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [[ -z "$REPO_ROOT" ]]; then
  exit 0
fi

AUDIT="$REPO_ROOT/skills/skill-standardizer/scripts/audit.py"
NOTIFIER="$REPO_ROOT/hooks/skill_drift_state.py"
STATE="$REPO_ROOT/.skill-standardizer/drift-state.json"

# Only meaningful in a checkout that actually has the standardizer.
if [[ ! -f "$AUDIT" || ! -f "$NOTIFIER" ]]; then
  exit 0
fi
command -v python3 >/dev/null 2>&1 || exit 0

# Audit exits 2 on drift; we read the drifted set out of the JSON, so the exit
# code is irrelevant here. Any failure degrades to an empty report (silent).
report="$(python3 "$AUDIT" --global-policy prefer-primary-link --format json 2>/dev/null)"
[[ -z "$report" ]] && exit 0

printf '%s' "$report" | python3 "$NOTIFIER" --state "$STATE" 2>/dev/null

exit 0
