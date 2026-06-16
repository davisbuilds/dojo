# External Skill-Repo Comparison: ECC, gstack & dimillian vs. dojo

**Date:** 2026-06-16
**Scope:** Deep review of three external skill repositories compared to dojo, to surface what dojo could leverage, what each does better/worse, and concrete next steps.
**Status:** Research only — no building yet.

### Repos reviewed (pointers)

| Ref | Local clone | Upstream | Shape |
|---|---|---|---|
| **ECC** | `_clones/skills/ECC/` | `github.com/` (Everything Claude Code, v2.0.0) | Breadth platform — 271 skills, 9-harness fan-out |
| **gstack** | `_clones/skills/gstack/` | `github.com/garrytan/gstack` (v1.58.x) | Depth stack — ~70 mega-skills + Bun CLI toolkit |
| **dimillian** | `_clones/skills/dimillian/` | `github.com/Dimillian/Skills` | Curated personal — 16 Codex-native skills |
| dojo | `dojo/` (this repo) | local | Curated library — 53 skills, contract + hooks |

> All file paths cited within a given Part are relative to that repo's clone root above (e.g. in Part 1, `scripts/skills-health.js` means `_clones/skills/ECC/scripts/skills-health.js`).

---

## Part 1 — ECC ("Everything Claude Code") vs. dojo

### What each repo actually is

**ECC** is a sprawling, commercial-grade **distribution platform**: 271 skills, 92 commands, 67 agents, per-language rule sets, MCP configs, and a full Node.js tooling layer (install profiles, doctor, dashboards, observability, release gates). Its defining feature is **multi-harness fan-out** — one source tree compiled into `.claude/`, `.codex/`, `.opencode/`, `.cursor/`, `.gemini/`, `.qwen/`, `.kiro/`, `.trae/`, `.zed/` adapters. It's a product (versioned 2.0.0, sponsors, CHANGELOG, marketplace plugin manifests).

**dojo** is a focused, **curated skill library**: 53 skills, markdown-first, with a tight quality contract enforced by hooks + CI. It optimizes for *authoring discipline and context economy*, not breadth or distribution.

These are different categories of project. dojo is a workshop; ECC is a factory with a storefront. The useful question is not "which is better" but "which factory machinery is worth importing into the workshop without becoming a factory."

### Evaluation criteria

Authoring quality bar · context economy · validation/enforcement · multi-harness portability · distribution/install · testing · security model · observability/health · maintainability at scale · discoverability.

### What dojo could leverage from ECC (ranked)

1. **Skill-health / quality dashboard (`scripts/skills-health.js`, `doctor.js`)** — *highest value.* ECC tracks per-skill success rate, failures, amendments, version drift, and renders a dashboard. dojo's `skill-evals/` validates *structure* (contract pass/fail) but has no runtime *health* signal — which skills actually fire, get used, or regress. A lightweight `skills-health.py` aggregating trigger-eval results + usage over time would serve dojo's "description is the trigger" principle with evidence instead of intuition.
2. **Per-language / per-domain "rules" layer (`rules/common/*.md` + `rules/<lang>/`)** — ECC separates *always-follow guidelines* (coding-style, testing, security, git-workflow, per-language conventions) from *skills* (on-trigger workflows). dojo collapses everything into skills. A small `rules/` tier (or a `reference`-type convention) lets dojo encode standing conventions without burning a trigger slot — and reduces trigger-collision pressure, which dojo's own docs flag.
3. **Harness-adapter compliance as a *checked* invariant (`scripts/harness-adapter-compliance.js --check`)** — dojo claims to be "agent-agnostic" and ships `.claude/`, `.agents/`, `.agent/` skill dirs, but only **2 of 53 skills** (`brainstorming`, `writing-plans`) are mirrored there. The agnostic promise is mostly unbacked. ECC's pattern — single source of truth + a `--check` script that fails CI on drift — is what dojo needs to either honor or formally drop the claim.
4. **`doctor`-style drift diagnosis (`doctor.js`)** — reports missing/drifted managed files for an install target. dojo's `skill-standardizer` + `skills-lock.json` gesture at this; a single `doctor` entrypoint ("is my install consistent?") is cleaner.
5. **Governance/observability hooks (opt-in)** — ECC's `governance-capture.js` (secrets, policy violations, approval requests) and `observe-runner.js` are **async, env-gated** PreToolUse hooks. dojo's hooks are all blocking-validation; an opt-in, non-blocking observation hook would feed #1 without slowing the agent.
6. **Bilingual docs as a pattern** (`README.zh-CN.md`, `docs/zh-CN/`, `docs/ja-JP/`) — likely out of scope, noted for completeness.

