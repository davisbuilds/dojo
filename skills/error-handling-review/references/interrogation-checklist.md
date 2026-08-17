# Interrogation Checklist

The five questions to ask at **every** failure-handling site, and the
hidden-failure patterns to sweep for. The point is not to flag every `catch` —
it is to find the ones that make a real fault invisible.

## The Five Questions

### 1. Logging quality
- Is the error logged at all, at an appropriate severity?
- Does the log carry enough context to debug it cold — the operation that
  failed, the relevant IDs, the input or state that triggered it?
- Would this log let someone diagnose the issue six months from now, or is it a
  bare `log(err)` with no story?

### 2. User / operator feedback
- Does the person affected get clear, actionable feedback about what failed?
- Does the message say what they can do about it, or is it a generic
  "something went wrong"?
- Are technical details exposed or hidden appropriately for the audience
  (end user vs. developer vs. operator)?

### 3. Catch specificity
- Does the block catch only the error types it actually expects?
- **List every unexpected error type this block could also catch and hide** — a
  `TypeError` from a typo, a `KeyError` from a renamed field, a cancellation, an
  out-of-memory. This list is the finding.
- Should it be several narrow handlers instead of one broad one?

### 4. Fallback justification
- Is there fallback / default-on-failure behavior?
- Is the fallback **explicitly requested** by the user or documented in the
  spec, or invented here to make an error disappear?
- Would a person be confused about why they are seeing fallback output instead
  of an error — silently stale data, an empty list that reads as "no results"?
- Is it a fallback to a mock/stub/fake outside test code? That signals an
  architectural gap, not a recovery.

### 5. Propagation
- Should this error bubble to a higher-level handler instead of dying here?
- Is it being swallowed where the caller needed to know?
- Does catching here skip cleanup or resource release the `finally`/`with`
  should own?

## Hidden-Failure Patterns (sweep)

- **Empty catch block** — nothing logged, nothing rethrown. Effectively always a
  `CRITICAL`.
- **Catch-and-continue** — logs, then proceeds as if nothing failed, so the next
  line runs on bad state.
- **Return-default-on-error** — `return null` / `return []` / `return {}` in a
  catch with no log; the caller cannot distinguish "no data" from "it broke".
- **Optional chaining as an error dodge** — `a?.b?.c` used so a missing/failed
  step silently yields `undefined` instead of surfacing why.
- **Unexplained fallback chains** — try A, then B, then C, with no comment on why
  or which one served the result.
- **Silent retry exhaustion** — retries loop to a cap and then return a default
  without recording that every attempt failed.
- **Swallowed cancellation/timeout** — a broad catch treats an abort or timeout
  as an ordinary failure and hides that the operation never completed.

## Severity Mapping

- `CRITICAL` — a fault produces no log and no signal: empty catch, catch-all that
  swallows, default-on-error with no logging. The failure is invisible.
- `HIGH` — the failure is visible but mishandled: over-broad catch that could
  hide unrelated errors, an unjustified fallback that masks the cause, or a
  message too generic to act on.
- `MEDIUM` — handled, but weaker than it should be: missing context in the log,
  a catch that could be narrower, a message that could be more specific.
