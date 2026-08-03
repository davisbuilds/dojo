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

Dojo currently treats its canonical catalog as though every skill
should be visible in every harness and project. Adapters expose the whole
catalog, even though the deliberately curated global installation contains only
31 canonical skills.

Measured against the one harness for which an authoritative listing limit can
be established, whole-catalog distribution leaves no margin at all. Codex
derives its skills budget as 2% of the model context window in tokens, falling
back to 8,000 characters only when the window is unknown
(`codex-rs/core-skills/src/render.rs`, `default_skill_metadata_budget`, at
pinned revision `f57467275c`). The window passed is the **full** one, not the
95%-effective figure — `codex-rs/core/src/session/mod.rs` calls
`default_skill_metadata_budget(turn_context.model_info.context_window)` — so at
the observed 272,000 window the budget is **5,440 tokens**.

Exceeding it is not a soft condition, and the degradation is worse than the
vendor source alone suggests. Codex shortens descriptions first, then removes
them entirely — but in practice the shortening lands **mid-word, with no
ellipsis and no marker of any kind**. A truncated listing is indistinguishable
from a catalog whose descriptions were simply written short. Exactly the routing
signal a skill catalog exists to provide is destroyed, invisibly, and nothing in
the repository reports it.

The measured position, from `codex debug prompt-input` — which dumps the
model-visible listing deterministically, so these are observations of the
effective catalog rather than estimates from the filesystem:

| Session root | Listed entries | Demand (est. tokens) | % of budget | Truncated |
|---|---|---|---|---|
| Ordinary global session | 41 | ~4,232 | 78% | 0 |
| `blueprint-finance` | 42 | ~4,363 | 80% | 0 |
| `viral` | 47 | ~5,257 | **97%** | 0 |
| `dojo` itself | 41 | ~4,232 | 78% | 0 |

Measured 2026-08-02. Read them as dated observations, not as constants — and
note how far they moved in one day. The 2026-08-01 measurement of the same four
roots read 96%, 98%, **111% with 19 truncated**, and **177% with 94 truncated**.

Three things follow, and the first is not the one this contract originally
argued. **Every Codex figure above was recovered by hand, in a day, without
anyone deciding what any target should receive.** Disabling one unused foreign
skill returned 18 points; deleting one line from an adapter generator took
`dojo` from 177% to 78%. Those were real defects and fixing them was correct,
but nothing in the repository proposed them, measured them, or now prevents
their return — the same authoring that produced them can reproduce them, and
the only reason anyone looked was that someone happened to be looking.
**The canonical catalog is not the population that matters**: those baseline
entries include harness-bundled skills, plugin entries, and foreign skills, and
one foreign directory contributed four listed entries because Codex lists
nested subskills. **Codex does not shadow by name across roots**, unlike Claude
Code — the property that made `dojo` pay twice for 32 skills until its
`.agents/skills` link was removed, and that will do so again for any target
that acquires one.

Codex now truncates nowhere. `viral` remains **non-deployable at 97%** against
the 90% ceiling this contract sets — roughly one average skill from silent
truncation, with no mechanism to notice it crossing.

Every earlier figure in this contract was a filesystem count, understating the
real listing by **1.78×**. Review did not catch that; running a probe that had
been assumed not to exist did. **A measurement nobody can reproduce is the
problem statement.**

The instability compounds it. On 2026-07-31 alone the full catalog measured
111%, then 90%, then 77%, then 75% — first from trimming ten descriptions, then
from retiring eight skills. **Four different values in one day, none of them the
result of a distribution decision.** Editing a description moves it; authoring a
skill moves it; neither action involves anyone deciding what a target should
receive.

That is the instability profiles address, and headroom does not remove it.
Trimming and retirement are one-time recoveries against a quantity that grows
by authoring, and nothing in the repository currently reports the number at
all — it was measured by hand each time, and only because someone happened to
be looking. An explicit, versioned selection is what keeps a deployable target
deployable without depending on that.

