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

### Harness adapters promote the whole catalog to project scope, blowing the skill-listing budget
- **What**: `scripts/gen_harness_adapters.py` links `.claude/skills -> ../skills`,
  which makes every cataloged skill *project-scope* in whatever directory holds
  the adapter. Measured 2026-07-26 on macbook: the same symlink placed at
  `~/Dev/.claude/skills` produced a 58-skill listing costing ~6,738 est. tokens —
  **3.4x** the ~1% context budget Claude Code allots the listing, past which
  descriptions are silently truncated. Project scope also *shadows* user scope, so
  31 of the 32 deliberately installed `~/.agents/skills` entries were overridden by
  their dojo counterparts. Working inside `dojo` itself hits the same cost locally.
- **Scope corrected 2026-07-29** (re-measured by live enumeration, not filesystem
  inspection): **project-scope skills are not inherited by subdirectories.** A
  `.claude/skills` adapter affects only sessions rooted at the directory holding
  it — 88 skills at `~/Dev` vs 60 at `~/Dev/agentmonitor`, first 30 identical. So
  no shadowing occurs in a subproject session, the cost of the extras is
  **~1,948 est. tokens** and only at the adapter's own directory, and **Codex is
  unaffected entirely** (`.claude/` is not a path it reads). Two further caveats
  for the profile work: the "~1% budget" figure remains **unverified** against
  vendor docs, and plugin plus bundled skills are roughly half of any Claude
  listing — outside dojo's reach at any profile width. Measured Codex cost of the
  shared 32 is ~3,185 est. tokens, which is the catalog a profile would govern.
- **Why it matters**: the adapter is documented as making skills "discoverable",
  but at full-catalog width it degrades the routing it is meant to enable, and it
  silently changes which copy of a drifted skill is authoritative. Contradicts the
  repo's own "context is sacred" principle.
- **Next**: teach the generator distribution *profiles* (see the existing
  "Add explicit distribution profiles" direction) so an adapter links a named
  subset rather than the whole tree; and/or emit per-skill symlinks so a profile
  is expressible. Report estimated listing cost under `--check` so budget
  regressions are visible. Relates to
  `skills-health: many canonical dojo skills aren't installed globally`.
- **Contract**: `docs/specs/2026-07-27-distribution-profiles-spec.md` is ready
  for planning. It defines a mandatory core plus capability overlays, exact
  managed realizations, authoritative harness-scoped budgets, and a prohibition
  on legacy adapter refreshes silently restoring whole-catalog links.

### Cross-machine profile drift is silent and can restore superseded skill behavior
- **What**: on 2026-07-27 the Mac mini's globals were **28 skills content-drifted**
  against a clean `origin/main` dojo checkout, including a `verify-before-complete`
  still on v1's broad "about to state work is fixed" wording — the exact text v2's
  narrow circuit-breaker was written to replace. The mini had been silently running
  superseded behavior. Remediated via `sync.py --only-existing --apply`; a canonical
  checkout being current is **not** evidence that installed globals are.
- **Why it matters**: dojo can prove its repository is internally consistent while the
  machines actually running the skills differ. The artifact that needs versioning is
  the *selected distribution profile plus its harness realization*, not the checkout.
  Nothing currently fails, warns, or reports when they diverge.
- **Next**: have the mini's weekly health job run a read-only standardizer audit
  after the scheduled checkout refresh and report canonical commit, installed profile,
  missing expected skills, content-drift count, and harness CLI versions. Detect and
  notify; do not auto-rewrite globals as part of a git pull.
- **Contract**: folded into
  `docs/specs/2026-07-27-distribution-profiles-spec.md`; the selected profile,
  canonical revision, target and harness policy identities, content drift, and
  budget outcome are explicit conformance evidence, while scheduled checks stay
  audit-only.
- **Do not reimplement the ignore logic**: `skill_standardizer_lib.py` already handles
  this correctly via `IGNORE_NAMES` (`.DS_Store`, `__pycache__`, `.git`,
  `.pytest_cache`) and `IGNORE_FILE_SUFFIXES` (`.pyc`, `.pyo`), applied in the compare,
  scan, and `_copy_ignore` copytree paths. Verified 2026-07-27: MacBook audit reports 0
  issues where a naive `diff -rq` reports six `__pycache__`-only false positives, and
  the mini received 0 `.pyc` files from the sync. Any *new* drift check (e.g. in the
  mini health job) must reuse this logic rather than rolling its own `diff`.

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

### write-spec/write-plan: make high-risk validation incrementally adoptable for legacy artifacts
- **What**: adding `risk_profile: high` / `readiness` to a mature legacy spec or
  plan currently activates the entire new-contract gate at once. A pre-existing
  accepted artifact without `SC-NN` / `EV-*-NN` IDs must be retrofitted wholesale
  before the validator will accept even a narrow high-risk amendment.
- **Why it matters**: the conditional high-risk YAML is supposed to let existing
  workflows adopt stronger authority/evidence/readiness checks where they matter.
  An all-or-nothing migration encourages agents to omit the metadata entirely—the
  opposite of progressive, risk-adaptive adoption.
- **Next**: make ID enforcement conditional without weakening new contracts:
  require full `SC`/`EV` closure when an ID-bearing schema/version is declared or
  any contract IDs exist, while allowing a high-risk legacy artifact to use named
  contract surfaces plus all other authority, failure-window, evidence, and
  readiness gates. Add fixtures for (1) a new ID-based high-risk spec/plan, (2) a
  legacy no-ID artifact receiving a high-risk amendment, and (3) partial-ID input
  that must fail rather than silently downgrade.

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
