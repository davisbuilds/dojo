# High-Risk Contract Protocol

Load this reference only when the Risk Profile Gate selects `high`. Keep the
contract mechanism-free: specify observable permissions, invariants, failure
outcomes, and proof scenarios, never files or implementation order.

## Contract Content

1. Give every success criterion a unique `SC-NN` ID.
2. In `## Authority And Safety`, state:
   - which actor may observe or mutate which class of state;
   - what must remain forbidden even through indirect paths;
   - identity, authorization, and evidence-freshness rules;
   - safe behavior for unknown or unsupported external policy;
   - invariants that hold across partial failure, retry, and recovery.
3. In `## Evaluation Scenarios`, define fixed observable scenarios:
   - `EV-NEG-NN` — forbidden behavior fails without a side effect;
   - `EV-REC-NN` — interruption or partial failure reaches a safe outcome;
   - `EV-CON-NN` — retry or concurrency preserves the invariant;
   - `EV-LEG-NN` — legacy or version-skewed state is rejected, contained, or
     migrated safely.
4. Mark a class not applicable only with a concrete reason and the observable
   condition that would make it applicable; retain its stable ID for traceability.

The scenarios name outcomes and actors, not test files, shell mechanics, or the
implementation seam. `write-plan` chooses those.

## Readiness Review

Keep `readiness: draft` while running:

1. Deterministic validation.
2. Adversarial critique seeded to attack ambient credentials, indirect escape
   paths, executable hooks, contradictory invariants, crash windows, external
   identity/policy semantics, retry/idempotency, and legacy state.
3. Revision of every blocking finding.
4. Closure critique against the revised artifact and originating goal.

Record the four readiness markers from the addendum. Set `readiness: ready` only
when validation passed, both critiques completed, and blocking findings are
`none`. A validator proves marker structure and ID coverage; the critic judges
whether the authority and recovery model is actually credible.