The 31-skill global subset that currently fits is undocumented curation. It exists as
installed state rather than as a reviewable declaration, so it cannot be
reproduced on a second machine, reviewed as a unit, or distinguished from drift.
Maintainers therefore cannot express which skills should be distributed
together, prove that an effective catalog fits a harness, or tell intentional
exclusion apart from missing or stale state.

**Claude Code is a second motivating case, and it is over budget too.** Earlier
revisions recorded it as permanently audit-only because no authoritative limit
could be established. That was wrong for the same reason the Codex figures were
wrong — the probe was never looked for in the right place. Two exist:
`--debug-file` states the budget verdict in one line, and
`OTEL_LOG_RAW_API_BODIES="file:<dir>"` writes the complete model-visible request
body per call, needing no telemetry configuration despite the prefix.

The limit is a vendor constant, which is precisely what SC-04 accepts as
authoritative: `skillListingBudgetFraction` defaults to **0.01** and the budget
is `context_tokens × 4 bytes × that fraction` **characters** (bundle v2.1.220,
alongside `skillListingMaxDescChars` = 1536). That is **8,000 characters at a
200k window and 40,000 at 1M**.

| Session | Skills | Chars | vs 8,000 |
|---|---|---|---|
| Ordinary global session | 45 | 16,535 | **2.07×** |
| `viral`-rooted | 51 | 20,220 | **2.53×** |
| `dojo`-rooted | 75 | 23,287 | **2.91×** |

Measured 2026-08-02. **This is the harness where the recovery did not happen.**
Every lever that moved Codex from 96% to 78% moved Claude Code by a few
percent, because none of them addressed membership: description trimming
recovered 537 characters against an 8,535-character overage, and the two
symlink and foreign-skill fixes touched roots Claude Code either does not read
or deduplicates. Nothing is left to trim. A 45-skill listing against an
8,000-character budget allows ~178 characters per entry, and the contract that
governs this catalog requires descriptions to carry trigger conditions. The
only remaining lever is which skills are present at all, which is what a
profile is.

Two properties distinguish it from Codex and both matter
to this contract. **Claude Code shadows by name across scopes** where Codex does
not, so a project-scope link adds only skills absent from user scope rather than
duplicating the catalog. And **its degradation drops descriptions outright**
rather than clipping them: over budget, lower-priority skills render as a bare
`- skill-name`, so the model sees a name and nothing about when to use it.
Bundled and explicitly-invoked skills are exempt.

The exposure is **model-dependent**, which bounds urgency without removing the
problem: at a 1M window the same 75-skill listing fits with no warning, so
degradation is confined to 200k-context models.

One earlier correction still stands: the assumption that project-scope skills
are inherited by subdirectory sessions was false, and this contract does not
depend on it.

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
  includes `create-cli` and `secure-code`; `research` includes `deep-research`
  and `research-architect`; `design` includes `design-critique` and
  `web-design-guidelines`; `knowledge` includes `obsidian-markdown` and
  `session-retro`; `shipping` includes `gh-commit-push-pr` and `vercel-deploy`;
  and `skill-authoring` includes `skill-creator` and `skill-standardizer`.
  `full` resolves to every canonical skill at the selected revision. Complete
  overlay membership is explicit profile evidence, not inferred from category
  names or installed state. **Anchors constrain the profile definition, not the
  realization:** an anchor may be suppressed on a harness that ships its own
  equivalent — `skill-authoring`'s `skill-creator` is suppressed on Codex — and
  the overlay still satisfies this criterion, because the capability is present
  at the target either way. An anchor absent from the definition remains a
  violation.
