# Uncertainty Triage

Use this reference before writing a contract when the request has material
unknowns. The aim is not to produce a complete list of unknown unknowns; it is
to turn preventable uncertainty into decisions and make the remaining uncertainty
safe, visible, and bounded.

## Triage The Unknown

| Kind | Action before handoff | Where it belongs |
| --- | --- | --- |
| Answerable now | Inspect the project, docs, or evidence and record the resolved constraint. | Contract / assumptions |
| Contract-blocking decision | Ask the user or use the appropriate decision skill; do not plan yet. | Resolved contract decision |
| Irreducible future uncertainty | State the signal that reveals it and the containment expectation. It must not change the current contract. | Assumptions And Constraints |
| Future choice | Exclude it from this delivery and say when to revisit it. | Out of Scope |

An `Open Questions` entry is not a parking lot. A ready contract says `None`, or
explains why the retained question is non-blocking and cannot change scope,
success criteria, or verification.

## Work With The User

Ask focused questions only after resolving what the repository can answer. Good
questions change the contract, for example:

- What observable behavior must never change?
- Which user, consumer, or permission boundary matters most?
- What outcome distinguishes a useful result from a merely plausible one?
- Which trade-off does the user want if the two desired outcomes conflict?

Ask one decision at a time when it needs discussion. Do not turn ordinary
implementation reconnaissance into a user interview.

## Unknown-Unknown Lenses

Use only the lenses that fit the work. For a small mechanical change, a quick
boundary check is enough. For a high-impact change, consider:

- **Consumers and compatibility** — scripts, integrations, or users that observe
  current behavior.
- **Inputs and boundaries** — blank, malformed, old, cross-tenant, or untrusted
  inputs; data that must not be exposed or changed.
- **Dependencies and failure** — unavailable, slow, partial, retried, or
  version-skewed collaborators.
- **Operations and containment** — the signal that reveals a bad outcome and the
  expected safe behavior while it is investigated.

These lenses discover candidates for investigation; they do not justify adding
speculative scope. If a finding changes the contract, resolve it before planning.
If it does not, make it an explicit bounded assumption or future follow-up.

## Escalation

- Use `brainstorming` when the desired outcome or chosen direction is unclear.
- Use `first-principles` when an architectural trade-off dominates the decision.
- Use `deep-research` when the contract depends on facts not available locally.

The resulting spec remains mechanism-free: record the decision and the
observable end state, not the code or task sequence that will realize it.