### What ECC does better

- **Multi-harness portability, for real** — the adapter pipeline is the thing dojo gestures at but doesn't deliver.
- **Distribution & install ergonomics** — install profiles/components/modules with JSON schemas, `install.sh`/`install.ps1`, plugin marketplace manifests, uninstall. dojo assumes you work *in* the repo.
- **Breadth** — per-language reviewers/build-resolvers, 14 MCP configs, domain skills dojo will never have.
- **Observability & ops maturity** — dashboards, cost tracking, release approval gates, session inspection.
- **Testing surface** — real `tests/` tree (Python + JS) vs. dojo's single manifest test.
- **Security as documented practice** — `the-security-guide.md` (28KB), `SECURITY.md`, `gateguard` skill + hook, IOC scanning. dojo has `audit-skill`/`secure-code` skills (better-packaged) but no repo-level security posture doc.

### What dojo does better (don't regress)

- **Context economy & authoring discipline** — `skill-contract-v1.md` with typed skills (`workflow`/`reference`), required vs. recommended checks, CI strict-mode enforcement is *more rigorous per skill* than ECC. ECC frontmatter is thin (`name`, `description`, `metadata.origin`) with no enforced contract.
- **Signal-to-noise** — 53 curated skills you can reason about vs. 271 of varying quality. ECC's git log shows constant firefighting ("remove broken routing reference to non-existent skill," "sync skill counts after rebase").
- **Hook hygiene** — dojo's hooks are readable single-purpose bash. ECC's `hooks.json` inlines a ~600-char minified Node bootstrap into *every* hook entry — clever but borderline unauditable. Don't copy.
- **Honest scope** — dojo docs largely match behavior (except the multi-harness gap). ECC's AGENTS.md asserts "80%+ coverage required" / "all tests pass" as success metrics the repo doesn't visibly meet.
- **Progressive-disclosure rigor** — dojo formalizes the 3-tier loading model; ECC relies on it implicitly.

### What ECC does worse (cautionary)

1. Skill sprawl / dilution across 271 skills; some are thin stubs.
2. Unauditable hook bootstrap (minified inline JS in `hooks.json`).
3. Tooling sprawl — ~50 scripts, dual package managers (`yarn.lock` *and* `package-lock.json`), a 40KB `ecc_dashboard.py` at repo root.
4. Aspirational docs — AGENTS.md describes an ideal that isn't enforced.
5. Root-level clutter — ~30 top-level files/guides; 89KB README.

### Recommendations (ECC-derived)

1. **Resolve the multi-harness gap first.** Either adopt the adapter-compliance `--check` pattern and back the agnostic claim across all skills, *or* delete `.agent/`/`.agents/` and scope the claim to "harness-portable markdown." The current state misleads.
2. **Add a `skills-health` report** (Python, in `skill-evals/`) aggregating trigger-eval pass rates + usage over time.
3. **Introduce a thin `rules/` (or `reference`-skill) tier** for standing conventions.

Skip ECC's install platform, dashboards, and inline-bootstrap hooks — they solve distribution-at-scale problems dojo doesn't have, and importing them would cost the signal-to-noise that makes dojo good.

---

## Part 2 — gstack vs. dojo (and vs. ECC)

### What gstack actually is

**gstack** (`github.com/garrytan/gstack`, v1.58.x) is a **deeply-integrated, CLI-backed agent operating environment** shipped as ~70 heavyweight skills. Unlike ECC's breadth-of-thin-prompts, gstack is depth-of-thick-playbooks: individual `SKILL.md` files run **50–100KB+** (`review/SKILL.md` is 103KB, `qa` 80KB, `ship` 76KB). Each skill is the prose layer over a real Bun/TypeScript toolkit — `bin/` (75 executables), `lib/` (worktrees, redaction, decision memory), 272 Bun test files, a 64KB `setup` installer, a persistent semantic-memory subsystem ("gbrain", Supabase-backed), and an evals harness. Versioned per-skill (`version:` in frontmatter), with an **894KB CHANGELOG** and **139KB TODOS.md**. Where ECC is a factory-with-storefront, gstack is a single opinionated, batteries-welded-in stack.

