---
date: 2026-07-27
author: gpt-5.6-sol
topic: distribution-profiles
stage: spec
status: draft
source: conversation
risk_profile: high
readiness: ready
---

# Distribution Profiles Spec

## Problem

Dojo currently treats its 57-skill canonical catalog as though every skill
should be visible in every harness and project. Adapters expose the whole
catalog, even though the deliberately curated global installation contains only
31 canonical skills.

Measured against the one harness for which an authoritative listing limit can
be established, whole-catalog distribution is not merely wasteful — it does not
fit. Codex derives its skills budget as 2% of the model context window in
tokens, falling back to 8,000 characters only when the window is unknown
(`codex-rs/core-skills/src/render.rs`, `default_skill_metadata_budget`, at
pinned revision `f57467275c`). At the observed window of 258,400 that budget is
**5,168 tokens**. The curated 31-skill installation costs ~3,315 estimated
tokens (**64%** of budget); the full 57-skill canonical catalog would cost
~5,718 (**111%**). Exceeding the budget is not a soft condition: Codex shortens
descriptions first and emits a truncation warning, then removes descriptions
entirely — degrading exactly the routing signal a skill catalog exists to
provide, and doing so silently from the maintainer's point of view.

The 31-skill subset that currently fits is undocumented curation. It exists as
installed state rather than as a reviewable declaration, so it cannot be
reproduced on a second machine, reviewed as a unit, or distinguished from drift.
Maintainers therefore cannot express which skills should be distributed
together, prove that an effective catalog fits a harness, or tell intentional
exclusion apart from missing or stale state.

Claude Code is deliberately **not** a motivating case here. No authoritative
listing limit for it can be established from vendor documentation or a
reproducible local probe, so under SC-04 it is audit-only until such a policy
exists. Earlier framings of this problem rested on an unverified Claude listing
budget and on an assumption that project-scope skills are inherited by
subdirectory sessions; neither survived verification, and the contract no longer
depends on either.

## Contract

When this ships, every Dojo-managed global or project-scope skill realization
can be traced to an explicit, versioned distribution profile rather than an
implicit whole-catalog mirror. Profiles resolve deterministically from a small
baseline plus composable capability overlays, and the effective harness catalog
is evaluated after scope precedence, shadowing, foreign skills, commands, and
harness-specific presentation are accounted for. Every Dojo-owned workflow
that can create or refresh adapter state honors the selected profile; no legacy
whole-catalog generator remains an indirect path that can silently re-widen a
profile-scoped target.

`dojo profiles verify --all` is a read-only, deterministic contract check. It
succeeds only when every profile definition is valid and every currently
observed deployable realization matches its selected profile and canonical
source revision while remaining at or below 90% of an authoritative,
harness-version-scoped listing limit. A limit is authoritative when it is
vendor-published for the observed harness/model, derived from vendor
implementation source at a pinned revision, or established by a reproducible
versioned measurement with a conservative observed bound. A harness with none of
these sources remains audit-only. The report identifies the profile and source
revision, resolved membership, observed drift, scope collisions, foreign and
plugin entries, routing coverage, harness and policy versions, estimated listing
cost, limit, and remaining headroom. The same inputs produce byte-identical
machine-readable output. The command returns 0 only for a complete conformant
evaluation, 2 for evaluated drift, unsupported policy, or nonconformance, and 1
when evaluation itself cannot finish; a partial report is marked incomplete and
can never accompany exit 0.

The command name is an observable user-interface contract, not a decision about
internal dispatch: the implementation may provide it through an executable,
wrapper, or equivalent entrypoint, but the exact invocation must work.

Profile application is an explicit maintainer action against named targets.
Unknown, malformed, empty, stale, over-budget, unsupported, or ambiguous input
fails without changing active harness state. A successful application either
activates the complete selected realization for a target or leaves its prior
active realization recoverable; it never reports a mixed or partially widened
catalog as conformant.

## Success Criteria

- **SC-01 — Explicit selection:** Canonical inventory and distributed inventory
  are separate concepts. Every managed realization names one profile
  composition and one canonical source revision; absence from a profile is
  intentional exclusion, not an implicit installation request.
