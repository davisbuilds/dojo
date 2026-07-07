#!/usr/bin/env bash
set -euo pipefail

MODE="working"
BASE="origin/main"
HEAD_REF="HEAD"
MAX_DIFF_LINES=4000
MAX_DIFF_LINES_EXPLICIT=0
DEEP=0
BASE_NOTE=""

usage() {
  cat <<USAGE
Usage: collect_review_context.sh [options]

Options:
  --mode <working|staged|branch>   Review target mode (default: working)
  --base <ref>                     Base ref for branch mode (default: origin/main)
  --head <ref>                     Head ref for branch mode (default: HEAD)
  --max-diff-lines <n>             Max diff lines to print (default: 4000)
  --deep                           Use a larger default diff budget (8000 lines)
  -h, --help                       Show this help
USAGE
}

need_value() {
  local flag="$1"
  local value="${2:-}"
  if [[ -z "$value" || "$value" == --* ]]; then
    echo "$flag requires a value" >&2
    usage
    exit 1
  fi
}

ref_exists() {
  git rev-parse --verify "$1" >/dev/null 2>&1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      need_value "$1" "${2:-}"
      MODE="${2:-}"
      shift 2
      ;;
    --base)
      need_value "$1" "${2:-}"
      BASE="${2:-}"
      shift 2
      ;;
    --head)
      need_value "$1" "${2:-}"
      HEAD_REF="${2:-}"
      shift 2
      ;;
    --max-diff-lines)
      need_value "$1" "${2:-}"
      MAX_DIFF_LINES="${2:-}"
      MAX_DIFF_LINES_EXPLICIT=1
      shift 2
      ;;
    --deep)
      DEEP=1
      shift
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

if [[ "$DEEP" == "1" && "$MAX_DIFF_LINES_EXPLICIT" == "0" ]]; then
  MAX_DIFF_LINES=8000
fi

if ! [[ "$MAX_DIFF_LINES" =~ ^[1-9][0-9]*$ ]]; then
  echo "--max-diff-lines must be a positive integer" >&2
  usage
  exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Not inside a git repository." >&2
  exit 1
fi

section() {
  printf '\n=== %s ===\n' "$1"
}

REVIEW_TARGET=""
UNTRACKED_FILES=()
UNTRACKED_COUNT=0
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
  if ! ref_exists "$BASE"; then
    if [[ "$BASE" == "origin/main" ]] && ref_exists "main"; then
      BASE_NOTE="origin/main unavailable; fell back to local main"
      BASE="main"
    else
      echo "Base ref not found: $BASE" >&2
      exit 1
    fi
  fi
  if ! ref_exists "$HEAD_REF"; then
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
printf 'Deep: %s\n' "$([[ "$DEEP" == "1" ]] && echo true || echo false)"
printf 'Max diff lines: %s\n' "$MAX_DIFF_LINES"
if [[ -n "$BASE_NOTE" ]]; then
  printf 'Base note: %s\n' "$BASE_NOTE"
fi

section "CHANGED FILES"
"${NAME_STATUS_CMD[@]}" || true
if [[ "$MODE" == "working" ]]; then
  while IFS= read -r untracked_path; do
    if [[ -n "$untracked_path" ]]; then
      UNTRACKED_FILES+=("$untracked_path")
      UNTRACKED_COUNT=$((UNTRACKED_COUNT + 1))
    fi
  done < <(git ls-files --others --exclude-standard || true)
  if [[ "$UNTRACKED_COUNT" -gt 0 ]]; then
    for untracked_path in "${UNTRACKED_FILES[@]}"; do
      printf '??\t%s\n' "$untracked_path"
    done
  fi
fi

CHANGED_FILES=()
CHANGED_COUNT=0
while IFS= read -r file_path; do
  if [[ -n "$file_path" ]]; then
    CHANGED_FILES+=("$file_path")
    CHANGED_COUNT=$((CHANGED_COUNT + 1))
  fi
done < <("${NAME_ONLY_CMD[@]}" || true)
if [[ "$MODE" == "working" && "$UNTRACKED_COUNT" -gt 0 ]]; then
  CHANGED_FILES+=("${UNTRACKED_FILES[@]}")
  CHANGED_COUNT=$((CHANGED_COUNT + UNTRACKED_COUNT))
fi

if [[ "$CHANGED_COUNT" -eq 0 ]]; then
  section "SUMMARY"
  echo "No changes detected for this mode."
  exit 0
fi

section "DIFF STAT"
"${STAT_CMD[@]}" || true
if [[ "$MODE" == "working" && "$UNTRACKED_COUNT" -gt 0 ]]; then
  printf '\nUntracked files: %s\n' "$UNTRACKED_COUNT"
fi

section "TEST FILES TOUCHED"
printf '%s\n' "${CHANGED_FILES[@]}" | grep -E '(^|/)(test|tests|spec|__tests__)/|(\.|_)(test|spec)\.' || echo "(none)"

section "SENSITIVE OR HIGH-RISK PATHS"
printf '%s\n' "${CHANGED_FILES[@]}" | grep -E '(^|/)(auth|security|permission|permissions|payment|billing|migration|migrations|schema|infra|deploy|docker|k8s|terraform|secret|secrets|config)(/|$)|\.sql$|schema\.rb$' || echo "(none)"

section "ATTENTION MARKERS IN CHANGED FILES"
MARKER_RE='[T]ODO|[F]IXME|[H]ACK|[X]XX'
if command -v rg >/dev/null 2>&1; then
  rg -n --no-heading -e "$MARKER_RE" "${CHANGED_FILES[@]}" 2>/dev/null || echo "(none)"
else
  grep -R -n -E "$MARKER_RE" "${CHANGED_FILES[@]}" 2>/dev/null || echo "(none)"
fi

section "DIFF"
DIFF_TMP="$(mktemp)"
"${DIFF_CMD[@]}" > "$DIFF_TMP" || true
if [[ "$MODE" == "working" && "$UNTRACKED_COUNT" -gt 0 ]]; then
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
