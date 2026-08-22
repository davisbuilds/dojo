---
date: 2026-07-27
author: gpt-5.6-sol
topic: distribution-profiles
stage: spec
status: complete
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

**The measured position below is superseded as of 2026-08-04. It is retained
because the reason it was wrong is the strongest argument this contract makes.**

| Session root | Listed entries | Charged (tokens) | % of budget | Truncated |
|---|---|---|---|---|
| Ordinary global session | 41 | 4,132 | 76% | 0 |
| `blueprint-finance` | 42 | 4,263 | 78% | 0 |
| `viral` | 47 | 5,159 | **95%** | 0 |
| `dojo` itself | 41 | 4,132 | 76% | 0 |

Measured 2026-08-02 from `codex debug prompt-input` with Codex's own arithmetic:
only skill lines are charged, the intro prose and section headers are not, and
the alias roots table is a rounded difference of two whole bodies rather than a
sum of lines. The 2026-08-01 measurement of the same four roots read 96%, 98%,
**111% with 19 truncated**, and **177% with 94 truncated**.

**Every figure in that table describes a session the operator never runs.**
`codex debug prompt-input` does not load remote-connector plugins; it renders
the `codex exec` surface. Interactive `codex-tui` sessions — the only kind a
person opens — additionally receive every skill synced from account-level
ChatGPT connectors. Measured 2026-08-04 from the session rollout that a real TUI
session wrote (`~/.codex/sessions/**/rollout-*.jsonl`, which records the block
that was actually sent):

| Surface | Roots | Entries | True demand | % of budget | Rendered as |
|---|---|---|---|---|---|
| `codex debug prompt-input` / `codex exec` | 4 | 41 | 4,132 | 103% | full descriptions |
| `codex-tui`, same cwd, same model, same minute | 9 | 110 | **9,838** | **246%** | every description clipped to ≤77 chars |

**The budget is 4,000 tokens, not the 5,440 this contract assumed through
revision 12.** Established by saturation rather than by a vendor constant: two
`codex-tui` renders of radically different inputs — 110 entries and 56 entries —
each total **exactly 4,000 tokens**, entry cost plus alias table, with zero
difference between them. Codex spends the listing budget to the last token, which
is the vendor-parity property Task 0 already asserts; the error was the
denominator. `codex debug models` reports a 272,000 window for this model
(2% = 5,440), while the interactive surface budgets against 4,000.

**Corrected 2026-08-10 by sweeping the full session history.** An earlier
revision concluded that "the interactive budget does not move with the model",
contradicting the pinned vendor path where `session/mod.rs` passes
`model_info.context_window` into `default_skill_metadata_budget`. That was an
overclaim drawn from two models on a single build. Across 89 parseable rollouts
spanning twelve CLI builds, the saturated total — which is the ceiling — is:

| Build | Ceiling |
|---|---|
| 0.139.0 | 5,358 |
| 0.142.3 / 0.142.4 | 5,534 |
| 0.143.0, 0.144.1, 0.144.6 | **5,440** = 2% × 272,000, the vendor formula exactly |
| 0.144.1 (second model) | **7,440** = 2% × 372,000 |
| 0.145.0 | ~4,000 |
| 0.146.0 | **4,000** |
| 0.147.0 | **≥ 4,843** — underivable; nothing saturates |

`2% × context_window` was therefore **correct through 0.144.x**, including for a
larger-window model, and **0.145.0 changed it**. The vendor source was not wrong;
it described a build that has since moved.

What survives is stronger than the claim it replaces, because it is the general
rule rather than one build's constant: **the ceiling is a property of the harness
build, must be established by saturation, and samples from two builds may never
be pooled.** Whether 0.145.0 introduced a fixed cap or changed the window it
passes is **unanswered rather than closed**; a build whose models differ in
window would settle it, as 0.144.1's 7,440 did for its predecessor.

