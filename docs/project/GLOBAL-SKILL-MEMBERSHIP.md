# Global Skill Membership

Which dojo skills are installed into the machine-global roots
(`~/.agents/skills`, symlinked from `~/.codex/skills`), why, and what it costs.

This is a living decision record, not a backlog item and not a plan. The backlog
holds work someone should do; this holds a standing choice and the measurement
behind it. `profiles/` holds the reviewed *definitions* of what a profile
contains; this file records what a specific machine actually carries and why it
diverges from any of them.

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
| find-skills | 71 | 1 | 0 | 71.0 | — |
| handoff | 84 | 2 | 0 | 42.0 | — |
| gpt-imagen | 81 | 2 | 0 | 40.5 | — |
| obsidian-canvas | 79 | 2 | 0 | 39.5 | — |
| blind-spots | 140 | 2 | 2 | 35.0 | — |
| audit-skill | 105 | 3 | 0 | 35.0 | — |
| gemini-imagen | 66 | 2 | 0 | 33.0 | — |
| web-design-guidelines | 100 | 4 | 0 | 25.0 | design |
| design-critique | 109 | 2 | 3 | 21.8 | design |
| api-design | 104 | 6 | 0 | 17.3 | engineering |
| obsidian-bases | 86 | 5 | 1 | 14.3 | — |
| secure-code | 128 | 11 | 0 | 11.6 | engineering |
| frontend-design | 81 | 6 | 1 | 11.6 | design |
| vercel-react-best-practices | 110 | 9 | 1 | 11.0 | — |
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

**2026-08-12 — the rest of the low-use tier is deliberately held.** Cutting only
these two leaves the target over the deployable ceiling. That is a knowing
choice: a skill that is cheap to reinstall but expensive to miss is worth paying
for until the cost is felt.

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
- **`design-critique` + `web-design-guidelines`** — decide as a pair, not
  individually. 209 tokens and nine consultations combined, and their
  descriptions exist partly to disambiguate each other ("for rule-compliance…use
  web-design-guidelines instead" / "for visual taste…use design-critique
  instead"). Two skills that must explain how they differ cost twice and split
  their own routing signal.

## Reproducing this measurement

Cost model and observation live in `scripts/profiles/`; the authoritative Codex
surface is the session rollout, never a live probe. Re-derive the ceiling by
saturation after any Codex update — two renders with different entry counts that
both clip must total the same number, and that number is the limit.

Zero use is only evidence for a skill that is **installed**. An uninstalled skill
shows zero because it was never offered.
