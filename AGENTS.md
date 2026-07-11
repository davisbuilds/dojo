# AGENTS.md

`dojo` is a repository of extensible, agent-agnostic skills and hooks. Skills are markdown-first (`SKILL.md` per directory) with optional `scripts/`, `references/`, `assets/`, and `commands/`. The generated `skills.json` manifest is the runtime inventory source of truth.

## Documentation Map

- `docs/system/ARCHITECTURE.md` — high-level flow, skill structure + frontmatter spec, progressive disclosure tiers, hook pipeline table, manifest + validation pipelines, directory map.
- `docs/system/FEATURES.md` — full skill catalog grouped by category (GitHub workflows, code review, design, etc.).
- `docs/system/OPERATIONS.md` — setup, dependency install, all skill-management commands, hook configuration, CI, optional skill dependencies.
- `docs/system/SKILL-BEST-PRACTICES.md` — research-backed authoring guidance, design contract, anti-patterns, trigger collision guidance.
- `docs/system/skill-contract-v1.md` — SKILL.md quality contract (skill types, required checks) enforced by CI.
- `docs/project/ROADMAP.md` — shipped highlights, improvement backlog, and cross-cutting findings.
- `docs/project/VISION.md` — long-term direction and guiding principles.
- `docs/project/BACKLOG.md` — future-only friction points and deferred follow-ups noticed during implementation.
- `docs/project/GIT_HISTORY_POLICY.md` — branch hygiene and merge strategy (squash disabled; merge-commit or rebase, full per-commit history preserved).
- `spec/agent-skills-spec.md` — full skill specification.
- `rules/` — standing always-follow conventions (skill authoring, doc/commit hygiene), separate from on-trigger skills; composable into SKILL.md via `<!-- INCLUDE: rules/<name> -->`.

The auto-generated `skills.json` manifest is the runtime source of truth for what's available.

## Working Conventions

- **Hooks already enforce most invariants.** Editing a `SKILL.md` triggers validation on write, manifest regen on save, and skill-structure check at session stop. If a hook blocks you, fix the underlying problem rather than working around it.
- **Command wrappers (`commands/*.md`)** remain canonical runbooks even in harnesses that don't expose command files — treat them as part of the skill.

## Key Design Principles

1. **Context is sacred**: The context window is finite and shared. Only add information the agent doesn't already have/know.

2. **Progressive disclosure**: Metadata always loaded (~100 words) → SKILL.md body on trigger (<5k words) → bundled resources as needed.

3. **Degrees of freedom**: Match specificity to task fragility - high freedom for flexible tasks (text instructions), low freedom for fragile operations (specific scripts).

4. **Description is the trigger**: The `description` field determines when the agent uses the skill. Include both what it does AND specific scenarios/triggers.

## Testing

- **Pre-push** (matches CI): `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict`.
- **TDD**: red/green for new features and major changes.

## Working Agreement

- **Push back before building.** If a request is incoherent or self-contradictory, or a spec/plan is vague or skips key decisions, stop and interview me — ask clarifying questions and confirm intent before writing code or changing files. Don't guess at scope or comply silently. (Clear, well-scoped requests don't need this.)
- **Keep docs current.** After a significant change, PR, or completed spec/plan, update any now-stale reference docs under `docs/system/` (including `ROADMAP.md`) so they match shipped behavior. Skip this for trivial changes.
- **Commit logically.** Commit completed work in coherent chunks as you proceed. Push only when explicitly asked.
- **Re-ground after compaction.** A compaction summary loses precise paths, context, and verification state — before continuing, re-read this project's `AGENTS.md`, its reference docs, and recent commits.