The TUI listing charged 4,000 tokens *after* clipping — exactly the budget, which
is why nothing downstream of the rendered output could detect it. Demand by source:
`vercel` 4,048 · dojo + bundled 3,875 · `google-drive` 660 ·
`openai-developers` 561 · `github` 335 · `browser` 86 · `gmail` 74 ·
`computer-use` 67. **A single account-level connector consumed 74% of the entire
skills budget**, and the 31 dojo skills this contract governs reached the model
as 75-character fragments.

Three properties of that finding bear directly on what this contract must
require. **The clipping had been live since at least 2026-07-28** — eleven
captured sessions show it — including the sessions of 2026-08-02, the day the
superseded table was measured. **The connectors are not locally installed and
not locally governed**: `codex plugin list` reports marketplace state and cannot
see them at all, and the one that was disabled was disabled under a second
config key (`vercel@openai-curated` while the loader read
`vercel@openai-curated-remote`), so the CLI reported `installed, disabled` for a
plugin that was supplying 54 skills. **Their presence is not deterministic**:
two `codex-tui` sessions hours apart on 2026-07-28 differed in whether the
connectors were listed at all, with no local change between them.

`openai-templates` is the standing case for why this cannot be inferred from
disk: 20 skills, **1,870 tokens — 47% of the 4,000 budget** — if listed,
structurally indistinguishable on disk from connectors that do list, and present
in **zero** of eleven captured sessions. It is a latent half of the budget that
no local state predicts.

**The local control does not work, and the recovered budget did not stay
recovered.** Both established by controlled test on 2026-08-06.
`[plugins."<name>@openai-curated-remote"] enabled = false` is **inert** — set for
`google-drive` with its cache intact and `openai-developers` left untouched as a
control, the next session listed all five google-drive skills unchanged. Removal
in the ChatGPT web app *does* work. So the only surface governing 22% of this
target's demand is an account setting, and `codex plugin list` cannot see those
entries at all: it reports them `not installed` while they are listing.

Then the recovered budget was refilled. Removing `google-drive` and `gmail`
freed **734 tokens**; a Codex desktop update the same day added a new
`openai-primary-runtime` marketplace plus `sites` and `visualize`, worth **723**.
Net recovery **11 tokens — 0.3% of budget**. Entry count 56 → 56, charged total
still exactly 4,000, still 50 of 56 descriptions clipped.

| Source | Tokens | % of 4,000 |
|---|---|---|
| dojo | 3,121 | **78%** |
| remaining connectors | 896 | 22% |
| Codex bundled | 728 | 18% |
| new runtime plugins (arrived via app update) | 723 | 18% |
| **total** | **5,468** | **137%** |

Three distribution-relevant changes in six hours — a connector sync, a user
uninstall, a desktop app update — none of them a distribution decision, netting
to nothing. **That is this contract's argument, observed rather than reasoned.**

**The harness's own warning is not a sufficient signal, and this contract must
not treat it as one.** Removing the largest connector took the same target from
246% to 144%. At 246% Codex printed *"Skill descriptions were shortened…"*; at
144% it printed nothing at all — while still clipping **50 of 56 descriptions and
removing 6,984 characters**, `research-architect` from 622 to 203,
`test-strategy` from 513 to 203. A maintainer watching the warning would have
concluded the problem was fixed. Silence from the harness is evidence about the
warning's threshold, never about conformance.

**What this establishes is that membership is now the binding constraint on
Codex, not merely on Claude Code at 200k.** Scored against the observed 4,000
ceiling, with the unavoidable floor of 959 tokens (harness-bundled entries, local
plugin entries, and the alias roots table):

| Composition | Skills | Demand | % of 4,000 |
|---|---|---|---|
| `core` | 8 | 1,865 | 47% |
| `core` + any one overlay | 11–12 | 2,097–2,328 | 52–58% |
| `core` + any three overlays | 18 | ~2,874 | 72% |
| `core` + all six overlays | 27 | 3,697 | **92%** |
| currently installed set | 31 | 4,007 | **100%** |
| `full` | 48 | 5,590 | **140%** |

The undocumented 31-skill curation this contract was written to replace does not
fit the harness it runs on, by 407 tokens against the 90% ceiling — and with
every connector removed it still does not. `full` is 140%. Every composition of
`core` plus up to three overlays fits, and all twenty three-overlay combinations
fit. Model calibrated against the live render to **0.00%**.

