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

#### skills-health: 13 canonical dojo skills aren't installed globally, so they're unmeasurable
Status: noted
- **What**: 13 of 55 canonical `skills/` are installed in none of the global
  catalog dirs AgentMonitor scans (`~/.claude/skills`, `~/.codex/skills`,
  `~/.agents/skills`) and have never fired, so AgentMonitor emits no health row
  and they land in the report's collapsed "no data" bucket
  (agent-native-architecture, algorithmic-art, autonomous-engineering, caveman,
  compound-docs, design-md, fetchmd, loop-design, markdown-converter,
  self-improve, template, theme-factory, vercel-react-native-skills).
- **Why it matters**: A skill that isn't installed anywhere the agent can trigger
  it can't generate trigger health, so the loop can't tell whether its
  description works. A prior skill-standardizer run likely used `--only-existing`,
  which skips skills not already installed globally, so newly-added canonical
  skills never got pushed out.
- **Sketch**: Run `skill-standardizer` sync without `--only-existing` to install
  the missing canonical skills into the primary global root, then re-check the
  health report. Decide whether `template` (a scaffold, not a real skill) should
  be excluded from expected-coverage counts.

#### Shared SemVer helper
Status: noted
- **What**: SemVer parsing/validation now exists in multiple scripts.
- **Why it matters**: The duplication is small, but future changes to prerelease
  or build-metadata handling could drift between validation, manifest generation,
  and version-bump checks.
- **Sketch**: Move the regex plus parse/compare helpers into a small importable
  module under `skills/skill-evals/scripts/` or `scripts/lib/`, then have
  validators and generators use the same implementation.

#### Skill version bump helper
Status: noted
- **What**: The release check requires authors to bump SKILL.md and add a
  changelog heading, but no command helps perform that edit.
- **Why it matters**: The policy is enforceable, but manual edits are repetitive
  and easy to get slightly wrong during frequent skill maintenance.
- **Sketch**: Add a small helper such as
  `python3 skills/skill-evals/scripts/bump_skill_version.py skills/api-design patch`
  that updates the top-level `version` field and prepends a `CHANGELOG.md`
  heading for the new release.

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

#### `init_skill.py` scaffold deadlocks the pre-write validation hook
Status: noted
- **What**: `skills/skill-creator/scripts/init_skill.py` emits a SKILL.md template
  with no top-level `version` field, which the contract has required since the
  SemVer baseline. `hooks/pre-tool-use-validate-skill.sh` validates the *existing*
  on-disk SKILL.md before allowing a Write or Edit, so the freshly scaffolded file
  fails validation and blocks the very edit that would add `version`. Hit while
  creating `blind-spots`; worked around by deleting the scaffold and
  writing SKILL.md from scratch (the hook passes when the file is absent).
- **Why it matters**: Every new skill authored with the official initializer walks
  into this. The workaround makes the initializer worse than useless — it costs a
  delete before you can proceed.
- **Sketch**: Add `version: 1.0.0` to `SKILL_TEMPLATE`. Optionally have the hook
  skip files whose content is still the unmodified TODO scaffold, so a broken
  template degrades to a warning rather than a deadlock.

#### Command wrappers are documented but never wired into any harness
Status: resolved (2026-07-15)
- **Resolution**: `scripts/gen_harness_adapters.py` now links each skill's
  `commands/<rel>.md` into `.claude/commands/<rel>.md` (local-only, gitignored),
  preserving the nested `workflows/` layout (`/workflows:brainstorm`). It refuses
  on cross-skill name collisions, prunes symlinks whose source was removed, never
  touches a hand-authored file, and reports drift under `--check`. Commands are
  governed by the symlink phase, so CI's `--skip-symlinks` run is unaffected.
- **Follow-up (optional)**: only `.claude/commands/` is wired; other harnesses
  (Codex prompts, `.agents`) use different command mechanisms and were left out.
  Wire those if/when a consuming harness needs them.
