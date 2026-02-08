#!/bin/bash
# Search for potential duplicate issues
# Usage: find_duplicates.sh <owner/repo> "<search_terms>"

set -e

REPO="$1"
SEARCH="$2"

if [[ -z "$REPO" || -z "$SEARCH" ]]; then
    echo "Usage: find_duplicates.sh <owner/repo> \"<search_terms>\""
    exit 1
fi

echo "=== SEARCHING FOR SIMILAR ISSUES ==="
echo "Query: $SEARCH"
echo ""

# Search open issues
echo "--- Open Issues ---"
gh issue list --repo "$REPO" --search "$SEARCH" --state open --limit 10 \
    --json number,title,labels,createdAt,author \
    --jq '.[] | "#\(.number) [\([.labels[].name] | join(", "))] \(.title) (by @\(.author.login), \(.createdAt | split("T")[0]))"'

echo ""

# Search closed issues (potential already-fixed duplicates)
echo "--- Closed Issues (potential prior fixes) ---"
gh issue list --repo "$REPO" --search "$SEARCH" --state closed --limit 10 \
    --json number,title,labels,createdAt,author \
    --jq '.[] | "#\(.number) [\([.labels[].name] | join(", "))] \(.title) (by @\(.author.login), \(.createdAt | split("T")[0]))"'