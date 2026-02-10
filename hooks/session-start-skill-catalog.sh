#!/bin/bash

# SessionStart hook: inject skill catalog, recent activity, and repo pointer
# Outputs context to orient any agent harness at the start of a session.

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [[ -z "$REPO_ROOT" ]]; then
  exit 0
fi

MANIFEST="$REPO_ROOT/skills.json"

# --- Pointer to AGENTS.md ---
echo "## Repository Conventions"
echo "Read AGENTS.md at the repo root for skill structure, commands, and design principles."
echo ""

# --- Skill Catalog ---
echo "## Available Skills"
echo ""

if [[ -f "$MANIFEST" ]] && command -v jq >/dev/null 2>&1; then
  # Read from the machine-readable manifest (fast, no YAML parsing)
  count=$(jq '.skills | length' "$MANIFEST")
  jq -r '.skills[] | "- **\(.name)**: \(.description)"' "$MANIFEST"
else
  # Fallback: parse SKILL.md files directly
  count=0
  for skill_md in "$REPO_ROOT"/skills/*/SKILL.md; do
    [[ -f "$skill_md" ]] || continue
    fm_name=$(sed -n '/^---$/,/^---$/p' "$skill_md" | sed '1d;$d' | grep -m1 '^name:' | sed 's/^name:[[:space:]]*//' | sed 's/^["'"'"']//;s/["'"'"']$//')
    fm_desc=$(sed -n '/^---$/,/^---$/p' "$skill_md" | sed '1d;$d' | grep -m1 '^description:' | sed 's/^description:[[:space:]]*//' | sed 's/^["'"'"']//;s/["'"'"']$//')
    if [[ -n "$fm_name" && -n "$fm_desc" ]]; then
      echo "- **${fm_name}**: ${fm_desc}"
      count=$((count + 1))
    fi
  done
fi

echo ""
echo "Total: ${count} skills available."
echo ""

# --- Recent Git Activity ---
echo "## Recent Activity"
echo ""
git -C "$REPO_ROOT" log --oneline --no-decorate -10 2>/dev/null || echo "(no git history)"
echo ""

exit 0
