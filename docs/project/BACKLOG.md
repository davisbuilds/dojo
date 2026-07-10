# Improvement Backlog

Living list of future friction points, design gaps, and follow-up actions noticed
during normal repo work. Lightweight: items get added when they bite, removed
when they ship or prove not worth doing. This is not a release contract;
`docs/system/ROADMAP.md` is the higher-bar shipped/in-progress view.

Convention: each item has **What** (the friction), **Why it matters**, and
optionally **Sketch** (a one-line implementation thought). Status values:
`noted` / `in-progress` / `dropped`.

When an item ships, remove it from this doc and record it as a concise completed
highlight in `docs/system/ROADMAP.md` instead of keeping a shipped note here.
This file stays future-only.

---

## Open

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

#### write-plan: `Assumptions Verified` must cite the file being cut, not a neighbor
Status: noted
- **What**: A plan's per-task `Assumptions Verified` line can cite a file:line
  that confirms a data *shape* but lives in a different file than the one the task
  actually edits (e.g. citing a historical importer to justify a parser task).
- **Why it matters**: It reads as grounded verification but isn't — the target
  file may not have the assumed structure at all, so the task is mis-sized or
  wrong. Observed live: a plan cited an importer's typed fields to justify editing
  a parser that had zero handling for those fields.
- **Sketch**: Add a rule to `Map Before You Cut` / Task Design Rules: an
  `Assumptions Verified` claim must reference the exact file/symbol the task
  edits. Cross-file shape references are research context, not verification, and
  must be labeled as such.

#### write-plan: "resolve, don't defer" — no conditional guesses in steps, no lookups in the risk register
Status: noted
- **What**: Implementation steps sometimes contain conditional hedges ("if
  already wired", "if snapshots are broadcast", "if X exists"), and the Risks
  section is used to park questions that are answerable now with a grep/read.
- **Why it matters**: A conditional in a step is an unverified guess shipped as a
  prescription; a "risk" that is really a skipped lookup gives false confidence
  and mis-sizes the task. Observed live: two tasks were mis-sized because an
  assumed-existing fetch and an assumed SSE payload were deferred rather than
  checked.
- **Sketch**: Add a rule: any step with "if <unverified condition>" is not ready —
  verify and rewrite as a fact. And: a Risk must be an irreducible future
  uncertainty, not a lookup that can be resolved before execution.

#### write-plan: "verify the verification" — confirm new tests are actually discovered by the runner
Status: noted
- **What**: Plans name per-task verification commands (e.g. new test file paths)
  without confirming the test runner's discovery config actually picks the file
  up.
- **Why it matters**: A test placed outside the runner's glob silently never runs,
  so the plan's own CI gate passes while the new coverage is absent. Observed
  live: new tests were slated for `src/**` while the runner only globs `tests/**`.
- **Sketch**: Add a Verification Requirements item: confirm new test files match
  the runner's discovery config (script/glob in `package.json` or equivalent) and
  that the literal proof command runs them, before claiming plan readiness.

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
