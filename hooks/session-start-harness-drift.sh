#!/bin/bash

# WHY: runs on the interactive machine, not in CI or a scheduled job, because
# interactive sessions write the data it reads. Deliberately not scoped with
# --cwd: the checker already files baselines per working directory, so leaving
# the observation unscoped reports the most recent interactive session wherever
# it ran instead of going silent where Codex is rarely the harness in use.

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
[[ -z "$REPO_ROOT" ]] && exit 0

CHECKER="$REPO_ROOT/scripts/profiles/drift_check.py"
[[ -f "$CHECKER" ]] || exit 0

report="$(bash "$REPO_ROOT/hooks/run-python.sh" "$CHECKER" --update 2>/dev/null)"
code=$?

# WHY: clean (0) and cannot-evaluate (1) stay silent, because a hook that speaks
# every session gets ignored. Saturation (4) prints every session on purpose:
# this session is running with the clipped listing it describes.
case "$code" in
  2 | 3 | 4) printf '%s\n' "$report" ;;
esac

exit 0
