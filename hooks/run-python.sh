#!/bin/bash
# Use the checkout's installed environment; never sync or download in a hook.
set -e
HOOK_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ ! -x "$HOOK_DIR/../.venv/bin/python3" ]]; then
  echo "Dojo hook unavailable: run 'uv sync --locked' in the Dojo checkout." >&2
  exit 1
fi
exec "$HOOK_DIR/../.venv/bin/python3" "$@"
