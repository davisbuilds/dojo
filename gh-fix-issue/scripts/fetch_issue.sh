#!/bin/bash
# Fetch GitHub issue details in structured format
# Usage: fetch_issue.sh <owner/repo> <issue_number>

set -e

REPO="$1"
ISSUE="$2"

if [[ -z "$REPO" || -z "$ISSUE" ]]; then
    echo "Usage: fetch_issue.sh <owner/repo> <issue_number>"
    exit 1
fi

echo "=== ISSUE #$ISSUE ==="
gh issue view "$ISSUE" --repo "$REPO" --json number,title,body,state,labels,assignees,author,createdAt,comments \
    --jq '
"Number: \(.number)
Title: \(.title)
State: \(.state)
Author: \(.author.login)
Created: \(.createdAt)
Labels: \([.labels[].name] | join(", "))
Assignees: \([.assignees[].login] | join(", "))

--- DESCRIPTION ---
\(.body // "(no description)")

--- COMMENTS (\(.comments | length)) ---
" + ([.comments[] | "[\(.author.login) @ \(.createdAt)]:\n\(.body)\n"] | join("\n---\n"))'

echo ""
echo "=== LINKED PR/BRANCH INFO ==="
gh issue view "$ISSUE" --repo "$REPO" --json timelineItems \
    --jq '[.timelineItems[] | select(.source.url != null)] | if length > 0 then map("Linked: \(.source.url)") | join("\n") else "No linked PRs" end' 2>/dev/null || echo "No linked PRs"