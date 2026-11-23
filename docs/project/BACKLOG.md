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
  By 2026-11-20 (`8b9c86d`) the suite had grown to 1,114 collected cases; the
  category counts above are from the earlier inventory.
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
- **Decision, 2026-11-20**: the maintainer gated the next review candidate on
  [skilleval](https://github.com/davisbuilds/skilleval)'s experimental results
  plus observed friction, so no choice is pending from the maintainer. The
  experiment stays with skilleval; it compares current, compact, and minimal
  added guidance under the same harness/repo controls, assessing outcomes,
  authority boundaries, unnecessary artifacts/stops, context cost, and time.
- **Next**: when results arrive, select the candidate they and observed friction
  support; do not infer low value from invocation counts.
- **Revisit when**: skilleval reports results, real usage exposes more friction,
  or model/tool changes warrant recalibration.

### Remaining command permission patterns hardcode dojo-relative paths

- **What**: `local-review` and `repo-hardening`
  command wrappers still declare literal `Bash(... skills/<name>/...)` prefixes.
  Their runnable bodies use installed absolute paths, which these matchers do not
  cover. Observed in source on 2026-10-03 and still present on 2026-11-20 at
  line 5 of `skills/local-review/commands/review.md` and
  `skills/repo-hardening/commands/repo-{audit,harden}.md`; effective behavior is
  harness-dependent.
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
- **Why or evidence, 2026-10-06**: the [development CLI](../system/OPERATIONS.md#dojo-development-cli)
  connects existing tools and exposes revision, scope, findings, and evidence
  limits. Its first live creator inspection surfaced a profile/exposure mismatch.
  Tests and author-driven use establish functionality, not a measured reduction
  in supervision or an improvement in task outcomes.
- **Outstanding acceptance check**: the pilot called for a live Codex creator
  catalog inspection on both pilot hosts. Two-host coverage remains unverified.
  On each host, run `uv run --locked bin/dojo inspect skill-creator --harness codex --cwd . --json`
  and record the host, probe context, exit code, and catalog findings. The
  result describes a fresh prompt rendering.
  [Original acceptance criteria](https://github.com/davisbuilds/dojo/blob/2726ee4bc47e02c2a4c2363e15254ae0585475dd/docs/design/2026-10-06-dojo-cli-pilot.md#L49-L56)
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
- **What**: canonical `skills/` that are installed in none of the catalog dirs
  AgentMonitor scans emit no health row, so `scripts/skills_health.py --runtime`
  lumps them into one "no data" bucket. Missing or drifted members of the
  selected profile look the same as intentionally excluded skills.
- **Why or evidence, 2026-11-20**: AgentMonitor scans `~/.claude/skills` and
  `$CODEX_HOME/skills` by default, overridable with
  `AGENTMONITOR_SKILL_CATALOG_DIRS` (agentmonitor `src/config.ts`, `7da48d5`).
  `scripts/skill_health_runtime.py` counts absent skills as "no data" and has no
  profile awareness. The catalog has 40 skill directories; the July/August
  installation censuses (26 of 57, then 17 of 48) predate later retirements and
  are not current. AgentMonitor's backlog tracks the consumer-side gap
  ("Version attribution only reaches skills in the installed catalog").
- **Next**: do **not** install the entire catalog merely to manufacture runtime
  coverage. The distribution-profile contract makes intentional exclusion
  explicit; have the health report distinguish excluded skills from missing or
  drifted members of the selected profile. Recompute the census on the target
  host before using it for a decision.

### Port skill-standardizer tests to pytest under tests/
- **What**: `skills/skill-standardizer/scripts/test_skill_standardizer.py` uses a
  hand-rolled `main()` runner and an `assert_true` helper instead of pytest. It
  is the only test file outside `tests/`, and `scripts/check` (the local and CI
  gate) runs it as a separate check.
- **Why it matters**: `tests/` already tests skill-owned scripts —
  `tests/test_bump_skill_version.py` covers `skills/skill-evals/scripts/`
  via `importlib.spec_from_file_location`, and skill-evals ships no tests of its
  own. The standardizer is the sole outlier.
- **Interim state**: each test restores cwd and
  `AGENTS_HOME`/`CODEX_HOME`/`CLAUDE_HOME` through `isolated_tempdir()`, and
  `tests/test_skill_standardizer_suite.py` loads the file with `importlib` to run
  every test under pytest, check that restoration, and run the direct runner
  without pytest. What remains is shipped test code, the separate check, and
  two ways to invoke one file. The Test Tiers rule in
  `docs/system/ARCHITECTURE.md` (behavior ships; code tests do not) makes the
  port plain conformance.
- **Next**: port the tests into `tests/test_skill_standardizer_suite.py` with
  `tmp_path`/`monkeypatch` while keeping the stdlib-only direct runner and its
  pytest-free check, which are a current contract. Deleting the original,
  dropping its `scripts/check` line, and updating the `Run skill-standardizer
  regression tests` section of `docs/system/OPERATIONS.md` and the "known
  exception" paragraph under Test Tiers in `docs/system/ARCHITECTURE.md` retire
  that contract, so they need their own decision first. Symlinking the file into
  `tests/` was rejected: like the interim wrapper, it keeps a dead `main()` and
  two entry points.

### Shared SemVer helper
- **What**: SemVer parsing/validation now exists in multiple scripts. On
  2026-11-20 four `SEMVER_RE` copies existed: `scripts/generate_skills_manifest.py`,
  `skills/skill-creator/scripts/quick_validate.py`,
  `skills/skill-evals/scripts/check_skill_versions.py`, and
  `skills/skill-standardizer/scripts/skill_standardizer_lib.py`.
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
- **Evidence, 2026-11-20**: the "after a few real bumps" gate is met. Skill
  changelogs hold 151 version headings, 143 dated and 8 undated, and
  `bump_skill_version.py` already writes `## <version> - <date>` with a bullet.
- **Next**: decide whether to require headings like `## 1.2.3 - YYYY-MM-DD`
  plus at least one bullet in the version check, and whether to grandfather or
  backfill the 8 undated headings.

### Install/update workflows should understand skill versions
- **What**: `skill-standardizer` audit/sync reports show source and current
  versions with a behind/ahead/equal/divergent/unknown delta (2026-10-21), but
  `skill-installer` listings still do not report available/current versions.
- **Decision, 2026-11-20**: the maintainer chose to keep and diverge Dojo's
  `skill-installer` and install it for Claude Code; Codex keeps its bundled
  copy. Version 2.0.0 rebased it on the Codex CLI 0.163.0 bundled copy; see its
  [changelog](../../skills/skill-installer/CHANGELOG.md) and
  [Global Skill Membership](GLOBAL-SKILL-MEMBERSHIP.md).
- **Why it matters**: `list-skills.py` marks a skill only "already installed",
  so an available update looks the same as an up-to-date copy.
- **Next**: show installed and available versions in `skill-installer` listings,
  reusing the standardizer's semantics in
  `skills/skill-standardizer/references/policy.md#version-deltas`. Re-check the
  bundled Codex copy for upstream changes when doing so.

### skill-standardizer cannot keep a skill out of the shared global root
- **What**: `--normalize-primary` promotes any concrete skill in a secondary
  global root to `~/.agents/skills`, and `--enforce-mirror` creates one there.
  Neither knows that a skill is meant for one harness only.
- **Why or evidence, 2026-11-20**: a temp-home dry run with a Claude-only
  `skill-installer` in `~/.claude/skills` planned `PROMOTE_TO_PRIMARY`. Applied,
  that would expose Dojo's copy to Codex beside its bundled one. `--only-existing`
  syncs the copy in place and is safe.
- **Next**: let the standardizer honor harness-scoped skills, for example by
  reading `profiles/harness-equivalences.yaml` when the canonical repo is Dojo or
  through a repeatable flag; until then, review dry runs for this skill.

### Scan-timeout test races scanner startup under load
- **What**: `tests/test_audit_skill.py::test_scan_timeout_stops_scanner_and_its_child`
  gives `run_scan` a 1 s timeout, in which `scan.sh` must start a fake Python
  engine that writes its PID file. When startup is slower than that, the
  "Scanner never started" assertion fails without any cleanup defect.
- **Why or evidence**: failed once in a full `scripts/check` run on 2026-10-15
  (MacBook, Python 3.12), then passed in isolation five times and in two further
  full runs. The last 100 `skill-contract-pilot.yml` runs (2026-10-20 to
  2026-11-20) had no failures. The fake engine spawns its sleeping child before
  writing the PID file, because the file records both PIDs.
- **Next**: shorten the work before the PID write (for example, start the child
  with a cheaper command than a second Python interpreter), or raise the timeout
  enough to cover cold interpreter startup; revisit if it fails in CI.

### Revalidate earlier catalog improvement candidates before selecting work

- **What**: the March 2026 roadmap proposed sharing image-provider plumbing,
  bundling fetched web guidelines, research caching,
  example specs, semantic trigger scoring, and broader hook/validator tests.
- **Why or evidence**: these were source-review suggestions, not evidence that a
  capability was missing from today's model/harness or that a merger would help.
  Generic database, documentation, accessibility, profiling, and dependency skill
  ideas had no demonstrated gap; file or resource counts do not establish value.
- **Revisit when**: observed user friction or a selected catalog review supplies a
  current need. Check existing skills, tools, examples, and tests before adopting
  any candidate; preserve distinct triggers when they serve different tasks.

### Decide the open Codex equivalences for `gpt-imagen` and `local-review`

- **What**: `profiles/harness-equivalences.yaml` leaves two Codex pairs
  undeclared until someone decides them: `gpt-imagen` against Codex's bundled
  `imagegen`, and `local-review` against Codex's `.system/review-agent`.
- **Why or evidence**: a wrong declaration silently removes a selected skill, so
  both stay undeclared and are reported as collisions. `gpt-imagen` belongs to no
  overlay, so its suppression would never fire today (2026-08 observations).
- **Next**: compare the two image skills' actual capabilities (masking, batch
  output, the pinned model) rather than their descriptions, and declare the pair
  only if the bundled path covers them; the `local-review` pair needs a
  maintainer decision because `local-review` is a `core` member.

### Reconcile Claude Code `unresolved` origins against the probe's source counts

- **What**: `scripts/profiles/probe_claude.py` (`classify` origin assignment)
  labels any listed entry it finds in no inspectable root `unresolved`, and
  `scripts/profiles/observe.py` (`observe_claude`) exempts `unresolved` entries
  alongside `harness-bundled` ones. A comment deferred reconciling that bucket
  against the per-source counts in the debug log's `Loading skills from` line
  to a later plan task, which never shipped (checked 2026-11-22).
- **Why or evidence**: bundled skills ship inside the binary and land in this
  bucket, but so would anything else the probe cannot see; while it is exempt,
  an unseen non-bundled entry is never charged or reported.
- **Next**: compare the bucket's size with the bundled count that line
  reports, and mark the observation unsupported when they disagree.
