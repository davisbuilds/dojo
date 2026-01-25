#!/bin/bash
# List available labels in a repository
# Usage: list_labels.sh <owner/repo>

set -e

REPO="$1"

if [[ -z "$REPO" ]]; then
    echo "Usage: list_labels.sh <owner/repo>"
    exit 1
fi

echo "=== AVAILABLE LABELS ==="
gh label list --repo "$REPO" --limit 100 --json name,description,color \
    --jq '.[] | "• \(.name)\(if .description != "" then " - \(.description)" else "" end)"'