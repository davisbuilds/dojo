# Global Skill Membership

Which dojo skills are installed into the machine-global roots
(`~/.agents/skills`, symlinked from `~/.codex/skills`), why, and what it costs.

This is a living decision record, not a backlog item and not a plan. The backlog
holds work someone should do; this holds a standing choice and the measurement
behind it. `profiles/` holds the reviewed *definitions* of what a profile
contains; this file records what a specific machine actually carries and why it
diverges from any of them.

## Which harness this binds

**One root, two budgets.** `~/.agents/skills` is read by both harnesses, so
membership is shared — but the two score it very differently:

| Harness | Budget | Installed dojo set | Binding? |
|---|---|---|---|
| Codex (build 0.146.0) | 4,000 tokens | ~78% before the unavoidable 24% | **yes — over the ceiling** |
| Claude Code @ 1M | 40,000 chars | 41–58% | no |
| Claude Code @ 200k | 8,000 chars | 2.07–2.91× | yes, but off-path |

So every cut recorded here is driven by **Codex**, and Claude Code at the 1M
window — the only one in use — is unaffected either way. The 200k column is a
real exposure on a path nobody currently takes; if that changes, the same
membership decisions apply with a tighter budget, since Claude's own levers
(description trimming, symlink topology) were measured and cannot reach it.

Do not read a cut here as a judgement that a skill is unhelpful in Claude Code.
It is a statement that a shared root has to fit the smaller of two ceilings.

## Why membership is the binding constraint

Codex renders a skill listing into every session with a hard token ceiling and
clips descriptions to fit — mid-word, unmarked. Trimming descriptions cannot
reach the ceiling because most of the listing is not dojo's to trim. Membership
is the only remaining lever. See
`docs/specs/2026-07-27-distribution-profiles-spec.md` for the contract and
`ops/docs/harness-decision-register.md` R34–R37 for how this was established.

## The budget (build 0.146.0, measured 2026-08-12)

| | Tokens | % of 4,000 |
|---|---|---|
| Ceiling (observed by saturation) | 4,000 | 100% |
| Deployable ceiling (90%) | 3,600 | 90% |
| Unavoidable — Codex bundled, local plugins, alias table | 959 | 24% |
| **Room for dojo skills** | **2,641** | **66%** |
| Installed dojo skills (31) | **3,129** | 78% |
| **Over by** | **488** | |

The ceiling is a property of the **CLI build** — 0.143.0/0.144.x saturated at
5,440, and 0.145.0 changed it. Re-derive after a Codex update rather than
trusting this table.

Account-synced ChatGPT connectors add demand outside this budget and outside
local control; a local `enabled = false` on one is inert. Removal in the ChatGPT
web app is the only lever.

## Measured cost and use

**This table is the measurement that informed the decisions below — it is the
state *before* any removal.** Rows since removed are marked; see Decisions for
the current position.

Cost is the rendered listing line, from untruncated source, in Codex's own
arithmetic — calibrated to 0.00% against a live render. Codex use counts
*sessions that consulted the skill* across 317 rollouts, matched only inside
tool-call inputs; the listing block and directory listings name every skill and
would otherwise report the whole catalog as used. Claude use is lifetime
dispatch count. The two are independent rankings, not one scale.

