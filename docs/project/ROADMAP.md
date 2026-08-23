# Skills Roadmap

Actionable improvement backlog for the skills catalog. This is a living snapshot, not a release contract.

Last updated from the [skills analysis](../archive/skill-analysis/skills-analysis-2026-3-07.md) (2026-03-07), with later completed highlights appended as shipped. Last reviewed 2026-08-22.

## In Progress

_The distribution-profiles entry below **completed** at spec revision 16 (2026-08-15,
`status: complete`) and is retained here as the program record; nothing else is
currently in progress. Its full history lives in the linked spec, plan, and
standing membership record._

| Item | Current State |
|------|---------------|
| Distribution profiles | **Contract complete at revision 16** (`status: complete`) in `docs/specs/2026-07-27-distribution-profiles-spec.md`, with execution history in `docs/plans/2026-07-31-distribution-profiles-plan.md` and the standing choice in `docs/project/GLOBAL-SKILL-MEMBERSHIP.md`. Phase 1 ships reviewed profile definitions, harness-specific budget policies, effective-catalog observation from real session records, byte-identical evidence, a CI measurement gate, and a machine-side drift checker. The checker fails closed when it cannot evaluate and reports saturation as a standing exit-`4` condition rather than accepting it through `--update`. Tasks 6–8 were descoped because routing fixtures were test polish, cross-target scheduling/transport belongs to deployment integration, and a wrapper entrypoint would not improve measurement correctness. Phase 2's applicator was also descoped: rare manual remediation did not justify high-risk locking, concurrency, and recovery machinery. |

## Completed Highlights

