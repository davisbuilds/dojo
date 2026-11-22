#!/bin/bash

# WHY: warns and never blocks. Each construct is legitimate in some form, and a
# false positive that stops work costs more than the trap it prevents. It fails
# open at every step because it runs ahead of every Bash call on the machine.
# Written for bash 3.2 (macOS /bin/bash): no mapfile, no associative arrays.

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

if [[ "$command" =~ (^|[[:space:]\;])for[[:space:]]+[A-Za-z_][A-Za-z0-9_]*[[:space:]]+in[[:space:]]+\$\{?[A-Za-z_][A-Za-z0-9_]*\}?([[:space:]]|\;|$) ]]; then
  add_warning "zsh does not word-split unquoted variables: 'for x in \$VAR' iterates ONCE over the whole string and reports a clean zero rather than failing. Use an array -- list=(a b c); for x in \"\${list[@]}\" -- or 'while IFS= read -r'."
fi

# WHY: a spelled-out --replace is presumably deliberate. The search stops at the
# next | ; & or newline so `rg x | sort -rn` stays quiet; missing a pattern that
# contains one of those before the flag is the cheaper error for a warning.
rg_replace_re='(^|[[:space:]|;&(])rg[[:space:]]([^|;&'$'\n'']*[[:space:]])?-[A-Za-qs-z]*r[A-Za-z]*([[:space:]|;&)]|$)'
if [[ ! "$command" =~ --replace ]]; then
  if [[ "$command" =~ $rg_replace_re ]]; then
    add_warning "rg -r is --replace, not recursive. ripgrep is already recursive; -r rewrites every match so the output reads like real hits and is not. The line-number flag is -n alone."
  fi
fi

# WHY: deliberately narrow. It fires only when one command both defines a
# multi-word quoted loop item and uses that variable unquoted, the shape that
# produced four false CI failures on 2026-07-31; a general "unquoted variable as
# argv" rule would be pure noise.
if [[ "$command" =~ for[[:space:]]+([A-Za-z_][A-Za-z0-9_]*)[[:space:]]+in[[:space:]]+\"[^\"]*[[:space:]][^\"]*\" ]]; then
  loop_var="${BASH_REMATCH[1]}"
  if [[ "$command" =~ [[:space:]]\$\{?"$loop_var"\}?([[:space:]]|\;|$) ]]; then
    add_warning "The loop item is a multi-word string, and \$$loop_var is used unquoted. zsh passes it as ONE argument, so a command like 'python3 \$$loop_var' tries to exec a file whose name contains spaces. Pass argv instead: run() { \"\$@\"; }."
  fi
fi

if [[ "$command" =~ (^|[[:space:]\;])(path|cdpath|fpath|manpath)= ]]; then
  add_warning "In zsh, 'path' (and cdpath/fpath/manpath) is tied to PATH. Assigning it masks command lookup for the rest of the shell. Use a task-specific name."
fi

[[ -n "$warnings" ]] || exit 0

jq -n --arg ctx "Shell safety warning (not blocking):
$warnings" '{
  hookSpecificOutput: {
    hookEventName: "PreToolUse",
    additionalContext: $ctx
  }
}' 2>/dev/null || exit 0

exit 0
