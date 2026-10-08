# Backlog

Future-only gaps and opportunities worth revisiting. Capture recurring friction,
meaningful risk or cost, unresolved decisions, or concrete revisit triggers.
Fix simple, quick, or blocking issues inline when within the active task's scope.

## Conventions

- **Entry:** state **What** and **Why or evidence**. Add **Next** (a useful first
  action) or **Revisit when** (a concrete gate) where helpful; no fixed template
  is required.
- **Evidence:** date and source volatile claims. Support causal or performance
  claims with measurements, or label them **hypothesis, unmeasured**.
- **Delegation:** agents can execute entries directly. Recording a candidate does
  not expand the active task or select a roadmap priority. Use an issue when
  persistent discussion or coordination helps; no mandatory graduation step.
- **Ownership:** keep cross-repository work with the capability-owning repository.
  If an issue owns the details, retain only a useful linked summary here; avoid
  parallel checklists. Keep private evidence out of public entries and issues.
- **Closure:** reconcile affected entries as work lands. Remove resolved concerns,
  retain unresolved remainders, and preserve durable rationale in its owning
  reference. Roadmap records selected direction; Git and PRs hold routine shipped
  history. Revisit the broader list during prioritization or when stale entries
  impede work.

## Open

### Review test requirements against the current skill design principles

- **What**: review validators and their tests together for requirements that no
  longer earn their constraints. Preserve meaningful regression coverage; do not
  target a smaller test count or rewrite the whole suite by default.
- **Why or evidence, 2026-10-04**: collection at `7ce4996` yielded 800 cases
  across 37 test files; the suite passed in about 13 seconds. The inventory
  includes 140 portable-command-path cases, 256 distribution/measurement cases,
  102 research-tooling cases, and 58 plan/spec-validator cases. This was an
  inventory and sampled source review, not an assessment of every assertion or
  evidence of improved agent outcomes. The research revision removes mandatory
  prompt blocks, instruction-count limits, and exact skeleton-prose assertions;
  its tooling retains draft-hygiene, citation, and CLI coverage. Remaining
  candidates include fixed profile vocabulary/membership in
  `tests/test_profiles_definitions.py` and plan/spec validator requirements.
- **Next**: identify the current consumer or protected failure for each disputed
  requirement before keeping, narrowing, replacing, or retiring it. Change the
  owning instructions, validators, and tests together. Keep coverage for safe
  mutation, authority boundaries, portability, evidence fidelity, and real CLI
  contracts. Distinguish evaluation-runner unit tests from live agent evidence;
  deterministic green checks do not establish skill effectiveness. Research
  and authoring revisions resolve their local subsets; the broader suite pass is
  deferred. Conditional retirement criteria now live in
  [test-strategy’s review reference](../../skills/test-strategy/references/verification-checklist.md).
  The authoring validator no longer gates prose headings or length;
  remaining candidates above still need consumer-grounded review.

### Check heading fragments in local Markdown links

- **What**: extend the existing link checker to validate supported local heading
  fragments, preserving its deliberate exclusions and reporting coverage limits.
- **Why or evidence, 2026-10-07**: the source survey found that
  `scripts/check_links.py` strips fragments and checks only file existence.
  A renamed reference heading can therefore break a skill's navigation while
  CI passes. No currently broken link was established.
- **Next or revisit when**: a bounded tooling pass or missed heading link warrants
  it; use fixtures for valid/stale headings, duplicates, inline formatting, and
  fenced examples. Define supported Markdown anchors rather than claiming full
  renderer equivalence. Addy's reference-link validator is implementation context,
  not a reason to add another skill or runtime workflow.

### Isolate standardizer tests from process state

- **What**: several standalone standardizer tests leave cwd and harness-home
  environment variables pointing into deleted temporary directories.
- **Why or evidence**: on 2026-10-02, bare `pytest -q` collected these tests and
  subsequent tests failed at `Path.cwd()`. CI deliberately runs `pytest tests/`
  and the standardizer script in separate processes; `pyproject.toml` now also
  scopes default pytest discovery to `tests/`. Explicitly collecting the standalone
  suite still needs isolation.
- **Next**: restore cwd and environment per test before unifying test discovery;
  preserve direct-script execution without adding a runtime pytest dependency.

### Evaluate workflow revisions and extend the composition audit

- **What**: measure the marginal value of the compact workflow guidance and audit
  the remaining catalog for redundant coaching or recursive handoffs.
- **Why or evidence**: the 2026-09-15/16 incidents recorded in `f6c4852`,
  `c471546`, and `b05ff54` motivated the shipped first pass; the current policy lives in
  [best practices](../system/SKILL-BEST-PRACTICES.md).
  Deterministic validation and manual replay cases establish structure and
  expected behavior, not model-performance improvement. Methodology skills and
  higher-priority harness loading policies can still add process outside the
  revised cluster.
