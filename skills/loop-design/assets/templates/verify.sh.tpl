#!/usr/bin/env bash
# Stop-condition oracle for loop: {{NAME}}
#
# Exit 0  == the loop is DONE.
# Exit !0 == keep going.
#
# This script is the single source of truth for "done" — not the agent's opinion.
# Do not weaken it to make the loop stop. If the goal changes, change the goal and the oracle together.
#
# Self-test the oracle BEFORE you loop:  ./verify.sh --selftest [N]
# A flaky oracle is worse than no oracle — it breaks the stop condition in both
# directions (the loop fixes what is not broken, or stops on what is). The gate
# runs the oracle N times (default 10) on the current unchanged state; every run
# must return the same exit code. If they disagree, fix the oracle first.
set -euo pipefail

run_oracle() {
  {{DONE_WHEN}}
}

if [ "${1:-}" = "--selftest" ]; then
  n="${2:-10}"
  first=""
  for i in $(seq 1 "$n"); do
    if run_oracle >/dev/null 2>&1; then rc=0; else rc=$?; fi
    if [ -z "$first" ]; then
      first="$rc"
    elif [ "$rc" != "$first" ]; then
      echo "[selftest] NON-DETERMINISTIC: run $i exit=$rc != $first. Fix the oracle before looping."
      exit 1
    fi
  done
  echo "[selftest] oracle stable across $n runs (exit=$first)."
  exit 0
fi

run_oracle
