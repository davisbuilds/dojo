#!/usr/bin/env bash
# Thin wrapper around the @google/design.md CLI.
# Pins the version in one place so every skill invocation is deterministic.
# Bump DESIGN_MD_VERSION when re-validating against a newer release.

set -euo pipefail

DESIGN_MD_VERSION="0.1.1"

if ! command -v npx >/dev/null 2>&1; then
  echo "run_cli.sh: 'npx' is not on PATH. Install Node.js (>=18) before running this skill." >&2
  exit 127
fi

exec npx --yes "@google/design.md@${DESIGN_MD_VERSION}" "$@"
