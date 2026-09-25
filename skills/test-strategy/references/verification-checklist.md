# Reviewing Test Evidence

Use these questions when coverage is uncertain or a test review is requested.
Select the relevant ones; this is not a required completion checklist or report.

- Could a plausible regression pass these assertions? Did the failing baseline
  exercise the intended behavior rather than a missing symbol or earlier guard?
- Is the oracle independent of the code under test? Are assertions about the
  contract, including order or interactions only where those matter?
- Does a negative result have a known positive control? Is an existing control
  sufficient, or would a targeted mutation expose a meaningful coverage gap?
- Does the dependency substitute preserve the semantics this claim needs? What
  wiring, platform, or real-service behavior remains untested?
- Could shared state, leaked resources, or unbounded waits make the result
  misleading? Are external effects authorized and isolated?
- Do results apply to the current change and relevant runtime inputs? Are
  project-required checks satisfied? Which remaining limit affects the claim?

For authority boundaries, use `authority-boundary-testing.md`: both permitted
and forbidden operations, observation outside the subject, and proof from the
effective runtime. Do not infer enforcement from generated policy alone.