### Distinctive mechanisms (the high-signal parts)

1. **Templated SKILL.md generation.** Skills are authored as `SKILL.md.tmpl` and compiled to `SKILL.md` via `bun run gen:skill-docs` (`scripts/gen-skill-docs.ts`). Generated files carry an `<!-- AUTO-GENERATED from SKILL.md.tmpl — do not edit directly -->` marker. Templates use includes (`{{PREAMBLE}}`, `{{BASE_BRANCH_DETECT}}`) and compose from a `sections/` directory with its own `manifest.json` and per-section `.md.tmpl` files. This is a real DRY/composition layer for skill authoring — shared preambles and sections live once and fan into many skills.
2. **Explicit `triggers:` frontmatter array.** In addition to `description`, each skill lists literal trigger phrases (`review this pr`, `code review`, `check my diff`). Triggers are first-class data, not prose buried in the description.
3. **Section "carving" (in-skill progressive disclosure) with behavioral enforcement.** Large skills are split into sections the agent Reads on demand via a "STOP-Read" path. A `CARVE_GUARDS` registry + periodic eval tier runs a *real* agent and asserts it actually Read the required sections at runtime ("registered ⇒ asserted" is structural). This is progressive disclosure taken one level deeper than dojo's whole-file model — and it's *tested behaviorally*, not just structurally.
4. **Mature evals harness.** `eval:bg`, `eval:compare`, `eval:summary`, `eval:watch`, tiered gates (`test:gate`, `test:periodic`), and **multi-model evals** (`test:codex`, `test:gemini`). Background-running, comparison across runs/models, cost-scoped to changed skills.
5. **AI-slop scanning in CI** (`slop`, `slop:diff`, `slop-scan.config.json`).
6. **Redaction engine** (`lib/redact-*.ts`) — secret/PII redaction for audit logs.
7. **gbrain** — cross-session semantic decision memory (decision log + semantic search, Supabase backend), far beyond dojo's file-based `MEMORY.md`.
8. **Rich frontmatter** — `preamble-tier`, `version`, `allowed-tools`, `triggers` (vs. dojo's `name`/`description`/`type`).

### What dojo could leverage from gstack (ranked)

1. **SKILL.md templating + section composition (`.tmpl` → generated, with AUTO-GENERATED markers)** — *highest authoring-infra value.* Even keeping skills small, dojo repeats boilerplate (preambles, trigger blocks, contract-required sections) by hand across 53 skills. A `gen-skill-docs`-style compile step with shared includes would DRY that up and make the contract easier to satisfy mechanically. Pairs naturally with dojo's existing `skill-standardizer`.
2. **Explicit `triggers:` frontmatter** — complements dojo's "description is the trigger" principle and makes dojo's existing `run_trigger_evals.py` first-class: evals would assert against declared triggers instead of inferring them. Low-cost, high-leverage given the infra already exists.
3. **Behavioral eval tier** — dojo's `skill-evals` checks structure + trigger collisions statically. gstack's pattern of running a real agent and asserting it took the intended path (e.g. invoked the right skill, read the right section) is the natural next rung for dojo's eval ladder. Adopt the *idea* (behavioral assertion, cost-scoped to changed skills), not gstack's Bun harness.
4. **Section carving** — directly relevant the moment any dojo skill outgrows the <5k-word budget; lets a skill stay disclosed-on-demand internally rather than splitting into sibling skills.
5. **slop-scan in CI** — automated AI-slop detection complements dojo's `design-critique` / `web-design-guidelines` skills by catching slop in *authored content* (skill prose, docs) at commit time.
6. **Per-skill `version:`** — cheap provenance; helps the health/drift tooling proposed in Part 1.

### What gstack does better than dojo

- **Authoring infrastructure** — templating, section composition, generation markers. dojo hand-writes everything.
- **Eval & test maturity** — 272 tests, background/multi-model evals, behavioral guards. dojo has one manifest test + static skill-evals.
- **Operational integration** — real CLI toolkit, persistent semantic memory, redaction, decision logging.
- **Per-skill versioning & changelog discipline.**

### What dojo does better than gstack

- **Context economy** — this is gstack's biggest violation of dojo's core principle. A 103KB `SKILL.md` is the antithesis of "<5k words / context is sacred." Carving mitigates it at runtime, but the authored surface is enormous and the per-invocation **bash preamble** (session tracking, update checks, branch detect) adds token + latency tax to *every* skill use.
- **Low coupling / portability** — dojo skills are portable markdown. gstack skills are welded to gstack's CLI, gbrain, Supabase, and Bun; you adopt the whole stack or nothing.
- **Auditability & onboarding** — dojo is readable end-to-end in an hour. gstack's 894KB CHANGELOG, 139KB TODOS, 64KB `setup`, and 100KB skills are not human-auditable in any practical sense.
- **Honest, enforced contract** — dojo's typed `skill-contract-v1` with CI strict mode is a clearer quality bar than gstack's implicit conventions.

### gstack vs. ECC (how the two large repos compare)

They are **opposite extremes**, and dojo sits between them:

| Dimension | ECC | gstack |
|---|---|---|
| Philosophy | Breadth — 271 thin, portable prompt-skills | Depth — 70 thick, integrated playbook-skills |
| Portability | High (prose fans out to 9 harnesses) | Low (welded to gstack CLI/gbrain/Bun) |
| Distribution | Modular install profiles/components, marketplace | Monolithic `setup` — take the whole stack |
| Testing | Moderate (Python+JS tests) | Heavy (272 Bun tests, multi-model evals) |
| Authoring infra | Thin frontmatter, no composition | Templating + section composition + carving |
| Memory | `memory-persistence` hooks | gbrain (semantic, Supabase) |
| Coherence | Lower (sprawl; constant catalog firefighting) | Higher (one opinionated philosophy) |
| Context economy | Better per-skill (small files) | Worse per-skill (huge files, mitigated by carving) |

- **gstack does better than ECC:** depth, testing/eval rigor, authoring composition, internal coherence.
- **ECC does better than gstack:** multi-harness portability, modular/optional install, per-skill independence, discoverability of individual capabilities.

### Net guidance from gstack

Borrow gstack's **authoring infrastructure** (templating/composition, explicit triggers, behavioral evals, slop-scan, per-skill versioning) — these strengthen dojo *without* growing it. Reject gstack's **scale and coupling** (mega-skills, mandatory CLI/memory stack, per-invocation preambles, changelog/TODO sprawl) — they directly oppose dojo's context-economy and portability advantages.

---

## Part 3 — dimillian ("Dimillian/Skills") vs. dojo

### What dimillian actually is

**dimillian** (`_clones/skills/dimillian/`, `github.com/Dimillian/Skills`) is a **curated personal skill collection** — 16 focused, self-contained, markdown-first skills by the Ice Cubes / IceCubesApp developer. It is the **closest sibling to dojo** of the three: small, single-purpose skills, each a `SKILL.md` with optional `references/`. Its niche is Apple-platform depth (`_clones/skills/dimillian/swift-concurrency-expert/`, `swiftui-liquid-glass/`, `swiftui-performance-audit/`, `macos-spm-app-packaging/`) plus a few portable workflow skills (`review-swarm/`, `bug-hunt-swarm/`, `orchestrate-batch-refactor/`, `project-skill-audit/`). It is explicitly **Codex-native** (README: "place these skill folders under `$CODEX_HOME/skills`").

### Distinctive mechanisms

1. **Lightweight per-skill harness interface file** — every skill ships `agents/openai.yaml` (e.g. `_clones/skills/dimillian/review-swarm/agents/openai.yaml`) carrying `interface.display_name`, `short_description`, and a `default_prompt` with `$skill-name` invocation syntax. This is the *minimal* multi-harness adapter: no build step, no fan-out generator — just a small sidecar YAML per harness. Contrast ECC's compiled adapters (`_clones/skills/ECC/scripts/harness-adapter-compliance.js`) and gstack's template generation (`_clones/skills/gstack/scripts/gen-skill-docs.ts`).
2. **Auto-generated GitHub Pages catalog.** `_clones/skills/dimillian/scripts/build_docs_index.py` walks every `SKILL.md`, extracts frontmatter, and writes `_clones/skills/dimillian/docs/skills.json`, which a static site (`docs/index.html` + `app.js` + `styles.css`) renders as a browseable, published catalog (`dimillian.github.io/Skills/`). Regeneration is wired via a **git pre-commit hook** (`_clones/skills/dimillian/scripts/git-hooks/pre-commit`) that rebuilds and `git add`s the manifest.
3. **Codeless multi-agent swarm pattern.** `review-swarm/SKILL.md` and `bug-hunt-swarm/SKILL.md` orchestrate four read-only parallel sub-agents plus a main-agent synthesis pass — pure prompt orchestration, no supporting code, fully portable.
4. **References as curated domain knowledge** — e.g. `swift-concurrency-expert/references/` bundles WWDC/concurrency notes; `swiftui-liquid-glass/references/liquid-glass.md`. Skills are thin; the depth lives in curated reference docs.
5. **Meta-skill: `project-skill-audit/`** — analyzes a project's past Codex sessions, memory, and conventions to recommend new/updated skills (analogous to dojo's `self-improve` + `find-skills`).