- **SC-02 — Composable profiles:** The public profile vocabulary consists of a
  `core` baseline, the capability overlays `engineering`, `research`, `design`,
  `knowledge`, `shipping`, and `skill-authoring`, plus a `full` inspection
  profile. Overlay order cannot change resolved membership, member overlap
  across overlays collapses deterministically, and every resolved member must
  exist in the canonical catalog. Each capability overlay adds at least two
  non-`core` members and includes these required anchors: `engineering`
  includes `api-design` and `create-cli`; `research` includes `deep-research`
  and `research-architect`; `design` includes `frontend-design` and
  `design-critique`; `knowledge` includes `obsidian-markdown` and
  `compound-docs`; `shipping` includes `gh-commit-push-pr` and `gh-review-pr`;
  and `skill-authoring` includes `skill-creator` and `skill-standardizer`.
  `full` resolves to every canonical skill at the selected revision. Complete
  overlay membership is explicit profile evidence, not inferred from category
  names or installed state.
- **SC-03 — Usable baseline:** `core` contains the general delivery loop:
  `brainstorming`, `write-spec`, `write-plan`, `diagnose`, `local-review`,
  `test-strategy`, `verify-before-complete`, and `handoff`. Acceptance proves at
  least one concrete supported harness/model realization where `core` plus one
  non-empty capability overlay and a three-entry foreign baseline remains
  within the effective-catalog budget. A harness where the pinned baseline does
  not fit is audit-only rather than repaired by weakening the budget or
  rewriting skills.
- **SC-04 — Budgeted effective catalog:** A realization is deployable only when
  the complete catalog visible to the harness—including user and project scope,
  shadowed names counted according to actual harness behavior, foreign skills,
  plugin-provided entries observed read-only, and selected command metadata—uses
  no more than 90% of that harness's authoritative listing limit. A measured
  policy records the exact harness and model versions, context window, listing
  representation, tokenizer or conservative estimator, measurement date, and
  repeatable probe; two unchanged runs must agree within 2%, and the lower
  observed limit governs. Where the harness's own estimator is knowable from
  vendor source, the policy must use that same estimator rather than an
  independent one, so budget arithmetic matches the harness's own rather than
  merely approximating it. Codex computes both its budget and its per-entry cost
  with a 4-bytes-per-token approximation, so a Codex policy uses characters
  divided by four and the 5% undercount bound is satisfied by construction. An unknown or stale limit, uninspectable scope, or
  unknown precedence rule is reported as unsupported rather than assumed safe.
  The `full` profile receives no budget exemption and is never the default.
- **SC-05 — Exact managed realization:** A conformant target exposes every
  selected Dojo skill and selected command surface at the canonical version and
  content identity, exposes no unselected Dojo-managed skill at that target
  scope, and observes and reports foreign and plugin-provided entries without
  modifying them.
- **SC-06 — Deterministic conformance evidence:** A verification report is
  stably ordered and records the selected profile composition and identity,
  canonical revision, resolved names and versions, missing and unexpected
  managed entries, content and topology drift, foreign entries, shadowed names,
  plugin-provided entries, target scopes, harness and budget-policy versions,
  budget utilization, included-skill count, skills with routing fixtures,
  assertions executed, assertion outcomes, and observed collision candidates.
  Repeating the check against unchanged inputs yields byte-identical
  machine-readable output.
- **SC-07 — Safe mutation boundary:** Applying a profile requires an explicit
  profile composition and explicit target. It may change only Dojo-managed
  realization state within those targets, preserves recoverable copies before
  replacing or deactivating active managed state, and never changes canonical
  skill content, plugin caches, foreign skills, or unrelated files.
- **SC-08 — Failure containment:** Invalid profiles, missing canonical members,
  dirty or unidentifiable selected source state, unsupported harness policy,
  over-budget effective catalogs, interrupted activation, and conflicting
  concurrent requests cannot silently widen the catalog or produce a conformant
  result. The prior target remains usable or is explicitly reported as
  nonconformant with a recovery path.
