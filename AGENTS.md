# AGENTS.md

`dojo` is a repository of extensible, agent-agnostic skills and hooks. Skills are markdown-first (`SKILL.md` per directory) with optional `scripts/`, `references/`, `assets/`, and `commands/`. The generated `skills.json` manifest is the runtime inventory source of truth.

## Documentation Map

- `docs/system/ARCHITECTURE.md` — high-level flow, skill structure + frontmatter spec, progressive disclosure tiers, hook pipeline table, manifest + validation pipelines, directory map (including `profiles/` and `scripts/profiles/`).
- `docs/system/FEATURES.md` — full skill catalog grouped by category (code review, design, research, etc.).
- `docs/system/OPERATIONS.md` — setup, dependency install, all skill-management commands, measuring a session's listing cost against each harness's budget, hook configuration, CI, optional skill dependencies.
- `docs/system/SKILL-BEST-PRACTICES.md` — research-backed authoring guidance, design contract, anti-patterns, trigger collision guidance.
- `docs/system/skill-contract-v1.md` — SKILL.md packaging gates and advisory authoring checks used by CI.
- `docs/project/ROADMAP.md` — selected direction and the context behind current priorities.
- `docs/project/VISION.md` — long-term direction and guiding principles.
- `docs/project/BACKLOG.md` — future-only friction points and deferred follow-ups noticed during implementation.
- `docs/project/GIT_HISTORY_POLICY.md` — branch hygiene and merge strategy (squash disabled; merge-commit or rebase, full per-commit history preserved).
- `spec/agent-skills-spec.md` — full skill specification.
- `rules/` — standing always-follow conventions (skill authoring, doc/commit hygiene), separate from on-trigger skills; composable into SKILL.md via `<!-- INCLUDE: rules/<name> -->`.

## Working Conventions

- **Hooks already enforce most invariants.** Editing a `SKILL.md` triggers validation on write, manifest regen on save, and skill-structure check at session stop. If a hook blocks you, fix the underlying problem rather than working around it.
- **Command wrappers (`commands/*.md`)** remain canonical runbooks even in harnesses that don't expose command files — treat them as part of the skill.

## Key Design Principles

Context economy, degrees of freedom, and trigger quality are owned by
`docs/system/SKILL-BEST-PRACTICES.md`; progressive-disclosure tiers by
`docs/system/ARCHITECTURE.md`. The local preference:

- **Earn the constraint**: Design for capable agents. Add missing capabilities, preferences, or demonstrated safeguards; let generic coaching shrink as it loses value. Consultation does not inherit a sibling's workflow. Follow the authoring and retirement guidance in `docs/system/SKILL-BEST-PRACTICES.md`, grounded in `docs/project/VISION.md`.

## Testing

- **Python environment**: `uv sync --locked`; use `uv run --locked` for repo tools. Dependencies live in `pyproject.toml` and `uv.lock`; bare `uv run --locked pytest` selects `tests/`.

- **Pre-push**: `scripts/check`, the same gate CI runs (about 30 s; `--fast` skips the test suites). It only checks, never writes, and names every failed check. Add a new CI check to the script rather than to the workflow.
- **Focused skill checks**: `uv run --locked bin/dojo check <skill>` verifies one skill's packaging and links while you edit it; `uv run --locked bin/dojo inspect <skill> --harness codex` investigates why a skill is missing, stale, or mis-exposed in Codex. Both are narrower than the pre-push command and CI, and don't replace them. Options and limits: [operations](docs/system/OPERATIONS.md#dojo-development-cli).
- **TDD**: red/green for new features, major refactors, and large changes; the red step must fail on the behavior being fixed, not on a missing symbol.

## Git

[GIT_HISTORY_POLICY.md](docs/project/GIT_HISTORY_POLICY.md) owns merge settings: merge commits by default, rebase allowed, squash disabled, branches deleted on merge. `main` requires the `check` and `Validate Strict Skill Set` checks; branches need not be up to date. Commit subjects and PR titles/bodies are Conventional Commits that Release Please parses ([release contract](docs/system/OPERATIONS.md#cli-and-tooling-releases)); use `docs(<skill>): ...` for skill instruction changes. Merging an ordinary PR updates the open Release Please PR; merging that release PR tags and publishes a CLI/tooling release.

## Working Agreement

- **Clarify before building** when a request is vague, contradictory, or skips a
  key decision; clear, well-scoped requests need no interview.
- **Comments.** Don't add code comments. The one exception is a decision record:
  start it with `WHY:` and state a non-obvious reason the code can't express.
  Never justify a shortcut in a comment; fix it or record it in
  `docs/project/BACKLOG.md`. `python3 scripts/check_comments.py` enforces a
  ratchet: after deleting comments run it with `--update`, and never raise a
  count in `.comment-baseline.json`.
- **Fix small issues now; backlog the rest.** Fix simple, quick, or blocking
  issues in this repo as part of the current change and call them out. Record in
  `docs/project/BACKLOG.md` only what can't be finished now or needs the
  maintainer's decision; don't open a branch or PR just for a backlog entry.
  Add an item only for recurring friction, meaningful risk/cost, an unresolved
  decision, or a concrete trigger. Record **What / Why or evidence / Next or
  Revisit when**; keep the backlog future-only, use the capability-owning
  repository as canonical for cross-repo work, date/source volatile claims (or
  label a hypothesis), and remove resolved work while preserving any unresolved
  remainder. Agents can execute backlog entries directly; use GitHub Issues
  when persistent discussion or coordination helps, with one detailed owner and
  links where useful.
- **Keep docs current** when a change makes a documented contract, boundary,
  procedure, or direction stale. Reconcile affected backlog entries as work
  lands; update Roadmap when selected direction changes, not for every shipment.
- **Planning and continuity.** Reuse clear task context. Save planning docs when
  decisions, acceptance, or coordination need persistence. Leave a brief handoff
  only when needed to resume unfinished work. Commit shared docs and keep status
  current. Before archiving, preserve lasting decisions and open work in
  maintained docs and repair links.
- **Commit and push.** Commit coherent chunks, staging by explicit path. Push
  your task branch and open a PR once the work is complete and the local gate
  passes; don't push directly to `main`.
- **Merge** only under the standing merge authority in the maintainer's
  workspace instructions, or when the maintainer asks. Without those
  instructions in context, leave the PR for the maintainer.
- **Re-ground after compaction** in source, this file, the owning docs, and
  recent commits. A summary and your own earlier proposals are not user approval.
