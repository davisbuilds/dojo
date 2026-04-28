# External Skill Audit — 2026-04-28

Comprehensive evaluation of five external skill repositories against dojo's
current 48-skill catalog. Goal: identify what is worth porting, adapting, or
borrowing — and what is noise.

> **Status:** proposal. Nothing has been ported. Verdicts below need user
> sign-off before any new SKILL.md or extension lands.

## Scope

| Repo | Author | Shape |
|---|---|---|
| [mattpocock/skills](https://github.com/mattpocock/skills) | Matt Pocock | Curated skill pack (~17 skills across engineering / productivity / misc) |
| [google-labs-code/design.md](https://github.com/google-labs-code/design.md) | Google Labs | Format **specification** + CLI (`@google/design.md`) — not a skill pack |
| [garrytan/gstack](https://github.com/garrytan/gstack) | Garry Tan / YC | Full agent-engineering product (~32 skills, custom browser, telemetry, GBrain integration) |
| [Dimillian/Skills](https://github.com/Dimillian/Skills) | Thomas Ricouard | 16 skills, heavily Apple/Swift-focused with cross-platform multi-agent patterns |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | Addy Osmani | 20 lifecycle skills (define → ship) packaged as marketplace plugin |

## Rubric

Each external skill scored 1–5 on six dimensions:

1. **Novelty vs. dojo** — does it cover ground we don't already have?
2. **Trigger quality** — would the description actually fire in dojo's catalog?
3. **Progressive disclosure** — does it respect context budget?
4. **Determinism** — bundled scripts/CLI vs. pure prose ("vibes")?
5. **Maintenance cost** — what would it cost dojo to keep this fresh?
6. **Author signal** — credibility/track record of upstream curator.

A composite **Verdict** of `Adopt` (port largely as-is), `Adapt` (extract pattern,
reshape into dojo's contract), or `Skip` (overlap, low signal, or not portable).

---

## Repo 1 — mattpocock/skills (MIT)

Strong opinions, small skills, all built around two ideas: (a) a project-level
shared vocabulary lives in `CONTEXT.md` and `docs/adr/`, and (b) every skill
should reference it. License: MIT. Author signal high (TypeScript educator,
Total TypeScript).

| Skill | Novelty | Trigger | Disclosure | Determinism | Maint | Verdict |
|---|---|---|---|---|---|---|
| `tdd` | 2 | 4 | 4 | 2 | 2 | **Skip** — overlaps `test-strategy` |
| `grill-me` | 4 | 4 | 5 | 2 | 1 | **Adapt** — fold "interview, one Q at a time, recommend an answer" pattern into `brainstorming` |
| `grill-with-docs` | 5 | 4 | 4 | 2 | 3 | **Adapt** — extract the `CONTEXT.md` + ADR domain-awareness pattern as a small reference; lifts existing `brainstorming` and `first-principles` |
| `diagnose` | **5** | 5 | 4 | 3 | 2 | **Adopt** — net-new "build a deterministic feedback loop *before* debugging" workflow |
| `improve-codebase-architecture` | **5** | 4 | 4 | 2 | 3 | **Adopt** — Ousterhout-flavored "deepening opportunities" review (deep modules, deletion test, seams). No equivalent in dojo |
| `zoom-out` | 3 | 3 | 5 | 1 | 1 | **Skip** — 9-line micro-skill; better folded into `first-principles` as a one-liner |
| `to-prd` | 2 | 4 | 4 | 2 | 2 | **Skip** — overlaps `writing-plans` + `gh-fix-issue` |
| `to-issues` | 2 | 4 | 4 | 2 | 2 | **Skip** — overlaps `writing-plans` |
| `github-triage` | 2 | 4 | 4 | 3 | 2 | **Skip** — overlaps `gh-triage-issues` |
| `caveman` | **5** | 5 | 5 | 1 | 1 | **Adopt** — token-compression communication mode. Genuinely novel; dojo has nothing like it |
| `write-a-skill` | 2 | 4 | 3 | 2 | 2 | **Skip** — `skill-creator` is more rigorous |
| `git-guardrails-claude-code` | 3 | 3 | 4 | 5 | 2 | **Skip** — partially covered by dojo's `pre-tool-use-git-push-protected-branch.sh` and `hookify` |
| `setup-pre-commit`, `migrate-to-shoehorn`, `scaffold-exercises` | 1 | 2 | 4 | 4 | 3 | **Skip** — too project-specific |

**Top picks:** `diagnose`, `caveman`, `improve-codebase-architecture`,
+ `CONTEXT.md`/ADR domain-awareness reference.

---

## Repo 2 — google-labs-code/design.md (Apache-2.0)

**Not a skill pack.** It is a format spec + CLI: `@google/design.md lint|diff|export|spec`.
Defines a YAML-frontmatter + Markdown format for design tokens (colors, typography,
spacing, components, do's/don'ts), with a contrast-ratio-aware linter and a
W3C DTCG / Tailwind exporter.

| Asset | Novelty | Determinism | Verdict |
|---|---|---|---|
| `DESIGN.md` format | **5** | n/a | **Adopt as new skill** `design-md` |
| `npx @google/design.md` CLI | **5** | **5** | bundle as the skill's deterministic backend |

Dojo already has `frontend-design`, `web-design-guidelines`, `theme-factory`, and
`obsidian-bases` (all format-aware skills). None of them speak the DESIGN.md
format. A thin `design-md` skill that wraps the CLI for `lint`, `diff`, and
`export --format tailwind|dtcg` slots cleanly into the catalog and pairs with
`frontend-design`.

**Caveat:** spec is at `version: alpha`, expect format churn. Skill should pin
to a CLI version and surface a "regenerate when spec moves" note.

---

## Repo 3 — garrytan/gstack (MIT)

A full software-factory product, not a portable skill pack. ~32 skills, but
they are tightly coupled to gstack's bundled binaries (`gstack-config`,
`gstack-analytics`, `gstack-taste-update`), the GStack Browser (Chromium fork),
GBrain MCP server, ngrok-based agent pairing, and a per-project taste
profile that decays 5%/week. The README itself opens with a 1,237-contributions
GitHub-screenshot flex from the YC president — author signal is real, but
adoption demands buying into the whole stack.

Most "skills" are 1,000–2,000 line auto-generated `SKILL.md` files (`/office-hours`
is 1,978 lines, `/cso` is 1,358, `/retro` is 1,619) with bundled telemetry that
writes to `~/.gstack/analytics/skill-usage.jsonl` on every run. This violates
dojo's "context is sacred" principle and our skill-contract size norms.

| Skill | Novelty | Trigger | Disclosure | Determinism | Maint | Verdict |
|---|---|---|---|---|---|---|
| `office-hours` (forcing-question brainstorming) | 4 | 4 | 1 | 3 | 5 | **Skip** — overlaps `brainstorming` + `first-principles`; size is disqualifying |
| `cso` (OWASP + STRIDE + supply chain) | 3 | 4 | 1 | 3 | 5 | **Skip** — `secure-code` + `repo-hardening` cover this |
| `retro` (weekly engineering retro) | 3 | 4 | 1 | 3 | 5 | **Skip** — `session-retro` covers this |
| `learn` (persistent learning store) | 3 | 4 | 1 | 3 | 5 | **Skip** — `self-improve` + `compound-docs` cover this |
| `careful` (destructive-command guardrails) | 3 | 4 | 5 | **5** | 2 | **Adapt** — extend `pre-tool-use-git-push-protected-branch.sh` into a broader destructive-command hook; pattern is good, implementation simple |
| `qa` / `design-shotgun` / `design-html` / `pair-agent` | 4 | 4 | 1 | 2 | 5 | **Skip** — depend on bundled GStack Browser, not portable |
| `autoplan` / `plan-ceo-review` / `plan-eng-review` | 3 | 4 | 1 | 3 | 5 | **Skip** — overlaps `writing-plans` |

**Net take:** gstack is interesting to study but a poor source of portable
skills. The single take-home pattern is `careful` — broaden dojo's existing
git-push hook into a destructive-command guard (rm -rf /, DROP TABLE, kubectl
delete in prod, etc.) with an allowlist for known-safe paths. Keep it as a
hook, not a skill.

---

## Repo 4 — Dimillian/Skills (MIT)

16 skills, ~70% Apple-platform-specific (SwiftUI, Swift Concurrency, Tuist,
SPM packaging, iOS debugging) — irrelevant to dojo's general-purpose skill
tooling. The remaining ~30% are interesting cross-platform multi-agent
patterns.

| Skill | Novelty | Trigger | Disclosure | Determinism | Maint | Verdict |
|---|---|---|---|---|---|---|
| `swift-concurrency-expert` / `swiftui-*` (×6) | n/a | n/a | n/a | n/a | n/a | **Skip** — out of scope for dojo |
| `ios-debugger-agent`, `macos-spm-app-packaging`, `macos-menubar-tuist-app`, `app-store-changelog` | n/a | n/a | n/a | n/a | n/a | **Skip** — Apple-specific |
| `bug-hunt-swarm` | **5** | 5 | 4 | 3 | 2 | **Adopt** — read-only 4-agent parallel root-cause investigation. Dojo has no parallel investigation pattern |
| `review-swarm` | 4 | 5 | 4 | 3 | 2 | **Adapt** — fold the "4 parallel reviewers + main agent ranks" pattern into `local-review` as an optional `--swarm` mode |
| `orchestrate-batch-refactor` | 3 | 4 | 4 | 3 | 3 | **Skip** — overlaps `autonomous-engineering` (slfg variant) |
| `project-skill-audit` | **5** | 4 | 4 | 4 | 2 | **Adapt** — pattern of "audit *real session history* before recommending new skills" complements `find-skills` and `skill-evals` but isn't covered. Dojo's analog should read git log + recent transcripts (Codex memory equivalent) |
| `review-and-simplify-changes` | 2 | 4 | 4 | 3 | 2 | **Skip** — overlaps `simplify` + `local-review` |

**Top picks:** `bug-hunt-swarm` (Adopt), `review-swarm` pattern (Adapt into
`local-review`), `project-skill-audit` pattern (Adapt — recommend new dojo
skills based on real usage signals).

---

## Repo 5 — addyosmani/agent-skills (MIT)

20 lifecycle skills wrapped in 7 slash commands (`/spec`, `/plan`, `/build`,
`/test`, `/review`, `/code-simplify`, `/ship`). Polished, well-organized,
references the Google SWE book and Hyrum's Law. But: the skills are
essentially a curated *engineering textbook* expressed as SKILL.md files.
Heavy overlap with dojo's existing catalog, and most descriptions start
with weak triggers like "Delivers changes incrementally" or "Refines ideas
iteratively" rather than the scenario-rich descriptions dojo's contract
encourages.

| Skill | Novelty | Trigger | Disclosure | Determinism | Maint | Verdict |
|---|---|---|---|---|---|---|
| `idea-refine` | 2 | 3 | 4 | 1 | 2 | **Skip** — overlaps `brainstorming` |
| `spec-driven-development` | 2 | 4 | 4 | 1 | 2 | **Skip** — overlaps `writing-plans` |
| `planning-and-task-breakdown` | 2 | 4 | 4 | 1 | 2 | **Skip** — overlaps `writing-plans` |
| `incremental-implementation` | 3 | 3 | 4 | 1 | 2 | **Skip** — overlaps `verify-before-complete` + `test-strategy`; "thin vertical slice" idea worth a one-line addition to `writing-plans` |
| `test-driven-development` | 2 | 4 | 4 | 1 | 2 | **Skip** — overlaps `test-strategy` |
| `context-engineering` | 4 | 4 | 4 | 2 | 3 | **Skip** — interesting but reads as CLAUDE.md guidance, not a triggered skill; dojo handles this via per-project AGENTS.md |
| `source-driven-development` | **4** | 4 | 4 | 2 | 2 | **Adapt** — "every framework decision must cite official docs" pattern is genuinely useful; could extend `deep-research` with a "framework-doc-cite" mode, or fold into a new `cite-sources` reference |
| `frontend-ui-engineering` | 2 | 4 | 4 | 1 | 3 | **Skip** — overlaps `frontend-design` + `vercel-react-best-practices` + `web-design-guidelines` |
| `api-and-interface-design` | 3 | 4 | 4 | 1 | 2 | **Skip** — partially overlaps `create-cli`; rest is generic prose |
| `browser-testing-with-devtools` | 3 | 4 | 4 | 2 | 3 | **Skip** — overlaps `playwright` |
| `debugging-and-error-recovery` | 3 | 4 | 4 | 1 | 2 | **Skip** — mattpocock's `diagnose` is sharper |
| `code-review-and-quality` | 2 | 4 | 4 | 1 | 2 | **Skip** — overlaps `local-review` + `code-review-agents` |
| `code-simplification` | 2 | 4 | 4 | 1 | 2 | **Skip** — overlaps `simplify` |
| `security-and-hardening` | 2 | 4 | 4 | 1 | 2 | **Skip** — overlaps `secure-code` + `repo-hardening` |
| `performance-optimization` | 2 | 4 | 4 | 1 | 2 | **Skip** — generic; overlaps `vercel-react-best-practices` |
| `git-workflow-and-versioning`, `ci-cd-and-automation`, `shipping-and-launch` | 2 | 3 | 4 | 1 | 2 | **Skip** — overlap dojo's `gh-*` + `vercel-deploy` clusters |
| `deprecation-and-migration` | 4 | 4 | 4 | 1 | 2 | **Skip-but-flag** — pattern ("code as liability", compulsory vs advisory deprecation) is good. Probably not worth a full skill, could become a one-page reference |
| `documentation-and-adrs` | 3 | 4 | 4 | 1 | 2 | **Skip** — overlaps `session-retro` + `compound-docs`; ADR pattern better captured via mattpocock's `grill-with-docs` adaptation |
| `references/*-checklist.md` | 4 | n/a | 5 | 4 | 2 | **Borrow** — performance / security / accessibility / testing checklists are useful as reference files (link-in, don't fork) |

**Net take:** addyosmani is a thoughtful, well-cited collection but it largely
reproduces ground dojo already covers. Two narrow extracts (`source-driven-development`
pattern; the four reference checklists) are worth borrowing. License is MIT,
so we can vendor checklists with attribution.

---

## Recommended Adoptions (ruthless cut)

The bar: net-new behavior dojo can't already produce, with a clear trigger,
and either deterministic backing or sharply-scoped prose. Anything that
"looks useful" but overlaps existing skills is rejected.

### A. New skills (4)

| Skill | Source | What it does | Why net-new |
|---|---|---|---|
| `caveman` | mattpocock | Token-compression communication mode — drops articles, hedges, pleasantries while keeping technical accuracy. Persists across turns until "stop caveman" | dojo has no equivalent; ~75% token savings on long sessions |
| `diagnose` | mattpocock | Feedback-loop-first debugging discipline: build deterministic pass/fail signal *before* hypothesizing | `verify-before-complete` is a completion gate, not a debugging workflow |
| `improve-codebase-architecture` | mattpocock | Ousterhout-style "deepening" review — find shallow modules, propose deep replacements via the deletion test | dojo has review/simplify/refactor skills but none focused on module depth |
| `bug-hunt-swarm` | dimillian | Read-only 4-subagent parallel root-cause investigation, ranked diagnosis | dojo has `autonomous-engineering` (build) and `local-review` (review) but no parallel *investigation* primitive |
| `design-md` | google-labs | Wrap `npx @google/design.md` for lint / diff / export-to-tailwind on DESIGN.md files | net-new format support; pairs with `frontend-design` |

### B. Extensions to existing skills (3)

| Existing skill | Extension | Source |
|---|---|---|
| `brainstorming` | Add "ADR + CONTEXT.md persistence" mode that updates project vocabulary inline, plus the "interview one question at a time, *recommend an answer per question*" pattern | mattpocock `grill-me` / `grill-with-docs` |
| `local-review` | Add optional `--swarm` mode that runs four read-only review subagents in parallel, then ranks findings | dimillian `review-swarm` |
| `find-skills` | Pair with a new lightweight `dojo-skill-audit` that scans recent transcripts/commits and recommends skills based on real friction (vs. generic ideation) | dimillian `project-skill-audit` |
| `deep-research` | Add a "source-cited" mode that requires every framework-specific recommendation to cite an official-doc URL | addyosmani `source-driven-development` |

### C. Reference borrows (1)

| Borrow | From | Where it lives |
|---|---|---|
| Performance / security / accessibility / testing checklists | addyosmani `references/` | Vendored under `skills/<consumer>/references/` with attribution comment, not as a separate skill. Consumers: `secure-code`, `web-design-guidelines`, `vercel-react-best-practices`, `test-strategy` |

### D. Hook extension (1)

| Hook | Extension | Source |
|---|---|---|
| `pre-tool-use-git-push-protected-branch.sh` | Generalize into a destructive-command hook that warns on `rm -rf /`, `DROP TABLE/DATABASE`, `git reset --hard`, `kubectl delete` (with `node_modules`/`.next`/`dist` allowlisted) | gstack `careful` |

### E. Skip wholesale

- gstack `office-hours`, `cso`, `retro`, `learn`, `qa`, `pair-agent`, `autoplan`, `plan-*`, `design-shotgun`, `design-html`, etc. (overlap + non-portable)
- addyosmani's other 18 skills (overlap with dojo's catalog)
- mattpocock's `tdd`, `to-prd`, `to-issues`, `github-triage`, `write-a-skill`, `zoom-out`, `setup-pre-commit`, `migrate-to-shoehorn`, `scaffold-exercises`, `git-guardrails-claude-code`
- dimillian's Apple-platform skills, `orchestrate-batch-refactor`, `review-and-simplify-changes`

### Estimated effort

- 4 new skills × ~2hr each = ~8hr
- 4 skill extensions × ~1hr each = ~4hr
- Checklist borrows + hook extension = ~2hr
- Total: ~14hr for first pass; iteration likely

---

## License & attribution

| Source | License | Attribution path |
|---|---|---|
| mattpocock/skills | MIT | README acknowledgements + `metadata.upstream` in skill frontmatter |
| google-labs-code/design.md | Apache-2.0 | README acknowledgements + LICENSE.txt for any vendored code |
| garrytan/gstack | MIT | README acknowledgements (we're only borrowing one hook idea) |
| Dimillian/Skills | MIT | README acknowledgements + `metadata.upstream` in skill frontmatter |
| addyosmani/agent-skills | MIT | README acknowledgements + comment header on vendored checklists |

All five licenses permit derivative works with attribution. No GPL-style
copyleft concerns. README acknowledgements section already exists at
`README.md:141`; we extend it.

---

## Top 5 dojo self-critiques

Independent of the external audit, observed while comparing dojo against
five other curators:

### 1. Description quality is uneven across the catalog

Several existing skills have weak triggers — examples that would not reliably
fire from a user prompt:
- `screenshot`: "Use when the user explicitly asks for a desktop or system screenshot" — fine
- `playwright`: "Use when the task requires automating a real browser from the terminal" — generic
- `verify-before-complete`: "Use when you are about to state work is fixed, passing, done, or complete" — relies on agent self-awareness, not user phrasing
- `template`: literally a starter template, but its description suggests it might fire on user prompts about scaffolding

**Fix:** pass through `skill-evals` strict triggers report on the whole catalog; tighten descriptions to scenario-rich phrasing matching the contract.

### 2. Planning/brainstorming/research overlap is real

`brainstorming`, `writing-plans`, `first-principles`, `deep-research` all
operate in adjacent territory. Adding mattpocock's `grill-me` patterns risks
making this worse unless we explicitly draw boundaries between them
(brainstorm = WHAT, plan = HOW, first-principles = WHY, research = WHO-says,
grill = test-the-plan).

**Fix:** add a short routing table to `docs/system/FEATURES.md` clarifying which
skill handles which phase, then update each description to point at sibling
skills for adjacent phases.

### 3. GitHub workflow micro-skills proliferation

`gh-commit-push-pr`, `gh-fix-issue`, `gh-review-pr`, `gh-triage-issues` — four
skills, each ~one verb. Defensible (description-as-trigger is sharper that way)
but worth re-examining whether one parameterized `gh-workflow` skill with mode
arguments would have higher leverage.

**Fix:** measure first — check if all four actually fire on real user prompts in
recent transcripts, before consolidating.

### 4. Vercel skill cluster is imported wholesale

Five `vercel-*` skills (composition-patterns, react-best-practices,
react-native-skills, deploy, preview-logs) share a flavor that doesn't fully
match dojo's enforced contract style. They're useful, but a contract-pass
would tighten them.

**Fix:** run `validate_skill_contract.py --strict` on each and fix the gaps;
tag them in `metadata.upstream` so it's clear they're imported.

### 5. Missing: a feedback-loop-first debugging skill

`verify-before-complete` is a completion gate. There's nothing in dojo that
matches mattpocock's `diagnose` — the discipline of *constructing a
deterministic, agent-runnable pass/fail signal as the first move on a hard
bug*. This is the single highest-leverage gap surfaced by the audit.

**Fix:** part of the Adopt list above.

---

## Open questions for user

1. Adopt order — start with `caveman` + `diagnose` (lowest cost, immediate value), then `improve-codebase-architecture` + `bug-hunt-swarm`, then `design-md`?
2. For extensions — extend in place or fork (e.g., `brainstorming` → `brainstorming` + `grill-with-docs` as a separate skill)?
3. Should the destructive-command hook be opt-in (env var) or always-on?
4. Is the `dojo-skill-audit` adaptation worth building now, or after we have more transcript history to audit against?

---

## Appendix — clones used

All five repos cloned at depth 1 to `~/Dev/tmp/skills/` for analysis. Re-clone
if revisiting; tmp/ is treated as scratch per parent `AGENTS.md`.

```
~/Dev/tmp/skills/
├── addyosmani/
├── dimillian/
├── google-design-md/
├── gstack/
└── mattpocock/
```