- **SC-09 — Legacy migration:** Existing whole-catalog directory links,
  intersection-only global installations, concrete secondary copies, and
  version-skewed managed content are detected without mutation. Migration
  requires explicit application, preserves the previous managed state, and
  yields either the exact selected profile or a reported nonconformant target.
- **SC-10 — Routing confidence follows distribution:** Routing evaluation runs
  over each resolved deployable profile and the complete effective catalog
  observed at its target rather than the full canonical catalog in isolation.
  All declared positive, negative, and sibling-collision assertions relevant to
  included Dojo skills pass against selected and foreign competitors. Every
  capability overlay contributes at least one positive and one negative or
  sibling-collision assertion for its required anchors. Coverage is reported
  separately and cannot be inflated by installing skills solely to create
  runtime data.
- **SC-11 — Cross-machine comparability:** Two machines selecting the same
  profile identity and canonical revision receive the same expected Dojo skill
  names, versions, and content identities. Harness-specific foreign entries,
  versions, and budget outcomes remain explicit differences rather than hidden
  profile drift.
- **SC-12 — Audit-only automation:** Session hooks, scheduled health checks, and
  checkout refreshes may detect and report profile drift, but they cannot apply,
  remove, relink, or widen installed skill state without a separately authorized
  maintainer action.
- **SC-13 — No indirect re-widening:** Existing adapter-generation and
  maintenance entrypoints are profile-aware. Against a profile-managed target,
  they preserve the selected realization; without an explicit profile for an
  unprofiled target, they refuse to create a whole-catalog skill link. Running a
  documented adapter refresh cannot convert a scoped target back to all 57
  canonical skills.

## Evaluation

Acceptance is mechanical, not an experiment. The contract is accepted when the
profile verifier and its behavior fixtures prove all success criteria across
the nominal, boundary, and failure scenarios below. The fixed catalog fixture
contains all 57 canonical skills, the current 31-skill curated global subset,
all 26 currently absent canonical skills, at least three foreign entries, and
both user- and project-scope observations. Budget fixtures straddle the boundary
at exactly 8,900, 9,000, and 9,100 basis points of an authoritative harness
limit. Comparison uses exact integer token counts (`cost * 10_000 <= limit *
9_000`) before presentation rounding, so a trivial or empty catalog cannot
satisfy the check. Estimator calibration uses at least three non-degenerate
catalog shapes spanning below, at, and above the boundary; an estimator that
undercounts observed cost by more than 5% is not authoritative.

The reference behavior is explicit:

- Profile composition is set union over `core` and named overlays; names and
  report rows are ordered lexically, duplicate inclusions collapse to one member,
  and composition order has no semantic effect.
- An empty or core-only capability overlay is invalid. Every deployable
  composition includes `core`; `full` is a fixed inspection profile containing
  the complete canonical catalog and is not implicitly combined with other
  overlays.
- Overlay definitions are flat in the initial contract and cannot reference
  other overlays, so dependency cycles are not applicable. If nested overlays
  are introduced later, cycle handling requires a contract revision before they
  are accepted.
- Unknown profile names, naming the same overlay token more than once in one
  selection request, duplicate profile definitions, unknown skill names, and
  mutually exclusive selections such as `full` plus a capability overlay are
  invalid. Repeating the same skill across different valid overlays is ordinary
  member overlap and collapses through set union.
- A Dojo skill visible at both user and project scope is one effective routing
  entry with the project copy authoritative where the harness documents that
  precedence, while both physical observations and the shadowing relationship
  remain visible in conformance evidence.
- Foreign entries are never profile members. They are preserved and counted in
  the effective listing budget, including entries discovered read-only from
  plugin caches.
- Profile identity is derived deterministically from normalized composition
  names, the reviewed profile definitions, and resolved membership. A
  realization identity additionally binds that profile identity to the
  canonical revision, target identity, harness/model version, and budget-policy
  identity. A canonical revision change is a new realization request, never an
  idempotent replay.