Read every number in this contract as a dated observation of a **named
surface**, not as a constant.

Three things follow, and the first is not the one this contract originally
argued. **Every Codex figure above was recovered by hand, in a day, without
anyone deciding what any target should receive.** Disabling one unused foreign
skill returned 18 points; deleting one line from an adapter generator took
`dojo` from 177% to 76%. Those were real defects and fixing them was correct,
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

On the `exec` surface Codex truncates nowhere, and `viral` sits at **95%**
against the 90% ceiling this contract sets. **On the interactive surface Codex
truncates everywhere** — every description in every observed `codex-tui` session
since 2026-07-28, unmarked. The two sentences describe the same machine on the
same day, and until 2026-08-04 only the first was known.

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

Demand does not move with the window; only the budget does. So one set of
measurements scores against both, and the answer differs entirely:

| Session | Skills | Demand (chars) | vs 40,000 (1M) | vs 8,000 (200k) |
|---|---|---|---|---|
| Ordinary global session | 45 | 16,535 | 41% | **2.07×** |
| `viral`-rooted | 51 | 20,220 | 51% | **2.53×** |
| `dojo`-rooted | 75 | 23,287 | 58% | **2.91×** |

Measured 2026-08-02. **At the window this operator actually runs, Claude Code is
conformant with room** — every session sits between 41% and 58% against a 90%
ceiling, and a captured 1M session emits no budget warning at all. The 200k
column is a real exposure, not a hypothetical one, but it is not on the path
anyone uses today.

That reframes rather than removes the case. Two things survive it. The margin is
**one model selection wide**: the same catalog, on the same machine, on the same
day, is 58% or 291% depending only on which model the session runs, and nothing
announces the difference — the harness emits a warning the user never sees and
the model receives bare skill names with no indication anything was dropped.
And the levers that rescued Codex do not exist here: description trimming
recovered 537 characters, the symlink and foreign-skill fixes touched roots
Claude Code either does not read or deduplicates. If a 200k session ever matters,
the only remaining lever is which skills are present at all — which is what a
profile is.

