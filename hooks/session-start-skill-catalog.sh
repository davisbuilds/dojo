#!/bin/bash

# SessionStart hook: inject skill catalog, recent activity, and repo pointer
# Outputs context to orient any agent harness at the start of a session.

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [[ -z "$REPO_ROOT" ]]; then
  exit 0
fi

SKILLS_DIR="$REPO_ROOT/skills"
if [[ ! -d "$SKILLS_DIR" ]]; then
  exit 0
fi

# --- Pointer to AGENTS.md ---
echo "## Repository Conventions"
echo "Read AGENTS.md at the repo root for skill structure, commands, and design principles."
echo ""

# --- Skill Catalog ---
echo "## Available Skills"
echo ""

count=0
for skill_md in "$SKILLS_DIR"/*/SKILL.md; do
  [[ -f "$skill_md" ]] || continue
  skill_dir=$(dirname "$skill_md")
  skill_name=$(basename "$skill_dir")

  # Extract YAML frontmatter between --- markers
  frontmatter=$(sed -n '/^---$/,/^---$/p' "$skill_md" | sed '1d;$d')
  if [[ -z "$frontmatter" ]]; then
    continue
  fi

  # Extract name and description from frontmatter
  fm_name=$(echo "$frontmatter" | grep -m1 '^name:' | sed 's/^name:[[:space:]]*//' | sed 's/^["'"'"']//;s/["'"'"']$//')
  fm_desc=$(echo "$frontmatter" | grep -m1 '^description:' | sed 's/^description:[[:space:]]*//' | sed 's/^["'"'"']//;s/["'"'"']$//')

  if [[ -n "$fm_name" && -n "$fm_desc" ]]; then
    echo "- **${fm_name}**: ${fm_desc}"
    count=$((count + 1))
  fi
done

echo ""
echo "Total: ${count} skills available."
echo ""

# --- Recent Git Activity ---
echo "## Recent Activity"
echo ""
git -C "$REPO_ROOT" log --oneline --no-decorate -10 2>/dev/null || echo "(no git history)"
echo ""

exit 0
