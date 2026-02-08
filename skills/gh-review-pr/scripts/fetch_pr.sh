#!/bin/bash
# Fetch GitHub PR details for review
# Usage: fetch_pr.sh <owner/repo> <pr_number>

set -e

REPO="$1"
PR="$2"

if [[ -z "$REPO" || -z "$PR" ]]; then
    echo "Usage: fetch_pr.sh <owner/repo> <pr_number>"
    exit 1
fi

echo "=== PR #$PR ==="
gh pr view "$PR" --repo "$REPO" --json number,title,body,state,isDraft,mergeable,author,createdAt,baseRefName,headRefName,labels,reviewDecision,reviewRequests,additions,deletions,changedFiles \
    --jq '
"Number: \(.number)
Title: \(.title)
State: \(.state)
Draft: \(.isDraft)
Mergeable: \(.mergeable)
Author: \(.author.login)
Created: \(.createdAt)
Base: \(.baseRefName) ← Head: \(.headRefName)
Labels: \([.labels[].name] | join(", "))
Review Decision: \(.reviewDecision // "PENDING")
Changes: +\(.additions) -\(.deletions) in \(.changedFiles) files

--- DESCRIPTION ---
\(.body // "(no description)")"'

echo ""
echo "=== CI/CHECK STATUS ==="
gh pr checks "$PR" --repo "$REPO" 2>/dev/null || echo "No checks configured"

echo ""
echo "=== EXISTING REVIEWS ==="
gh pr view "$PR" --repo "$REPO" --json reviews \
    --jq 'if .reviews | length > 0 then .reviews | map("[\(.author.login)] \(.state): \(.body // "(no comment)")") | join("\n---\n") else "No reviews yet" end'

echo ""
echo "=== COMMENTS ==="
gh pr view "$PR" --repo "$REPO" --json comments \
    --jq 'if .comments | length > 0 then .comments | map("[\(.author.login) @ \(.createdAt)]:\n\(.body)") | join("\n---\n") else "No comments" end'

echo ""
echo "=== FILES CHANGED ==="
gh pr diff "$PR" --repo "$REPO" --name-only

echo ""
echo "=== DIFF ==="
gh pr diff "$PR" --repo "$REPO"