- **SC-03 — Usable baseline:** `core` contains the general delivery loop:
  `brainstorming`, `first-principles`, `write-spec`, `write-plan`, `diagnose`,
  `local-review`, `test-strategy`, and `verify-before-complete`. Membership is
  set from observed use rather than assertion (see Assumptions). `handoff` was
  removed: 2 observed Codex sessions against `session-retro`'s 14, which covers
  the adjacent need. `first-principles` was added at 52 sessions, second only to
  `verify-before-complete`. `diagnose` is retained on 12 sessions, last used
  eight days before this revision. Acceptance proves, for **every** deployable
  harness/model pair rather than one representative, a concrete realization
  where `core` plus one non-empty capability overlay and a three-entry foreign
  baseline remains within the effective-catalog budget. Both currently
  deployable pairs must be covered, including a 200k-context Claude Code pair,
  since its budget scales with the model's context window and a 1M-window pass
  proves nothing about a 200k one. A harness/model pair where the pinned
  baseline does not fit is audit-only rather than repaired by weakening the
  budget or rewriting skills.
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
  divided by four and the 5% undercount bound is satisfied by construction.
  **Claude Code budgets in characters directly** — `context_tokens × 4 ×
  skillListingBudgetFraction` — so a Claude Code policy compares characters to
  characters and performs no token conversion at all; converting would introduce
  an error the harness itself never makes. A policy must also record the
  **model** it was measured against, not only the harness version, because that
  budget moves with the context window. **Cost is computed from the untruncated
  source description**, never from an observed listing: a harness that elides to
  fit produces output that always fits, so calibrating against it would certify
  the failure this criterion exists to catch. Observing that a rendered entry
  differs from its source is itself a nonconformance signal, whether the harness
  marks the elision or not. An unknown or stale limit, uninspectable scope, or
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
  profile identity and canonical revision, **for the same harness**, receive the
  same expected Dojo skill names, versions, and content identities. Across
  different harnesses the same profile identity may resolve to different
  membership, and every such difference must be attributable to a declared
  harness-equivalence suppression naming the entry that displaced the member.
  A membership difference with no such attribution is drift, not resolution.
  Harness-specific foreign entries, versions, and budget outcomes likewise
  remain explicit differences rather than hidden profile drift.
- **SC-12 — Audit-only automation:** Session hooks, scheduled health checks, and
  checkout refreshes may detect and report profile drift, but they cannot apply,
  remove, relink, or widen installed skill state without a separately authorized
  maintainer action.
- **SC-13 — No indirect re-widening:** Existing adapter-generation and
  maintenance entrypoints are profile-aware. Against a profile-managed target,
  they preserve the selected realization; without an explicit profile for an
  unprofiled target, they refuse to create a whole-catalog skill link. Running a
  documented adapter refresh cannot convert a scoped target back to the full
  canonical catalog.

## Evaluation

Acceptance is mechanical, not an experiment. The contract is accepted when the
profile verifier and its behavior fixtures prove all success criteria across
the nominal, boundary, and failure scenarios below. The fixed catalog fixture
contains the full canonical catalog at the selected revision, the current
curated global subset, every canonical skill absent from it, at least three foreign entries, and
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
  names and the reviewed profile definitions — **intent, and harness-independent**.
  Resolved membership belongs to realization identity, which additionally binds
  the canonical revision, target identity, harness/model version, budget-policy
  identity, and the identity of the harness-equivalence declaration applied. Two
  harnesses can therefore share one profile identity and hold different
  realizations without either being drift. A canonical revision change, or a
  change to the equivalence declaration, is a new realization request rather than
  an idempotent replay.
