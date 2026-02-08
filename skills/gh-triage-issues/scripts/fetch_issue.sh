#!/bin/bash
# Fetch issue details for triage analysis
# Usage: fetch_issue.sh <owner/repo> <issue_number>

set -e

REPO="$1"
ISSUE="$2"

if [[ -z "$REPO" || -z "$ISSUE" ]]; then
    echo "Usage: fetch_issue.sh <owner/repo> <issue_number>"
    exit 1
fi

echo "=== ISSUE #$ISSUE ==="
gh issue view "$ISSUE" --repo "$REPO" --json number,title,body,state,labels,assignees,author,createdAt,reactionGroups,comments \
    --jq '
"Number: \(.number)
Title: \(.title)
State: \(.state)
Author: \(.author.login)
Created: \(.createdAt)
Labels: \(if .labels | length > 0 then [.labels[].name] | join(", ") else "(none)" end)
Assignees: \(if .assignees | length > 0 then [.assignees[].login] | join(", ") else "(none)" end)
Reactions: \([.reactionGroups[] | select(.users.totalCount > 0) | "\(.content): \(.users.totalCount)"] | if length > 0 then join(", ") else "(none)" end)
Comments: \(.comments | length)

--- DESCRIPTION ---
\(.body // "(no description)")"'