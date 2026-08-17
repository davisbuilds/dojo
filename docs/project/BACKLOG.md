# Backlog

Living list of future design gaps, tech debt, and better ways to do a thing noticed
during normal execution. Fix simple, quick, or blocking issues inline; capture only
durable follow-ups worth revisiting cold. Add an item only when it cannot be fixed inline
and represents recurring friction, meaningful risk or cost, an unresolved decision, or a
concrete trigger. This is not a release contract; `docs/project/ROADMAP.md` is the
higher-bar shipped/in-progress view.

This repository is the canonical owner for its follow-ups; cross-repository work belongs
with the repository that owns the capability, with links from affected repositories only
when useful. Date and source volatile external or runtime claims, or label them a
hypothesis.

Convention: each item has **What** (the friction), **Why or evidence**, and
optionally **Next** (the smallest action that makes it actionable) or **Revisit
when** (an intentional external or measurable gate). Default state is omitted; use
**Revisit when** for gates and `State: blocked — <reason>` only when work is genuinely
blocked externally.

When an item ships, remove it from this doc and record it as a concise completed
highlight in `docs/project/ROADMAP.md` instead of keeping a shipped note here.
This file stays future-only.

Review this file after a significant shipped slice or at least quarterly: confirm each
item is still open, refresh dated evidence, promote selected work to a plan, convert it
to a trigger, or move completed decisions and work to the Roadmap or decision history.

---

## Open

### `allowed-tools` permission patterns still hardcode a dojo-relative path

- **What**: command wrappers declare permissions as literal command prefixes —
  `allowed-tools: [Bash(bash skills/secure-code/scripts/scan.sh:*), ...]` in
  `secure-code/commands/scan.md` and similarly in the other wrappers that ship
  scripts. The bodies now use `<skill-dir>/scripts/...` so the command resolves
  in whatever repository the session is in, but the permission pattern was left
  alone.
- **Why or evidence**: found 2026-08-14 while fixing the runnable paths. The
  frontmatter is a **matcher**, not an instruction the agent substitutes, so
  rewriting it to `<skill-dir>` would not make it match — it would only stop it
  matching in dojo too. The command an agent actually runs after substitution is
  an absolute path under whichever root the skill was loaded from
  (`~/.agents/skills/secure-code/scripts/scan.sh`), which the current pattern
  does not match either. Net effect: outside dojo these commands prompt for
  permission every time rather than being pre-approved.
- **Now**: bodies are correct and the commands work; only the pre-approval is
  lost. Not guessed at, because a plausible-looking permission pattern that
  silently fails to match is worse than an honest prompt.
- **Next**: establish what Claude Code's `allowed-tools` matcher actually
  supports — whether a leading wildcard (`Bash(bash *secure-code/scripts/scan.sh:*)`)
  matches an absolute path — from the vendor's own documentation or a probe,
  rather than by pattern-guessing. Then apply it across the wrappers that ship
  scripts, and extend `tests/test_skill_script_paths.py` to cover frontmatter.
- **Revisit when**: doing it, or if a wrapper starts prompting unexpectedly.

### Port two pr-review-toolkit specialists into dojo before disabling the plugin
- **What**: auditing Claude plugins on 2026-07-29 found two agents in
  `pr-review-toolkit@claude-plugins-official` that cover ground **no dojo skill
  does**, and they are the only reason the plugin is still enabled:
  - `silent-failure-hunter` (130 lines) — enumerates every catch block, fallback,
    default-on-failure value, "logged but execution continues" path, and optional
    chain that can hide an error, then interrogates each for logging quality, user
    feedback, and catch-block specificity.
  - `type-design-analyzer` (118 lines) — rates encapsulation and *invariant
    expression*: whether a type makes illegal states unrepresentable.
- **Why it matters**: `secure-code` is a scanner and `local-review` is a workflow;
  neither hunts swallowed errors, and nothing in the catalog reviews type design.
  The remaining four agents (`code-reviewer`, `code-simplifier`,
  `comment-analyzer`, `pr-test-analyzer`) are baseline knowledge and duplicate
  existing skills, so the plugin cannot be dropped without losing these two.
