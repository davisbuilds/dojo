#!/bin/bash

# PreToolUse hook: warn on shell constructs that fail *silently* rather than
# loudly. Never blocks -- these are all legitimate in some form, and a false
# positive that stops work costs more than the trap it prevents.
#
# The shared property of everything detected here is that it produces plausible
# output instead of an error, so nothing prompts a second look:
#
#   1. `for x in $VAR` in zsh. zsh does not word-split unquoted parameters, so
#      the loop runs ONCE over the whole string. It does not fail -- it reports
#      a clean zero. On 2026-07-31 this silently returned "no inbound
#      references" for seven skills that had more than sixty across sixteen
#      files, and separately reported four passing CI checks as stale.
#
#   2. `rg -r` / `-rn`. That is --replace, not "recursive". ripgrep is recursive
#      by default; `-r` rewrites every match in the output, so the results read
#      like real search hits and are not.
#
#   3. zsh reserved names (`path`, `cdpath`, `fpath`, `manpath`) used as locals.
#      Assigning to `path` masks command lookup for the rest of the shell.
#
# Written for bash 3.2 (macOS /bin/bash): no mapfile, no associative arrays.
# Fails open at every step -- any unexpected condition exits 0 silently, since
# this runs ahead of every Bash call on the machine.

input=$(cat 2>/dev/null) || exit 0
[[ -n "$input" ]] || exit 0

command -v jq >/dev/null 2>&1 || exit 0

tool_name=$(echo "$input" | jq -r '.tool_name // empty' 2>/dev/null) || exit 0
[[ "$tool_name" == "Bash" ]] || exit 0

command=$(echo "$input" | jq -r '.tool_input.command // empty' 2>/dev/null) || exit 0
[[ -n "$command" ]] || exit 0

warnings=""

add_warning() {
  if [[ -n "$warnings" ]]; then
    warnings="$warnings
$1"
  else
    warnings="$1"
  fi
}

# --- 1. unquoted variable as a for-loop word list -----------------------------
# Matches `for x in $LIST` / `for x in ${LIST}` but not `"${arr[@]}"`, not a
# quoted scalar, and not `$(...)` command substitution, which does split.
if [[ "$command" =~ (^|[[:space:]\;])for[[:space:]]+[A-Za-z_][A-Za-z0-9_]*[[:space:]]+in[[:space:]]+\$\{?[A-Za-z_][A-Za-z0-9_]*\}?([[:space:]]|\;|$) ]]; then
  add_warning "zsh does not word-split unquoted variables: 'for x in \$VAR' iterates ONCE over the whole string and reports a clean zero rather than failing. Use an array -- list=(a b c); for x in \"\${list[@]}\" -- or 'while IFS= read -r'."
fi

# --- 2. ripgrep --replace mistaken for recursive -------------------------------
# Matches a short-flag cluster containing r (-r, -rn, -rln) but not --replace
# spelled out, which is presumably deliberate.
if [[ "$command" =~ (^|[[:space:]])rg[[:space:]] ]] && [[ ! "$command" =~ --replace ]]; then
  if [[ "$command" =~ (^|[[:space:]])-[A-Za-qs-z]*r[A-Za-z]*([[:space:]]|$) ]]; then
    add_warning "rg -r is --replace, not recursive. ripgrep is already recursive; -r rewrites every match so the output reads like real hits and is not. The line-number flag is -n alone."
  fi
fi

# --- 3. multi-word literal reaching a command as one unquoted argv element -----
# `for c in "a.py --check"; do python3 $c; done` -- the loop is correct (one
# quoted item, one iteration), but zsh passes $c whole, so this execs a file
# literally named "a.py --check". Deliberately narrow: it fires only when the
# same command both defines a multi-word quoted item and uses that variable
# unquoted, which is the shape that produced four false CI failures on
# 2026-07-31. A general "unquoted variable as argv" rule would be pure noise.
if [[ "$command" =~ for[[:space:]]+([A-Za-z_][A-Za-z0-9_]*)[[:space:]]+in[[:space:]]+\"[^\"]*[[:space:]][^\"]*\" ]]; then
  loop_var="${BASH_REMATCH[1]}"
  if [[ "$command" =~ [[:space:]]\$\{?"$loop_var"\}?([[:space:]]|\;|$) ]]; then
    add_warning "The loop item is a multi-word string, and \$$loop_var is used unquoted. zsh passes it as ONE argument, so a command like 'python3 \$$loop_var' tries to exec a file whose name contains spaces. Pass argv instead: run() { \"\$@\"; }."
  fi
fi

# --- 4. zsh reserved array/scalar names used as locals -------------------------
if [[ "$command" =~ (^|[[:space:]\;])(path|cdpath|fpath|manpath)= ]]; then
  add_warning "In zsh, 'path' (and cdpath/fpath/manpath) is tied to PATH. Assigning it masks command lookup for the rest of the shell. Use a task-specific name."
fi

[[ -n "$warnings" ]] || exit 0

# Warn without blocking. additionalContext reaches the model; exit 0 permits the
# call. If the harness does not understand the JSON it is ignored and the call
# still proceeds, which is the intended failure mode.
jq -n --arg ctx "Shell safety warning (not blocking):
$warnings" '{
  hookSpecificOutput: {
    hookEventName: "PreToolUse",
    additionalContext: $ctx
  }
}' 2>/dev/null || exit 0

exit 0