| Skill | Tok | Codex | Claude | Tok/use | Group |
|---|---|---|---|---|---|
| research-architect | 179 | 1 | 1 | 89.5 | research |
| screenshot | 75 | 1 | 0 | 75.0 | — |
| ~~find-skills~~ *(removed)* | 71 | 1 | 0 | 71.0 | — |
| handoff | 84 | 2 | 0 | 42.0 | — |
| gpt-imagen | 81 | 2 | 0 | 40.5 | — |
| obsidian-canvas | 79 | 2 | 0 | 39.5 | — |
| blind-spots | 140 | 2 | 2 | 35.0 | — |
| ~~audit-skill~~ *(removed)* | 105 | 3 | 0 | 35.0 | — |
| gemini-imagen | 66 | 2 | 0 | 33.0 | — |
| ~~web-design-guidelines~~ *(removed)* | 100 | 4 | 0 | 25.0 | design |
| ~~design-critique~~ *(removed)* | 109 | 2 | 3 | 21.8 | design |
| api-design | 104 | 6 | 0 | 17.3 | engineering |
| obsidian-bases | 86 | 5 | 1 | 14.3 | — |
| secure-code | 128 | 11 | 0 | 11.6 | engineering |
| ~~frontend-design~~ *(removed)* | 81 | 6 | 1 | 11.6 | design |
| ~~vercel-react-best-practices~~ *(removed)* | 110 | 9 | 1 | 11.0 | — |
| create-cli | 109 | 13 | 0 | 8.4 | engineering |
| diagnose | 116 | 15 | 0 | 7.7 | **core** |
| session-retro | 103 | 15 | 1 | 6.4 | knowledge |
| obsidian-markdown | 89 | 9 | 5 | 6.4 | knowledge |
| write-plan | 115 | 13 | 12 | 4.6 | **core** |
| playwright | 72 | 14 | 1 | 4.8 | — |
| skill-creator | 79 | 21 | 1 | 3.6 | skill-authoring |
| deep-research | 104 | 26 | 6 | 3.3 | research |
| local-review | 86 | 28 | 7 | 2.5 | **core** |
| skill-standardizer | 69 | 18 | 8 | 2.7 | skill-authoring |
| write-spec | 115 | 23 | 18 | 2.8 | **core** |
| test-strategy | 150 | 55 | 0 | 2.7 | **core** |
| brainstorming | 93 | 37 | 12 | 1.9 | **core** |
| first-principles | 88 | 55 | 7 | 1.4 | **core** |
| verify-before-complete | 143 | 103 | 0 | 1.4 | **core** |
| **installed total** | **3,129** | | | | **31 skills** |

`core` occupies the whole bottom of this table. The eight reviewed core members
are the eight most-used installed skills, from an independent signal — the set
was chosen before any of this was measured.

## Decisions

**2026-08-12 — remove `audit-skill` and `find-skills`.** 176 tokens, four
consultations between them across 317 Codex sessions and zero Claude dispatches.
Neither is an overlay anchor, so no profile definition changes. Removed from
`~/.agents/skills` and the `~/.codex/skills` symlink; both remain in the canonical
catalog and reinstall from dojo.

**2026-08-12 — remove the design group and `vercel-react-best-practices`
(400 tokens).** `design-critique`, `web-design-guidelines`, `frontend-design`,
and `vercel-react-best-practices`. The reasoning is *scope*, not disuse:
these fire on UI and React/Next.js work, which happens in a few known
repositories rather than in every session on the machine. A skill whose triggers
are project-shaped belongs in project scope. `design-critique` and
`web-design-guidelines` were also the mutually-disambiguating pair flagged below
— removing both together avoids keeping one and leaving its description still
pointing at a sibling that is gone.

**Resulting position: 26 skills, 2,553 tokens against 2,641 of room — +88
headroom.** The installed set fits the deployable ceiling for the first time,
down 576 tokens (18%) from 3,129.

**Consequence to know.** These four are now unavailable in an arbitrary
directory. They remain in the canonical catalog, and dojo's own checkout exposes
them to Claude Code through `.claude/skills`. To restore one for a specific
project, add it to that project's skills root rather than to the global root —
that is the point of the cut. `~/.agents/.removed-20260812/` holds copies, though
the canonical source is dojo.

## Verified position after the cuts (2026-08-12, build 0.146.0)

Measured from a live `codex-tui` rollout in `~/Dev/podsave` — the same directory
as the pre-cut baseline, so the only variable is the removals.

| | Before (08-06) | After (08-12) |
|---|---|---|
| Listed entries | 56 | **50** |
| dojo demand | 3,129 | **2,553** |
| Total true demand | 4,936 (137%) | **4,554 (114%)** |
| dojo entries clipped | 50 of 56 | **20 of 50** |
| Characters removed | 6,317 | **2,186** |
| Longest description | 207 | **248** |

The cost model predicted 2,553 and the render charged 2,553. Two-thirds of the
damage is gone and thirty skills that were being severed now render in full.

**dojo is now the compliant part of the listing:**

| Source | Tokens | % of 4,000 | Controlled from |
|---|---|---|---|
| dojo-managed | 2,553 | 64% | this repository |
| plugin | 806 | 20% | Codex desktop app update |
| connector | 708 | 18% | ChatGPT account |
| harness-bundled | 366 | 9% | Codex itself |
| alias table | 121 | 3% | — |
| **total** | **4,554** | **114%** | |

