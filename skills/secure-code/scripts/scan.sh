#!/usr/bin/env bash
# Run semgrep on target files/directories and output JSON.
# Usage: scan.sh <targets...> [--config <config>]
set -euo pipefail

CONFIG="p/default"
TARGETS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --config)
      CONFIG="$2"
      shift 2
      ;;
    *)
      TARGETS+=("$1")
      shift
      ;;
  esac
done

if [[ ${#TARGETS[@]} -eq 0 ]]; then
  echo "Usage: scan.sh <file-or-directory...> [--config <config>]" >&2
  echo "Default config: p/default" >&2
  exit 1
fi

exec semgrep --json --disable-version-check --metrics=off --config "$CONFIG" "${TARGETS[@]}"