For calibration, since it is the number a maintainer would need: at 200k,
harness-bundled entries are **exempt from stripping** and consume 3,774 of the
8,000 budget at full length, leaving ~4,226 for everything dojo governs. Against
a measured mean of 313 characters per dojo entry, that is **about 13 skills** —
`core` plus roughly one overlay, which is what SC-03's fits-proof already
specifies.

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
  baseline remains within the effective-catalog budget. **A pair is deployable
  when it is declared as in use**, not merely because its limit is knowable.
  The declared set is Codex at its current window and Claude Code at 1M. A
  pair whose limit is established but which nobody runs — Claude Code at 200k
  today — is **measured and reported, never gating**: the verifier scores it and
  says so, and a session that does run there is told it is non-conformant rather
  than left to discover bare skill names on its own. Declaring a pair deployable
  is a maintainer act, so adding one is a contract change and cannot happen by a
  session quietly selecting a different model. A deployable pair where the
  pinned baseline does not fit is audit-only rather than repaired by weakening
  the budget or rewriting skills.
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
  **A measurement must name the invocation surface it was taken from, and only a
  surface declared in use can make a pair deployable.** A harness may render its
  listing differently per entry point: Codex's `debug prompt-input` and `exec`
  omit account-synced connector plugins that its interactive TUI loads, so the
  same machine, model, and working directory measured 41 entries at 76% on one
  surface and 110 entries at 178% on the other. A probe that renders a code path
  nobody runs is not authoritative however deterministic it is, and its agreement
  with the harness's own arithmetic — which held to 0.15% — says nothing about
  whether it observed the right session. Where the harness records what it
  actually sent, that record is the authoritative observation and a live probe is
  a cross-check against it, never a substitute. **Demand the operator does not
  control locally must be reported as a named, separately attributed share**,
  because it can appear, change, or vanish between two sessions with no local
  action: account-level connector skills are governed by a config key distinct
  from the one the harness's own plugin CLI displays, are absent from that CLI's
  inventory entirely, and were observed present in one session and absent in
  another two hours later. A budget verdict that cannot attribute demand to a
  controllable source is reported as unsupported rather than as a pass.
  **Where a vendor-reported limit and the limit observed by saturation disagree,
  the observed limit governs and the disagreement is reported.** A harness that
  spends its listing budget to the last token discloses that budget exactly: two
  renders of different inputs that both saturate must total the same number, and
  that number is the limit. Codex's model catalog reported a 272,000 window
  (2% = 5,440) while two interactive renders each totalled exactly 4,000 — a 36%
  overstatement that made a 100%-of-budget target read as 74%. A limit taken from
  a vendor catalog without a saturation check is recorded as **provisional**, and
  a policy carrying a provisional limit cannot make a pair deployable.
  **A harness's own degradation warning is never sufficient evidence of
  conformance.** Codex warns at 246% of budget and stays silent at 144% while
  clipping 50 of 56 descriptions, so absence of a warning is a fact about the
  warning's threshold, not about the listing. A warning may be consumed as a
  positive signal of degradation; its absence may not be consumed as a negative
  one.
  **A conformance verdict is bounded by the harness build and the uncontrolled
  entry set it was measured against, and is invalidated when either moves.** Both
  were observed to move demand with no local action and no notification: an
  account connector sync, and a desktop application update that introduced an
  entire new plugin marketplace worth 18% of budget. A verdict therefore records
  the harness build identity and the set of entries outside local control, and a
  target whose either has changed since its last observation is reported as
  **stale rather than conformant**. Re-measurement is the only way to clear it —
  a control surface's own report may not substitute, because a local disable of
  an account-synced entry is **inert**: setting it changes the configuration and
  changes nothing the model sees.
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
profile verifier and its behavior fixtures prove the **Phase 1** success criteria
(SC-01…SC-06, SC-10, SC-11, and the audit-only halves of SC-09 and SC-12) across
the nominal, boundary, and failure scenarios below. The Phase 2 criteria (SC-07,
SC-08, SC-13, the migration half of SC-09, and the EV-REC/EV-CON scenarios) were
descoped in revision 15 and do not gate acceptance; they remain written as the
contract an applicator would satisfy if one is ever built. The fixed catalog fixture
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
  measures 4,132 tokens, 76% of the Codex budget, on 2026-08-02 —
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
  rule that the filesystem never adds an entry the probe did not list.
- **A live foreign entry does exist, and an earlier draft of this bullet said it
  did not.** Having established that `microsoft-foundry` was no longer listed,
  that draft concluded the foreign-entry fixture would have to be constructed —
  reasoning from one absence to a general one without running the probe. The
  probe reports `spreadsheet`, installed under `~/.codex/skills` and listed in
  every session. Recorded because the error is this contract's own subject
  matter: an absence is a claim about the instrument, and the instrument was
  sitting one command away.
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
  member. Codex **lists** `skill-creator`, `skill-installer`, `imagegen`,
  `plugin-creator`, and `openai-docs` as `.system` entries; Claude Code carries a
  different set, none overlapping. Installing dojo's copy alongside is
  duplication, and `skill-creator` is duplicated in **every** Codex session
  today. **Corrected 2026-08-03:** earlier revisions also named `review-agent`
  here. It exists at `~/.codex/skills/.system/review-agent/` and appears in **no
  listing** — not in the Task 0 capture and not in a live probe re-run. Only
  listed entries can displace a member, so it is not an equivalence candidate.
  This is the "filesystem is not the listing" rule catching this contract's own
  prose, which is why the declaration requires observed evidence rather than a
  directory.
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

