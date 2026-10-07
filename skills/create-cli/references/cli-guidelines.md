# Command Line Interface Guidelines (adapted)

Source + contribution:
- Full guide: https://clig.dev/
- Propose changes: https://github.com/cli-guidelines/cli-guidelines

Adapted for Dojo: the upstream human-first emphasis becomes consumer-aware
design below. Agent discovery, bounded evidence, and asynchronous lifecycle
guidance are local additions, not claims about the upstream guide.

Table of contents:
- Foreword
- Introduction
- Philosophy
  - Design for the intended consumers
  - Simple parts that work together
  - Consistency across programs
  - Saying (just) enough
  - Ease of discovery
  - Conversation as the norm
  - Robustness
  - Empathy
  - Chaos
- Guidelines
  - The Basics
  - Help
  - Documentation
  - Output
  - Errors
  - Arguments and flags
  - Interactivity
  - Subcommands
  - Robustness
  - Future-proofing
  - Signals and control characters
  - Configuration
  - Environment variables
  - Naming
  - Distribution
  - Analytics
  - Further reading
- Authors

This is a practical rubric for designing CLI interfaces (args/flags/subcommands/help/output/errors/config). Choose defaults for the intended consumers while preserving human inspectability and composability.

## Foreword

- CLI still uniquely powerful: inspect/control systems; works interactively and in automation.
- A CLI may primarily serve people, scripts, agents, or a mix; make that choice explicit.
- Keep behavior understandable and results inspectable by the person responsible for them.

## Introduction

- This guide mixes philosophy + concrete rules; bias: examples over theorizing.
- Out of scope: full-screen TUIs (vim/emacs-like).
- Language/tooling agnostic: apply principles regardless of implementation stack.

## Philosophy

### Design for the intended consumers

- Choose defaults for the actual consumer; preserve stable machine contracts (`--json`, `--plain`, exit codes) and readable diagnostics where needed.
- Don’t leak developer-only output to normal users; reserve for verbose/debug.

### Simple parts that work together

- Assume your output becomes someone else’s input.
- Respect stdio, exit codes, signals; keep primary output on stdout.
- Prefer line-oriented plain text for piping; add JSON for structured needs.

### Consistency across programs

- Follow common conventions unless they harm usability.
- Reuse standard flag names (`--help`, `--version`, `--json`, `--dry-run`, …).

### Saying (just) enough

- Too little: “hangs” with no feedback. Too much: noisy debug spew.
- Make progress/status visible, but keep success output brief.

### Ease of discovery

- Help text is part of UX. Put examples first; suggest next commands.
- When user errs, help them recover: point to the right syntax/flag.

### Conversation as the norm

- Expect trial-and-error loops. Design for repeated invocations.
- Provide safe “dry run”/preview; show intermediate state; confirm scary actions.

### Robustness

- Be correct *and* feel robust: responsive, clear, no scary traces by default.
- Handle bad input gracefully; validate early; clear errors.

### Empathy

- Be on the user’s side. Make success likely; make failure informative.
- Character is fine; clutter is not.

### Chaos

- Terminal ecosystem inconsistent; follow norms, but break them intentionally when needed.
- If you diverge, do it with clarity and document it.

## Guidelines

### The Basics

- Use a real argument parsing library when possible (built-in or reputable OSS).
- Exit codes: `0` on success, non-zero on failure; map a few important failure modes.
- Stdout for primary output (and machine-readable output). Stderr for messages/logs/errors.

### Help

- Always support `-h`/`--help`. Do not overload `-h`.
- If run with missing required args, show concise help + 1–2 examples + “use --help”.
- Git-like CLIs: support `mycmd help`, `mycmd help subcmd`, `mycmd subcmd --help`.
- Link to a support path (repo/issues/docs). Prefer deep links per subcommand (when you have web docs).
- Lead with examples; show common flags/commands first; keep formatting readable without escape-char soup.
- Help is usually enough for a small command tree. Add runtime schema discovery for large or changing interfaces when it helps consumers construct valid requests; don't require a schema command or per-command skill everywhere.

### Documentation

- Provide web docs (searchable, linkable).
- Provide terminal docs (`mycmd help ...`); consider man pages where sensible.

### Output

- Use TTY detection for presentation and interactivity, not to guess the caller's required data contract; provide an explicit stable output mode where consumers need one.
- If fancy human output breaks parsing, offer `--plain` (stable, line-based) and/or `--json`.
- On success: usually print *something*, but keep it brief; add `-q/--quiet` when useful.
- If you change state, say what changed and what the new state is.
- Suggest “next commands” in workflowy tools.
- Use color sparingly; disable when not a TTY, `NO_COLOR` set, `TERM=dumb`, or `--no-color`.
- No animations/progress bars when stdout isn’t a TTY.
- Use a pager for long output only when interactive; common `less` opts: `-FIRX`.
- For large results, offer filtering, field selection, or limits before emitting data. Streaming NDJSON does not itself bound what enters an agent's context. Make truncation/partial coverage explicit and provide stable IDs or a continuation route.
- Return decision-relevant summaries with retrievable evidence when useful: log/artifact paths, affected resources, and the scope or revision behind a finding. Distinguish no matches from unavailable data or a check not run.