- Suppression is resolution, not subtraction from the contract. A suppressed
  member is reported as suppressed, with the harness entry that displaced it, so
  evidence distinguishes *"the profile did not include it"* from *"the profile
  included it and the harness already had it"*. A member suppressed on every
  supported harness is a profile-definition error, not a valid resolution.
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
  assumed limit. **Both Codex and Claude Code now meet the authoritative-source
  bar** — each limit is read from vendor implementation source at a pinned
  version — so the initial deployable set is two harnesses, not one. Acceptance
  must not assume they behave alike: their budgets differ (5,440 tokens against
  8,000–40,000 characters), their scope precedence differs (Codex does not
  shadow by name across roots; Claude Code does), their degradation differs
  (mid-word clipping against whole-description removal), and Claude Code's
  budget is a function of the **model's** context window, so one machine can be
  conformant and non-conformant in the same repository depending on which model
  a session runs. A harness/model pair whose limit cannot be established remains
  audit-only. The `core`-fits proof in SC-03 must be discharged against **each**
  deployable harness/model pair rather than a single representative one.
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
  explicitly applies a profile. The effective listing it participates in
  measures ~4,232 estimated tokens, 78% of the Codex budget, on 2026-08-02 —
  within the ceiling, and it was at 96% the day before. The contract's job is to
  make that figure provable and durable rather than to reduce it. On Claude Code
  the same installation participates in a listing 2.07× over budget, so no
  target is conformant across both harnesses and the first honest verification
  run will say so.
- **The live subjects are real but they move, which is itself the evidence.**
  Both machines carry the same 32 installed entries — 31 canonical skills plus
  the foreign `microsoft-foundry`. That agreement was verified 2026-07-31,
  **had silently broken by 2026-08-02** across 9 skills whose content was
  updated on one machine and not the other, and was restored the same day by an
  explicit sync. Membership never diverged; content identity did, which is
  exactly what SC-11 compares. Nothing reported the divergence, and the only
  reason it was found is that someone hashed both machines by hand while
  checking something else. Read the cross-machine agreement case as a real
  subject that needs re-establishing before each use, not as a standing fact.
  `microsoft-foundry` remains installed but is **disabled in Codex config**, so
  it is present on disk and absent from the listing — a useful live case for the
  rule that the filesystem never adds an entry the probe did not list, but *not*
  a live foreign-entry observation in the Codex listing, which must be
  constructed.
- Listing cost is a moving target, and every figure in this contract is a
  measurement with a date rather than a constant. Description edits move it
  without changing skill membership, and skill authoring moves it without any
  deliberate distribution decision at all. Acceptance therefore turns on the
  verifier computing the figure at verify time, never on a number quoted here
  remaining true.
- Whether an individual skill earns its slot is outside this contract. Profiles
  make membership explicit, reviewable, and enforceable; they do not establish
  that any member improves outcomes. Membership remains a maintainer judgment
  informed by evidence gathered elsewhere, which is why overlay composition is
  reviewable data rather than a contract term.
- The `core` and anchor membership named above was set on 2026-07-31 from
  observed session use, measured separately per harness — Codex over 183
  skill-using sessions, Claude over 14 — and excluding a catalog-wide read
  sweep that touches every skill and means nothing. Codex consultation is
  detected from tool calls against a skill's `SKILL.md` and from the
  announcement several skills require; Claude from `Skill` dispatches. Counts
  are not summed across harnesses: the mechanisms differ and only rates are
  comparable. That is an engagement signal, not an outcome one — it shows what
  gets consulted, never whether consulting it helped — so it should be
  re-derived rather than trusted when outcome evidence exists.
- The two harnesses overlap substantially, and the pattern is one of degree
  rather than of disjoint sets. Ten of the eighteen most-used skills appear in
  both; `write-spec` and `write-plan` are the clearest shared members (21 and 13
  Codex sessions, 7 and 7 Claude). The strongest skew is
  `verify-before-complete` at 55% of Codex skill-using sessions with none
  observed in Claude, then `first-principles` and `test-strategy` at 28%.
  Claude's sample is small and its detection catches only explicit dispatch, so
  absence there is weak evidence. A single harness-independent baseline is
  supportable on current data; whether it should stay that way is a
  contract-revision question for when outcome evidence exists.