- **Known defect to fix on port**: `silent-failure-hunter` hardcodes another
  project's conventions — three `Sentry` references, two `logError`, and two
  `constants/errorIds.ts` — and will flag missing error IDs against a file that
  does not exist in this portfolio. Rewrite those checks against the actual stacks
  (Next.js/Supabase, Python) rather than copying them.
- **Also worth lifting** (pattern, not prose): both the plugin's `review-pr`
  command and its `code-reviewer` agent score each finding 0-100 and **report only
  at >= 80**, and `review-pr` maps diff content to specialists (test files ->
  test analyzer, new types -> type analyzer). `code-review@claude-plugins-official`
  goes further with five parallel reviewers on distinct lenses, two of which —
  git blame/history and prior PR comments on the same files — no dojo review skill
  attempts. Compare against `local-review` before reinventing.
- See also the separate branch-hygiene entry below, which owns the one gap found
  in the `commit-commands` plugin.
- **Next**: two new skills, or one `error-handling-review` skill plus a
  `type-design` section in an existing review skill. Add trigger fixtures so the
  routing collision with `local-review` and `secure-code` is tested, given the
  catalog already has 17 entry points for "review this".

### The gh-* family covers creating work but not cleaning up after it
- **What**: auditing the `commit-commands@claude-plugins-official` plugin on
  2026-07-29 (now disabled) surfaced one thing the catalog does not cover. The
  `gh-*` family is now just `gh-commit-push-pr` — `gh-fix-issue`, `gh-review-pr`,
  and `gh-triage-issues` were retired 2026-07-31 as unused. What survives is still
  about *producing* work, and **nothing covers post-merge branch and worktree
  hygiene.** A repo-wide search for `worktree`, `branch -d`, `[gone]`, or `prune`
  across every `SKILL.md` returns no relevant hit. Retirement narrowed the family
  but did not touch this gap.
- **Specific gaps**:
  - **Worktree-before-branch ordering.** A branch marked `[gone]` that carries an
    attached worktree (`+` prefix in `git branch -v`) cannot be deleted until the
    worktree is removed. Deleting in the wrong order fails confusingly. This was
    the plugin's `clean_gone` command's only real contribution, in ~10 lines.
  - **Stacked-PR retarget hazard.** Squash-merging a base PR and deleting its
    branch **auto-closes the stacked child PR**. The child must be retargeted to
    `main` first. Already learned the hard way; it lives in an agent memory note,
    which means Codex cannot see it — the two memory stores are mutually invisible
    and measurably disjoint. That argues for the catalog, not a memory.
  - **Stale local branches after remote deletion**, and the `pulldevmain` blocked
    -checkout case (a repo left on a feature branch silently stops receiving
    updates — observed 2026-07-27 for `pmalpha`).
- **Why it matters**: these are exactly the "safe to do, easy to get wrong, rarely
  done" operations that earn a skill. The failure mode is not a bad commit, it is
  a silently closed PR or a repo that quietly stops syncing.
- **Not a gap**: `gh-commit-push-pr` already pre-loads git context with
  `` !`git ...` `` interpolation in its command wrapper and its Edge Cases table
  covers no-changes, existing-PR, merge-conflict, binary-file, and
  sensitive-file cases. The commit/push/PR path itself is well covered and is a
  strict superset of what the plugin offered — do not reimplement it.
- **Next**: either a `gh-branch-hygiene` skill or an Edge Cases/cleanup section
  appended to `gh-commit-push-pr`. Prefer the latter if it stays under a few dozen
  lines, since the catalog already has routing-collision pressure and this is
  adjacent to an existing trigger rather than a new intent.

### Harness adapters can still promote the whole catalog to project scope
- **What**: `scripts/gen_harness_adapters.py` links `.claude/skills -> ../skills`,
  making every cataloged skill project-scope in whatever directory holds the
  adapter. Nothing prevents a refresh from restoring that link, and nothing
  reports the cost when it does.
