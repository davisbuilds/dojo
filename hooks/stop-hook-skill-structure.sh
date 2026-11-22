#!/bin/bash

input=$(cat)

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

changed_skills=()
while IFS= read -r file; do
  if [[ "$file" == skills/* ]]; then
    skill_name=$(echo "$file" | cut -d'/' -f2)
    if [[ -n "$skill_name" ]]; then
      changed_skills+=("$skill_name")
    fi
  fi
done < <(cd "$REPO_ROOT" && git diff --name-only HEAD 2>/dev/null; git diff --cached --name-only 2>/dev/null; git ls-files --others --exclude-standard 2>/dev/null)

changed_skills=($(printf '%s\n' "${changed_skills[@]}" | sort -u))

VERSION_CHECKER="$REPO_ROOT/skills/skill-evals/scripts/check_skill_versions.py"
if [[ -f "$VERSION_CHECKER" ]]; then
  version_output=$(bash "$REPO_ROOT/hooks/run-python.sh" "$VERSION_CHECKER" --base "${DOJO_VERSION_CHECK_BASE:-origin/main}" 2>&1)
  version_status=$?
  if [[ "$version_status" -ne 0 ]]; then
    echo "$version_output" >&2
    exit 2
  fi
fi

if [[ ${#changed_skills[@]} -eq 0 ]]; then
  exit 0
fi

errors=()

for skill_name in "${changed_skills[@]}"; do
  skill_dir="$SKILLS_DIR/$skill_name"

  if [[ "$skill_name" == _* ]]; then
    continue
  fi

  if [[ ! -d "$skill_dir" ]]; then
    continue
  fi

  skill_md="$skill_dir/SKILL.md"
  if [[ ! -f "$skill_md" ]]; then
    errors+=("$skill_name: missing SKILL.md")
    continue
  fi

  fm_name=$(sed -n '/^---$/,/^---$/p' "$skill_md" | sed '1d;$d' | grep -m1 '^name:' | sed 's/^name:[[:space:]]*//' | sed 's/^["'"'"']//;s/["'"'"']$//')

  if [[ -z "$fm_name" ]]; then
    errors+=("$skill_name: SKILL.md missing 'name' in frontmatter")
  elif [[ "$fm_name" != "$skill_name" ]]; then
    errors+=("$skill_name: directory name doesn't match frontmatter name '$fm_name'")
  fi

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
