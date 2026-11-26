# A compact verification map

Use this example when the project lacks an obvious place to connect behavior to
checks. Adapt an existing testing/operations reference; neither this table nor
one file per feature is required. Keep executable details in their scripts or
tests and link them. Exact commands and prerequisites must come from the repo.

For a task service, a small map might describe:

| Behavior | Entry and prerequisites | Check and observable outcome | Boundary |
| --- | --- | --- | --- |
| Submit and process a task | Public submit command; isolated initialized store, test identity, worker ready | Submit via the command, observe the task through its public status interface, and inspect the resulting artifact | A local fake delivery service does not establish real provider delivery |
| Recover a failed task | Same isolated instance; documented controllable worker failure | Observe the failure, retry through the supported interface, and verify exactly one intended result | Do not inject failure into a shared worker |
| Reject an invalid task | Same entry point and identity as the valid case | A valid submission establishes reachability; invalid input is rejected without creating work | A refusal caused by missing auth would not exercise input validation |

The nearby setup reference would own the actual build/install, seed/reset,
readiness, interaction, evidence, and teardown commands. Record any credential or
platform prerequisites without embedding secrets. Identify which resources a
run owns and keep its evidence outside the directory teardown removes.

A later executor should be able to select a behavior, establish its prerequisites,
run its check, and distinguish success from failure or unavailable evidence.
Keep run-specific revisions, outputs, and coverage in run evidence; update the
maintained map when a behavior or verification path changes.
