# External Skill-Repo Comparison: ECC & gstack vs. dojo

**Date:** 2026-06-16
**Scope:** Deep review of `_clones/skills/ECC` (and `_clones/skills/gstack`) compared to dojo, to surface what dojo could leverage, what each does better/worse, and concrete next steps.
**Status:** Research only — no building yet.

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

## Consolidated next-steps shortlist (both repos)

Ordered by value-to-effort for dojo specifically:

1. **Resolve the multi-harness gap** (from ECC) — adopt an adapter-compliance `--check`, or scope the claim. *Correctness, not enhancement.*
2. **Explicit `triggers:` frontmatter + wire into `run_trigger_evals.py`** (from gstack) — small change, leverages existing infra.
3. **SKILL.md templating / section composition with AUTO-GENERATED markers** (from gstack) — biggest authoring-infra win; pairs with `skill-standardizer`.
4. **`skills-health` report** (from ECC) — evidence for "description is the trigger."
5. **Behavioral eval tier** (from gstack) — next rung after static skill-evals.
6. **slop-scan in CI** (from gstack) + **thin `rules/` tier** (from ECC) — both relieve quality/trigger pressure.

Explicitly **out of scope** for dojo: ECC's install platform/dashboards/inline-bootstrap hooks; gstack's mega-skill model, mandatory CLI/gbrain stack, and per-invocation preambles.