- Overlays are authored once and harness-independent, but they **resolve against
  a harness**. A profile states the capabilities a target should have; what
  physically lands is that set minus anything the harness already provides. The
  suppression is not free-form per-harness membership — it is a single declared,
  reviewable rule with one trigger: the harness ships its own equivalent of a
  member. Codex carries `skill-creator`, `skill-installer`, image generation,
  `review-agent`, `plugin-creator`, and `openai-docs` as `.system` entries;
  Claude Code carries a different three, none overlapping. Installing dojo's copy
  alongside is duplication, and `skill-creator` is duplicated in **every** Codex
  session today.
- Equivalence is declared per canonical skill, never inferred from a name match,
  and carries the evidence for the claim. An undeclared name collision between a
  profile member and a harness-bundled entry is reported as a collision rather
  than silently suppressed — the failure mode of guessing here is losing a skill
  the maintainer wanted.
- This is the correction to an earlier exclusion. Revisions 1–8 held that
  overlays must resolve identically everywhere because per-harness membership
  "would change profile identity semantics". The concern was right and the
  conclusion was not: it is resolved by separating the two identities rather than
  by forbidding the divergence. Profile identity captures **intent** and stays
  harness-independent; realization identity captures **what landed** and already
  binds the harness. Suppression moves resolved membership from the first to the
  second, which is where it belonged.
