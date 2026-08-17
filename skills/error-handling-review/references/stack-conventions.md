# Stack Conventions

Concrete shapes for surfacing, logging, and propagating failures. Use these
**only when the repository declares no convention of its own** — always prefer
the logging helpers, error-reporting sink, and error-boundary patterns named in
the repo's `CLAUDE.md`/`AGENTS.md` or already used in neighboring code. Do not
invent a project's helper names; cite the ones actually present.

## TypeScript (Next.js / Supabase)

- **Narrow the catch.** `catch (e)` types `e` as `unknown`; narrow before use
  (`if (e instanceof SomeError)`), and rethrow what you did not expect rather
  than letting one block absorb every throw.
- **Surface, don't swallow.** In a Server Action or route handler, return a typed
  error result or throw to the nearest error boundary / `error.tsx`; don't
  `return null` into UI that will render as empty.
- **Supabase calls return `{ data, error }`, they don't throw.** The silent
  failure here is ignoring `error` and proceeding with `data` that is `null`.
  Check `error` on every call and propagate it; a missing `error` check is a
  finding even though there is no `catch` block.
- **Logging.** Use the repo's structured logger and error-reporting sink if one
  exists; include the operation and relevant IDs. A bare `console.error(e)` in a
  server path is `MEDIUM` at best (no context, no sink).
- **Promises.** An unhandled rejection or a `.catch(() => {})` that discards is a
  silent failure; `.catch` must log-with-context and rethrow or convert to a
  handled result.

## Python

- **Catch specific exceptions.** `except Exception:` (or bare `except:`) is a
  code smell; name the expected exceptions and let the rest propagate.
- **Preserve the chain.** Re-raise with `raise NewError(...) from exc` so the
  original traceback survives; `raise NewError(...)` alone erases the cause.
- **Log with context, then decide.** Use the `logging` module (`logger.exception`
  inside an `except` captures the traceback); do not `logging.error(str(e))`,
  which drops the stack.
- **No default-on-error without a log.** `except X: return None`/`return []` that
  hides the failure from the caller is `CRITICAL`/`HIGH` depending on whether
  anything is logged.
- **Cleanup belongs in `finally`/`with`,** not inside a broad `except` that also
  swallows the error.

## General

- Every language has a "success-shaped default returned on failure" trap — the
  empty list, the zero, the `None`/`null`, the cached-stale value. The tell is a
  caller that cannot distinguish a legitimate empty result from a suppressed
  fault. That distinction is the finding.