- **2026-08-15 (revision 16). Contract closed at shipped scope; the `verify --all`
  CLI is dropped.** Operator decision, `status: complete`. What ships is the
  deliverable: the read-only measurement stack under `scripts/profiles/`
  (probes, definitions, resolution, budget policy, rollout-authoritative
  observation, byte-identical evidence), the Phase-1 CI gate, recurring
  machine-side drift checks, and the standing membership decision in
  `docs/project/GLOBAL-SKILL-MEMBERSHIP.md`. Three Phase-1 tasks are **descoped,
  not delivered**: Task 8 (`dojo profiles verify --all`) because a single
  entrypoint would only wrap a measurement the audit repeatedly proved could be
  wrong — it solves no measurement-correctness problem, which was the whole
  difficulty; Task 7 (cross-target comparison) because scheduling, transport,
  and host reachability are deployment integrations while Task 5 already emits
  portable evidence for comparison; Task 6 (routing-coverage fixtures) because
  it is test polish, not a governance capability. Task 10's standing position
  is carried by `GLOBAL-SKILL-MEMBERSHIP.md`. This is the program's formal
  close, not an assertion that every original task landed.

- **2026-08-14 (revision 15). Phase 2 (apply) descoped; acceptance closes at
  Phase 1.** Operator decision. The two remediations the program ran — the
  six-skill machine-global cut and the Codex CLI version-skew fix — were
  performed by hand, rarely, cheaply, and correctly. Governance of the ~26-skill
  machine-global catalog is now carried by Phase 1's measurement plus recurring
  drift checks (installed-versus-canonical, listing stability), declared
  cross-target manifests (toolchain, project-skill wiring), and a
  manual `sync.py --apply` after each merge. Against that realized problem size
  the staged applicator — realization identity, per-target locking, concurrency,
  partial-failure recovery (Tasks 11–16) — is disproportionate high-risk
  mutation code for a rare, small, adequately-handled action. SC-07, SC-08,
  SC-13, the migration half of SC-09, and the EV-REC/EV-CON scenarios move out
  of scope: retained as the contract an applicator *would* owe, no longer gating
  acceptance. This is a scope reduction, recorded as one. It also settles the
  Phase-1-supplies-the-referent argument below: deployment-specific drift
  monitors can consume Phase 1's declarations without a profiles applicator.

- **2026-08-06 (revision 14).** **The local control is inert, and the recovered
  budget did not stay recovered.** Two controlled results.
  `[plugins."<name>@openai-curated-remote"] enabled = false` does nothing —
  tested single-variable with `google-drive` disabled, its cache intact, and
  `openai-developers` left untouched as a control; the next session listed all
  five google-drive skills unchanged. Removal in the ChatGPT web app works. This
  retroactively explains the `vercel` case, where a disable and an uninstall
  happened with no session between them, so for two days the natural reading was
  wrong. Then removing `google-drive` and `gmail` freed 734 tokens and a Codex
  desktop update added 723 the same day — **net 11 tokens, 0.3%** — with entry
  count unchanged at 56, charged total still exactly 4,000, and still 50 of 56
  descriptions clipped.

  SC-04 gains one clause: **a verdict is bounded by the harness build and the
  uncontrolled entry set, and is invalidated when either moves**, reported as
  *stale* rather than conformant, clearable only by re-measurement — never by a
  control surface's own report, since that report can be inert.

  The Problem section's central claim was that the effective catalog moves
  without anyone taking a distribution decision. Over six hours it moved three
  times — connector sync, user uninstall, application update — and netted to
  nothing. The contract no longer needs to argue this.