### What dojo could leverage from dimillian (ranked)

1. **Published, auto-generated discoverability catalog** — dojo already emits `skills.json` but has no browseable, published view. dimillian's pattern (`build_docs_index.py` → `docs/skills.json` → static site, regenerated by hook) is a near-zero-dependency way to ship a public/local skill catalog. dojo's existing `post-tool-use-regen-manifest.sh` already does the regen half; adding a static renderer is small.
2. **Lightweight per-skill harness-interface sidecar** — directly relevant to the **multi-harness gap** flagged in Part 1. Of the three approaches (ECC compiled fan-out, gstack templating, dimillian sidecar YAML), the **dimillian sidecar is the best fit for dojo's scale** — it honors the agnostic claim per-skill without a build platform. Worth evaluating as the concrete mechanism behind shortlist item #1.
3. **Swarm orchestration as a portable, codeless pattern** — compare against dojo's `code-review-agents` skill; dimillian's read-only-swarm-plus-synthesis is a clean reference.

### What dimillian does better than dojo

- **Published discoverability** (the Pages catalog) — dojo has none.
- **Lightest-weight multi-harness story** that actually ships (sidecar YAML per skill).
- **Domain depth** for Apple platforms (different niche, but a model for reference-doc-backed expertise).

### What dimillian does worse than dojo

