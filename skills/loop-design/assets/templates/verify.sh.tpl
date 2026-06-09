#!/usr/bin/env bash
# Stop-condition oracle for loop: {{NAME}}
#
# Exit 0  == the loop is DONE.
# Exit !0 == keep going.
#
# This script is the single source of truth for "done" — not the agent's opinion.
# Do not weaken it to make the loop stop. If the goal changes, change the goal and the oracle together.
set -euo pipefail

{{DONE_WHEN}}
