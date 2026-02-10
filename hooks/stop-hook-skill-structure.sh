#!/bin/bash

# Stop hook: validate structure of skill directories that have staged changes.
# Checks that modified skill directories have required SKILL.md and that the
# skill name in frontmatter matches the directory name.
#
# Exit codes:
#   0 = all checks passed
#   2 = structural issues found

input=$(cat)

# Recursion prevention
stop_hook_active=$(echo "$input" | jq -r '.stop_hook_active')
if [[ "$stop_hook_active" = "true" ]]; then
  exit 0
fi

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [[ -z "$REPO_ROOT" ]]; then
  exit 0
fi

SKILLS_DIR="$REPO_ROOT/skills"
if [[ ! -d "$SKILLS_DIR" ]]; then
  exit 0
fi

# Get list of skill directories with staged or unstaged changes
changed_skills=()
while IFS= read -r file; do
  # Check if the changed file is under skills/
  if [[ "$file" == skills/* ]]; then
    # Extract the skill directory name (first path component after skills/)
    skill_name=$(echo "$file" | cut -d'/' -f2)
    if [[ -n "$skill_name" ]]; then
      changed_skills+=("$skill_name")
    fi
  fi
done < <(cd "$REPO_ROOT" && git diff --name-only HEAD 2>/dev/null; git diff --cached --name-only 2>/dev/null; git ls-files --others --exclude-standard 2>/dev/null)

# Deduplicate
changed_skills=($(printf '%s\n' "${changed_skills[@]}" | sort -u))

if [[ ${#changed_skills[@]} -eq 0 ]]; then
  exit 0
fi

errors=()

for skill_name in "${changed_skills[@]}"; do
  skill_dir="$SKILLS_DIR/$skill_name"

  # Skip if the directory doesn't exist (deleted skill)
  if [[ ! -d "$skill_dir" ]]; then
    continue
  fi

  # Check SKILL.md exists
  skill_md="$skill_dir/SKILL.md"
  if [[ ! -f "$skill_md" ]]; then
    errors+=("$skill_name: missing SKILL.md")
    continue
  fi

  # Extract frontmatter name and check it matches directory name
  fm_name=$(sed -n '/^---$/,/^---$/p' "$skill_md" | sed '1d;$d' | grep -m1 '^name:' | sed 's/^name:[[:space:]]*//' | sed 's/^["'"'"']//;s/["'"'"']$//')

  if [[ -z "$fm_name" ]]; then
    errors+=("$skill_name: SKILL.md missing 'name' in frontmatter")
  elif [[ "$fm_name" != "$skill_name" ]]; then
    errors+=("$skill_name: directory name doesn't match frontmatter name '$fm_name'")
  fi

  # Check description exists
  fm_desc=$(sed -n '/^---$/,/^---$/p' "$skill_md" | sed '1d;$d' | grep -m1 '^description:')
  if [[ -z "$fm_desc" ]]; then
    errors+=("$skill_name: SKILL.md missing 'description' in frontmatter")
  fi
done

if [[ ${#errors[@]} -gt 0 ]]; then
  echo "Skill structure issues found in modified skills:" >&2
  for err in "${errors[@]}"; do
    echo "  - $err" >&2
  done
  exit 2
fi

exit 0