- **2026-08-04 (revision 13, same day as 12).** **The budget was also wrong, and
  in the same direction.** Verifying revision 12's own projection produced two
  findings it had not predicted. **(1) The limit is 4,000 tokens, not 5,440.**
  Two `codex-tui` renders — 110 entries and 56 — each total *exactly* 4,000,
  entry cost plus alias table, zero difference. Codex saturates its budget, so
  two saturating renders disclose the limit precisely; the vendor catalog's
  272,000 window (2% = 5,440) overstates the interactive budget by 36%. Every
  Codex percentage in revisions 7–12 is therefore understated on top of being
  measured on the wrong surface: the live target was 246%, not 178%. **(2) The
  harness's warning has false negatives.** Removing the largest connector took
  the target from 246% to 144%; Codex warned at the first and said nothing at the
  second, while still clipping 50 of 56 descriptions and removing 6,984
  characters. Revision 12 had proposed consuming that warning as a check — it
  would have reported the target healthy.

  SC-04 gains two clauses: an observed-by-saturation limit **governs over a
  vendor-reported one**, with a vendor limit unbacked by a saturation check
  recorded as *provisional* and unable to make a pair deployable; and a harness
  warning may be consumed as positive evidence of degradation but **never its
  absence as evidence of conformance**.

  **The consequence is that membership becomes the binding constraint on Codex
  too, which no prior revision established.** Against the observed ceiling the
  undocumented 31-skill curation sits at 100% of budget — over the 90% ceiling by
  407 tokens — and stays over with every connector removed; `full` is 140%.
  `core` is 47%, `core` plus any one overlay 52–58%, and all twenty
  `core`-plus-three-overlay combinations fit. The overlay sizing chosen in Task 1
  against Claude Code's 200k budget turns out to be right for Codex as well, from
  an independent direction. Model calibrated against the live render to 0.00%
  after correcting the locator form — dojo entries render with absolute paths,
  not root aliases, which was worth 9% on its own.

  Three corrections in one day, two of them found by measuring rather than
  reasoning and within minutes of each other. The pattern is recorded rather than
  smoothed over: this contract's numbers have been wrong in the same direction
  every time, and every correction so far has come from looking at a surface
  nobody had looked at yet.

- **2026-08-04 (revision 12).** **The probe was measuring a surface nobody
  runs.** A live `codex-tui` session emitted the skill-shortening warning while
  the verifier reported 76% of budget and zero degradation for the same
  directory, model, and minute. The TUI listing held **110 entries across 9
  roots at 178% of budget with every description clipped to ≤77 characters**;
  `codex debug prompt-input` — the basis of every Codex figure in revisions
  7–11 — renders the `exec` path and omits account-synced connector plugins
  entirely. The gap is 69 entries and 5,679 tokens, of which one connector
  (`vercel`) is 4,048. SC-04 gains three normative clauses: a measurement must
  **name its invocation surface** and only a declared-in-use surface can make a
  pair deployable; where the harness records what it sent, that record is
  authoritative and a live probe is a cross-check rather than a substitute; and
  demand outside local control must be **separately attributed**, with an
  unattributable verdict reported as unsupported rather than as a pass. No
  success criterion was weakened and no scope changed.

  Three properties make this worse than a stale number, and each one is a
  requirement in disguise. The clipping had been live since **2026-07-28**,
  including on the day revision 11's table was measured, so the contract has
  been arguing from a conformant reading of a degraded machine for a week. The
  connectors are **not locally governed**: `codex plugin list` cannot see them,
  and the one that was disabled was disabled under a second config key while the
  loader read another, so the CLI truthfully reported `installed, disabled` for
  a plugin supplying 54 skills. And their presence is **not deterministic** —
  two TUI sessions two hours apart differed in whether connectors were listed,
  with no local change between them.

  This reverses the direction of the previous three revisions. Revisions 7, 10,
  and 11 each found that better information *reduced* urgency; this one restores
  it, and on stronger evidence than the contract originally had. The failure it
  describes is no longer hypothetical or off-path: the operator's 31 governed
  skills reached the model as 75-character fragments, in the harness the
  operator uses, for a week, while two separate instruments — the vendor's own
  plugin CLI and this repository's verifier — both read clean. That is precisely
  the silent, unannounced, unattributable degradation the contract exists to
  make visible, and it was found by a warning line in a screenshot rather than
  by anything either repository runs.

