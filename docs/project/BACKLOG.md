# Improvement Backlog

Living list of future friction points, design gaps, and follow-up actions noticed
during normal repo work. Lightweight: items get added when they bite, removed
when they ship or prove not worth doing. This is not a release contract;
`docs/project/ROADMAP.md` is the higher-bar shipped/in-progress view.

Convention: each item has **What** (the friction), **Why it matters**, and
optionally **Sketch** (a one-line implementation thought). Status values:
`noted` / `in-progress` / `dropped`.

When an item ships, remove it from this doc and record it as a concise completed
highlight in `docs/project/ROADMAP.md` instead of keeping a shipped note here.
This file stays future-only.

---

## Open

#### research-architect: deferred tooling awaits first real runs
Status: noted
- **What**: `scripts/score_report.py`, `scripts/diff_runs.py`, and
  `references/rubric-library.md` remain deliberately deferred. The first
  golden-question seed now exists at `evals/golden-questions/social-playbooks/`;
  stages 8–9 specify the manual verification and synthesis procedures the
  scripts would automate.
- **Why it matters**: Building rubric libraries and golden-question evals
  before any real run would encode guesses; the first stage-10 postmortems are
  the intended seed material. Once 2–3 real runs exist, automating the stage-8
  structural pass and cross-run diff removes the most error-prone manual work.
- **Sketch**: After 2–3 real runs, extract discriminating rubric patterns from
  `01-question.md` artifacts into rubric-library.md, then script scoring and
  diffing to match the manual stage-8 spec.

#### skills-health: runtime join is last-wins, undercounts a version-split skill
Status: noted
- **What**: `skill_health_runtime.enrich_report` indexes health rows as
  `rows_by_name = {row["name"]: row}`, so if AgentMonitor returns more than one
  row for a skill (same name, different `version` — the phase-1 `(name, version)`
  keying), the join silently keeps only the last row. The report then shows one
  version's `invocations`/`misfire` numbers, not the skill's total.
- **Why it matters**: Invocation volume is a ranking input; undercounting a
  version-split skill would mis-rank it (e.g. a heavily-used skill that bumped
  versions mid-window could look under-used). Not observable today — the live
  payload has 79 rows / 79 unique names, zero splits — but it becomes wrong as
  version churn increases.
- **Sketch**: When multiple rows share a name, aggregate before ranking — sum
  `invocations`/`misfires`/`misfireEligible`, `neverFired` only if all rows are
  never-fired, and surface the newest/installed version for display. Add a
  fixture with two rows for one dojo skill to lock the behavior.

#### skills-health: many canonical dojo skills aren't installed globally, so they're unmeasurable
Status: noted
- **What**: As of 2026-07-15, 26 of 57 canonical `skills/` are installed in none
  of the global catalog dirs AgentMonitor scans (`~/.claude/skills`,
  `~/.codex/skills`, `~/.agents/skills`) and have never fired, so AgentMonitor
  emits no health row and they land in the report's collapsed "no data" bucket
  (agent-native-architecture, algorithmic-art, autonomous-engineering, caveman,
  code-review-agents, compound-docs, design-md, fetchmd, gh-commit-push-pr,
  gh-fix-issue, gh-review-pr, gh-triage-issues, hookify, loop-design,
  markdown-converter, nextjs-app-router, repo-hardening, self-improve,
  skill-evals, skill-installer, template, theme-factory,
  vercel-composition-patterns, vercel-deploy, vercel-preview-logs,
  vercel-react-native-skills). The earlier "13 of 55" figure was a stale
  point-in-time AgentMonitor snapshot; the catalog has since grown and prior
  syncs used `--only-existing`.
- **Why it matters**: A skill that isn't installed anywhere the agent can trigger
  it can't generate trigger health, so the loop can't tell whether its
  description works. A prior skill-standardizer run likely used `--only-existing`,
  which skips skills not already installed globally, so newly-added canonical
  skills never got pushed out.
- **Sketch**: Run `skill-standardizer` sync without `--only-existing` to install
  the missing canonical skills into the primary global root, then re-check the
  health report. Decide whether `template` (a scaffold, not a real skill) should
  be excluded from expected-coverage counts.

