#!/usr/bin/env bash
set -euo pipefail

GLOBAL_DIR="${VC_GLOBAL_CONFIG_DIR:-/tmp/.vercel-global}"
CACHE_DIR="${XDG_CACHE_HOME:-/tmp}"

mkdir -p "$GLOBAL_DIR" "$CACHE_DIR"

export VERCEL_DISABLE_AUTO_UPDATE=1
export NO_UPDATE_NOTIFIER=1
export XDG_CACHE_HOME="$CACHE_DIR"

exec vc -Q "$GLOBAL_DIR" "$@"
