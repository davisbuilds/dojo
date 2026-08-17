---
name: error-handling-review
description: Review changed code for silent failures and inadequate error handling — empty or over-broad catch blocks, errors logged-and-swallowed, unjustified fallbacks, null/optional-chaining that hides failures, and retries that exhaust silently. Use when the user asks to review error handling, check catch/try-except blocks, audit fallback behavior, or hunt for swallowed errors. Not general diff review (local-review) or security scanning (secure-code).
skill-type: workflow
version: 1.0.0
---

# error-handling-review

## Overview

A specialist review lens that hunts **silent failures**: errors that occur
without being surfaced, logged with context, or made actionable. A silent
failure turns a five-minute fix into a multi-hour debugging session, because the
first evidence anyone sees is downstream corruption, not the original fault.

This is a deliberately-invoked deep pass, narrower and more opinionated than a
general review. Reach for it when a change adds or touches error handling.

## When To Use

- The diff adds or changes `try/catch`, `try/except`, `Result`/`Either`
  handling, error callbacks, or promise `.catch(...)`.
- A change introduces fallback logic, default-on-failure values, or retries.
- The user asks to "review the error handling", "check the catch blocks",
  "audit fallback behavior", or "find swallowed errors".

## Boundaries

- **Not general code review.** Correctness, performance, and style belong to
  `local-review`. This lens looks only at how failures are handled.
- **Not security scanning.** SAST and the lethal trifecta are `secure-code`.
- **Read-only.** Produce findings; do not edit source.
- **No invented evidence.** Every finding cites a real file and line in the diff.

## Workflow

1. **Scope the change.** Get the diff (`local-review`'s collector, `git diff`, or
   the files named). Review only changed and directly-adjacent code.
2. **Locate every failure-handling site.** `catch`/`except` blocks, error
   callbacks and event handlers, error-state branches, fallback/default values,
   "logged but execution continues" paths, and optional-chaining/null-coalescing
   that can skip a failing operation.
3. **Interrogate each site** against the five questions in
   `references/interrogation-checklist.md`: logging quality, user feedback,
   catch specificity, fallback justification, and propagation. For a catch
   block, **list the specific unexpected error types it could hide.**
4. **Sweep for hidden-failure patterns**: empty catch blocks, catch-and-continue
   with only a log, returning `null`/`undefined`/defaults on error without
   logging, optional chaining used to dodge a failing call, fallback chains with
   no stated reason, and retries that exhaust without informing anyone.
5. **Judge against *this* repository's declared conventions**, not a hardcoded
   stack. Read the repo's `CLAUDE.md`/`AGENTS.md` for its logging and
   error-reporting rules; `references/stack-conventions.md` gives concrete
   shapes for TypeScript (Next.js/Supabase) and Python when the repo is silent.
6. **Report** in the output contract below.

## Output Contract

Findings first, ordered by severity. For each finding:

- `Severity`: `CRITICAL` (silent failure, empty or catch-all block that swallows)
  · `HIGH` (over-broad catch, unjustified fallback, unactionable message) ·
  `MEDIUM` (missing context, could be more specific)
- `Location`: `path:line`
- `Issue`: what is wrong and why it hides a failure
- `Hidden errors`: the specific unexpected error types this site could suppress
- `User/operator impact`: what a person sees instead of the real fault
- `Recommended fix`: the concrete change (surface, log-with-context, narrow the
  catch, or justify the fallback in a comment/spec)
- `Example`: the corrected shape, in the file's language

Close with **Residual risks** — failure paths you could not evaluate (untouched
callers, external services). State explicitly when the error handling is sound;
a clean pass is a real result.

## Verification

- Every finding cites a real `path:line` from the diff.
- Every `CRITICAL`/`HIGH` names the concrete unexpected error(s) that get hidden,
  not just "this is broad".
- Severity matches the stated impact.
- Residual risks section is present even when there are no findings.

## Resources

- `references/interrogation-checklist.md` — the five-question interrogation and
  the hidden-failure pattern catalog, with the reasoning behind each.
- `references/stack-conventions.md` — concrete logging/propagation shapes for
  TypeScript (Next.js/Supabase) and Python, used only when the repo declares no
  convention of its own.

## Sibling skills

- `local-review` — general diff review (correctness, security, performance).
  Run this lens when that pass flags error handling, or invoke it directly.
- `secure-code` — security scanning; orthogonal.
- `verify-before-complete` — completion gate; run after fixes land.