- Routing coverage is currently sparse: 48 skills pass the structural contract,
  but only three declare trigger fixtures (`blind-spots`, `test-strategy`,
  `verify-before-complete`, measured 2026-08-02; the catalog count is whatever
  `skills.json` holds at verify time and has moved four times during this
  contract's life). Profile work reports that limitation
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
- **EV-NEG-06 (SC-02, SC-06, SC-11):** One profile identity resolved against two
  harnesses, where the first ships a bundled equivalent of a member and the
  second does not. The member is suppressed on the first and present on the
  second; both realizations are conformant; evidence names the suppressed member
  and the bundled entry that displaced it; and the effective-catalog count for
  the first shows the member once, not twice. An undeclared name collision
  between a member and a bundled entry is reported as a collision and does **not**
  suppress. A member suppressed on every supported harness fails as a
  profile-definition error. Two machines running the same harness and profile
  identity still resolve identically.
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
- **EV-LEG-01 (SC-05, SC-09):** A whole-catalog project link is detected as the
  full canonical membership at the selected revision rather than accepted as an
  implicit `full` profile — the fixture pins a count so a partial scan cannot
  pass, and that count tracks the catalog rather than a number quoted here. Explicit
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

- **2026-08-02 (revision 10).** Re-measured, and the Problem's live-breach
  evidence has moved to a different harness. Codex now **truncates nowhere**:
  the ordinary session sits at 78% (was 96%), `dojo` at 78% (was 177% with 94
  truncated), `viral` at 97% (was 111% with 19 truncated). Two merged changes
  did it — disabling one unused foreign skill, and dropping `.agents` from the
  adapter generator's harness list so the catalog stops being linked into Codex
  project scope.

  The honest reading is that the earlier framing was partly right for the wrong
  reason. Two of the three Codex breaches were **defects, not distribution
  problems**, and they were fixable without profiles. What survives, and is
  strengthened: none of those fixes was proposed, measured, or is now prevented
  from regressing by anything in this repository, and the figures moved by a
  factor of two in one day with no distribution decision taken. `viral` is still
  non-deployable at 97% against the 90% ceiling.

  **Claude Code is where the argument now rests.** It moved by a few percent
  under the same levers — 2.13× to 2.07× ordinary, 2.98× to 2.91× in `dojo` —
  because none of them touched membership, which is the only lever it has. A
  45-entry listing against 8,000 characters allows ~178 characters per
  description while this repository's own skill contract requires descriptions
  to carry trigger conditions. There is nothing left to trim.

  Two live subjects were re-checked rather than assumed. The cross-machine
  agreement case had **silently broken** since revision 9 — 9 skills differing
  in content identity, membership unchanged, nothing reporting it — and was
  restored by an explicit sync; it is now documented as a subject requiring
  re-establishment rather than a standing fact. `microsoft-foundry` is installed
  but disabled, so it is no longer a live foreign-entry observation in the Codex
  listing and that fixture must be constructed. The catalog count is 48, not 49
  — the fourth stale count in this document pair, now stated with the date and
  the computed source rather than as a bare number.

  No success criterion, evaluation scenario, or authority boundary changed.

- **2026-08-01 (revision 9).** Overlays now resolve **against a harness**.
  Revisions 1–8 required identical membership everywhere, on the reasoning that
  per-harness membership "would change profile identity semantics". The concern
  was correct; the conclusion was not. It is resolved by separating two
  identities that had been conflated — profile identity is **intent** and stays
  harness-independent, realization identity is **what landed** and already bound
  the harness. Resolved membership moves from the first to the second.

  The mechanism is deliberately narrow: not free-form per-harness membership,
  but one declared rule with one trigger — the harness ships its own equivalent
  of a member. It is declared per canonical skill with evidence, never inferred
  from a name match, and an undeclared collision is reported rather than
  silently suppressed, because the failure mode of guessing is losing a skill
  the maintainer wanted.

  The evidence is live rather than anticipated: Codex bundles `skill-creator`,
  `skill-installer`, image generation, `review-agent`, `plugin-creator`, and
  `openai-docs` as `.system` entries while Claude Code bundles a different three
  with no overlap, and dojo's `skill-creator` is duplicated in **every** Codex
  session today. The two harnesses also differ in budget by 3–5×, in scope
  precedence, and in degradation mode, so identical membership had stopped being
  a simplification and become a misstatement.

  SC-02 gains the distinction that anchors constrain the definition rather than
  the realization; SC-11 scopes cross-machine comparability to a shared harness
  and requires every cross-harness difference to name the entry that displaced
  the member; **EV-NEG-06** is added, taking the scenario count to 16. No
  authority boundary changed.

- **2026-08-01 (revision 8).** Claude Code becomes a **second deployable
  harness**, and this is the first revision to change a success criterion rather
  than only its evidence.

  Revisions 2 through 7 recorded Claude Code as permanently audit-only because
  no authoritative listing limit could be established. That rested on a July
  finding that declared three routes exhausted and concluded *"nothing needs
  it."* The routes were individually defensible; the conclusion was not. It
  converted an open question into a closed one, and this contract built on the
  closure. Two probes exist — `--debug-file` states the budget verdict in one
  line, and `OTEL_LOG_RAW_API_BODIES="file:<dir>"` writes the full model-visible
  request body — and the limit is a vendor constant. **This is the second time
  in one week that an assumed-absent probe turned out to exist**; the first
  produced revision 7.

  The unverified "~1% budget" claim is confirmed exactly
  (`skillListingBudgetFraction` = 0.01). The "3.4× over" claim does not
  reproduce: an ordinary session measures 2.13× and a `dojo`-rooted one 2.98×.

  Three consequences are structural. **SC-03 now requires the fits-proof against
  every deployable harness/model pair**, not one representative — Claude Code's
  budget scales with the model's context window, so a 1M-window pass proves
  nothing about a 200k one. **SC-04 gains a Claude Code estimator rule** (budget
  in characters, no token conversion) and an explicit requirement that cost come
  from untruncated source rather than observed listing, because a harness that
  elides to fit always appears to fit. **The Assumptions entry on external
  policy** now states the two harnesses' differences as load-bearing: budgets,
  scope precedence, and degradation mode all differ, and Claude Code alone can
  be conformant and non-conformant in the same repository depending on the
  session's model.

  No evaluation scenario or authority boundary changed.

- **2026-07-31 (revision 7).** Corrections and one sequencing constraint. Three
  counts were stale: 57 skills pass the structural contract (now 49), two
  declare trigger fixtures (now three), and EV-LEG-01's fixture pinned the
  literal number 57 — replaced with a count that tracks the catalog, since a
  fixture quoting a constant is the same defect this contract exists to prevent.

  The budget table is restated. A fresh measurement puts the curated
  installation at 56% and the full catalog at 85%, against 50% and 75% recorded
  days earlier. The disagreement is not resolved here on purpose: the two passes
  used different estimators, neither is reproducible from the repository, and
  adjudicating them is exactly what the verifier is for. Recording the conflict
  is stronger evidence for this contract than either figure alone.

  Added a delivery-sequence constraint to Handoff. Nothing in the contract
  changed — no success criterion, evaluation scenario, or authority boundary is
  modified — but the verify and apply halves are separable and the plan is
  directed to treat them as separate phases.

  **Amended 2026-08-01, same revision.** The Problem section is rewritten around
  measurements rather than estimates. `codex debug prompt-input` dumps the
  model-visible listing deterministically; it had been assumed no such probe
  existed, and the assumption was never tested. Under it, every figure this
  contract previously carried — including revision 7's own 56% and 85% — was a
  filesystem count understating the effective listing by 1.78×.

  Three findings change the argument rather than merely its numbers. The
  budget is **5,440**, not 5,168: `codex-rs/core/src/session/mod.rs` passes the
  full context window, confirmed both from source and behaviorally by bracketing
  a truncating listing against a non-truncating one. Codex **does not shadow by
  name across roots**, so SC-04's "shadowed names counted according to actual
  harness behavior" resolves to counting both copies. And truncation is **live
  today** in two repositories, applied mid-word with no marker — so this contract
  is not preventing a future failure, it is describing a present one.

  No success criterion, evaluation scenario, or authority boundary changed.

- **2026-07-31 (revision 6).** Corrects revision 5's measurement, which was
  wrong in a way that inverted one of its conclusions. Codex reads a skill
  through a `custom_tool_call`, not a shell command; revision 5 counted only
  shell reads and so scored `write-spec` and `write-plan` at **zero** Codex use
  when the real figures are 21 and 13 sessions. The corrected denominator is
  183 Codex skill-using sessions, not 17.

  Two claims are withdrawn. `handoff` was said to have zero use — it has 2
  sessions, still far below `session-retro`'s 14, so it stays out of `core` for
  a weaker reason than stated. `diagnose` was said to have zero use and kept on
  judgment — it has 12 sessions and a last use eight days ago, so it belongs in
  `core` on evidence and the judgment was unnecessary.

  The larger withdrawal is the claim that the harnesses use near-disjoint skill
  sets. That was an artifact: with the corrected detector, ten of the eighteen
  most-used skills appear in both, and `write-spec`/`write-plan` — the supposed
  Claude-only pair — are among the most-used in Codex. A single
  harness-independent baseline is supportable on current data, and the risk
  recorded in revision 5 is downgraded accordingly.

  The retirements in dojo PR #51 were re-checked against the corrected detector
  and all eight hold: every retired skill shows 1–4 uses, none since May except
  one, against 21–100 for the surviving `core` members.

- **2026-07-31 (revision 5).** *Superseded in part by revision 6 — the figures below came from a detector that missed most Codex use.* Membership moved from assertion to observation.
  Session use was measured across both harnesses for all 49 skills, excluding a
  catalog-wide read sweep that touches everything and means nothing, and the
  named members were re-derived from it.

  `core` drops `handoff` — zero observed invocations, and `session-retro`,
  which is used, covers the adjacent need — and gains `first-principles`, the
  most-consulted skill in the catalog at 13 sessions. `diagnose` stays at zero
  observed use: it is the only debugging skill, `first-principles` routes to it
  by name, and absence of use for something that fires only when work breaks is
  weaker evidence than the same number elsewhere.

  Three anchors change on the same basis: `engineering` swaps `api-design`
  (zero use) for `secure-code`, `knowledge` swaps `compound-docs` for
  `session-retro`, and `design` swaps `frontend-design` for
  `web-design-guidelines`, which is also the routing hub the rest of the design
  cluster defers to.

  **Corrected the same day:** the first pass summed session counts across
  harnesses, which is wrong — Codex consultation and Claude dispatch are
  detected by different mechanisms and only comparable as rates. Recomputed per
  harness (17 and 14 skill-using sessions) the membership conclusions hold, but
  the divergence they rest on is much starker than the summed view showed: only
  four of the twelve most-used skills appear in both harnesses at all. That is
  now recorded as the largest open risk to having a single `core`.

  Two limits are now stated rather than left implicit: this is an *engagement*
  signal and not an outcome one, so it should be re-derived when outcome
  evidence exists; and overlays resolve identically on every harness even
  though Codex ships built-in equivalents of several `skill-authoring` members,
  which the contract measures but deliberately does not resolve. No success
  criterion, evaluation scenario, or authority boundary changed structurally.

- **2026-07-31 (revision 4).** SC-02 named `gh-review-pr` as a required anchor
  of the `shipping` overlay. That skill was retired the same day, so the
  contract required membership in a skill that does not exist — the first
  instance of this spec being falsified by the repository rather than by a
  measurement. Replaced with `vercel-deploy`, which is non-`core`, live, and
  squarely about getting work out the door. Every other anchor was checked
  against the catalog and is present. Counts throughout are now stated as
  measurements with a date rather than as constants, since the catalog moved
  from 57 skills to 49 and from 90% of budget to 75% between revisions 3 and 4.
  No other success criterion, evaluation scenario, or authority boundary
  changed.

- **2026-07-31 (revision 3).** Problem re-measured after a description-trimming
  pass on ten skills. The full canonical catalog moved from ~5,718 estimated
  tokens (111% of the Codex budget) to ~4,667 (90%), and the curated
  installation from 64% to 50%. Revision 2 argued that whole-catalog
  distribution "does not fit"; that is no longer literally true, so the argument
  is restated on zero-margin instability rather than on overflow. The finding
  that matters more: listing cost changed by roughly a fifth in one day from
  edits that touched no skill membership, which is itself evidence that a
  quoted figure cannot be load-bearing and the verifier must compute at verify
  time. No success criterion, evaluation scenario, or authority boundary
  changed.

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

**Delivery sequence.** The plan must deliver the read-only half before the
mutating half, as separately shippable phases:

- **Phase 1 — verify only.** Profile definitions, resolution, effective-catalog
  budget evaluation, and conformance evidence: SC-01 through SC-06, SC-10,
  SC-11, plus the audit-only halves of SC-09 and SC-12. `dojo profiles verify
  --all` works end to end and reports drift. Nothing mutates target state, so
  the entire recovery, idempotence, and concurrency surface is out of phase 1 by
  construction rather than by omission.
- **Phase 2 — apply.** SC-07, SC-08, SC-13, migration under SC-09, and the
  EV-REC and EV-CON scenarios.

This is a sequencing constraint, not a scope reduction: every success criterion
and evaluation scenario remains in the contract and phase 2 is required for
acceptance. The reason to split is that phase 1 carries most of the value and
almost none of the risk. It answers the question no tool in this repository
answers today — what does the effective catalog cost right now, against an
authoritative limit — and the figures in this contract had to be measured by
hand, twice, with conflicting results, precisely because it does not exist.
Phase 2 automates an action a maintainer performs rarely, and is where the whole
partial-failure and concurrency apparatus lives.

Phase 1 also supplies the missing referent for cross-machine drift monitoring
(`ops` register D6): a drift monitor needs a declaration of intended membership
to compare against, and no such declaration exists until profiles do.
