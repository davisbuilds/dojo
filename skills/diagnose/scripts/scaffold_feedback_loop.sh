#!/usr/bin/env bash
# Scaffold a Phase 1 feedback loop for the diagnose skill.
#
# Writes a starter template for one of the common loop kinds. Fill in the
# bug specifics (the `# TODO:` markers) and run.
#
# Usage:
#   bash scaffold_feedback_loop.sh <kind> [path]
#
# Kinds:
#   failing-test    Failing test stub (language-agnostic placeholder)
#   curl            curl/HTTP script against a running dev server
#   cli-diff        CLI invocation diffing stdout against a snapshot
#   playwright      Headless-browser script (Node.js)
#   replay          Replay a captured trace from disk
#   harness         Throwaway harness exercising one function call
#   hitl            Human-in-the-loop bash loop (copy of hitl-loop.template.sh)
#
# Default path is ./repro.<ext>. Existing files are NOT overwritten.

set -euo pipefail

KIND="${1:-}"
DEST="${2:-}"

if [[ -z "$KIND" ]]; then
  echo "usage: bash scaffold_feedback_loop.sh <kind> [path]" >&2
  echo "kinds: failing-test curl cli-diff playwright replay harness hitl" >&2
  exit 2
fi

# Speed / sharpness / determinism checklist appended to every template.
LOOP_CHECKLIST='# Iterate on the loop itself:
#   - Faster?       Cache setup, skip unrelated init, narrow scope.
#   - Sharper?      Assert on the specific symptom, not "did not crash".
#   - Deterministic? Pin time, seed RNG, isolate filesystem, freeze network.
# Goal: a 2-second deterministic loop. 30-second flaky loops barely help.'

write_if_absent() {
  local path="$1" content="$2"
  if [[ -e "$path" ]]; then
    echo "refusing to overwrite existing file: $path" >&2
    exit 1
  fi
  printf '%s\n' "$content" > "$path"
  if [[ "$path" == *.sh || "$path" == *.js || "$path" == *.py ]]; then
    chmod +x "$path"
  fi
  echo "wrote $path"
}

case "$KIND" in
  failing-test)
    PATH_OUT="${DEST:-./repro_test.txt}"
    write_if_absent "$PATH_OUT" "# Failing test stub
#
# Pick the seam that reaches the bug: unit, integration, or e2e.
# The test should:
#   1. Set up the minimal state needed to trigger the bug.
#   2. Invoke the code path the user reported as failing.
#   3. Assert on the *exact* symptom (error message, wrong value, slow timing).
#
# Pseudocode:
#
#   describe('<bug summary>', () => {
#     it('reproduces the reported failure', async () => {
#       # TODO: arrange — minimal fixture
#       const result = await codePathUnderTest(/* TODO: input */);
#       # TODO: assert — exact symptom (not just truthiness)
#       expect(result).toEqual(/* TODO: expected */);
#     });
#   });
#
$LOOP_CHECKLIST"
    ;;

  curl)
    PATH_OUT="${DEST:-./repro_curl.sh}"
    write_if_absent "$PATH_OUT" "#!/usr/bin/env bash
# curl-based reproduction loop against a running dev server.
set -euo pipefail

BASE_URL=\"\${BASE_URL:-http://localhost:3000}\"
# TODO: endpoint, method, headers, payload that triggers the bug
ENDPOINT=\"/api/TODO\"
PAYLOAD='{\"TODO\": \"value\"}'

echo \">>> hitting \$BASE_URL\$ENDPOINT\"
RESPONSE=\$(curl -sS -X POST \\
  -H 'Content-Type: application/json' \\
  -d \"\$PAYLOAD\" \\
  \"\$BASE_URL\$ENDPOINT\")

echo \"\$RESPONSE\"

# TODO: assert on the exact symptom — error string, wrong field, status code
echo \"\$RESPONSE\" | grep -q 'EXPECTED_SYMPTOM' && {
  echo 'BUG REPRODUCED'
  exit 0
}
echo 'bug did NOT reproduce' >&2
exit 1

$LOOP_CHECKLIST"
    ;;

  cli-diff)
    PATH_OUT="${DEST:-./repro_cli_diff.sh}"
    write_if_absent "$PATH_OUT" "#!/usr/bin/env bash
# CLI invocation diffing stdout against a known-good snapshot.
set -euo pipefail

# TODO: command + args that trigger the bug
CMD=(echo TODO_REPLACE_ME)
SNAPSHOT=\"\${SNAPSHOT:-./snapshot.txt}\"

