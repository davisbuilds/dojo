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
- **Next**: Task 13 of `docs/plans/2026-07-31-distribution-profiles-plan.md`
  makes the generator profile-aware and decides `.agent/skills`'s fate. The
  measurement half is already shipped — `scripts/profiles/` computes the cost of
  any target against either harness — so the remaining work is the refusal, not
  the arithmetic.
- **Revisit when**: Task 13 is implemented, or a `.claude/skills` link is
  observed on a 200k-window session, which is the only configuration where this
  currently degrades anything.

### A skill in the primary global root that no harness links is invisible to the audit

- **What**: `microsoft-foundry` sits in `~/.agents/skills/` on both machines and is
  linked from neither `~/.codex/skills` nor `~/.claude/skills`, so no harness can
  ever load it. The standardizer reports nothing — 0 issues, 0 actions — because
  its checks run from the secondary roots inward, and a name absent from both of
  them is simply never considered.
- **Why or evidence**: measured 2026-08-12 while confirming which root Codex reads.
  `microsoft-foundry` is absent from every captured `codex-tui` listing across
  0.146.0 and 0.147.0, which is what proves Codex reads via `~/.codex/skills`
  rather than `~/.agents/skills` directly. It costs no listing budget precisely
  because it is unreachable — the cost is that the primary global root is not a
  truthful statement of what is installed, and `prefer-primary-link` treats that
  root as the source of truth everywhere else.
- **Next**: report it (`ORPHANED_PRIMARY_GLOBAL`) rather than act on it — the fix
  is either "link it into the harness roots" or "remove it", and only the operator
  knows which. Note this is the mirror image of `STALE_SECONDARY_GLOBAL`, added
  2026-08-12: that one is a secondary entry with no primary, this is a primary
  entry with no secondaries.
- **Revisit when**: a skill is expected to be available and is not, or the next
  time the global roots are audited by hand.

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

### write-plan/write-spec: acceptance criteria that pass while the property is false
- **What**: the contract has one degeneracy rule — "do not accept bare
  existence/sign/completion checks such as `> 0`, 'not empty', or 'completes'"
  (`skills/write-plan/SKILL.md:179`) — and it is scoped to a *verification run's
  output magnitude*. It does not reach the `Done When` bullets themselves, and
  three distinct degenerate forms got past it in a single project:
  1. **An enumeration satisfiable while the invariant it stands for is violated.**
     A criterion that lists the cases that must hold is not the property; an
     implementation can satisfy every listed case and still break it.
  2. **A partition assertion where only one branch exists yet.** "Only X takes the
     legacy path" is unfalsifiable while *everything* takes the legacy path. The
     test passes, is committed as proof, and silently starts meaning something
     only after a later task creates the other branch.
  3. **An assertion over a collection that is always empty.** "…and carries every
     declared `--runtime-executable`" where no spec of that class declares any.
     Vacuously true, and reads as coverage.
