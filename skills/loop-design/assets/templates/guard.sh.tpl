#!/usr/bin/env bash
# Reward-hacking gate for loop: {{NAME}}
#
# Cheap, deterministic, ALWAYS-ON. Run this BEFORE ./verify.sh every iteration.
# It is the layer the maker cannot talk its way past — distinct from (and far
# cheaper than) the judge. A prompt that says "don't weaken the tests" is the
# weakest defense; this gate is the real one.
#
# It fails if the maker modified a protected path (e.g. the tests the oracle
# checks). That is the classic way a loop satisfies the oracle without doing the
# work: delete an assert, mock the logic, hardcode the expected value.
#
# Exit 0 == protected paths untouched; proceed to the oracle.
# Exit 3 == protected paths changed; the result is suspect. Revert and re-do, or
#           escalate to a human. Do not let the loop continue.
#
# Checks tracked edits/deletions AND new untracked files under the protected
# paths (git status --porcelain), so a test cannot be gutted, deleted, or shadowed.
# If your runner commits mid-iteration, also diff against the iteration's start
# commit: export LOOP_BASE_REF=<sha> and this additionally fails on committed edits.
set -euo pipefail

PROTECTED=({{PROTECTED_PATHS_ARR}})

if [ "${#PROTECTED[@]}" -eq 0 ]; then
  echo "[guard] No protected paths configured — gate is a no-op. Set protected_paths in the blueprint."
  exit 0
fi

dirty="$(git status --porcelain -- "${PROTECTED[@]}" 2>/dev/null || true)"
if [ -n "${LOOP_BASE_REF:-}" ]; then
  committed="$(git diff --name-only "$LOOP_BASE_REF" -- "${PROTECTED[@]}" 2>/dev/null || true)"
  dirty="$(printf '%s\n%s' "$dirty" "$committed")"
fi

if [ -n "$(printf '%s' "$dirty" | tr -d '[:space:]')" ]; then
  echo "[guard] Protected paths changed: ${PROTECTED[*]}"
  echo "$dirty" | sed 's/^/[guard]   /'
  echo "[guard] This is reward hacking — the oracle was satisfied by weakening its own checks."
  echo "[guard] Revert protected paths (git checkout -- ${PROTECTED[*]}) and re-do the work, or stop."
  exit 3
fi
echo "[guard] Protected paths unchanged: ${PROTECTED[*]}"
