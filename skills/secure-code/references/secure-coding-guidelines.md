# Security review lenses

Use the lens that matches the question; this is not a compulsory checklist.

| Boundary | Evidence that often changes the conclusion |
| --- | --- |
| Identity and tenant scope | Scope on every lookup, join, cache key, background job, write, and alternate API; object authorization after identifier resolution |
| Input to interpreter | Where attacker control survives encoding or validation; shell arguments versus shell strings; option injection even without a shell |
| Filesystem and process | Canonical target, symlink/race behavior, effective UID, inherited environment, writable executable/config dependencies, sandbox enforcement |
| Network and callbacks | Redirects, DNS/address resolution, internal destinations, recipient binding, credential forwarding, retries, webhook authenticity |
| State and lifecycle | Replay, concurrency, idempotency, partial failures, checks separated from use, revoke/delete paths, fail-open fallbacks |
| Sensitive output | Logs, exception bodies, exports, telemetry, debug routes, backups; intended reader and retention rather than just variable names |
| Dependencies and artifacts | Affected version actually used, reachable vulnerable feature, runtime versus lockfile, build/install hooks and generated artifacts |

Trace the path across its owners. An input validator in one endpoint does not
protect an equivalent worker entry point; a frontend restriction does not bind a
backend; two modules sharing credentials do not form a permission boundary.

Severity follows concrete impact and reachable preconditions. A potentially
unsafe primitive with trusted, constrained inputs is an observation, not enough
for a vulnerability finding. A credible violation can be established by source
and runtime configuration without performing a harmful exploit.