- Vendor documentation or a repeatable, version-scoped probe can establish
  precedence. A probe must reproduce the same winner and visible-set behavior
  twice against controlled duplicate names. A harness/model version change or a
  conflicting observation invalidates the policy and makes the target
  audit-only.
- `verify --all` validates every profile definition but evaluates deployability
  only for currently observed or explicitly requested target realizations. An
  unapplied `full` definition does not make unrelated conformant targets fail.

## Scope

### In Scope

- Named, versioned selection of subsets from the canonical Dojo catalog.
- A mandatory `core`, composable capability overlays, and an explicit `full`
  inspection profile.
- Global and project-scope realizations for supported skill-native harnesses,
  including their selected skill and command surfaces.
- Effective-catalog budget evaluation using observed scope precedence,
  shadowing, foreign entries, and harness presentation.
- Read-only conformance and drift evidence across canonical, global, project,
  and cross-machine state.
- Explicit, recoverable activation and migration of Dojo-managed realization
  state.
- Profile-aware behavior for every Dojo-owned adapter generator or maintenance
  workflow capable of touching managed target state.
- Routing evaluation scoped to the profiles users can actually receive.

### Out of Scope

- Installing the entire canonical catalog merely to generate health data.
- Automatically choosing a profile from observed user behavior.
- Removing, rewriting, or synchronizing plugin caches or foreign skills.
- Defining one universal profile that bypasses harness-specific budgets.
- Retiring, merging, or rewriting individual skills to make a profile fit.
- Remote orchestration that mutates another machine; cross-machine comparison
  consumes independently produced conformance evidence.
- Treating runtime invocation volume as proof that a profile is correctly
  selected.

## Assumptions And Constraints

- The canonical catalog remains the complete authoring inventory and may be
  larger than any deployable profile.
- `core` is mandatory for a deployable composition. Capability overlays are
  additive; subtraction and per-project forks are excluded from the initial
  contract because they make profile identity and support ambiguous.
- The exact membership of every overlay other than `core` is explicit,
  reviewable profile data, contains its required anchors, and contributes at
  least two non-`core` members. Changing membership changes profile identity and
  conformance expectations.
- Skill versions and content identities come from the selected canonical source
  revision rather than independently maintained version pins. Evidence is stale
  whenever the profile definition, selected canonical skill content, target
  realization, harness version, or listing-limit declaration changes.
- Harness listing limits and scope precedence are external policy. Vendor
  documentation, vendor implementation source at a pinned revision, and
  reproducible versioned probes are the only authoritative sources. A missing,
  stale, or contradictory policy makes the target audit-only until policy is
  re-established; it never silently falls back to the `full` profile or an
  assumed limit. On the evidence available at authoring time this means Codex is
  the initial deployable harness and Claude Code is audit-only — so acceptance
  must not assume more than one deployable harness exists, and the `core`-fits
  proof in SC-03 is discharged against Codex.
- The 90% deployability ceiling is an initial conservative guardrail that
  reserves 10% for estimator variance and harness-added metadata. Calibration
  still must satisfy the 5% maximum undercount bound. A future threshold change
  is a profile-contract revision, not a local override.
- Dirty state is classified narrowly. Uncommitted changes to selected profile
  definitions or selected canonical skills are readable for audit but never
  deployable. Unrelated working-tree changes do not block application. A source
  with no verifiable canonical revision is audit-only even if its content can be
  hashed.
- The 31-skill global installation is evidence of intentional curation, not the
  default profile definition. Existing selection is preserved until a maintainer
  explicitly applies a profile. Its measured cost (~3,315 estimated tokens, 64%
  of the Codex budget) shows headroom exists today; the contract's job is to make
  that headroom provable and durable, not to reduce it further.
- Whether an individual skill earns its slot is outside this contract. Profiles
  make membership explicit, reviewable, and enforceable; they do not establish
  that any member improves outcomes. Membership remains a maintainer judgment
  informed by evidence gathered elsewhere, which is why overlay composition is
  reviewable data rather than a contract term.