- **Why or evidence**: all three, tokenmaxxing
  `docs/plans/2026-08-03-detached-worker-authority-profiles-plan.md`, 2026-07-26 →
  2026-08-04. Form 1 is recorded by the spec against itself (Revision 4: "Revision
  3's *enumerated* SC-03 was satisfiable" while the property was violated); forms
  2 and 3 were caught during execution of Task 4 and are noted inline in the plan.
  Notably this survived a critique subagent pass that did find four other blocking
  defects, so it is not covered by "have a critic read it" either.
- **Next**: add a degeneracy gate to `## Verification Requirements` covering the
  criteria and not just the output, phrased as the test the author must run
  against their own bullet: **assert it against a case you believe is false; if it
  still passes, it is not a criterion.** Concretely — (a) prefer stating the
  invariant with the enumeration as examples, and ask what satisfies the list
  while violating the intent; (b) a "only X does A" bullet requires a paired
  assertion that some non-X does not-A **and** a note that the pair is
  distinguishable *now*, else it is `pending`, not met; (c) an assertion over a
  collection must say what makes it non-empty. Related and worth the same bullet:
  when a task wires two components that share no test runner, the `Done When` must
  name where the contract is pinned or state plainly that it is not — the
  test-discovery rule at `SKILL.md:182` asks whether the runner finds the test,
  never whether anything tests the seam between two runners. Validator support is
  possible but partial: (b) and (c) are prose-detectable ("only", "every declared")
  as advisories; (a) is not mechanically checkable and belongs in
  `references/seam-selection.md`.

### write-plan: no validator signal for a step that depends on an external tool
- **What**: `write-plan` 2.3.0 added a `**Behavior Measured**` block — required
  when a step depends on a tool the repo does not own, with a command and its
  observed output as the artifact rather than a citation — and loosened
  `Assumptions Verified` to "state the claim and the evidence appropriate to it".
  The guidance exists; nothing checks it. A plan whose steps invoke `tmux`, `git`,
  `npm`, a sandbox policy, or a vendor CLI can still carry only in-repo citations
  and validate clean.
- **Why or evidence**: the guidance was written because a *correct* citation
  attached to a false external-behavior claim reads as verified (five such claims
  in tokenmaxxing, 2026-08-03/04; the tmux one cited `internal/tmux/tmux.go:68`
  accurately and proved nothing about tmux). A second project hit the staleness
  form of the same gap on 2026-08-10. Guidance alone did not prevent either — both
  authors believed they had verified.
- **Next**: advisory-only check in `validate_plan.py` — a task whose steps name a
  known-external binary but carry no `Behavior Measured` block gets flagged, in
  the same non-blocking channel as the existing weak-acceptance advisories. Keep
  the binary list short and obvious (`tmux`, `git`, `npm`, `docker`, `codex`,
  `claude`, `gh`) rather than attempting general detection; a false negative is
  fine, a false positive that trains people to ignore advisories is not.

### write-plan/test-strategy: high-risk proof can name the right artifact while leaving the property mutable
- **What**: the high-risk workflow asks for authority maps, evidence lifecycle,
  side-effect windows, recovery, partial rollout, and effective-runtime probes,
  but it does not force three distinctions that decide whether those sections
  are evidence or labels:
  1. **Identity is not capture.** Hashing or naming live inputs does not prove a
     later verifier, reviewer, or publisher consumed those bytes. The plan must
     name the freeze/copy/revalidation barrier between producer and every
     consumer, including mutation and inode/symlink swaps between phases.
  2. **“Idempotent” is not recovery.** A transition spanning a durable artifact,
     remote/local effect, outcome ledger, and lifecycle move needs persisted
     intent, effect order, receipts, and a reconciler for every crash point. The
     adjective alone hides the same partial-failure window the section is meant
     to expose.
  3. **Policy fixtures are not network-boundary proof.** A loopback server or
     injected dialer can prove parsing and refusal logic, but not that production
     connected to the public address it validated. Network authority needs the
     observed peer from the real transport plus a fixed public end-to-end
     control; the subject's requested URL is not the peer.
- **Why or evidence**: surfaced 2026-08-11 while planning evidence-grounded
  validation in tokenmaxxing. A structurally valid high-risk plan traced every
  contract ID and carried all required readiness tables, yet an adversarial
  closure review still found (a) roles reading live report/diff/transcript paths
  after their generation hash was computed, (b) publication/lifecycle/outcome
  effects described as idempotent with no durable executor, and (c) an SSRF test
  design whose allowed “public” request terminated at a loopback fixture. The
  same review found activation before declaration/recovery/inspection consumers;
  this is the topology form of the issue: enforcement cannot flip until its
  producer, recovery, and operator paths exist. These are reusable risks in
  migrations, queues, deployment controllers, auth systems, evidence pipelines,
  and any workflow that crosses mutable or remote state.
- **Existing guidance that is already sufficient**: do not widen `write-spec`
  for the initial contract revisions. Its high-risk protocol already requires
  actor authority, indirect forbidden paths, unsupported-policy behavior,
  partial failure, retry, concurrency, and adversarial closure; those misses
  were failures to apply the guidance, and the required critique loop caught
  them. Likewise, the existing effective-runtime/host-observer rule already
  rejects prompt compliance as authority proof. The gap is the more specific
  proof obligation above, not another tokenmaxxing/Agy checklist.
- **Next / ownership split**:
  - `write-plan/references/high-risk-readiness.md`: add a compact “prove the
    handoff” check for mutable evidence (capture/revalidate), multi-effect
    transitions (intent/order/receipt/reconcile), and activation topology (no
    default-on enforcement before declaration, recovery, and operator
    consumers). Require the plan critic to attack each distinction explicitly.
  - `test-strategy/references/authority-boundary-testing.md`: for network
    boundaries, separate deterministic policy tests, actual connected-peer
    observation, and a public end-to-end control; prohibit claiming a loopback
    fixture proves public-destination enforcement.
  - `write-spec`: no change from this incident unless another run shows the
    mechanism-free authority/recovery questions themselves are absent rather
    than skipped.
  Add skill-eval fixtures where a polished plan says “digest-bound” without a
  capture barrier, “idempotent” without a reconciler, flips enforcement before
  recovery exists, or labels a loopback transport “public”; each should be
  rejected by critique even when structural validation passes.

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
