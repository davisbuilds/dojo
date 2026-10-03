# Error-Handling Review Lens

Trace what a caller or operator observes when an operation fails. A broad catch,
optional chain, fallback, or absent log is a lead, not a defect by itself.

- Can an exception, error-valued return, timeout, or rejected promise become an
  ordinary empty result or success status? Identify the consumer that then takes
  the wrong action. Check both returned error fields and thrown exceptions.
- Does fallback preserve the promised semantics, including freshness and source
  identity? Expected cache misses and explicitly best-effort work can recover
  silently; failed authoritative reads must not masquerade as verified absence.
- Do retries preserve idempotency, respect cancellation, bound work, and surface
  exhaustion? Follow partial side effects before recommending another attempt.
- Is the failure handled at the right layer? Check propagation and cleanup before
  demanding local logging or rethrowing; double logging and leaking sensitive
  values can be regressions too. Use the project's existing reporting interface.
- Does catching an unexpected error let invalid state escape or skip necessary
  cleanup? Name a reachable error and consequence rather than listing theoretical
  exception classes. Cancellation semantics depend on the runtime and library.

Useful distinctions:

- `except CacheMiss: return None` can be correct when None is the documented
  miss result. `except Exception: return []` after an authoritative fetch can be
  wrong when a caller treats that list as evidence to delete existing records.
- A boundary handler that catches broadly and returns a typed failure is not
  automatically worse than a narrow catch. Look for a lost contract or effect.
- In Python, raising a new exception inside an except block normally retains
  implicit exception context. Do not claim the traceback is lost simply because
  `raise ... from exc` is absent. Inspect what is actually suppressed or rendered.

Use the main skill's finding threshold and priorities. Missing diagnostics is
worth reporting when it causes a concrete operational problem; no log format,
framework helper, or blanket severity is prescribed here.