- Routing coverage is currently sparse: 57 skills pass the structural contract,
  but only two declare trigger fixtures. Profile work reports that limitation
  honestly and adds collision evidence where adjacent included skills need it;
  it does not manufacture low-quality trigger phrases for every skill.
- `dojo profiles verify --all` is the required observable invocation. Whether
  that interface is delivered by a unified executable, wrapper, or another
  internal dispatch seam remains a planning decision.

## Authority And Safety

- **Canonical maintainer:** May define profile membership and authorize
  realization changes. Profile identity must bind the reviewed selection to a
  canonical source revision; ambient working-tree content cannot impersonate
  that revision.
- **Verifier:** May read canonical profile and catalog metadata, configured
  target roots, effective harness listings, harness versions, and listing-limit
  policy, including foreign and plugin-cache metadata needed for the budget. It
  has no mutation authority, including during scheduled or session-start
  execution.
- **Profile applicator:** May mutate only explicitly named Dojo-managed target
  state after showing the resolved profile, exact targets, budget result, and
  planned additions, replacements, deactivations, and link changes. It may not
  infer authority over plugin caches, foreign entries, canonical source, an
  entire home directory, or targets omitted by the maintainer.
- **Harness consumer:** May discover only the effective skill and command
  surfaces produced for its selected scope. Unsupported scope semantics fail
  closed instead of exposing the canonical catalog as a fallback.
- **Adapter maintenance:** Every Dojo-owned adapter writer shares the
  applicator's profile and target boundary. It cannot replace a managed
  realization with a whole-catalog link, and it cannot create an unprofiled
  realization by treating `full` as an implicit default.
- **Identity and freshness:** Conformance evidence identifies the profile
  composition and identity, canonical revision, harness/version policy, and
  observed targets. A clean selected source must match the named revision.
  Dirty selected profile or skill content and unidentifiable source state are
  audit-only. Any change to those inputs invalidates prior evidence.
- **Partial failure and recovery:** Activation cannot expose a mixed old/new
  managed set as conformant. A target retains its prior usable realization until
  the new one is fully valid, or is marked nonconformant with an exact
  recoverable predecessor. Recovery cannot widen authority or touch foreign
  state.
- **Retry and concurrency:** Reapplying the same profile identity to the same
  canonical revision, policy identity, and unchanged target is idempotent. A
  canonical revision change, profile-definition change, different composition,
  different policy identity, or stale observed state is a distinct request and
  must pass a fresh conflict check before activation; last-writer wins is
  forbidden.
- **External policy:** Unknown harness versions, listing limits, or precedence
  rules permit audit evidence only. They cannot authorize a mutation or a
  deployable verdict.

## Evaluation Scenarios

- **EV-NEG-01 (SC-01, SC-02, SC-07):** An application naming an unknown profile,
  an empty or core-only capability overlay, a repeated selection token,
  `full` plus another overlay, a duplicate profile definition, or a missing
  canonical skill is rejected; active project and global target state remains
  byte-identical. Member overlap across two valid overlays remains accepted.
- **EV-NEG-02 (SC-03, SC-04, SC-08):** Effective catalogs measured at 89% and
  90% of the authoritative limit are accepted, while 91%, an unknown or stale
  limit, an estimator that exceeds the undercount bound, and an uninspectable
  scope are non-deployable without changing active state. At least one concrete
  harness/model probe accepts `core`, one non-empty overlay, and three foreign
  entries.
- **EV-NEG-03 (SC-05, SC-07, SC-12):** A target containing foreign skills,
  plugin-cache entries, and unrelated files observes and budgets every visible
  entry, but an authorized application changes none of them. The same request
  from a scheduled audit has no mutation authority.
- **EV-NEG-04 (SC-04, SC-08):** A dirty checkout with changes to one selected
  skill is audit-only, while an unrelated documentation change does not block an
  otherwise valid application. A source without a verifiable canonical revision
  is audit-only.
- **EV-NEG-05 (SC-07, SC-13):** The documented adapter-maintenance entrypoint,
  run without a profile against either an unprofiled or profile-managed target,
  refuses to create a whole-catalog link and leaves active state byte-identical.
  Run with the selected profile, it preserves exact membership.
