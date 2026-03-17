#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$repo_root"

python3 skills/skill-creator/scripts/quick_validate.py skills/self-improve
python3 skills/skill-evals/scripts/validate_skill_contract.py --skills self-improve --strict

tmp_json="${TMPDIR:-/tmp}/self-improve-trigger-evals.json"
python3 skills/skill-evals/scripts/run_trigger_evals.py \
  --cases skills/skill-evals/assets/trigger-collision-cases-expanded.json \
  --skills-root skills \
  --skills self-improve,session-retro,compact-session,skill-creator,writing-plans \
  --pretty > "$tmp_json"

if rg -q '"passed": false' "$tmp_json"; then
  cat "$tmp_json"
  echo "Trigger eval failures detected." >&2
  exit 1
fi

echo "PASS: self-improve smoke test"
