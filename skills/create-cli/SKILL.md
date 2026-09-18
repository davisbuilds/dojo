---
name: create-cli
description: >
  Design command-line interface parameters and UX: arguments, flags, subcommands,
  help text, output formats, error messages, exit codes, prompts, config/env
  precedence, and safe/dry-run behavior. Use when you’re designing a CLI spec
  (before implementation) or refactoring an existing CLI’s surface area for
  consistency, composability, and discoverability.
skill-type: workflow
version: 2.0.0
---

# Create CLI

Design command-line syntax and behavior for its human and script consumers.
Use the relevant conventions during authorized implementation as well as when
producing a CLI design.

## When To Use

- Designing a CLI's commands, arguments, output, errors, or configuration.
- Refactoring a CLI interface for consistency or composability.
- Resolving a specific CLI UX decision during implementation.

## Boundaries

Follow the requested scope. A design-only request produces a design, not code;
an implementation request does not need a new CLI spec when decisions are
already settled. Reuse the project's established conventions and accepted
contract. Consulting this skill does not activate a separate design workflow.

Do not prescribe a language or parsing library unless that choice is in scope.
Consult sibling guidance only for a material unresolved concern; do not inherit
its full workflow, artifacts, or handoffs.

## Workflow

Identify the decisions still open: primary consumers, input sources, output
contract, interactivity, configuration precedence, and platform constraints.
Resolve facts from the repository; ask only questions that materially change
the interface. Use established defaults for routine choices.

Consult the relevant sections of `references/cli-guidelines.md` as needed.
Apply conventions to the affected surface; adding one flag does not call for
redesigning the command tree or generating examples for unrelated commands.

## Default Conventions

Use these unless the project's existing contract or the user says otherwise:

- Primary data goes to stdout; diagnostics and errors go to stderr.
- Define stable output and exit codes for script consumers. Add `--json` or
  `--plain` when there is a consumer, not as speculative surface area.
- Help and version are discoverable without performing the command's effects.
- Prompt only in an interactive session. `--no-input` must fail clearly when
  required input is absent rather than wait indefinitely.
- Destructive commands need an explicit, reviewable target and deliberate
  authorization through an appropriate preview/confirmation/noninteractive
  mechanism. Reuse existing authorization; do not invent an extra agent approval
  step from the CLI's own confirmation rules.
- Do not expose secrets through flags, logs, or diagnostics.
- Make config precedence predictable; prefer the existing project convention
  over introducing another configuration layer.
- Respect `NO_COLOR`, `TERM=dumb`, and non-TTY output. Keep machine output parseable.
- Handle interruption with bounded cleanup and honest partial-effect reporting.

## Output

For a requested full design, cover the command tree, relevant args/flags,
semantics, output/errors, configuration, safety, and representative invocations.
Use a compact table or examples where helpful; omit irrelevant sections.

For a narrow consultation or implementation task, report only the decisions
and evidence needed for that task. No separate spec, fixed example count, or
handoff menu is required.

## Verification

- The affected interface fits existing human and script consumers.
- Output and errors preserve their promised streams, shapes, and exit behavior.
- Relevant destructive, noninteractive, and interruption paths have explicit
  behavior and evidence appropriate to the task.
- Design examples agree with the contract. Implementation claims are supported
  by relevant CLI checks, including failure paths where affected.

## Resources

- `references/cli-guidelines.md` — consult by concern: help, arguments, output,
  configuration, errors, interaction, or distribution.
- Upstream guidelines: https://clig.dev/.