- **EV-REC-01 (SC-07, SC-08):** Interruption after new managed state is prepared
  but before activation leaves the prior realization active. Interruption during
  activation yields either the full new realization or an explicit
  nonconformant result with the prior realization recoverable; no mixed state is
  reported conformant.
- **EV-REC-02 (SC-06, SC-11):** A multi-target request succeeds for one target
  and encounters an unsupported harness on another. Evidence reports each
  target separately, preserves the unsupported target, and never claims
  cross-machine agreement for the partial result.
- **EV-REC-03 (SC-07, SC-08):** In a two-target request, target A activates and
  target B is interrupted after replacement has begun. Target A remains
  conformant; target B resolves to either its fully intact predecessor or the
  full new realization, or is explicitly nonconformant with its predecessor
  recoverable. No mixed B state is accepted.
- **EV-REC-04 (SC-07, SC-08, SC-09):** A target explicitly reported
  nonconformant after interruption is restored to its recorded predecessor and
  re-verified. The restored target matches its prior identity, foreign state is
  unchanged, and a second restoration request is idempotent.
- **EV-CON-01 (SC-06, SC-08):** Repeated application of the same profile identity
  to unchanged state produces no additional changes, while two concurrent
  requests for different profile identities allow at most one activation and
  reject the stale request without side effects.
- **EV-CON-02 (SC-02, SC-06, SC-10):** Every permutation of the same overlay set
  resolves to identical names, versions, content identities, routing assertions,
  budget result, and machine-readable conformance evidence.
- **EV-CON-03 (SC-06, SC-10):** A deployable profile's routing run evaluates
  declared cases against selected Dojo members plus observed foreign
  competitors, records included-skill and fixture coverage, and fails when a
  foreign description defeats a required positive or collision assertion.
- **EV-LEG-01 (SC-05, SC-09):** A whole-catalog project link is detected as 57
  managed skills rather than accepted as an implicit `full` profile. Explicit
  migration preserves its predecessor and activates only the selected profile.
  A subsequent documented adapter refresh preserves that membership.
- **EV-LEG-02 (SC-05, SC-09, SC-11):** An intersection-only installation with a
  stale concrete secondary copy is reported with missing, unexpected, content,
  and topology differences. Audit leaves it untouched; authorized migration
  yields the selected names and canonical identities without changing foreign
  entries.
- **EV-LEG-03 (SC-04, SC-08):** A harness version changes its listing format or
  precedence semantics after evidence was produced. Prior evidence is stale,
  the target becomes audit-only, and no prior budget verdict authorizes a new
  application.

## Open Questions

None. The profile vocabulary, baseline membership, additive composition,
budget thresholds, mutation boundary, evidence model, and initial exclusions
are settled for planning. Overlay membership remains ordinary reviewed profile
data constrained by required anchors, non-triviality, routing evidence, and
budget checks, not an unresolved behavioral decision.

## Revision History

- **2026-07-31 (revision 2).** Problem restated on Codex evidence. The original
  rested on a Claude Code listing budget that could not be verified and on an
  assumption that project-scope skills are inherited by subdirectory sessions,
  which is false. Neither claim survives, and neither is now load-bearing. The
  authoritative-limit definition admits vendor implementation source at a pinned
  revision; SC-04 requires the harness's own estimator where knowable; Claude
  Code is recorded as audit-only rather than the motivating case. No success
  criterion, evaluation scenario, or authority boundary changed — the mechanism
  is unmodified.

## Readiness Review

- Deterministic validation: passed
- Adversarial critique: complete
- Closure critique: complete
- Blocking findings: none

## Handoff

1. After readiness closes, hand off to `write-plan` to choose the thinnest
   implementation seams that satisfy this contract.
2. Preserve all success-criterion and evaluation-scenario IDs in downstream
   traceability.
3. Reopen contract decisions rather than hiding any implementation discovery
   that changes profile semantics, budget authority, or mutation safety.