#### Standardizer has no allowlist for foreign non-skill dirs in mirror roots
Status: resolved (2026-07-16)
- **What**: `~/.codex/skills/codex-primary-runtime` is a Codex-specific runtime
  directory with no `SKILL.md`, so every full-scan audit reported it as
  `INVALID_SKILL_DIR`. The `_`-prefix convention added in 1.0.1 covers dirs dojo
  controls (`skills/_fragments`), but Codex owns that path and won't rename it.
- **Resolution** (1.1.0): `KNOWN_NON_SKILL_DIRS` in `skill_standardizer_lib.py`
  is a built-in allowlist keyed by **root kind**, so `codex-primary-runtime` is
  exempt in `global-codex` only and the exemption cannot leak into the canonical
  root (covered by `test_known_non_skill_dir_still_reported_in_other_roots`).
  `--ignore-dir NAME` (repeatable, on both `audit.py` and `sync.py`) handles
  ad-hoc cases.
- **Why both**: the flag alone would not have fixed the reported problem — the
  warning only stops recurring if the operator remembers to pass it every run.
  Built-in for permanent tool-owned dirs, flag for one-offs.

#### skill-standardizer regression tests never run in CI
Status: resolved (2026-07-16)
- **What**: CI runs `python -m pytest tests/ -q`, which only collects the
  top-level `tests/` directory. The standardizer's 13-test regression suite lives
  at `skills/skill-standardizer/scripts/test_skill_standardizer.py` and is not
  referenced from `tests/`, so it ran only when invoked by hand — the same
  failure shape as the `_fragments` bug fixed in 1.0.1, where a test file looked
  like coverage but enforced nothing.
- **Resolution**: added a `Run skill-standardizer regression tests` step to
  `.github/workflows/skill-contract-pilot.yml` that invokes the file directly.
  Verified the step has real signal: injecting a regression into
  `KNOWN_NON_SKILL_DIRS` made it exit 1, and it exits 0 restored.
- **Scope**: this is the only test file outside `tests/` — no other skill has the
  hole.
- **Follow-up**: see "Port skill-standardizer tests to pytest" below.

#### Port skill-standardizer tests to pytest under tests/
Status: noted
- **What**: `skills/skill-standardizer/scripts/test_skill_standardizer.py` uses a
  hand-rolled `main()` runner and an `assert_true` helper instead of pytest. It
  is the only test file outside `tests/`, and CI needs a dedicated step for it.
- **Why it matters**: `tests/` already tests skill-owned scripts —
  `tests/test_bump_skill_version.py` covers `skills/skill-evals/scripts/`
  via `importlib.spec_from_file_location`, and skill-evals ships no tests of its
  own. The standardizer is the sole outlier.
- **The leak**: the suite mutates process-global state (`os.chdir`, and
  `AGENTS_HOME`/`CODEX_HOME`/`CLAUDE_HOME`) with no teardown, and leaves `cwd`
  pointing at a deleted tempdir. Verified this collides with nothing today —
  nothing in `tests/` or `scripts/` reads `cwd` or those vars — so the risk is
  latent, not active. `monkeypatch.setenv`/`monkeypatch.chdir` auto-restore and
  would remove it. (An earlier note here called this an active pollution risk;
  that was overstated.)
- **No longer blocked**: an earlier version of this entry said the port needed a
  call on whether the skill should keep shipping its own tests, since sync copies
  them to `~/.agents/skills/skill-standardizer/scripts/`. Settled — the Test
  Tiers rule in `docs/system/ARCHITECTURE.md` says behavior ships (`evals/`) and
  code tests do not. Nothing in a global install invokes the suite. It does run
  there (stdlib-only, hermetic tempdir fixtures — verified passing from `/tmp`),
  but "can run" is not "has a consumer". Losing it from the global copy costs
  nothing, so the port is plain conformance.
- **Sketch**: port ~13 tests to `tests/test_skill_standardizer.py` with
  `tmp_path`/`monkeypatch`, delete the original, drop the dedicated CI step, and
  update both the `Run skill-standardizer regression tests` section of
  `docs/system/OPERATIONS.md` and the "known exception" paragraph under Test
  Tiers in `docs/system/ARCHITECTURE.md`.
