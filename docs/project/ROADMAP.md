# Skills Roadmap

Actionable improvement backlog for the skills catalog. This is a living snapshot, not a release contract.

Last updated from the [skills analysis](../archive/skill-analysis/skills-analysis-2026-3-07.md) (2026-03-07), with later completed highlights appended as shipped. Last reviewed 2026-07-11.

## Completed Highlights

| Item | What Changed |
|------|-------------|
| 55 curated skills | Spanning GitHub workflows, code review, design, platform integrations, knowledge management, autonomous-loop design, pre-execution (brainstorm → spec → plan), and meta/skill tooling |
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
| Expanded trigger fixtures | 12→34 cases across 12 skill clusters |
| Rescore all skills | 23 skills bumped, 1 new entry (skill-evals), measured evidence |
| Rename json-canvas | → obsidian-canvas, updated all references |
| Extract system docs | Best practices, roadmap, contract extracted from analysis doc |
| Add test-strategy skill | Methodology skill with verification checklist, a catalog-expanding milestone before later additions |
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
| Authoring + multi-harness pipeline (#19) | Optional `triggers:` frontmatter wired into trigger evals (`--from-triggers` self-route + collision check); opt-in shared-fragment composition (`gen_skill_docs.py`); per-skill harness adapters (`gen_harness_adapters.py`) — dir-level symlinks for `.claude/.agents/.agent` + colocated Codex `openai.yaml` (54/54 skills), CI-enforced sync. Derived from the ECC/gstack/dimillian comparison in `docs/research/` |
| Published skill catalog | `gen_catalog.py` renders a self-contained searchable `docs/catalog/index.html` from `skills.json`; rebuilt by the post-tool-use hook, CI-checked (dimillian-derived) |
| Skill health report | `skills_health.py` aggregates contract status + declared-trigger routing into a read-only per-skill report (ECC-derived) |
| Minimal rules/ tier | `rules/` for standing always-follow conventions (skill-authoring, doc-hygiene), composable into SKILL.md via `rules/<name>` includes; referenced from AGENTS.md/CONTRIBUTING (ECC-derived) |
| AI-slop prose scan | `slop_scan.py` — high-precision deterministic linter for AI-slop tells in skill prose + core docs, CI-gated; complements the visual `design-critique` skill (gstack-derived) |
| Opt-in behavioral evals | `behavioral_evals.py` — drives a real local agent to verify declared triggers route to the right skill; gated on `DOJO_BEHAVIORAL_EVALS=1`, never in CI (gstack-derived) |
| Split write-spec into contract + plan | Closed the seam-first finding structurally: `write-spec` is now a mechanism-free **contract** (WHAT must be true — problem, falsifiable end-state, success criteria, evaluation), and the new `write-plan` owns the **execution** plan (task breakdown, files, steps, seam selection). Establishes `brainstorm (docs/design/) → spec (docs/specs/) → plan (docs/plans/)`; each layer has its own schema validator + on-write hook; brainstorming reshaped into a direction-level feeder; legacy plan-shaped specs migrated to `docs/plans/`. Follow-up: rename the cross-repo lifecycle-archive script to learn about `docs/design/` |
| Skill SemVer releases | Every cataloged skill declares `version: 1.0.0` as the baseline release; `skills.json` and the generated catalog expose per-skill versions; `check_skill_versions.py` enforces future release-relevant edits against a git base with required changelog entries |
| Skill feedback loop (phase 2) | `skills_health.py` gained an opt-in runtime layer (`skill_health_runtime.py`) that consumes AgentMonitor's `GET /api/v2/analytics/skills/health` and ranks dojo skills by trustworthy trigger signal — never-fired first, then a rarely-fired band, then invocation volume — with misfire shown labeled experimental and never in the sort key. `--findings` emits paste-ready BACKLOG blocks for never-fired skills (writes nothing); honest non-zero exit on unreachable/malformed AgentMonitor; the default run stays network-free and byte-identical. Closes the measure→improve loop AgentMonitor's phase-1 health endpoint opened |
| Grounded spec → plan handoff | `write-spec` now resolves contract-affecting questions before planning and records bounded uncertainty honestly; `write-plan` requires exact target evidence, resolve-now risk triage, and test-discovery proof. Advisory-only validator nudges surface missing grounding without changing a valid plan's exit status; both skills released as 2.0.0 with regression coverage. |

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
| autonomous-engineering | Chains 7+ skills sequentially | Open -- fragile, one failure cascades |

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
2. **code-review-agents**: dhh-rails-reviewer and kieran-rails-reviewer overlap in domain. Consider merging or clearly differentiating.
3. **vercel-deploy + vercel-preview-logs**: Could be one skill with deploy + diagnose commands.
4. **obsidian-markdown + obsidian-bases + obsidian-canvas**: Three separate reference skills. Already trimmed and disambiguated; merging is low priority since trigger routing works (f1 1.00 for all three).

### Resource Distribution

_Counts are from the 2026-03-07 analysis (~44-skill baseline) and are approximate; the catalog is now 54 skills. Treat as directional until recomputed._

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

2. **Add auto-detection to code-review-agents** -- Select relevant reviewers based on tech stack
3. **Bundle guidelines in web-design-guidelines** -- Don't depend on external URL fetch

### Low Impact

4. **Add caching to deep-research** -- Avoid re-researching previously answered questions
5. **Add rule testing to hookify** -- Let users validate rules before activation
6. **Add example specs to write-spec** -- Show what good specs look like
7. **Consolidate agent-native-architecture references** -- Reduce overlap between architecture-patterns.md and agent-execution-patterns.md
8. **LLM-based trigger scoring** -- Add semantic scoring tier for the 10 accepted lexical-limit pairs

## Planned / Open Areas

- Guarded promotion from `self-improve` proposals into harness-level canaries or rollback-aware improvement loops.
- Expanded test coverage for hook scripts and validation logic.