- **Why or evidence (re-measured 2026-08-03; three earlier figures here were
  wrong and are recorded below because the pattern is the finding)**:
  - Codex-facing `.agents` was dropped from `HARNESS_DIRS` in PR #54, which took
    a dojo-rooted Codex session from **177% of budget with 94 truncated
    descriptions to 76% with none**. The generator now also retires a
    pre-existing link, so the fix reaches machines that ran the old version.
  - `.claude/skills` **survives and is still a live cause**: a dojo-rooted Claude
    Code session lists 75 skills against 45 in an ordinary one. At the 1M window
    the operator actually uses that is 58% of 40,000 characters — inside the
    ceiling. At 200k it is 2.91×.
  - `.agent/skills` is read by **neither** harness. It is dead output.
- **Superseded claims, kept so the corrections are not re-made**: the original
  "3.4× the ~1% budget" does not reproduce (2.07× ordinary, 2.91× in dojo); the
  "~1% budget" is no longer unverified but a confirmed vendor constant
  (`skillListingBudgetFraction` = 0.01); "31 of 32 entries shadowed" was
  corrected in 2026-07-29 when project scope turned out not to be inherited by
  subdirectories; and every token figure predating 2026-08-02 charged the whole
  instructions block rather than only the skill lines, overstating by ~2 points.
- **Next**: the profile-aware generator fix (Task 13 of
  `docs/plans/2026-07-31-distribution-profiles-plan.md`) is **no longer planned** —
  Phase 2 (Tasks 11–16) was descoped (`ops` register R43) when the profiles
  program closed at Phase-1 measurement scope (spec revision 16, 2026-08-15). The
  behavior is intact: `gen_harness_adapters.py` still links
  `.claude/skills -> ../skills` (whole-catalog project promotion) and
  `.agent/skills -> ../skills` (dead output — read by neither harness). Two
  independent, much smaller fixes remain if pursued: drop `.agent` from
  `HARNESS_DIRS` to delete the dead link, and gate or remove the wholesale
  `.claude/skills` link. The measurement half (`scripts/profiles/`) already ships,
  so any fix is the refusal, not the arithmetic.
- **Revisit when**: a `.claude/skills` link is observed degrading a 200k-window
  session — the only configuration where this currently costs anything; the
  operator's 1M-window sessions stay inside budget. The `.agent/skills`
  dead-output cleanup can be done anytime as standalone hygiene.

### dojo has 47 script entrypoints and no front door for the human-run ones
- **What**: repo-level tooling a person invokes is reachable only by full path
  through `.venv/bin/python`. The sharpest case is the Task 0 probes: `codex debug
  prompt-input` and `claude --debug-file` were assumed not to exist for weeks, and
  now that they are wrapped, the capability answers a question nothing else in the
  repo answers — *what does this session's skill listing actually cost, on this
  harness, right now* — from `scripts/profiles/probe_codex.py`, where nobody will
  find it. `skill-standardizer/scripts/{audit,sync}.py` take **14 and 16
  arguments** and are run from a runbook, from memory, on two machines.
- **Why or evidence**: 47 `.py` files carry an argparse entrypoint (measured
  2026-08-03). They are not one population and should not be treated as one:
  - ~13 are **machine-invoked** by hooks or CI, which already call them by path.
    Two run on *every* Bash tool call, so added indirection there is a new runtime
    dependency, not a convenience.
  - ~30 are **skill-owned** under `skills/*/scripts/`, invoked by an agent that
    has just read the SKILL.md naming the exact command. The skill body is the
    interface; wrapping them fights progressive disclosure.
  - The remainder — the probes, the standardizer pair, `skills_health.py`,
    `run_trigger_evals.py`, `bump_skill_version.py` — are **human-invoked** and
    are the only ones a CLI would help.
  Noted in passing: dojo ships a `create-cli` skill, an SC-02 anchor of the
  `engineering` overlay, and has no CLI.