- **Rejected alternative**: symlinking `tests/test_skill_standardizer.py` to the
  skill's copy so pytest collects it while the skill still ships it. It would
  work (pytest collects module-level `test_*` functions; `assert_true` raises
  `AssertionError`), but it moves the `os.chdir`/`os.environ` leak into the
  shared 184-test run and leaves a dead `main()` plus two ways to invoke one
  file. It preserves the anomaly instead of resolving it.

#### bump_skill_version.py could regenerate the manifest itself
Status: noted
- **What**: `bump_skill_version.py` writes SKILL.md directly (subprocess, not the
  agent's Write/Edit tool), so the post-tool-use manifest-regen hook never fires
  and `skills.json`/catalog are left stale. It prints a reminder to run the
  generators, but the operator can still forget and fail CI's `--check`.
- **Why it matters**: The helper's whole point is doing the mechanical release
  edits in one command; a forgotten manifest regen re-introduces the friction it
  set out to remove.
- **Sketch**: Optionally invoke `generate_skills_manifest.py` and `gen_catalog.py`
  after a successful non-dry-run bump (behind a `--no-regen` escape hatch), or
  have the stop-hook manifest check auto-heal. Keep it opt-outable so scripted
  batch bumps can regenerate once at the end.

#### Shared SemVer helper
Status: noted
- **What**: SemVer parsing/validation now exists in multiple scripts.
- **Why it matters**: The duplication is small, but future changes to prerelease
  or build-metadata handling could drift between validation, manifest generation,
  and version-bump checks.
- **Sketch**: Move the regex plus parse/compare helpers into a small importable
  module under `skills/skill-evals/scripts/` or `scripts/lib/`, then have
  validators and generators use the same implementation.

#### Changelog entry format hardening
Status: noted
- **What**: Version checks currently require a `CHANGELOG.md` heading containing
  the new version, but do not require dates or entry content.
- **Why it matters**: This keeps adoption friction low, but changelog quality may
  vary once skills start receiving regular releases.
- **Sketch**: After a few real version bumps, consider requiring headings like
  `## 1.2.3 - YYYY-MM-DD` plus at least one bullet under the heading.

#### Install/update workflows should understand skill versions
Status: noted
- **What**: The manifest and catalog now expose skill versions, but installer and
  standardizer workflows do not yet report available/current version deltas.
- **Why it matters**: Version metadata is most useful when sync and install tools
  can say whether a local copy is behind, ahead, or divergent.
- **Sketch**: Extend skill install/standardization reports to show source and
  destination versions alongside existing drift information.

#### Command wrappers are documented but never wired into any harness
Status: resolved (2026-07-15)
- **Resolution**: `scripts/gen_harness_adapters.py` now links each skill's
  `commands/<rel>.md` into `.claude/commands/<rel>.md` (local-only, gitignored),
  preserving the nested `workflows/` layout (`/workflows:brainstorm`). It refuses
  on cross-skill name collisions, prunes symlinks whose source was removed, never
  touches a hand-authored file, and reports drift under `--check`. Commands are
  governed by the symlink phase, so CI's `--skip-symlinks` run is unaffected.
- **Why Claude Code only**: verified on `codex-cli 0.144.1` that Codex has no
  user-populated slash-command directory — its only `$CODEX_HOME/` filesystem
  surfaces are `config`, `generated`, `skills`, and `themes`. Slash commands in
  Codex are built-in TUI actions, plugin/marketplace-provided, or MCP-server
  prompts (`prompts/list`); none are wireable from a repo `.md` file. Codex
  instead consumes dojo skills via `~/.codex/skills/` (synced by the
  standardizer) and invokes them with `$skill-name` from each skill's generated
  `default_prompt`. So there is nothing to wire for Codex — the command wrappers
  are a Claude Code affordance, and the capability reaches Codex as the skill.
- **Follow-up (optional)**: `.agents` uses its own convention; wire it only if a
  consuming harness there needs command files.
