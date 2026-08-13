#!/bin/bash

# SessionStart hook: speak up when the harness's own skill listing has moved.
#
# Sibling to session-start-skill-drift.sh, which watches *our* installed skill
# copies. This one watches what the harness actually charges for them, which
# moves without anyone deciding it should: over 2026-08-04..12 the Codex listing
# ceiling changed three times, a desktop update added a whole plugin
# marketplace, and account-synced connectors refilled recovered headroom
# overnight. The harness stays silent well past the point where it begins
# clipping descriptions mid-word, so nothing else reports this.
#
# It belongs on the interactive machine rather than in CI or a scheduled job:
# the data it reads is written by interactive sessions, so the daily driver is
# the only place it can reliably see anything. Informational only, never blocks.
#
# Debounce comes free from --update: a change is reported once and then accepted
# as the new baseline, so a Codex upgrade does not nag every session afterwards.
#
# Deliberately NOT scoped with --cwd. Baselines are filed per working directory
# inside the checker, which is what stops one project's catalog being compared
# against another's -- measured at build 0.144.1, ~/Dev listed 55 entries and
# ~/Dev/dojo listed 112, so a shared baseline would report ~57 entries added on
# every project switch and the reverse on the way back. With per-directory
# baselines the comparison is already apples-to-apples, and leaving the
# observation unscoped means this reports on the most recent interactive session
# wherever it ran, rather than going silent in a repository where Codex is
# rarely the harness in use.

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
[[ -z "$REPO_ROOT" ]] && exit 0

CHECKER="$REPO_ROOT/scripts/profiles/drift_check.py"
[[ -f "$CHECKER" ]] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

report="$(python3 "$CHECKER" --update 2>/dev/null)"
code=$?

# 0 clean and 1 cannot-evaluate are both silent: a machine that has run no
# interactive Codex session has nothing to say, and a hook that speaks every
# session is a hook that gets ignored. Persistent blindness (3) is caught by the
# scheduled check, which is the surface that can tell "quiet" from "never".
#
# Saturation (4) is the one outcome that repeats until it is acted on, and it is
# printed every session on purpose: the listing it describes is the one this
# session is running with, so the cost of staying quiet is paid here and now, in
# skills selected against descriptions cut mid-word.
case "$code" in
  2 | 3 | 4) printf '%s\n' "$report" ;;
esac

exit 0