- **Next**: use the separate skill-effect experiment reported by the user on
  2026-09-17 for empirical comparison; keep that experiment with its owning
  project. Compare current guidance, compact guidance, and minimal added guidance
  with the same harness/repo controls. Assess outcomes, authority boundaries,
  unnecessary artifacts/stops, context cost, and time. Prioritize remaining
  skills from observed friction; do not infer low value from invocation counts.
- **Revisit when**: a candidate is selected, real usage exposes more friction,
  experimental results arrive, or model/tool changes warrant recalibration.

### Remaining command permission patterns hardcode dojo-relative paths

- **What**: `local-review` and `repo-hardening`
  command wrappers still declare literal `Bash(... skills/<name>/...)` prefixes.
  Their runnable bodies use installed absolute paths, which these matchers do not
  cover. Observed in source on 2026-10-03; effective behavior is harness-dependent.
- **Why or evidence**: fixing the instruction path does not fix permission matcher
  semantics. The security rewrite removed these ineffective declarations from
  `secure-code` and `audit-skill`; those wrappers now inherit harness permissions
  without adding a broad shell allowlist.
- **Next**: when revising the remaining wrappers, decide whether ordinary harness
  permissions suffice. If pre-approval adds value, verify a portable matcher with
  vendor documentation or a real positive/negative probe before applying it.
  Do not guess at wildcard semantics or broaden authority just to avoid prompts.

### Observe the bounded CLI pilot before expanding its scope

- **What**: exercise `bin/dojo check` and `bin/dojo inspect` on normal skill edits
  and harness-discovery investigations, including use by a fresh agent.
- **Why or evidence, 2026-10-06**: the [pilot](../design/2026-10-06-dojo-cli-pilot.md)
  connects existing tools and exposes revision, scope, findings, and evidence
  limits. Its first live creator inspection surfaced a profile/exposure mismatch.
  Tests and author-driven use establish functionality, not a measured reduction
  in supervision or an improvement in task outcomes.
- **Next**: observe whether an agent can reach the correct conclusion without
  reconstructing commands or overstating a pass. Add commands only for recurring
  unmet work. Claude probing needs an explicit capture/effect contract; revision
  comparisons remain with the separate ops/OpenBench pilot. Do not wrap every
  skill-owned script or create another evaluation runner.

### Revisit contract anchors if they obstruct a useful short guidance skill

- **What**: `reference` skills still need scope, boundaries, verification, and
  resource navigation when applicable. A short opinion or taste reference may
  not need all of those anchors; whether a new type would help remains a
  hypothesis.
- **Why or evidence**: the earlier `first-principles` example is obsolete: it is
  a reference skill and the 2026-09-23 revision fits the existing contract without
  a prescribed workflow. This item no longer supplies a blocking example for
  a new type.
- **Revisit when**: a concrete, useful short skill fails the contract solely for
  missing an anchor that adds no value. Compare relaxing that check with adding
  a new type before expanding the schema.

### research-architect: remaining deferred tooling
- **What**: `scripts/diff_runs.py` and `references/rubric-library.md` remain
  deliberately deferred. (`scripts/score_report.py` shipped in 2.2.0 and gained
  citation-coverage/applicability scoring in 2.3.0 after the third live run.)
- **Why it matters**: Across three runs there are now two confirmed
  discriminating rubric patterns: the per-tactic evidence floor (2026-07-12)
  and complete benchmark metadata or an unusable verdict (2026-08-22). That is
  still thin for a reusable library. The third run also proved manual cross-run
  diffing valuable, but only one of three reports preserved M1's exact section
  structure and two exports had opaque claim-to-URL linkage.
- **Next**: revisit after another real run exposes recurring work worth tooling.
  Current synthesis aligns claims and questions without fixed report headings;
  any future helper must tolerate missing, added, and reordered sections and
  opaque citations. Treat the dated rubric observations above as candidates for
  optional evidence lenses, not a reason to restore mandatory scorecards.

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
  retired rather than installed, giving a then-current census of 17 of 48.
  This is historical evidence, not current membership; `compound-docs` was
  retired on 2026-09-22. Recompute before using the census for a decision. The earlier
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

### Revalidate earlier catalog improvement candidates before selecting work

- **What**: the March 2026 roadmap proposed combining Vercel deploy/preview skills,
  sharing image-provider plumbing, bundling fetched web guidelines, research caching,
  example specs, semantic trigger scoring, and broader hook/validator tests.
- **Why or evidence**: these were source-review suggestions, not evidence that a
  capability was missing from today's model/harness or that a merger would help.
  Generic database, documentation, accessibility, profiling, and dependency skill
  ideas had no demonstrated gap; file or resource counts do not establish value.
- **Revisit when**: observed user friction or a selected catalog review supplies a
  current need. Check existing skills, tools, examples, and tests before adopting
  any candidate; preserve distinct triggers when they serve different tasks.