- **No quality contract or validation.** Frontmatter is `name` + `description` only, parsed by a naive line-splitter in `scripts/build_docs_index.py` (`split(":")` — not real YAML; would mangle complex values). No typed skills, no CI, no eval harness. dojo's `skill-contract-v1` + `skill-evals` are far stronger.
- **No lifecycle hooks** beyond the docs-rebuild pre-commit. dojo's 8-hook pipeline enforces invariants dimillian leaves to discipline.
- **Narrow, single-author scope** — minimal reusable infra; most value is in the Apple-domain content.

### Where dimillian sits among the three

dimillian is the **minimalist** corner of the spectrum: ECC = breadth platform, gstack = depth stack, **dimillian = curated personal collection** — the same category as dojo. The takeaway: benchmark dojo against **dimillian for taste/curation and lightweight publishing**, while borrowing heavier *infrastructure* from ECC and gstack. Notably, dimillian proves the multi-harness claim can be honored *cheaply* (sidecar files) rather than via a build system.

---

## Consolidated next-steps shortlist (all three repos)

Ordered by value-to-effort for dojo specifically. Source repo in parentheses.

1. **Resolve the multi-harness gap** (ECC for the `--check` invariant; **dimillian** for the lightweight sidecar mechanism) — adopt per-skill harness sidecars + a compliance check, or scope the claim. *Correctness, not enhancement.*
2. **Explicit `triggers:` frontmatter + wire into `run_trigger_evals.py`** (gstack) — small change, leverages existing infra.
3. **SKILL.md templating / section composition with AUTO-GENERATED markers** (gstack) — biggest authoring-infra win; pairs with `skill-standardizer`.
4. **Published discoverability catalog from `skills.json`** (dimillian) — static renderer over the manifest dojo already generates.
5. **`skills-health` report** (ECC) — evidence for "description is the trigger."
6. **Behavioral eval tier** (gstack) — next rung after static skill-evals.
7. **slop-scan in CI** (gstack) + **thin `rules/` tier** (ECC) — both relieve quality/trigger pressure.

Explicitly **out of scope** for dojo: ECC's install platform/dashboards/inline-bootstrap hooks; gstack's mega-skill model, mandatory CLI/gbrain stack, and per-invocation preambles; dimillian's contract-free authoring (dojo's stricter bar is a feature, keep it).