- **Next**: none as a separate effort. `bin/dojo` is already created by Task 8 of
  `docs/plans/2026-07-31-distribution-profiles-plan.md`, because `dojo profiles
  verify --all` is a literal contract term in the spec. Building a CLI before then
  means designing the same executable twice. Widen Task 8 to add
  `dojo probe codex|claude` — wiring, since the argparse exists — and decide the
  rest there.
- **Revisit when**: Task 8 is reached, or the plan is descoped short of it. If the
  plan stops before Task 8, this becomes a standalone decision rather than a
  free rider, and the probes are the only part that clearly earns a CLI on their
  own.
- **Keep out deliberately**: generators, validators, and skill-owned scripts. A
  wrapper that hooks and CI bypass creates two paths to one behavior that can
  drift — the exact failure this program keeps finding. Four subcommands is a
  tool; fifteen is a project nobody decided to start.

### Contract v1 has no shape for an opinion-only skill
- **What**: `workflow` skills must carry scope, boundaries, verification, output,
  execution, and resource-map anchors, CI-enforced under `--strict`. That imposes a
  ~300-500 word scaffolding floor regardless of how much insight the skill holds, so
  a skill that should be three sharp paragraphs of opinion cannot pass validation.
- **Why it matters**: current provider guidance holds that the highest-value skills
  encode particular opinions and taste rather than procedure. The contract makes that
  the one shape the catalog cannot express, and rewards padding to reach the anchors.
- **Next**: add an `opinion` (or `guidance`) `skill-type` requiring only valid
  frontmatter plus `description_trigger_ready`, with `context_budget` still advisory.
  Re-evaluate `first-principles` against it — it is 1,683 words largely because
  `workflow` gave it anchors to fill.

### research-architect: remaining deferred tooling
- **What**: `scripts/diff_runs.py` and `references/rubric-library.md` remain
  deliberately deferred. (`scripts/score_report.py`, the third of the original
  trio, shipped in 2.2.0 once two real runs justified it.)
- **Why it matters**: Across two runs there is exactly one confirmed
  discriminating rubric item (the per-tactic evidence floor, 2026-07-12).
  Building a rubric library on one data point would encode guesses — the mistake
  the deferral exists to avoid. `diff_runs.py` only pays off on multi-run plans
  and depends on M1 section alignment holding in practice.
- **Next**: Seed `rubric-library.md` once 2–3 more runs identify rubric items
  that actually discriminate (items that always pass are dead weight and belong
  in the postmortem, not the library). Build `diff_runs.py` on top of
  `score_report.py`'s claim/citation extraction rather than duplicating it: align
  sections by the M1 fixed order, then surface confident specifics appearing in
  only one report as hallucination candidates.

### skills-health: runtime join is last-wins, undercounts a version-split skill
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
- **Next**: When multiple rows share a name, aggregate before ranking — sum
  `invocations`/`misfires`/`misfireEligible`, `neverFired` only if all rows are
  never-fired, and surface the newest/installed version for display. Add a
  fixture with two rows for one dojo skill to lock the behavior.

### skills-health: many canonical dojo skills aren't installed globally, so they're unmeasurable
- **What**: As of 2026-07-15, 26 of 57 canonical `skills/` are installed in none
  of the global catalog dirs AgentMonitor scans (`~/.claude/skills`,
  `~/.codex/skills`, `~/.agents/skills`) and have never fired, so AgentMonitor
  emits no health row and they land in the report's collapsed "no data" bucket
  (agent-native-architecture, caveman, compound-docs, design-md,
  fetchmd, gh-commit-push-pr, loop-design, markdown-converter,
  nextjs-app-router, repo-hardening, skill-evals, skill-installer, template,
  theme-factory, vercel-composition-patterns, vercel-deploy,
  vercel-preview-logs). **Updated 2026-08-01:** eight of the original 26 were
  retired rather than installed, so the census is now 17 of 48. The earlier
  "13 of 55" figure was a stale
  point-in-time AgentMonitor snapshot; the catalog has since grown and prior
  syncs used `--only-existing`.