### Errors

- Catch and rewrite expected errors for humans; avoid stack traces by default.
- Keep signal-to-noise high; group repeated errors.
- Put the most important info last; use red intentionally (don’t drown the user).
- For unexpected crashes: provide a path to debug info + bug report instructions; write logs to a file if large.

### Arguments and flags

- Prefer flags over positional args for clarity and future flexibility.
- Provide long versions of all flags; use one-letter flags only for the most common.
- Multiple args ok for repeated simple items (`rm a b c`); avoid “2+ different positional concepts”.
- Standard flag names (common set):
  - `-h, --help` help
  - `--version` version
  - `-q, --quiet` less output
  - `-v, --verbose` more output (avoid `-v` meaning version)
  - `-d, --debug` debug output
  - `-f, --force` skip confirmation / force
  - `-n, --dry-run` preview only
  - `--json` structured output
  - `-o, --output <file>` output path
  - `--no-input` disable prompts
- Default should be right for most users (don’t rely on everyone aliasing a flag).
- Support `-` for stdin/stdout when input/output is a file.
- Avoid secrets in flags; prefer `--password-file` or stdin.
- Prefer order independence for flags/subcommands where the parser allows.

### Interactivity

- Prompt only if stdin is a TTY.
- `--no-input`: never prompt; if required input missing, fail with an actionable message.
- Password prompts: disable echo.
- Make escape hatch obvious (Ctrl-C, or explicit “press q”, etc).

### Subcommands

- Use subcommands for complexity; share global flags/config/help.
- Be consistent across subcommands: naming, flags, output, formatting.
- Consider noun-verb (`docker container create`) or verb-noun; pick one and stick to it.
- Avoid ambiguous pairs (`update` vs `upgrade`) unless sharply differentiated.
- Avoid implicit “catch-all” subcommands; don’t allow arbitrary abbreviations (future-proofing trap).

### Robustness

- Validate early; fail fast with good error messages.
- Be responsive: print something in <100ms (especially before network I/O).
- Show progress for long tasks (interactive only); don’t interleave logs confusingly.
- Use timeouts for network calls; allow configuration.
- Make reruns safe: idempotent where possible; recoverable; “crash-only” where feasible.
- For asynchronous operations, expose the needed start/status/wait behavior with bounded waits and a recoverable operation ID. Distinguish acceptance, readiness, completion, and checked effects. A timeout should identify whether work continues and how to inspect it; cancelling a wait need not cancel the operation. Keep synchronous commands simple.
- State what a dry run checks. Local request validation does not establish remote authorization, eventual success, or rollback support.

### Future-proofing

- Interfaces are contracts: args, flags, subcommands, config, env vars, output modes.
- Keep changes additive; deprecate loudly + early; provide migration paths.
- Allow human output to evolve; keep scripts stable by encouraging `--plain`/`--json`.

### Signals and control characters

- Ctrl-C: exit quickly; say something immediately; bound cleanup.
- Second Ctrl-C: optionally force; tell user what it does.
- Assume cleanup might not run; design for crash-only recovery.

### Configuration

- Pick the right mechanism:
  - Per-invocation: flags (and sometimes env).
  - Per-user/machine: flags + env; possibly config file.
  - Per-project (checked in): config file in repo.
- Follow XDG base directories for user-level config when applicable.
- Precedence (high → low): flags > process env > project config > user config > system config.
- Don’t silently modify other programs’ config; ask consent; prefer new files over editing existing ones.

### Environment variables

- Names: uppercase + digits + underscores; single-line values preferred.
- Respect common vars when relevant: `NO_COLOR`, `DEBUG`, `EDITOR`, `PAGER`, proxy vars, `TERM`, `TMPDIR`, `HOME`, `COLUMNS/LINES`.
- `.env` can be useful for per-project non-secret knobs; don’t use it as a full config system.
- Don’t accept secrets via env vars by default; prefer files/pipes/sockets/secret managers.

### Naming

- Command name: simple, memorable, lowercase; avoid too-generic collisions.
- Keep it short but not cryptic; easy to type matters.

### Distribution

- Prefer single binary when practical; otherwise use native packaging for uninstallability.
- Make uninstall easy; include instructions.

### Analytics

- Never phone home without explicit consent; explain what/why/how/retention.
- Prefer opt-in; if opt-out, make it obvious and easy to disable.
- Consider alternatives: docs instrumentation, download metrics, talking to users.

### Further reading

- POSIX Utility Conventions
- GNU Coding Standards (esp. flags/help conventions)
- 12 Factor CLI Apps
- Heroku CLI Style Guide
- [Justin Poehnelt: CLI design for agents](https://justin.poehnelt.com/posts/rewrite-your-cli-for-ai-agents/) — runtime discovery and bounded output; adopted selectively above, not a requirement for raw JSON inputs or a universal CLI rewrite.
- [Justin Poehnelt: native-app tooling](https://justin.poehnelt.com/posts/ship-mcp-server-native-app/) — an action/wait/inspection example; that lifecycle can inform a CLI without requiring MCP.

## Authors

Original “Command Line Interface Guidelines” authors (and many contributors): Aanand Prasad, Ben Firshman, Carl Tashian, Eva Parish. Design by Mark Hurrell.
