#!/usr/bin/env bash
set -euo pipefail

MODE="working"
BASE="origin/main"
HEAD_REF="HEAD"
MAX_DIFF_LINES=4000

usage() {
  cat <<USAGE
Usage: collect_review_context.sh [options]

Options:
  --mode <working|staged|branch>   Review target mode (default: working)
  --base <ref>                     Base ref for branch mode (default: origin/main)
  --head <ref>                     Head ref for branch mode (default: HEAD)
  --max-diff-lines <n>             Max diff lines to print (default: 4000)
  -h, --help                       Show this help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      MODE="${2:-}"
      shift 2
      ;;
    --base)
      BASE="${2:-}"
      shift 2
      ;;
    --head)
      HEAD_REF="${2:-}"
      shift 2
      ;;
    --max-diff-lines)
      MAX_DIFF_LINES="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Not inside a git repository." >&2
  exit 1
fi

section() {
  printf '\n=== %s ===\n' "$1"
}

REVIEW_TARGET=""
UNTRACKED_FILES=()
if [[ "$MODE" == "working" ]]; then
  REVIEW_TARGET="working tree vs HEAD"
  NAME_STATUS_CMD=(git diff --name-status)
  NAME_ONLY_CMD=(git diff --name-only --diff-filter=ACMRTUXB)
  STAT_CMD=(git diff --stat)
  DIFF_CMD=(git diff --no-color --patch)
elif [[ "$MODE" == "staged" ]]; then
  REVIEW_TARGET="staged changes vs HEAD"
  NAME_STATUS_CMD=(git diff --cached --name-status)
  NAME_ONLY_CMD=(git diff --cached --name-only --diff-filter=ACMRTUXB)
  STAT_CMD=(git diff --cached --stat)
  DIFF_CMD=(git diff --cached --no-color --patch)
elif [[ "$MODE" == "branch" ]]; then
  if ! git rev-parse --verify "$BASE" >/dev/null 2>&1; then
    echo "Base ref not found: $BASE" >&2
    exit 1
  fi
  if ! git rev-parse --verify "$HEAD_REF" >/dev/null 2>&1; then
    echo "Head ref not found: $HEAD_REF" >&2
    exit 1
  fi

  MERGE_BASE="$(git merge-base "$BASE" "$HEAD_REF")"
  REVIEW_TARGET="$HEAD_REF compared to merge-base($BASE, $HEAD_REF) = $MERGE_BASE"
  NAME_STATUS_CMD=(git diff --name-status "$MERGE_BASE" "$HEAD_REF")
  NAME_ONLY_CMD=(git diff --name-only --diff-filter=ACMRTUXB "$MERGE_BASE" "$HEAD_REF")
  STAT_CMD=(git diff --stat "$MERGE_BASE" "$HEAD_REF")
  DIFF_CMD=(git diff --no-color --patch "$MERGE_BASE" "$HEAD_REF")
else
  echo "Invalid mode: $MODE" >&2
  usage
  exit 1
fi

section "REVIEW TARGET"
printf 'Mode: %s\n' "$MODE"
printf 'Target: %s\n' "$REVIEW_TARGET"
printf 'Repo: %s\n' "$(basename "$(git rev-parse --show-toplevel)")"
printf 'Branch: %s\n' "$(git rev-parse --abbrev-ref HEAD)"

section "CHANGED FILES"
"${NAME_STATUS_CMD[@]}" || true
if [[ "$MODE" == "working" ]]; then
  while IFS= read -r untracked_path; do
    [[ -n "$untracked_path" ]] && UNTRACKED_FILES+=("$untracked_path")
  done < <(git ls-files --others --exclude-standard || true)
  for untracked_path in "${UNTRACKED_FILES[@]}"; do
    printf '??\t%s\n' "$untracked_path"
  done
fi

CHANGED_FILES=()
while IFS= read -r file_path; do
  [[ -n "$file_path" ]] && CHANGED_FILES+=("$file_path")
done < <("${NAME_ONLY_CMD[@]}" || true)
if [[ "$MODE" == "working" && ${#UNTRACKED_FILES[@]} -gt 0 ]]; then
  CHANGED_FILES+=("${UNTRACKED_FILES[@]}")
fi

if [[ ${#CHANGED_FILES[@]} -eq 0 ]]; then
  section "SUMMARY"
  echo "No changes detected for this mode."
  exit 0
fi

section "DIFF STAT"
"${STAT_CMD[@]}" || true
if [[ "$MODE" == "working" && ${#UNTRACKED_FILES[@]} -gt 0 ]]; then
  printf '\nUntracked files: %s\n' "${#UNTRACKED_FILES[@]}"
fi

section "TEST FILES TOUCHED"
printf '%s\n' "${CHANGED_FILES[@]}" | grep -E '(^|/)(test|tests|spec|__tests__)/|(\.|_)(test|spec)\.' || echo "(none)"

section "SENSITIVE OR HIGH-RISK PATHS"
printf '%s\n' "${CHANGED_FILES[@]}" | grep -E '(^|/)(auth|security|permission|permissions|payment|billing|migration|migrations|schema|infra|deploy|docker|k8s|terraform|secret|secrets|config)(/|$)|\.sql$|schema\.rb$' || echo "(none)"

section "TODO/FIXME MARKERS IN CHANGED FILES"
if command -v rg >/dev/null 2>&1; then
  rg -n --no-heading -e 'TODO|FIXME|HACK|XXX' "${CHANGED_FILES[@]}" 2>/dev/null || echo "(none)"
else
  grep -R -n -E 'TODO|FIXME|HACK|XXX' "${CHANGED_FILES[@]}" 2>/dev/null || echo "(none)"
fi

section "DIFF"
DIFF_TMP="$(mktemp)"
"${DIFF_CMD[@]}" > "$DIFF_TMP" || true
if [[ "$MODE" == "working" && ${#UNTRACKED_FILES[@]} -gt 0 ]]; then
  for untracked_path in "${UNTRACKED_FILES[@]}"; do
    if [[ -f "$untracked_path" ]]; then
      git diff --no-color --no-index -- /dev/null "$untracked_path" >> "$DIFF_TMP" || true
    fi
  done
fi
TOTAL_DIFF_LINES="$(wc -l < "$DIFF_TMP" | tr -d ' ')"
sed -n "1,${MAX_DIFF_LINES}p" "$DIFF_TMP"
if [[ "$TOTAL_DIFF_LINES" -gt "$MAX_DIFF_LINES" ]]; then
  printf '\n[diff truncated: showing first %s of %s lines]\n' "$MAX_DIFF_LINES" "$TOTAL_DIFF_LINES"
fi
rm -f "$DIFF_TMP"

section "REVIEW CHECKLIST"
cat <<'CHECKLIST'
- Verify correctness and possible regressions.
- Validate error handling and edge cases.
- Check for security and data integrity risks.
- Identify performance hot spots.
- Confirm tests for new behavior and risky paths.
CHECKLIST