- **2026-08-03 (revision 11).** Deployability is now scoped to the harness/model
  pairs actually **in use**, and the effect is that nothing this operator runs is
  in breach.

  The operator runs Claude Code only at a 1M window. Demand does not move with
  the window — only the budget does — so the existing measurements rescore
  without re-probing: 41%, 51%, and 58% against a 90% ceiling, confirmed by a
  captured 1M session that emits no budget warning. The 200k figures (2.07× to
  2.91×) are real and stay recorded, but they describe a path nobody takes.

  SC-03 previously required the fits-proof against every pair whose limit could
  be *established*, which silently promoted 200k to a gate. It now turns on
  whether a pair is **declared in use**: Codex, and Claude Code at 1M.
  Established-but-undeclared pairs are measured and reported, never gating — so
  a session that does run at 200k is told it is non-conformant instead of
  discovering bare skill names on its own. Declaring a pair is a maintainer act,
  so the gate cannot widen because a session picked a different model.

  This is the third consecutive revision in which better information reduced the
  urgency rather than confirming it: revision 7 found the measurements were
  1.78× overstated, revision 10 found two of three Codex breaches were ordinary
  defects, and this one finds the remaining harness conformant in practice. What
  survives is worth stating plainly, because it is now the whole case. `viral`
  sits at 95% on Codex against a 90% ceiling. The Claude Code margin is **one
  model selection wide** — 58% or 291% for the same catalog on the same day,
  with no announcement either way. The figures have moved by a factor of two in
  a single day, twice, with no distribution decision taken. Cross-machine
  agreement broke silently within 24 hours of being verified. And the curated
  31-skill set remains installed state rather than a reviewable declaration.
  None of that is firefighting; all of it is governance, which is what this
  contract was always for.

  Recorded for calibration since a maintainer will need it: at 200k,
  harness-bundled entries are exempt from stripping and take 3,774 of the 8,000
  budget at full length, leaving ~4,226 for dojo against a measured mean of 313
  characters per entry — **about 13 skills**, which is `core` plus roughly one
  overlay.

  No evaluation scenario or authority boundary changed.

- **2026-08-02 (revision 10).** Re-measured, and the Problem's live-breach
  evidence has moved to a different harness. Codex now **truncates nowhere**:
  the ordinary session sits at 76% (was 96%), `dojo` at 76% (was 177% with 94
  truncated), `viral` at 95% (was 111% with 19 truncated). Two merged changes
  did it — disabling one unused foreign skill, and dropping `.agents` from the
  adapter generator's harness list so the catalog stops being linked into Codex
  project scope.

  The honest reading is that the earlier framing was partly right for the wrong
  reason. Two of the three Codex breaches were **defects, not distribution
  problems**, and they were fixable without profiles. What survives, and is
  strengthened: none of those fixes was proposed, measured, or is now prevented
  from regressing by anything in this repository, and the figures moved by a
  factor of two in one day with no distribution decision taken. `viral` is still
  non-deployable at 95% against the 90% ceiling.

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
  EV-REC and EV-CON scenarios. **Descoped 2026-08-14 (revision 15) — not built,
  not owed. See below.**

Phase 1 carries most of the value and almost none of the risk. It answers the
question no tool in this repository answers today — what does the effective
catalog cost right now, against an authoritative limit — and the figures in this
contract had to be measured by hand, twice, with conflicting results, precisely
because it did not exist. Phase 2 would automate an action a maintainer performs
rarely, and is where the whole partial-failure and concurrency apparatus lives.

**Acceptance closes at Phase 1 (revision 15).** The two remediations this program
actually ran — the six-skill cut and the CLI version-skew fix — were done by
hand, infrequently, cheaply, and correctly, against a machine-global catalog of
~26 skills that is now governed by phase 1's measurement plus recurring drift
checks (installed-versus-canonical, listing stability), declared cross-target
manifests (toolchain, project-skill wiring), and a manual
`sync.py --apply` after each merge. Against that realized problem size, the
staged applicator with its realization-identity, locking, concurrency, and
recovery machinery is disproportionate — high-risk mutation code standing in for
a rare, small, adequately-handled action. SC-07, SC-08, SC-13, the migration
half of SC-09, and the EV-REC/EV-CON scenarios are therefore **out of scope**:
they define what an applicator *would* owe if one is ever built, and no longer
gate acceptance. This is a scope reduction, recorded as one.

Phase 1 also supplies the missing referent for cross-target drift monitoring: a
drift monitor needs a declaration of intended membership to compare against,
and no such declaration exists until profiles do.
