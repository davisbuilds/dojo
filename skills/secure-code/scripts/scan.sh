#!/usr/bin/env bash
# Keep the installed command entry point; the adapter owns argument validation.
set -euo pipefail
exec python3 "$(dirname -- "$0")/scan.py" "$@"