**The remaining 554-token overage cannot be closed from this repository.** dojo
fits its 2,641 allowance with 88 to spare; the overage is entirely the 1,880
tokens of plugins, connectors, and bundled entries. Cutting further would mean
deleting skills in use to make room for `openai-primary-runtime` and account
connectors. **Stop cutting dojo here.**

Also confirmed: the listing still saturates at exactly 4,000 on a **third model**
(`gpt-5.6-luna`), and Codex emitted **no shortening warning** at 114% while
clipping 20 skills — the warning's false negative, reproduced a third time.

## Runtime-plugin disable works (2026-08-12, controlled)

`documents`, `pdf`, `presentations`, and `spreadsheets` disabled in
`config.toml`; `template-creator` left enabled as a control, `sites` and
`visualize` untouched as a second control in a different marketplace. Result:
**the four vanished from the listing and all three controls remained.**

So **plugin-level `enabled = false` works for a configured marketplace plugin**,
unlike the `@openai-curated-remote` connector keys, which are inert. The
distinction is whether a local marketplace owns the plugin — account-synced
connectors have none, and only removal in the ChatGPT web app governs them.

## Position on build 0.147.0

Codex upgraded mid-test, so two variables moved at once. The controls above
isolate the disable; the build change shows up separately and is larger:

| | 0.146.0 (pre-cut) | 0.146.0 (post-cut) | 0.147.0 (post-disable) |
|---|---|---|---|
| Entries | 56 | 50 | **45** |
| Charged | 4,000 | 4,000 | **4,843** |
| Saturated | yes | yes | **no** |
| dojo clipped | 50 of 56 | 20 of 50 | **2 of 30** |
| Characters removed | 6,317 | 2,186 | **21** |
| Longest description | 207 | 248 | **622 — the source maximum** |

**The clipping is effectively over.** The longest description in the catalog
renders at full length, and the render is in `absolute` mode with no alias
table, which Codex only chooses when everything fits.

**The 0.147.0 ceiling is not yet derivable** and that is the correct answer, not
a gap: nothing saturates, so no render discloses the limit. All that is known is
that it is **at least 4,843**, up from 4,000. Re-derive when something clips
again.

Current attribution: dojo 2,547 (53%), connectors 1,102 (23%), Codex bundled 607
(13%), local plugins 593 (12%) — total 4,849.

> **Tooling note.** 0.147.0 reports the *symlink* path for global skills where
> 0.146.0 reported the resolved target. The classifier keyed on the target, so
> every dojo skill silently became `foreign` on the first 0.147.0 session — the
> totals still summed correctly. Fixed by resolving before classifying, plus an
> alarm when an implausible share falls through to `foreign`. A path shape is a
> constant scoped to a version.

## Candidates not yet decided

- **`research-architect`** — 179 tokens, the single most expensive skill in the
  catalog, two consultations in 317 sessions. It is a `research` overlay anchor,
  so removing it changes what that overlay means.
- **`obsidian-canvas`** — 39.5 tokens/use, worse than several already flagged.
  Easy to miss when ranking by absolute cost rather than cost per use.
- **The two image skills** — `gpt-imagen` (81) and `gemini-imagen` (66) total 147
  tokens for four consultations, **while Codex bundles its own `imagegen`** at
  `~/.codex/skills/.system/imagegen`. Declaring them equivalent was deliberately
  withheld (register R33) because dojo's pins `gpt-image-2` and exposes masking
  and batch that the bundled description does not claim — a wrong equivalence
  silently removes a selected skill. That reasoning governs *declaration*; it
  does not settle whether a Codex session needs two dojo image skills beside a
  bundled one.
- **Project-scoping the four removed skills.** Removal from global is done;
  deciding *which* repositories should carry them is not. Their descriptions
  still cross-reference each other ("for rule-compliance…use
  web-design-guidelines instead"), so a project that installs one and not its
  pair leaves a dangling pointer in the listing.

## Reproducing this measurement

Cost model and observation live in `scripts/profiles/`; the authoritative Codex
surface is the session rollout, never a live probe. Re-derive the ceiling by
saturation after any Codex update — two renders with different entry counts that
both clip must total the same number, and that number is the limit.

Zero use is only evidence for a skill that is **installed**. An uninstalled skill
shows zero because it was never offered.