- **Why it matters**: A skill that isn't installed anywhere the agent can trigger
  it can't generate trigger health, so the loop can't tell whether its
  description works. A prior skill-standardizer run likely used `--only-existing`,
  which skips skills not already installed globally, so newly-added canonical
  skills never got pushed out.
- **Direction**: do **not** install the entire catalog merely to
  manufacture runtime coverage. The distribution-profile contract makes
  intentional exclusion explicit and evaluates routing against deployable
  profiles; health coverage should distinguish excluded skills from missing or
  drifted members of the selected profile.

### Port skill-standardizer tests to pytest under tests/
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
- **Next**: port ~13 tests to `tests/test_skill_standardizer.py` with
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

### bump_skill_version.py could regenerate the manifest itself
- **What**: `bump_skill_version.py` writes SKILL.md directly (subprocess, not the
  agent's Write/Edit tool), so the post-tool-use manifest-regen hook never fires
  and `skills.json`/catalog are left stale. It prints a reminder to run the
  generators, but the operator can still forget and fail CI's `--check`.
- **Why it matters**: The helper's whole point is doing the mechanical release
  edits in one command; a forgotten manifest regen re-introduces the friction it
  set out to remove.
- **Next**: Optionally invoke `generate_skills_manifest.py` and `gen_catalog.py`
  after a successful non-dry-run bump (behind a `--no-regen` escape hatch), or
  have the stop-hook manifest check auto-heal. Keep it opt-outable so scripted
  batch bumps can regenerate once at the end.

### Shared SemVer helper
- **What**: SemVer parsing/validation now exists in multiple scripts.
- **Why it matters**: The duplication is small, but future changes to prerelease
  or build-metadata handling could drift between validation, manifest generation,
  and version-bump checks.
- **Next**: Move the regex plus parse/compare helpers into a small importable
  module under `skills/skill-evals/scripts/` or `scripts/lib/`, then have
  validators and generators use the same implementation.

### Changelog entry format hardening
- **What**: Version checks currently require a `CHANGELOG.md` heading containing
  the new version, but do not require dates or entry content.
- **Why it matters**: This keeps adoption friction low, but changelog quality may
  vary once skills start receiving regular releases.
- **Next**: After a few real version bumps, consider requiring headings like
  `## 1.2.3 - YYYY-MM-DD` plus at least one bullet under the heading.

### Install/update workflows should understand skill versions
- **What**: The manifest and catalog now expose skill versions, but installer and
  standardizer workflows do not yet report available/current version deltas.
- **Why it matters**: Version metadata is most useful when sync and install tools
  can say whether a local copy is behind, ahead, or divergent.
- **Next**: Extend skill install/standardization reports to show source and
  destination versions alongside existing drift information.

### Test isolation: a test leaves the process cwd deleted under Python 3.14
- **What**: some test in `pytest tests/` deletes the process working directory
  without restoring it; under Python 3.14's `os.getcwd()` a later test that reads
  cwd then fails only in full-suite ordering, never in isolation. The victim was
  `test_validate_plan.py::test_high_risk_plan_requires_linked_spec_and_structured_addendum`.
- **Why or evidence**: reproduced 2026-08-14 on local Python 3.14.6. The
  `discover_repo_root` crash half of this was fixed 2026-08-16 (it now catches
  `FileNotFoundError` and degrades to the artifact's directory), so the full
  suite is green on 3.14 — but the leaky test remains a latent flake generator
  for any other code that reads cwd. The poisoner was not isolated; it does not
  reproduce in the pairwise combinations tried.
- **Next**: find the test that deletes cwd without restoring (bisect via a
  session-scoped autouse fixture that asserts cwd is intact after each test),
  fix it to restore or avoid chdir, then add 3.14 to the CI matrix
  (`skill-contract-pilot.yml` pins 3.12) so the regression cannot return silently.
- **Revisit when**: moving CI to Python 3.14, or the failure appears in isolation.