| Item | What Changed |
|------|-------------|
| Workstation health drift severity | `drift_check.py` stays strict by default but adds an opt-in health mode: same-build, non-saturating membership changes entirely outside local control remain fully reported as `state: notice` with exit `0`. Controlled membership, build, surface, ceiling, blindness, and saturation still fail. Scheduled machine-health consumers can opt into the mode without weakening interactive SessionStart reporting. |
| Review specialists ported from pr-review-toolkit | Two agent-agnostic review lenses that no dojo skill covered, converted from the `pr-review-toolkit@claude-plugins-official` Claude subagents. **`error-handling-review`** (1.0.0) hunts silent failures — empty/over-broad catch blocks, log-and-swallow, unjustified fallbacks, optional-chaining that hides faults, silent retry exhaustion — with a five-question interrogation and hidden-failure pattern catalog (`references/`), findings-first with a hidden-errors list per catch; the source agent's hardcoded Sentry/`logError`/`constants/errorIds.ts` conventions were rewritten to repo-declared conventions plus concrete TypeScript (Next.js/Supabase) and Python shapes. **`type-design-review`** (1.0.0) rates a new/changed type on encapsulation, invariant expression, usefulness, and enforcement (1–10 each), flags anti-patterns (anemic models, exposed mutable internals, doc-only invariants), and gives language tools for making illegal states unrepresentable. Both are deliberately-invoked specialist lenses with per-skill `evals/trigger-cases.json` routing fixtures (precision/recall 1.0 against `local-review`/`secure-code`/`api-design`), cross-referenced from `local-review`'s siblings. Plugin kept enabled for now; retiring it is a slimmed BACKLOG follow-up. |
| Release-tooling plumbing: bump auto-regen + health-join fix | `skill-evals` 1.5.0 plus a `scripts/` fix. `bump_skill_version.py` now regenerates `skills.json` and cascades the catalog after a successful non-dry-run bump (new `regenerate_manifest`, behind a `--no-regen` batch escape hatch), so a version bump no longer leaves generated artifacts stale for CI's `--check`; it no-ops cleanly when the skill is bumped outside a dojo checkout (global install). Reuses PR #72's manifest→catalog cascade. Separately, `skill_health_runtime.enrich_report` aggregated version-split health rows before the join (`aggregate_rows`): AgentMonitor keys rows by `(name, version)`, so a skill that bumped mid-window returned multiple rows and the old last-wins dict silently undercounted its invocation volume, mis-ranking it — now volume/misfires/eligible are summed, `neverFired` holds only if every row never fired, newest `lastInvokedAt` wins, and `misfireRate` is recomputed from totals. Closes two BACKLOG items. |
| High-risk depth: prove-the-handoff + legacy ID adoption | `write-plan` 2.5.0, `write-spec` 2.2.0, `test-strategy` 1.3.0. Two spec/plan BACKLOG items. **Prove the handoff, not the label** (`high-risk-readiness.md`, `authority-boundary-testing.md` + behavioral fixtures): force the three distinctions that decide whether readiness tables are evidence or labels — identity is not capture (name the freeze/copy/revalidate barrier), "idempotent" is not recovery (persisted intent/order/receipt/reconciler), enforcement cannot activate before its declaration/recovery/operator topology; and network boundaries need three separate proofs (policy tests, the connected peer from the real transport, a fixed public end-to-end control) so a loopback fixture never proves public-destination enforcement. **Incremental high-risk adoption**: `risk_profile: high` on a mature legacy artifact no longer forces a wholesale `SC-NN`/`EV-*-NN` retrofit — an id-less artifact uses named contract surfaces while structural/authority/readiness gates still apply, and once any ID exists the full class discipline is enforced so a partial retrofit fails rather than downgrading (both validators). `write-spec` protocol otherwise unchanged. |
| Plan-validator advisories: external tools + degenerate acceptance | `write-plan` 2.4.0. `collect_advisories` now flags a task that invokes a known-external binary (`tmux`/`git`/`npm`/`docker`/`codex`/`claude`/`gh`) with no `**Behavior Measured**` block, and two prose-detectable degenerate `Done When` forms — an `only X` partition asserted while a single branch exists, and an `every declared …` assertion over a possibly-empty collection — all on the non-blocking ADVISORY channel, none changing exit status. Verification Requirements gains the degeneracy gate ("assert each bullet against a case you believe is false") and the Behavior-Measured nudge; `seam-selection.md` carries the non-mechanical enumeration-is-not-the-invariant form and the cross-runner-seam note. Also folds in the deleted-cwd guard: `discover_repo_root` catches `FileNotFoundError` and degrades to the artifact's directory instead of crashing under Python 3.14. Closes two spec/plan BACKLOG items. |
| Runnable commands anchored to `<skill-dir>` (PR #68) | A skill's runnable commands resolve against the *user's* working directory, not dojo, so a `skills/<name>/scripts/…` path fails everywhere except a dojo checkout — which is exactly where it was authored and tested, hiding the bug. It was live in fourteen skills, including `write-plan`/`write-spec`, whose validator step had therefore been unrunnable in every repo but dojo (surviving in one consumer repo only because a same-named local `skills/` directory shadowed the error). Rewrote 67 command paths to `<skill-dir>/…` — operands included (`--config <skill-dir>/rules/`), not just executables — and added `tests/test_skill_script_paths.py`, which scans shell-fenced and inline commands, exempts `skill-evals`/`skill-creator` (dojo's own gates), and leaves prose *file* references alone. Convention now documented in `SKILL-BEST-PRACTICES.md`. |
| Standardizer audit at project scope | `skill-standardizer` 1.3.0 makes `--root` usable against a repository's own `.agents/skills` / `.claude/skills`. Two faults surfaced the first time it was pointed at one. A link resolving to **canonical** read as a local duplicate, because `already_linked` recognised only links to the *global copy* — and project scope exists for skills deliberately cut from the global root (PR #61's four design skills), which have no global copy to route through, so the requirement was impossible to satisfy rather than merely wrong. It went unnoticed only because that same absence means there is no global entry to duplicate. And a dangling symlink reported as a directory missing its `SKILL.md`, which is untrue of it; it is now `DANGLING_SKILL_LINK`, because the repair differs — recreate the link, not author a file. The case that prompted it was a project-scoped `compact-session` pointing at a skill in neither canonical nor any global root. |
| Standardizer foreign-directory allowlist | `KNOWN_NON_SKILL_DIRS` now exempts the Codex-owned `codex-primary-runtime` only in the global Codex root; repeatable `--ignore-dir` remains for one-off foreign directories. Regression coverage prevents the exemption from leaking into the canonical catalog. |
| Skill-standardizer CI coverage | CI invokes the formerly uncollected standardizer regression suite directly, with a mutation probe proving the job fails on a broken allowlist. The remaining pytest-port cleanup stays in `BACKLOG.md`. |
| Claude command-wrapper wiring | `gen_harness_adapters.py` links each skill's `commands/` files into local `.claude/commands/`, preserves namespacing, refuses collisions, prunes stale generated links, and leaves hand-authored files alone. Codex has no corresponding user-populated command directory, so it continues to consume the skills themselves. |
| Pre-execution artifact attribution | `brainstorming` 2.0.0 and the current `write-spec` / `write-plan` 2.0.0 contracts now require generated design summaries, specs, and plans to record the producing agent in `author:` frontmatter (for example, `gpt-5.6-sol`). Templates and command wrappers require resolving the placeholder; spec/plan validators enforce it for current-schema artifacts without invalidating unattributed legacy documents. |
| Risk-adaptive spec/plan readiness + authority testing | `write-spec` and `write-plan` 2.0.0 keep routine artifacts lean while high-risk work adds explicit risk/readiness metadata, stable contract/scenario IDs, authority and failure invariants, linked-spec proof traceability, evidence lifecycle, consumer closure, empirical Task 0 capability gates, and adversarial critique closure. Their validators harden only deterministic structure. `test-strategy` 1.1.0 adds conditional two-sided effective-runtime authority probes with host-observed evidence, leak-first red/green, indirect/ambient/state-class coverage, and proof invalidation. Ships focused validator regression tests, routing controls, and behavioral replay scenarios. |
| 48 curated skills | Spanning GitHub workflows, code review, design, platform integrations, knowledge management, autonomous-loop design, pre-execution (brainstorm → spec → plan), blind spots, research orchestration, and meta/skill tooling |
| Retune verify-before-complete trigger | `verify-before-complete` 1.1.0 narrows the description from the universal "about to say fixed/passing/done/complete" (coextensive with *finishing work*, so it over-fired after nearly every chunk, Codex especially) to four circuit-breaker cases — delegated/subagent work, high-risk changes, missing/stale/conflicting evidence, explicit audits — plus a `Skip When` fast-exit for routine changes the repo's own checks already cover. Adds a `trigger-cases.json` fixture (19/19; the high-risk completion claim now routes here, red→green) and a `behavioral-scenarios.md` documenting the semantic over-fire the lexical scorer cannot measure |
| Hook quality pipeline | Session-start catalog injection, pre/post-tool-use validation and manifest sync, spec + plan validation, git checks, structure checks, session retro reminder |
| Skill packaging and distribution | `.skill` zip format with validation |
| Command wrappers | Deterministic slash-style entrypoints |
| Skill installer | Supports Claude Code and Codex destinations |
| Machine-readable manifest | `skills.json` with auto-regeneration |
| Polyglot validation | Scripts compatible with both `python` and `python3` |
| Trim Obsidian skills | obsidian-markdown 647→284, obsidian-bases 678→259, obsidian-canvas 675→192 |
| Soften compound-docs | 527→119 lines, removed XML tags and redundant sections |
| Strict contract enforcement | Strict validator covers the manifest-backed skill catalog in CI |
| Trigger collision fixes | 78.6%→92.9%, discriminating name tokens, expanded stopwords |
| Wire command wrappers into Claude Code | `gen_harness_adapters.py` now links each skill's `commands/<rel>.md` into `.claude/commands/` (local-only, gitignored), so advertised slash commands (`/review`, `/quiz-change`, `/workflows:brainstorm`) actually resolve instead of 404-ing. Preserves nested namespacing, refuses cross-skill collisions, prunes stale links, never clobbers a hand-authored command; governed by the symlink phase so CI's `--skip-symlinks` run is unchanged |
| Skill version-bump helper | `bump_skill_version.py` performs the two-file edit the release check requires in one command — updates the SKILL.md `version` field and prepends a `## <version> - <date>` CHANGELOG heading (created if absent). Supports major/minor/patch or `--set`, `-m` for the entry, and `--dry-run`; reuses the checker's SemVer parser, refuses non-increasing/duplicate versions. Dogfooded to bump `skill-evals` to 1.2.0 |
| Fix scaffold/validation deadlock | The pre-write SKILL.md hook now validates the *payload a Write/Edit would produce* (via `hooks/validate_skill_payload.py`) instead of the on-disk file, and `init_skill.py` scaffolds `version: 1.0.0` — so a freshly scaffolded skill no longer fails the very edit that would make it valid. Validator import degrades to allow if `quick_validate` is unavailable |
| Trigger scorer rewrite | `run_trigger_evals.py` scoring is now TF-IDF cosine over stemmed, hyphen-split tokens (IDF replaces the hand-maintained stopword list); `--cases` asserts by ranking (winner must be an expected trigger, each `avoid` below it) with `--threshold` for the old model. Adds multi-trigger cases, an empty-trigger match-nothing floor, and a `known_hard` flag for lexical-ceiling collisions reported apart from real failures. Expanded collision fixture 46/58→58/58 with no assertions weakened; `skill-evals` 1.1.0 |
| Expanded trigger fixtures | 12→34 cases across 12 skill clusters |
| Rescore all skills | 23 skills bumped, 1 new entry (skill-evals), measured evidence |
| Rename json-canvas | → obsidian-canvas, updated all references |
| Extract system docs | Best practices, roadmap, contract extracted from analysis doc |
| Add test-strategy skill | Methodology skill with verification checklist, a catalog-expanding milestone before later additions |
| Add research-architect skill | Deep-research prompt engineering from composable skeleton blocks, pluggable execution routing, executor-independent report verification, postmortem memory; stakes-based trigger split with deep-research (bumped to 2.0.0 as its execution backend) |
| Harden research orchestration from first live run | `research-architect` 2.0.0 formalizes verified multi-run synthesis as stage 9, moves postmortem to stage 10, closes nine stage-seam findings, and hardens prompt linting; `deep-research` 2.1.0 replaces self-declared credibility with conservative URL-host registry scoring and explainable provenance fields |
| Act on the second live research run | `research-architect` 2.2.0 splits source ranking into reliability vs. edge-relevance × recency (one ranking biased "what works now" questions toward "already arbitraged away"), defaults stages 3/5/8 to fresh subagents, verifies nodes as they land, lints statistics seeded without a retrievable source, and adds `score_report.py` for the stage-8 structural pass — sampling weighted toward quantitative and attribution claims, the dominant failure mode across every executor profiled. Skeleton stayed net-zero on shipped instruction count (3 additions, 3 deletions). `deep-research` 2.2.0 registers on-chain explorers and code hosts, which previously scored as unknown domains. `skill-evals` 1.3.0 exempts append-only run memory from release-version checks |
| Act on the third live research run | `research-architect` 2.3.0 catches real-but-wrong-domain citations, forbids claims about un-ingested artifacts, makes merge structure checkable, and separates citation support from applicability. `score_report.py` now classifies direct/resolvable/opaque/absent coverage, resolves explicit `[n]` bibliography markers, refuses false hit rates when an export loses claim-to-URL linkage, and reports a usable-citation rate. Dated profiles capture the three external web DR executors without promoting one-run quirks into universal workflow rules |
| Preserve verified first-party research sources | `deep-research` 2.3.0 adds registry-owned root/subdomain matching for first-party model, coding-harness, protocol, and agent-framework documentation. Relevant verified priority sources no longer disappear solely because an aggregate lexical score falls below threshold; retained exceptions carry an explicit reason and confidence gap, while off-topic, duplicate, lookalike, and over-budget controls remain intact. |
| Harden spec/plan validation from cross-repo dogfooding | `write-spec` and `write-plan` 2.1.0 require meaningful acceptance magnitudes when trivial output could pass, define behavior-preserving reference oracles on result-deciding edge inputs, and map fixes across the whole defect/property class. Narrow validator advisories flag obvious weak checks without becoming schema gates. `write-plan` now resolves linked specs and modified files from the consumer plan's Git root, with an explicit override and documented no-Git fallback. |
| Design systems layer | Added `design-md` (Google `@google/design.md` CLI wrapper) and `design-critique` (closed 37-pattern slop catalog with structured findings) plus 5 Refero exemplars; sibling-skills footer convention disambiguates the four-skill design pipeline |
| Add diagnose skill | Adapted mattpocock's feedback-loop-first debugging discipline into a six-phase workflow with a `scaffold_feedback_loop.sh` template generator (7 loop kinds) and a HITL bash harness |
| Add caveman skill | Adapted mattpocock's ultra-compressed communication mode as a `reference`-typed skill — sticky output style with explicit Auto-Clarity Exception list and verification checklist |
| Catalog typing + sibling clusters | Reclassified `verify-before-complete`, `test-strategy`, `first-principles`, `agent-native-architecture` from workflow→reference (body shape is reference). Added `Disciplines`, `Security`, and `UI Automation` categories to FEATURES.md. Added `Sibling skills` footers to 12 clusters (~40 skills): GitHub flow, skill management, knowledge capture, pre-execution thinking, code review, disciplines, obsidian, image-gen, vercel/react, format-to-md, security, UI automation |
| Soften brainstorming | Removed XML hard-gate, added Boundaries/Verification/Resources |
| Enhance first-principles | Added engineering principles, tension resolution table, verification (110→141 lines) |
| Deduplicate fetch_issue.sh | Unified to `scripts/fetch_issue.sh`, symlinked from both skills |
| Upgrade template | Commented scaffold with all contract sections + authoring checklist (35→78 lines) |
| gemini-imagen parity | Updated to Nano Banana 2, added 4 extreme aspect ratios, drift warning, two-tier workflow, text rendering callout, sample-prompts.md |
| Add loop-design skill | Workflow skill on top of `/loop` and `/goal`: a go/no-go oracle gate, a portable loop blueprint, and a stdlib scaffolder that emits the loop bundle (`LOOP.md`, `verify.sh` oracle, `progress.md` state, `verifier.md` checker, `BINDINGS.md` for Claude Code/Codex/Actions/Ralph). The scaffolder refuses to emit a loop without a `done_when` oracle, turning "no oracle → not a loop" into a hard gate |
| Add api-design skill | Workflow skill for API/interface contract design and review across HTTP endpoints, event/stream contracts, typed DTO/service boundaries, CLI machine outputs, compatibility planning, and implementation handoff |
| Authoring + multi-harness pipeline (#19) | Optional `triggers:` frontmatter wired into trigger evals (`--from-triggers` self-route + collision check); opt-in shared-fragment composition (`gen_skill_docs.py`); per-skill harness adapters (`gen_harness_adapters.py`) — dir-level symlinks for `.claude/.agents/.agent` (`.agents` retired 2026-08-01) + colocated Codex `openai.yaml` (all skills), CI-enforced sync. Derived from the ECC/gstack/dimillian comparison in `docs/research/` |
| Published skill catalog | `gen_catalog.py` renders a self-contained searchable `docs/catalog/index.html` from `skills.json`; CI-checked (dimillian-derived). `generate_skills_manifest.py` now refreshes it in the same run (the catalog is derived entirely from the manifest), so a manual manifest regen can't leave it stale — the post-tool-use hook relies on that cascade rather than a separate call. `--no-catalog` opts out. |
| Skill health report | `skills_health.py` aggregates contract status + declared-trigger routing into a read-only per-skill report (ECC-derived) |
| Minimal rules/ tier | `rules/` for standing always-follow conventions (skill-authoring, doc-hygiene), composable into SKILL.md via `rules/<name>` includes; referenced from AGENTS.md/CONTRIBUTING (ECC-derived) |
| AI-slop prose scan | `slop_scan.py` — high-precision deterministic linter for AI-slop tells in skill prose + core docs, CI-gated; complements the visual `design-critique` skill (gstack-derived) |
| Opt-in behavioral evals | `behavioral_evals.py` — drives a real local agent to verify declared triggers route to the right skill; gated on `DOJO_BEHAVIORAL_EVALS=1`, never in CI (gstack-derived) |
| Split write-spec into contract + plan | Closed the seam-first finding structurally: `write-spec` is now a mechanism-free **contract** (WHAT must be true — problem, falsifiable end-state, success criteria, evaluation), and the new `write-plan` owns the **execution** plan (task breakdown, files, steps, seam selection). Establishes `brainstorm (docs/design/) → spec (docs/specs/) → plan (docs/plans/)`; each layer has its own schema validator + on-write hook; brainstorming reshaped into a direction-level feeder; legacy plan-shaped specs migrated to `docs/plans/`. Follow-up: rename the cross-repo lifecycle-archive script to learn about `docs/design/` |
| Skill SemVer releases | Every cataloged skill declares `version: 1.0.0` as the baseline release; `skills.json` and the generated catalog expose per-skill versions; `check_skill_versions.py` enforces future release-relevant edits against a git base with required changelog entries |
| Skill feedback loop (phase 2) | `skills_health.py` gained an opt-in runtime layer (`skill_health_runtime.py`) that consumes AgentMonitor's `GET /api/v2/analytics/skills/health` and ranks dojo skills by trustworthy trigger signal — never-fired first, then a rarely-fired band, then invocation volume — with misfire shown labeled experimental and never in the sort key. `--findings` emits paste-ready BACKLOG blocks for never-fired skills (writes nothing); honest non-zero exit on unreachable/malformed AgentMonitor; the default run stays network-free and byte-identical. Closes the measure→improve loop AgentMonitor's phase-1 health endpoint opened |
| Add blind-spots skill | Closes the human side of the pre-execution stack: existing skills ground the *agent*, none help the *human* keep ownership of an agent-made change. Adapted from Anthropic's "Finding your unknowns" field guide — the blind-spot-pass and quiz patterns, since brainstorming/write-spec/write-plan already own the interview, contract, and plan patterns. Two independently invokable modes, both calibrated to what the user already knows: scope (`/understand-change`: entry points, call paths, blast radius, and explicitly-named unknown unknowns) and quiz (`/quiz-change`: reads the real diff, briefs the user on what changed, then asks one question per turn about the consequences the briefing left open). Deliberately diverges from the source on gating — no score, no pass/fail, no merge verdict, no unsolicited invocation. Ships a focused routing fixture (6 positive, 8 sibling negative controls, 1 generic-explanation control) plus frozen behavioral scenarios replayed by a human, since no runner here can drive a multi-turn conversation |
| Grounded spec → plan handoff | `write-spec` now resolves contract-affecting questions before planning and records bounded uncertainty honestly; `write-plan` requires exact target evidence, resolve-now risk triage, and test-discovery proof. Advisory-only validator nudges surface missing grounding without changing a valid plan's exit status; both skills released as 1.1.0 with regression coverage. |

## Cross-Cutting Findings

### Verbosity Issues

| Skill | Status | Notes |
|-------|--------|-------|
| ~~obsidian-bases~~ | Done | 678→259 lines, function catalog extracted to `references/functions.md` |
| ~~obsidian-markdown~~ | Done | 647→284 lines, removed standard Markdown syntax |
| ~~compound-docs~~ | Done | 527→119 lines, stripped XML ceremony and redundant sections |
| ~~obsidian-canvas~~ | Done | 675→192 lines, examples extracted to `references/examples.md` |
| first-principles | Open | ~200 lines of abstract methodology without concrete examples |
| agent-native-architecture | Open | 14 reference files -- some overlap between architecture-patterns.md and agent-execution-patterns.md |

### Overly Strict Language

| Skill | Example | Status |
|-------|---------|--------|
| ~~compound-docs~~ | "STRICT ENFORCEMENT", 7-step mandatory workflow | Done -- rewritten without XML ceremony |
| verify-before-complete | "Iron Law", "NEVER claim completion" | Keep -- appropriate for its purpose |
| brainstorming | "MUST use this before any creative work" | Open -- too broad for simple changes |

**Guidance:** Use "should" over "MUST" for advisory skills; reserve "MUST" for safety-critical behaviors.

### Gaps and Missing Skills

| Gap | Description | Suggested Skill |
|-----|-------------|----------------|
| Database | No skill for schema design, migration planning, or query optimization | `db-design` |
| Documentation | No skill for README generation, API docs, or changelog management | `docs-generator` |
| Accessibility | Mentioned in web-design-guidelines but no dedicated skill | `a11y-audit` |
| Performance Profiling | vercel-react-best-practices covers React perf but no general profiling | `perf-profiler` |
| Dependency Management | No skill for auditing, updating, or managing dependencies | `dep-audit` |

### Duplicate/Overlapping Concerns

1. **gpt-imagen + gemini-imagen**: Same workflow pattern with different APIs. Could share a common skill layer with provider-specific scripts.
2. **vercel-deploy + vercel-preview-logs**: Could be one skill with deploy + diagnose commands.
3. **obsidian-markdown + obsidian-bases + obsidian-canvas**: Three separate reference skills. Already trimmed and disambiguated; merging is low priority since trigger routing works (f1 1.00 for all three).

### Resource Distribution

_Counts are from the 2026-03-07 analysis (~44-skill baseline) and are approximate; the catalog is now 48 skills. Treat as directional until recomputed._

| Resource Type | Count | Skills With | Skills Without |
|---------------|-------|-------------|----------------|
| Scripts | 30+ | 16 skills | 28 skills |
| References | 40+ | 20 skills | 24 skills |
| Templates/Assets | 20+ | 11 skills | 33 skills |
| Commands | 15+ | 10 skills | 34 skills |

Many skills are instruction-only with no supporting resources. The highest-rated skills consistently have scripts, references, and templates.

## Priority Improvements

### High Impact

1. **Merge Vercel deploy skills** -- Combine vercel-deploy and vercel-preview-logs into one skill with deploy + diagnose commands

### Medium Impact

2. **Bundle guidelines in web-design-guidelines** -- Don't depend on external URL fetch

### Low Impact

3. **Add caching to deep-research** -- Avoid re-researching previously answered questions
4. **Add example specs to write-spec** -- Show what good specs look like
5. **LLM-based trigger scoring** -- Add semantic scoring tier for the 10 accepted lexical-limit pairs

## Planned / Open Areas

- Expanded test coverage for hook scripts and validation logic.