if [[ ! -f \"\$SNAPSHOT\" ]]; then
  echo \"capturing baseline snapshot at \$SNAPSHOT\" >&2
  \"\${CMD[@]}\" > \"\$SNAPSHOT\"
  echo 'baseline captured. fix the bug or revert, then re-run to compare.' >&2
  exit 0
fi

ACTUAL=\$(\"\${CMD[@]}\")
if diff -u \"\$SNAPSHOT\" <(printf '%s\\n' \"\$ACTUAL\"); then
  echo 'matches snapshot — bug NOT reproduced'
  exit 1
fi
echo 'differs from snapshot — BUG REPRODUCED'
exit 0

$LOOP_CHECKLIST"
    ;;

  playwright)
    PATH_OUT="${DEST:-./repro_playwright.js}"
    write_if_absent "$PATH_OUT" "// Playwright headless-browser reproduction loop.
// Run with: node repro_playwright.js
//
// Prereq: npm i -D playwright && npx playwright install
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext();
  const page = await ctx.newPage();

  // capture console + network for assertion
  const consoleErrors = [];
  page.on('console', (msg) => {
    if (msg.type() === 'error') consoleErrors.push(msg.text());
  });

  // TODO: navigate to the page that triggers the bug
  await page.goto(process.env.BASE_URL || 'http://localhost:3000');

  // TODO: drive the UI to the bug — clicks, form fills, etc.
  // await page.click('text=Export');

  // TODO: assert on the EXACT symptom
  // const errorBanner = await page.locator('.error-banner').textContent();
  // if (errorBanner?.includes('EXPECTED_SYMPTOM')) { ... }

  await browser.close();

  if (consoleErrors.length > 0) {
    console.log('BUG REPRODUCED. console errors:');
    consoleErrors.forEach((e) => console.log('  ', e));
    process.exit(0);
  }
  console.error('bug did NOT reproduce');
  process.exit(1);
})();

$LOOP_CHECKLIST"
    ;;

  replay)
    PATH_OUT="${DEST:-./repro_replay.sh}"
    write_if_absent "$PATH_OUT" "#!/usr/bin/env bash
# Replay a captured trace from disk through the code path in isolation.
#
# Pattern:
#   1. Capture once: real network request, payload, event log -> ./trace/
#   2. Replay: feed the captured input into the code under test.
#   3. Assert the same wrong output the user saw.
#
# Capturing rules:
#   - One file per input (./trace/req-001.json, ./trace/req-002.json...).
#   - Strip secrets before checking in.
#   - Note the exact app version + git SHA the trace was captured at.
set -euo pipefail

TRACE_DIR=\"\${TRACE_DIR:-./trace}\"
[[ -d \"\$TRACE_DIR\" ]] || { echo \"missing \$TRACE_DIR — capture a real failure first\" >&2; exit 2; }

reproduced=0
for f in \"\$TRACE_DIR\"/*; do
  echo \">>> replay \$f\"
  # TODO: pipe the captured input into the code under test
  # OUTPUT=\$(your_cli_or_handler < \"\$f\")
  # echo \"\$OUTPUT\" | grep -q 'EXPECTED_SYMPTOM' && reproduced=\$((reproduced + 1))
done

if (( reproduced > 0 )); then
  echo \"BUG REPRODUCED on \$reproduced trace(s)\"
  exit 0
fi
echo 'no traces reproduced the bug' >&2
exit 1

$LOOP_CHECKLIST"
    ;;

  harness)
    PATH_OUT="${DEST:-./repro_harness.sh}"
    write_if_absent "$PATH_OUT" "#!/usr/bin/env bash
# Throwaway harness — minimal subset of the system that exercises the bug
# code path with a single function call. Mock everything else.
#
# Use when:
#   - Spinning up the full app is slow.
#   - The bug is in one function but its callers are tangled.
#   - You need a tight loop for hypothesis testing.
set -euo pipefail

# TODO: language-appropriate harness invocation. Examples:
#   node -e \"require('./src/buggy').fn({ TODO: 'fixture' })\"
#   python -c \"from src.buggy import fn; print(fn(TODO))\"
#   go run ./cmd/harness
#
# The harness file should:
#   1. Import only the module under test.
#   2. Stub every external dep with the simplest fake that compiles.
#   3. Invoke the failing function with a minimal fixture.
#   4. exit 0 on bug-reproduced, exit 1 on not-reproduced.

echo 'TODO: implement harness invocation' >&2
exit 2

$LOOP_CHECKLIST"
    ;;

  hitl)
    PATH_OUT="${DEST:-./repro_hitl.sh}"
    HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [[ -f "$HERE/hitl-loop.template.sh" ]]; then
      cp "$HERE/hitl-loop.template.sh" "$PATH_OUT"
      chmod +x "$PATH_OUT"
      echo "wrote $PATH_OUT (copy of hitl-loop.template.sh)"
    else
      echo "could not find hitl-loop.template.sh next to this script" >&2
      exit 1
    fi
    ;;

  *)
    echo "unknown kind: $KIND" >&2
    echo "kinds: failing-test curl cli-diff playwright replay harness hitl" >&2
    exit 2
    ;;
esac
