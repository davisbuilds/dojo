---
date: 2026-07-31
author: claude-opus-5
topic: distribution-profiles
stage: plan
status: draft
source: conversation
risk_profile: high
readiness: ready
spec: docs/specs/2026-07-27-distribution-profiles-spec.md
---

# Distribution Profiles Plan

## Goal

Deliver the distribution-profiles contract in
`docs/specs/2026-07-27-distribution-profiles-spec.md`: named, versioned subsets of
the canonical dojo catalog, a read-only verifier that computes effective-catalog
listing cost against an authoritative harness limit, and an explicit,
recoverable applicator that no existing adapter entrypoint can bypass.

Delivered as the two phases the spec's Handoff mandates:

- **Phase 1 — verify only** (Tasks 0–10). SC-01…SC-06, SC-10, SC-11, and the
  audit-only halves of SC-09 and SC-12. `dojo profiles verify --all` works end to
  end. Nothing mutates target state. Independently shippable: it is a new
  directory of profile data plus one new read-only CLI plus one new CI gate, and
  it changes no existing runtime behavior.
- **Phase 2 — apply** (Tasks 11–16). SC-07, SC-08, SC-13, migration under SC-09,
  and the EV-REC and EV-CON scenarios.

Phase 2 is required for acceptance. Every `Done When` traces to a spec success
criterion or evaluation scenario; the Traceability table below is exhaustive in
both directions.

## Scope

### In Scope

- `profiles/` — reviewable YAML profile definitions (`core`, six capability
  overlays, `full`) and a versioned harness budget-policy record.
- `scripts/profiles/` — a new Python package: definition loading, resolution and
  identity, effective-catalog observation, the Codex listing/budget model,
  evidence assembly, routing coverage, cross-machine comparison, and (phase 2)
  the applicator.
- `bin/dojo` — the executable that makes `dojo profiles verify --all` work as
  literally written in the contract.
- Profile awareness in every existing entrypoint that can create or refresh
  adapter/target state: `scripts/gen_harness_adapters.py`,
  `skills/skill-standardizer/scripts/{audit,sync}.py`, and
  `skills/skill-installer/scripts/install-skill-from-github.py`.
- One new CI gate in `.github/workflows/skill-contract-pilot.yml`.
- Tests in `tests/` in the existing pytest style.

### Out of Scope

- Changing any skill's content, description, or membership in the canonical
  catalog to make a profile fit (spec Out of Scope; SC-03).
- Remote orchestration that mutates the other machine. SC-11 is discharged by
  consuming two independently produced evidence files (Task 7).
- Establishing a Claude Code listing limit. Claude Code stays audit-only under
  SC-04 until a policy exists; the profiles CLI observes and reports its targets
  but never issues a deployable verdict for them.
- Manufacturing trigger fixtures for skills that lack them. Task 6 reports the
  sparse-coverage limitation honestly (spec Assumptions).
- Nested/subtractive overlays and per-project profile forks (spec Assumptions).

## Assumptions And Constraints

- **No budget figure is a constant anywhere in this plan.** The spec records a
  live disagreement (56%/85% versus 50%/75%, different estimators, neither
  reproducible). Adjudicating it is an *output* of phase 1 (Task 10), never an
  input. No task's `Done When` quotes a percentage of budget as an expected
  value; they assert relations the verifier computes at verify time.
- **Measure the listing, not the filesystem.** This error has recurred four times
  in this program (ops `audits/dojo-skill-catalog-audit-2026-07-31.md`,
  "Verification addendum", C-1 and C-3). The filesystem scan supplies *candidate*
  membership; the harness model decides which candidates are actually listed and
  at what cost. `~/.claude/plugins/cache/openai-templates` ships 20 skills that
  appear in no live listing and cost nothing — the model must exclude them, and
  Task 0 proves it does against a captured live listing.
- **A count of zero is a claim about the instrument.** Every detector this plan
  adds (foreign-entry detection, shadowing detection, drift detection,
  whole-catalog-link detection) is proven against a case already known to exist
  before any absence is reported. Where no live positive case exists, the fixture
  pins a non-degenerate floor.
- **The shell is zsh and does not word-split unquoted variables.** No
  verification command in this plan iterates an unquoted variable; loops use
  arrays or `while IFS= read -r`. `rg -r` is `--replace` and appears nowhere.
- **Live subjects already exist.** Both machines carry an identical 32-entry
  `~/.agents/skills` (31 canonical dojo skills plus the foreign
  `microsoft-foundry`), verified 2026-07-31. SC-05's foreign-entry observation
  and SC-11's cross-machine agreement case are real, not constructed.
- **Codex is the only deployable harness** on current evidence, so acceptance
  must not assume a second one exists, and SC-03's "core fits" proof is
  discharged against Codex (spec Assumptions).
- **Python 3.12 in CI, 3.14 locally.** The only runtime dependency is
  `PyYAML==6.0.3` (`requirements.txt`). This plan adds no dependency. Local runs
  use `.venv/bin/python`; `python3` alone has no pytest on this machine.
- **The vendor source is available locally at the pinned revision.**
  `/Users/dg-mac-mini/Dev/_clones/codex` is at `f57467275c`, so Task 3's port of
  `codex-rs/core-skills/src/render.rs` is checkable line by line rather than
  reconstructed from prose.

### Open decisions for the maintainer

Only one item below is a contract question. The rest are recorded plan-level
decisions, stated so a reader can see they were decided rather than drifted into.

**Contract question — SC-10's per-overlay anchor clause.** None of the twelve
SC-02 anchors declares a trigger fixture today. Task 6 resolves this by
**authoring the twelve anchor fixtures** rather than deferring, because emitting
`coverage-gap` while claiming SC-10 proven would be a false completion claim. If
the maintainer would rather not add fixtures, SC-10's per-overlay clause needs a
contract revision instead. Task 6 assumes the authoring answer.

**Plan decisions, recorded not deferred:**

1. **Harness-bundled and plugin entries are counted in the budget.** SC-04
   enumerates user scope, project scope, shadowed names, foreign skills,
   plugin-provided entries, and command metadata. Codex's `.system` and
   `codex-primary-runtime` entries are none of those, yet they occupy the same
   budget — as do the **2 listed Codex plugin-cache entries**
   (`browser:control-in-app-browser`, `computer-use:computer-use`), for **10
   listed bundled-plus-plugin entries** in total. Omitting them understates the
   effective catalog materially. They are counted, with distinct origin labels so
   the evidence stays honest about what they are.
2. **SC-06 byte-identity is delivered by splitting the payload.** Dates come from
   the policy record, not the clock; `--json` emits a byte-identical `evidence`
   object, with wall-clock and host in a non-normative `envelope`. The existing
   report embeds `utc_now_iso()` (`skill_standardizer_lib.py:1178`), which is why
   the split is needed. This is an implementation choice, not a contract gap.
3. **`full` is not deployable at the current catalog size, and that is correct.**
   SC-04 gives it no exemption, so EV-LEG-01's whole-catalog link is reported as
   nonconformant full-canonical membership, never migrated into a deployable
   `full` realization.

**What phase 1's first honest run will say.** Measured 2026-08-01 against a
budget of 5,440: ordinary sessions (`~`, `~/Dev`, `~/Dev/ops`, `~/Dev/habits-ai`)
carry 46 entries demanding ~5,211 — **96% against a 90% ceiling**, already
non-deployable. `blueprint-finance` is at 47 entries / ~5,341 / 98%. And two
repos are **actively truncating**: `viral` at 52 entries / ~6,037 / 111% with 19
truncated descriptions, and `dojo` itself at 95 entries / ~9,616 / **177%** with
94 truncated. The cause in both is a `.agents/skills → ../skills` symlink putting
the whole canonical catalog at project scope. So the first honest output of this
work is not "here is your headroom" — it is that routing signal is being silently
destroyed in two repositories today and ordinary sessions have already crossed
the ceiling. Every figure here is a dated measurement; the verifier recomputes
all of them at verify time.

## Map Before You Cut

### The data/call path today

There is no profile concept anywhere. Three independent paths produce or refresh
the state a profile would govern:

1. **`scripts/gen_harness_adapters.py`** — `main()` at line 235. Lines 261–269
   create `<repo>/{.claude,.agents,.agent}/skills` as relative symlinks to
   `../skills` via `ensure_symlink()` (line 111), i.e. **one directory link that
   exposes the entire canonical catalog at project scope**. Lines 291–298 link
   each skill's `commands/*.md` into `.claude/commands/`. Both are gated by
   `--skip-symlinks`, which CI passes, so CI never creates them. This is the
   whole-catalog widener EV-NEG-05 and EV-LEG-01 target.
2. **`skills/skill-standardizer/scripts/sync.py`** — `main()` line 132 calls
   `build_audit_report()` then `apply_actions()` (line 152). The widening branch
   is `skill_standardizer_lib.py:649`, `if enforce_mirror and not only_existing:`
   — it proposes creating every canonical skill missing from each `global-*`
   root. `--only-existing` (line 100) is intersection-only and *structurally
   cannot change membership*; `--enforce-mirror` (line 85) can, and did on
   2026-07-31 (ops register R18). Documented as a runbook in
   `skills/skill-standardizer/SKILL.md:156-169` and
   `skills/skill-standardizer/commands/standardize-skills.md:29-32`.
3. **`skills/skill-installer/scripts/install-skill-from-github.py`** —
   `_default_dest()` (line 255) resolves to `~/.{claude,codex,agents}/skills`;
   `_copy_skill()` (line 184) adds an entry. `README.md:39-40` demonstrates it
   with `--repo davisbuilds/dojo --path skills/<skill-name>`, so it is a
   documented path that adds an unselected dojo skill to a managed target.

Read-only today and to remain so: `hooks/session-start-skill-drift.sh:27` runs
`audit.py --format json` and pipes it to a notifier; it never calls `sync.py`.
`hooks/post-tool-use-regen-manifest.sh` runs `gen_skill_docs.py`,
`generate_skills_manifest.py`, `gen_catalog.py` — none touch target state.
`hooks/session-start-skill-catalog.sh` reads `skills.json` and emits context.
These three are recorded as SC-12-conforming and pinned by a test (Task 9), not
assumed.

### Seams chosen, and why they beat the obvious option

- **Effective-catalog observation reuses `skill_standardizer_lib`, not a new
  scanner.** `resolve_context()` (line 127) already classifies canonical /
  `global-agents` / `global-codex` / `global-claude` / `plugin-cache` / local
  roots; `scan_root()` (line 202) already distinguishes symlink from concrete,
  records `link_target`, and computes a content identity via `hash_directory()`
  (line 176) with a stable ignore set. `is_plugin_cache_path()` (line 100)
  already isolates plugin caches. Writing a second scanner would duplicate the
  drift semantics SC-05/SC-09 need and let the two disagree. The profiles
  package imports it; it does not fork it.
- **Routing coverage reuses `run_trigger_evals.py`, not a new evaluator.**
  `--skills-root` (line 416) and `--skills` (line 417) already exist, and IDF is
  computed over the *entire* root while `--skills` narrows only the scored set
  (documented at line 130-136). Pointing `--skills-root` at an observed target
  root therefore scores selected dojo members against the foreign competitors
  actually present there — exactly SC-10 — with no new scoring code.
- **The verifier is a new read-only package, not a flag on an existing
  generator.** `gen_harness_adapters.py` is a writer with a `--check` mode over
  *committed sidecars*; hanging effective-catalog budget evaluation off it would
  couple a read-only contract check to a mutating tool and put it behind
  `--skip-symlinks` in CI. A separate package keeps phase 1 free of mutation
  authority by construction (spec Handoff).
- **Phase 2 does not extend `apply_actions()`.** This was the closest existing
  seam and it was assessed and rejected on evidence.
  `skill_standardizer_lib.py:1113-1166` iterates actions and, per action, calls
  `_backup_destination()` (line 1025), which `shutil.move`s the destination away
  (line 1043) *before* `_replace_with_copy()` recreates it. There is therefore a
  window in which the prior realization is neither active nor replaced — it is
  recoverable from backups, but not active. EV-REC-01 requires that interruption
  *before* activation leave the prior realization **active**, and EV-REC-03
  requires no mixed intermediate state be acceptable. A per-action
  move-then-write loop cannot provide either. Task 12 therefore adds a
  stage → activate → commit applicator in `scripts/profiles/apply.py`, reusing
  the standardizer's hashing and copy helpers but not its action loop.
  `apply_actions()` is left untouched.
- **SC-13 is enforced at each writer, not by a wrapper.** A wrapper that "all
  refreshes should go through" is exactly the indirect path SC-13 forbids;
  anyone running the documented command directly would bypass it. Tasks 13 and 14
  put the refusal inside the three writers themselves.

### The whole property class SC-13 must cover

Enumerated by grepping every reference to a global skills root and every
adapter-writing script, then reading each hit:

| # | Entrypoint | Can it widen a target? | Disposition |
|---|---|---|---|
| 1 | `scripts/gen_harness_adapters.py:261-269` | Yes — whole-catalog dir symlink | Task 13 |
| 2 | `scripts/gen_harness_adapters.py:291-298` (`.claude/commands`) | Yes — whole-catalog command surface | Task 13 |
| 3 | `skills/skill-standardizer/scripts/sync.py` `--enforce-mirror --apply` | Yes — installs every canonical skill globally | Task 14 |
| 4 | `skills/skill-standardizer/scripts/sync.py` `--only-existing` | **Yes, via the ungated deprecated-alias path** (lines ~455-495, ~895-940) | Task 14 (guard, not merely a neutrality test) |
| 5 | `skills/skill-standardizer/scripts/audit.py` | No (read-only) but plans #3's actions | Task 14 (profile-bounded planning) |
| 6 | `skills/skill-installer/scripts/install-skill-from-github.py:184,255` | Yes — adds an unselected dojo skill to a managed root | Task 14 |
| 7 | `hooks/session-start-skill-drift.sh` | No — audit only | Task 9 (pinned by test) |
| 8 | `hooks/post-tool-use-regen-manifest.sh` | No — manifest/catalog only | Task 9 (pinned by test) |
| 9 | `hooks/session-start-skill-catalog.sh` | No — reads `skills.json`, emits context | Task 9 (pinned by test) |
| 10 | `README.md:31-40` steps 4 and 5 | Documented invocations of #1 and #6 | Task 16 |
| 11 | `docs/system/OPERATIONS.md:140-152` | Documented invocation of #1 | Task 16 |
| 12 | `.github/workflows/skill-contract-pilot.yml` | No — passes `--skip-symlinks` | Task 9 (new gate added here) |

## Task Breakdown

### Task 0: Deterministic listing probe and budget inputs

**Objective**

Build the read-only probe every later task depends on. Codex ships two
deterministic debug commands that dump exactly what this contract needs, so the
probe is a scriptable parse — no LLM in the loop, no stored-artifact staleness,
re-runnable on demand at verify time.

**Files**

- Create: `scripts/profiles/probe_codex.py`
- Create: `tests/fixtures/profiles/prompt-input-dojo-2026-08-01.json`
- Create: `tests/fixtures/profiles/prompt-input-blueprint-2026-08-01.json`
- Create: `tests/fixtures/profiles/prompt-input-viral-2026-08-01.json`
- Test: `tests/test_profiles_probe.py`

**Dependencies**

None

**Research Context**

- `codex debug prompt-input` renders the model-visible prompt input list as JSON,
  including the whole `<skills_instructions>` block. `codex debug models` returns
  the model catalog as JSON. Both verified present via `codex debug --help`.
- `codex debug models` reports `context_window: 272000`,
  `max_context_window: 272000`, and a *separate*
  `effective_context_window_percent: 95` for `gpt-5.6-sol`.
  `codex-rs/core/src/session/mod.rs:3303` passes
  `turn_context.model_info.context_window` into `default_skill_metadata_budget`,
  i.e. the **full** window, not the 95%-effective one. That gives
  `272000 * 2 / 100 = 5,440`, which is what the behavioral bracket in step 6
  independently confirms.
- Reproduced directly in `~/Dev/dojo` on 2026-08-01: the block contains **95**
  entries, of which **2** are namespaced plugin entries (`browser:…`,
  `computer-use:…`). Paths render in alias form (`r2/imagegen/SKILL.md`), so the
  alias branch of `render.rs` is the live mode here.
- The first sampled entry ends mid-word (`…transparent-bac (file: …)`),
  confirming description truncation is occurring live, not hypothetically.

**Implementation Steps**

1. Implement `probe(cwd)` running `codex debug prompt-input` in that working
   directory and extracting the `<skills_instructions>` block from the JSON.
2. **Parse each entry anchored on the trailing ` (file: <path>)`, not on the
   first colon.** Plugin entries render as `namespace:name`, so a
   split-on-first-colon parser drops them silently and reports a confident zero —
   the failure mode this program has already hit repeatedly. Allow colons inside
   the name; take the description as everything between the first `: ` after the
   name and the trailing file locator.
3. Implement `models()` running `codex debug models`, returning `slug`,
   `context_window`, `max_context_window`, and
   `effective_context_window_percent` so the policy can record which one it used
   and why.
4. Classify each entry's `origin` from its resolved path: `dojo-managed`,
   `foreign`, `harness-bundled` (`.system`, `codex-primary-runtime`),
   `plugin` (namespaced, from a Codex plugin cache), and record its scope
   (user vs project).
5. Store one probe fixture per shape for hermetic tests — a dojo-rooted capture
   (heavy, truncating), a `blueprint-finance` capture (near-boundary, clean), and
   a `viral` capture (over-boundary, truncating). Tests read fixtures; only the
   live verification steps invoke `codex`.
6. Record the **behavioral budget bracket** as a derived assertion:
   `blueprint-finance` demands ~5,341 and does not truncate; `viral` demands
   ~6,037 and does. So the true budget lies in (5,341, 6,037), which excludes
   5,168 (2% of the 95%-effective window) and contains 5,440 (2% of the full
   window). The probe records this reasoning; the verifier still reads the window
   from `codex debug models` at verify time rather than trusting either number.

**Verification**

- Run: `.venv/bin/python scripts/profiles/probe_codex.py --cwd . --json | .venv/bin/python -c "import json,sys; d=json.load(sys.stdin); print(len(d['entries']), sum(1 for e in d['entries'] if e['origin']=='plugin'))"`
- Expect: a nonzero entry count and a nonzero plugin count, both derived from the
  live probe rather than compared to a stored constant.
- Run: `.venv/bin/python -m pytest tests/test_profiles_probe.py -q`
- Expect: all pass.

**Test Discovery Verified**

- Runner/discovery evidence: the repo has no `pytest.ini`/`pyproject.toml`; CI
  and `docs/system/OPERATIONS.md:31` both invoke `python -m pytest tests/ -q`,
  which collects any `tests/test_*.py`. `.venv/bin/python -m pytest tests/ -q
  --collect-only` currently reports `309 tests collected`.
- Literal proof: `.venv/bin/python -m pytest tests/test_profiles_probe.py -q`

**Done When**

- The parser recovers **both** namespaced plugin entries from the dojo fixture. A
  split-on-first-colon parser returns 0 here; the test asserts the count is
  nonzero *and* that both names contain a colon, so the anchor-on-`(file:` rule
  is actually exercised (the zero rule).
- Origin classification is proven against cases known to exist before any absence
  is reported: **at least one** `foreign`, **at least one** `harness-bundled`,
  **at least one** `plugin`, and
  `skill-creator` present at least twice with different origins in the dojo
  fixture (SC-04, SC-05).
- Counts are **never** compared against a hardcoded total. Every assertion is
  either a non-degeneracy floor (at least one) or a relation between two probe
  outputs;
  a test asserting `entries == 95` is itself a defect (spec Assumptions).
- **143 `SKILL.md` files exist across the plugin caches while only 2 are listed.**
  A test asserts the probe's plugin count is far below the on-disk count, pinning
  that the probe measures the listing and never the filesystem.
- `models()` returns `context_window` and `effective_context_window_percent` as
  distinct fields, and the recorded policy states which was used and cites
  `session/mod.rs:3303` as the reason (SC-04).
- The behavioral bracket holds: the non-truncating near-boundary capture demands
  less than the truncating over-boundary capture, and the resolved budget lies
  strictly between them (SC-04).

### Task 1: Profile definitions

**Objective**

Turn the spec's profile vocabulary into reviewable data: one file per profile so
a duplicate definition is a real, detectable condition rather than a silently
last-wins YAML key.

**Files**

- Create: `profiles/core.yaml`
- Create: `profiles/engineering.yaml`
- Create: `profiles/research.yaml`
- Create: `profiles/design.yaml`
- Create: `profiles/knowledge.yaml`
- Create: `profiles/shipping.yaml`
- Create: `profiles/skill-authoring.yaml`
- Create: `profiles/full.yaml`
- Create: `profiles/README.md`
- Create: `scripts/profiles/__init__.py`
- Create: `scripts/profiles/definitions.py`
- Test: `tests/test_profiles_definitions.py`

**Dependencies**

None

**Research Context**

- All 12 SC-02 anchors and all 8 SC-03 `core` members exist in `skills/`
  (verified by listing `skills/`, 50 entries of which `_fragments` is not a
  skill, leaving 49). `gh-commit-push-pr` and `vercel-deploy` are present in the
  canonical catalog but are **not** currently installed in `~/.agents/skills` —
  which is expected and is precisely the gap a declaration closes.
- `skills.json` entries carry `{name, description, path, version}`;
  `definitions.py` resolves membership against that manifest.

**Implementation Steps**

1. Define the schema in `definitions.py`: `name`, `kind` (`baseline` |
   `overlay` | `inspection`), `members` (list of canonical skill names),
   `description`. Load with `yaml.safe_load` and a duplicate-key-rejecting
   loader so a repeated key inside one file is an error, not last-wins.
2. Author `core.yaml` with exactly the SC-03 eight: `brainstorming`,
   `first-principles`, `write-spec`, `write-plan`, `diagnose`, `local-review`,
   `test-strategy`, `verify-before-complete`. Record in its `description` that
   membership was set from observed session use on 2026-07-31 and cite the spec,
   so the file carries its own provenance.
3. Author the six overlays. Each must contain its SC-02 anchors and at least two
   non-`core` members. Anchors: engineering → `create-cli`, `secure-code`;
   research → `deep-research`, `research-architect`; design → `design-critique`,
   `web-design-guidelines`; knowledge → `obsidian-markdown`, `session-retro`;
   shipping → `gh-commit-push-pr`, `vercel-deploy`; skill-authoring →
   `skill-creator`, `skill-standardizer`.
4. Author `full.yaml` with `kind: inspection` and `members: "*"` — a sentinel
   resolved against the manifest at resolve time, so it tracks the catalog and
   cannot go stale the way a pinned list would (the defect the spec's revision 7
   removed from EV-LEG-01).
5. Implement `load_definitions(profiles_dir)` returning definitions sorted by
   name, raising on: unreadable YAML, missing required key, unknown `kind`, two
   files declaring the same `name`, a member absent from `skills.json`, an
   overlay with fewer than two non-`core` members, an overlay missing an anchor,
   and `full` declaring anything other than the sentinel.
6. Write `profiles/README.md` stating that these files are reviewed data,
   changing membership changes profile identity, and pointing at the spec.

**Verification**

- Run: `.venv/bin/python -m pytest tests/test_profiles_definitions.py -q`
- Expect: all pass, including one rejection test per failure mode in step 5.
- Run (negative): copy `profiles/core.yaml` to `profiles/core-copy.yaml`, then
  `.venv/bin/python -c "import sys; sys.path.insert(0,'scripts'); from profiles.definitions import load_definitions; load_definitions('profiles')"`
- Expect: raises with a message naming both files and the duplicated profile
  name; remove the copy afterwards.

**Test Discovery Verified**

- Runner/discovery evidence: `python -m pytest tests/ -q` (CI step "Run
  regression tests") collects `tests/test_*.py`; no config file narrows it.
- Literal proof: `.venv/bin/python -m pytest tests/test_profiles_definitions.py -q`

**Done When**

- Exactly 8 definition files load. `core` has exactly the 8 SC-03 members
  (SC-03). Each of the 6 overlays has **≥ 2 non-`core` members** and contains
  both of its SC-02 anchors (SC-02).
- `full` resolves to **all 49 canonical skills**, computed from `skills.json` at
  resolve time; the test asserts the resolved count equals
  `len(json.load(open("skills.json"))["skills"])` rather than a literal, so
  authoring a skill cannot silently falsify it (SC-02, EV-LEG-01).
- Every resolved member of every profile exists in `skills.json` (SC-02).
- Each of the 8 rejection cases in step 5 raises, and each rejection test asserts
  the *message* names the offending profile and member — a bare raise does not
  pass (SC-01).

---

### Task 2: Resolution, identity, and selection validation

**Objective**

Make composition deterministic and give every composition a stable identity, so
"the same profile" is a checkable claim rather than a naming convention.

**Files**

- Create: `scripts/profiles/resolve.py`
- Test: `tests/test_profiles_resolve.py`

**Dependencies**

Task 1

**Implementation Steps**

1. Implement `resolve(selection, definitions, catalog)` where `selection` is a
   list of profile tokens. Membership is set union over `core` plus the named
   overlays; the result is sorted lexically; duplicate inclusions collapse to one
   member.
2. Reject, each with a distinct error code: unknown profile name; a selection
   with no `core`; an empty or `core`-only capability overlay; the same overlay
   token named more than once in one request; `full` combined with any other
   token. Accept member overlap across two *different* valid overlays as ordinary
   set union (the spec's explicit non-error case).
3. Implement `profile_identity(selection, definitions, resolved)` — a SHA-256
   over a canonical JSON serialization of `{normalized_selection,
   definition_bodies, resolved_members}`, all lexically ordered. Composition
   order must not reach the hash.
4. Implement `realization_identity(profile_identity, canonical_revision,
   target_identity, harness_model_version, budget_policy_identity)` as a second
   SHA-256 over those five fields. A canonical-revision change therefore yields a
   different realization identity by construction (spec Evaluation: "a canonical
   revision change is a new realization request, never an idempotent replay").
5. Add a permutation test that enumerates **all 720 permutations** of the six
   overlay tokens and asserts a single distinct resolved-member tuple and a
   single distinct `profile_identity` across all of them.

**Verification**

- Run: `.venv/bin/python -m pytest tests/test_profiles_resolve.py -q`
- Expect: all pass; the permutation test reports `len(set(identities)) == 1` over
  720 inputs.

**Test Discovery Verified**

- Runner/discovery evidence: as Task 1 — `pytest tests/` collects `tests/test_*.py`.
- Literal proof: `.venv/bin/python -m pytest tests/test_profiles_resolve.py -q`

**Done When**

- All **720** permutations of the six overlays yield one resolved-member tuple
  and one `profile_identity` (SC-02, EV-CON-02). A test over fewer than the full
  permutation set does not satisfy this.
- Each of the five rejection cases in step 2 returns its own distinct error code,
  asserted individually (EV-NEG-01).
- Member overlap across two different overlays resolves successfully and collapses
  to one member — asserted with a constructed pair sharing ≥ 1 member, so the
  accept path is exercised and not merely the reject paths (EV-NEG-01).
- Changing only `canonical_revision` changes `realization_identity` while leaving
  `profile_identity` unchanged (SC-01, spec Authority "Retry and concurrency").

---

### Task 3: Codex listing model and versioned budget policy

**Objective**

Compute listing cost with **Codex's own arithmetic** over **untruncated source
descriptions**, and detect truncation as a first-class nonconformance signal.

**Files**

- Create: `scripts/profiles/budget.py`
- Create: `profiles/policies/codex.yaml`
- Test: `tests/test_profiles_budget.py`

**Dependencies**

Task 0

**Research Context**

Read from `/Users/dg-mac-mini/Dev/_clones/codex` at `f57467275c`,
`codex-rs/core-skills/src/render.rs`:

- `default_skill_metadata_budget` (line 138): `Tokens(max(1, window * 2 / 100))`
  when the context window is known and positive; otherwise `Characters(8_000)`.
  **Either/or, never combined.** Called from
  `codex-rs/core/src/session/mod.rs:3303` with
  `turn_context.model_info.context_window` — the **full** window.
- `APPROX_BYTES_PER_TOKEN = 4` (line 23); `approx_token_count_from_bytes`
  (line 110) is `(bytes + 3) / 4`.
- An entry renders as `format!("- {}: {} (file: {})", name, description, path)`
  (line 524), or `format!("- {}: (file: {})", name, path)` when the description
  is empty (line 522). `line_cost` (line 589) costs the line **plus a trailing
  newline**.
- Descriptions are pre-truncated to
  `MAX_DEFAULT_CONTEXT_SKILL_DESCRIPTION_CHARS = 1_024` (line 20) with a `"..."`
  suffix (line 21) — a *separate* mechanism from budget-driven shortening.
- Codex renders in one of two modes — absolute paths, or an alias table
  (`- \`r{index}\` = \`{root}\``, line 818) whose `table_cost` is subtracted from
  the limit (line 664) — choosing via `aliased_render_is_better` (line 184).
  The live dojo probe renders in **alias** mode (`r2/imagegen/SKILL.md`).

**The instrument hazard this task exists to avoid.** Codex shortens descriptions
until they fit and then reports a listing that, by construction, fits. Calibrating
a cost model against captured listing output would therefore certify *exactly the
failure this contract exists to catch*: a truncated catalog would score at or
under budget every time. Cost is computed from **untruncated `description`
frontmatter in the source `SKILL.md`**, run through the arithmetic above. The
live listing is evidence about discovery, precedence, render mode, and truncation
— never about cost.

**Implementation Steps**

1. Port the primitives verbatim: `approx_token_count_from_bytes(n) == (n + 3) // 4`
   over UTF-8 **bytes**, `line_cost(entry)` including the trailing newline,
   `budget_for_window(window)`, and the 1,024-char description cap.
2. Implement `demand(entries)` — the cost of the listing Codex *would* render if
   nothing were shortened — summing `line_cost` over entries whose descriptions
   come from source frontmatter, plus the alias-table cost when alias mode wins.
   Compute both render modes and take the lower, mirroring
   `aliased_render_is_better`; record which mode won.
3. Implement the **truncation detector**: for every listed entry, compare the
   probed `listed_description` against the entry's `source_description`. Any
   inequality (beyond the deterministic 1,024-char cap) sets `truncated: true`
   for that entry and makes the target **nonconformant regardless of computed
   cost**. This is a conformance signal in its own right, not a warning.
4. Implement the SC-04 comparison as exact integer arithmetic:
   `deployable = demand * 10_000 <= limit * 9_000`. No float, no rounding before
   comparison.
5. Write `profiles/policies/codex.yaml`: harness, harness version, model, the
   window value **and which field it came from** (`context_window`, with
   `effective_context_window_percent` recorded alongside and explicitly *not*
   used, citing `session/mod.rs:3303`), listing representation, estimator
   (`vendor-source`), vendor path and pinned revision `f57467275c`, measurement
   date, the probe command, and a `policy_identity` hash. The window is re-read
   from `codex debug models` at verify time; the file records provenance, not a
   frozen number.
6. Add a `claude-code` policy stub declaring `authoritative: false` and
   `status: audit-only`, so Claude targets are explicitly unsupported rather than
   silently missing (SC-04, spec Problem).
7. Build boundary fixtures at exactly 8,900 / 9,000 / 9,100 basis points. Because
   entry costs are integers, choose each fixture's `limit` so it lands exactly on
   its basis point; assert the constructed demand/limit pair reproduces the
   intended basis point *before* asserting the verdict.
8. Add the **SC-03 / EV-NEG-02 fit proof** as its own named test:
   `test_core_plus_one_overlay_plus_three_foreign_fits` — resolve `core` plus one
   non-empty capability overlay, add three foreign entries, score against the
   live Codex policy, and assert deployable. This is the single case standing
   between this contract and zero deployable harnesses, so it is named and
   asserted rather than implied by a general boundary test.

**Verification**

- Run: `.venv/bin/python -m pytest tests/test_profiles_budget.py -q`
- Expect: all pass, including boundary, truncation, and fit-proof tests.
- Run: `.venv/bin/python -m pytest tests/test_profiles_budget.py -q -k vendor_parity`
- Expect: pass — the ported arithmetic reproduces `render.rs`'s worked constants.
- Run: `.venv/bin/python -m pytest tests/test_profiles_budget.py -q -k core_plus_one_overlay`
- Expect: pass — `core` + one overlay + three foreign entries is deployable.

**Test Discovery Verified**

- Runner/discovery evidence: as Task 1.
- Literal proof: `.venv/bin/python -m pytest tests/test_profiles_budget.py -q`

**Done When**

- **Cost never derives from probed listing text.** A test feeds a fixture whose
  probed descriptions are shortened relative to source and asserts the computed
  demand matches the **source-derived** figure, not the shortened one. A model
  calibrated on captured output fails this test — which is the point (SC-04).
- **Truncation alone makes a target nonconformant**, even when computed demand is
  under budget: asserted with a fixture that is truncated *and* cheap (SC-04,
  SC-05).
- The truncation detector fires on **live state today** — the dojo-rooted probe
  reports `truncated: true` — so the detector is proven against a case known to
  exist before any clean result is trusted (the zero rule).
- 8,900 bps and 9,000 bps are deployable; 9,100 bps is not; each fixture first
  asserts its own basis point (EV-NEG-02).
- **`core` + one non-empty overlay + three foreign entries is deployable against
  the live Codex policy**, proven by a named test (SC-03, EV-NEG-02).
- An unknown limit, a stale policy, an uninspectable scope, and a failed
  source/listing reconciliation each yield `unsupported`, distinct from
  `nonconformant` (SC-04, EV-LEG-03).
- An empty catalog is `unsupported: no entries observed`, never deployable (spec
  Evaluation).
- `full` is scored through the identical code path with no exemption (SC-04).
- The policy records `context_window` versus `effective_context_window_percent`
  and cites the caller that decides between them; the recorded budget is
  consistent with the behavioral bracket from Task 0 (SC-04).
### Task 4: Effective-catalog observation

**Objective**

Enumerate what each target actually exposes — from the probe, not the filesystem
— and model Codex's real duplication behavior rather than an assumed one.

**Files**

- Create: `scripts/profiles/observe.py`
- Test: `tests/test_profiles_observe.py`

**Dependencies**

Task 0, Task 3

**Assumptions Verified**

- `skills/skill-standardizer/scripts/skill_standardizer_lib.py:202` (`scan_root`)
  returns a `RootInventory` whose `SkillEntry` carries `is_symlink`,
  `link_target`, `resolved_path`, and `dir_hash` — the topology-plus-content
  identity SC-05 and SC-09 need. It skips dotted and underscore-prefixed entries
  (lines 211–216) and records a directory without `SKILL.md` as `invalid_entries`
  (line 226).
- `skill_standardizer_lib.py:100` (`is_plugin_cache_path`) hardcodes the needle
  `"/.claude/plugins/cache"` — **a Claude-only path Codex never reads.** Codex's
  own cache is `~/.codex/plugins/cache`, and 2 of its entries
  (`browser:control-in-app-browser`, `computer-use:computer-use`, both from
  `openai-bundled`) are listed in every session. Plugin-cache classification must
  therefore be per-harness; the existing helper cannot be used as-is for Codex.
- `skill_standardizer_lib.py:24` (`KNOWN_NON_SKILL_DIRS`) exempts
  `codex-primary-runtime` from `global-codex`, so it is invisible to the scan
  today — which is why the recorded decision to count bundled entries must add them back
  deliberately.

**Two verified mechanics that change the model.**

1. **Codex does not shadow by name across roots.** Unlike Claude Code, it lists
   both copies and charges for both. A dojo-rooted session carries 32 duplicated
   names / 33 redundant entries out of 95, and `skill-creator` is duplicated in
   every session (dojo's plus Codex's `.system`). SC-04 says shadowed names are
   counted "according to actual harness behavior" — for Codex the actual
   behavior is **no shadowing**, so duplicates are two entries and two costs.
2. **The Codex project-scope root is `.agents/skills` only** — not
   `.claude/skills`, not `.agent/skills`. Verified across six working
   directories. dojo's and viral's `.agents/skills → ../skills` symlinks are the
   sole cause of their truncation, which makes Task 13's cut narrower and more
   precisely targeted than "the three harness dirs".

**Implementation Steps**

1. Take the **probe** (Task 0) as the authority on what is listed and at what
   scope. Use `scan_root` only to attach content identity (`dir_hash`),
   topology (`is_symlink`, `link_target`), and source descriptions to entries the
   probe already reported. The filesystem never adds an entry the probe did not
   list.
2. Import the standardizer library by inserting
   `skills/skill-standardizer/scripts` on `sys.path` (it uses a bare
   `from skill_standardizer_lib import ...`; see `sync.py:9`). Confine the
   coupling to one helper.
3. Implement per-harness plugin-cache classification: `~/.claude/plugins/cache`
   for Claude, `~/.codex/plugins/cache` for Codex. Do **not** reuse
   `is_plugin_cache_path` for Codex; it would misclassify Codex's listed plugin
   entries as non-plugin and hide them.
4. Model duplication per harness: for Codex, a name appearing in two roots is
   **two effective entries with two costs**, with the duplication relationship
   recorded. Reserve the single-entry shadowing model for a harness that
   documents that precedence; where precedence is undocumented, mark the scope
   pair `unsupported` rather than guessing.
5. Attach `source_description` from canonical `SKILL.md` frontmatter to every
   `dojo-managed` entry so Task 3 can compute demand and detect truncation.

**Verification**

- Run: `.venv/bin/python -m pytest tests/test_profiles_observe.py -q`
- Expect: all pass.
- Run (live, read-only): `.venv/bin/python -c "import sys; sys.path.insert(0,'scripts'); from profiles.observe import observe; r=observe(cwd='.'); print(len(r.entries), sum(1 for e in r.entries if e.origin=='foreign'), sum(1 for e in r.entries if e.duplicate_of))"`
- Expect: all three numbers nonzero, each derived from the live probe. **No
  expected constant is asserted here** — an earlier revision of this plan
  expected `32 1` from a filesystem count, which was both wrong and an instance of
  the exact error this plan names as its second methodological assumption.

**Test Discovery Verified**

- Runner/discovery evidence: as Task 1.
- Literal proof: `.venv/bin/python -m pytest tests/test_profiles_observe.py -q`

**Done When**

- Every observed entry originates in probe output. A test injects an on-disk
  skill that the probe fixture does not list and asserts it is **absent** from
  the observation and contributes **zero** cost (SC-04, spec Assumptions).
- Non-degeneracy floors only, never totals: **at least one** foreign, **at least
  one** harness-bundled, **at least one** plugin, and **at least one**
  project-scope entry observed in the dojo fixture (SC-05).
- **Duplication is counted, not collapsed:** `skill-creator` appears twice in the
  dojo fixture with distinct origins and **both** contribute cost; a test asserts
  the total demand strictly exceeds the de-duplicated demand, so a collapsing
  model fails (SC-04).
- Codex plugin entries are classified as `plugin` via the **Codex** cache path; a
  test asserts that classifying with the Claude needle yields zero and is
  therefore wrong, pinning the per-harness split (SC-05).
- Project scope is attributed to `.agents/skills` for Codex; a fixture with
  `.claude/skills` and `.agent/skills` present but no `.agents/skills` yields
  **zero** project-scope Codex entries (SC-04).
- No observation path writes: a recursive hash of the fixture tree is
  byte-identical before and after (SC-12, spec Authority "Verifier").
### Task 5: Conformance evidence and drift detection

**Objective**

Assemble the deterministic report SC-06 enumerates, and detect every legacy
topology SC-09 names — without mutating anything.

**Files**

- Create: `scripts/profiles/evidence.py`
- Test: `tests/test_profiles_evidence.py`
- Test fixture: `tests/fixtures/profiles/catalog/` (the spec's fixed catalog
  fixture: full canonical catalog at the selected revision, the current curated
  subset, every canonical skill absent from it, ≥ 3 foreign entries, and both
  user- and project-scope observations)

**Dependencies**

Task 2, Task 3, Task 4

**Implementation Steps**

1. Implement `build_evidence(selection, targets, policy)` producing the SC-06
   field set: selected profile composition and identity, canonical revision,
   resolved names and versions, missing and unexpected managed entries, content
   and topology drift, foreign entries, shadowed names, plugin-provided entries,
   target scopes, harness and budget-policy versions, budget utilization,
   included-skill count, skills with routing fixtures, assertions executed,
   assertion outcomes, and observed collision candidates.
2. Split the payload per recorded decision 2: a byte-identical `evidence` object
   whose every date comes from the *policy record*, and a non-normative
   `envelope` with wall-clock and hostname. `--json` emits `evidence` only.
   Serialize with `json.dumps(..., sort_keys=True, ensure_ascii=False)` and
   lexically order every list.
3. Detect the SC-09 legacy topologies without mutation: (a) a whole-catalog
   directory link (a scope root that *is* a symlink to a canonical `skills/`
   tree) reported as **full canonical membership at the selected revision, not as
   an implicit `full` profile**; (b) an intersection-only installation (managed
   names are a proper subset of the profile with no unexpected entries); (c) a
   concrete secondary copy (a `global-codex`/`global-claude` entry that is a
   directory rather than a symlink into `global-agents`); (d) version-skewed
   managed content (`dojo-managed-drifted`).
4. Implement the dirty-state classification narrowly (EV-NEG-04): uncommitted
   changes to a *selected* profile definition or a *selected* canonical skill →
   audit-only; unrelated working-tree changes → no effect; a source with no
   verifiable canonical revision → audit-only even when hashable. Determine
   "selected" by intersecting `git status --porcelain` paths with the resolved
   member paths plus `profiles/`.
5. **Define `unprofiled` as a first-class target state with its own verdict.**
   No profile can be applied until Task 12, so for the whole of phase 1 **every
   real target is unprofiled** — this is phase 1's main operating mode, not an
   edge case. An unprofiled target reports `state: unprofiled` with full
   observation, demand, limit, headroom, and truncation evidence, and exits **2**
   (evaluated, not conformant). It is never `conformant: true` and never
   `unsupported` — it is a target with no declaration to compare against, which is
   precisely the gap the contract exists to close.
6. Define exit semantics for the caller: a full conformant evaluation → 0;
   evaluated drift, unsupported policy, or nonconformance → 2; evaluation could
   not finish → 1. A report that could not finish is marked
   `partial: true` and **cannot** be emitted with exit 0 — assert this as an
   invariant in code, not only in a test.

**Verification**

- Run: `.venv/bin/python -m pytest tests/test_profiles_evidence.py -q`
- Expect: all pass.
- Run (determinism): `.venv/bin/python -c "import sys,hashlib; sys.path.insert(0,'scripts'); from profiles.evidence import build_evidence_json as b; import json; a=b('tests/fixtures/profiles/catalog'); c=b('tests/fixtures/profiles/catalog'); print(hashlib.sha256(a.encode()).hexdigest()==hashlib.sha256(c.encode()).hexdigest())"`
- Expect: `True`

**Test Discovery Verified**

- Runner/discovery evidence: as Task 1.
- Literal proof: `.venv/bin/python -m pytest tests/test_profiles_evidence.py -q`

**Done When**

- Two runs over unchanged inputs produce **byte-identical** `evidence` JSON,
  asserted by SHA-256 equality, and a run with a perturbed input produces a
  *different* hash — so byte-identity is not achieved by emitting a constant
  (SC-06, EV-CON-02).
- The report contains **all 16** SC-06 fields; the test asserts the exact field
  set, so adding a field or dropping one fails (SC-06).
- The whole-catalog-link fixture is reported as full canonical membership with a
  count read from `skills.json` at check time (currently 49), **not** as an
  implicit `full` profile, and **not** as deployable (SC-05, SC-09, EV-LEG-01,
  recorded decision 3).
- The intersection-only-with-stale-concrete-secondary fixture reports all four
  difference classes — missing, unexpected, content, topology — each non-empty,
  and the fixture tree hash is byte-identical before and after the audit
  (SC-09, SC-11, EV-LEG-02).
- A dirty checkout touching one selected skill is `audit-only`; a dirty checkout
  touching only `docs/` is not; an unidentifiable source revision is
  `audit-only` (EV-NEG-04).
- `partial: true` with exit 0 is unreachable — asserted by a test that forces a
  truncated evaluation and checks both the flag and the exit code (spec Contract).
- An **unprofiled** target reports `state: unprofiled` with full budget and
  truncation evidence and exits 2 — distinct from both `conformant` and
  `unsupported`. Asserted against the live-shaped fixture, since this is the
  state every real target occupies throughout phase 1 (SC-01, SC-06).

---

### Task 6: Anchor routing fixtures and profile-scoped routing coverage

**Objective**

Make SC-10 satisfiable and then satisfy it. Evaluate routing against the catalog
a user actually receives — selected members **plus the foreign and bundled
competitors present at that target**.

**Decision (was deferred, now settled): author the twelve anchor fixtures.**
SC-10 requires every capability overlay to contribute a positive and a
negative-or-collision assertion **for its required anchors**. None of the twelve
SC-02 anchors declares a trigger fixture today — the only three that exist
(`blind-spots`, `test-strategy`, `verify-before-complete`) are not anchors. So
SC-10's per-overlay clause is unreachable without new fixtures, and emitting
`coverage-gap` while the traceability table claims SC-10 proven would be a false
completion claim. This task therefore authors fixtures for the twelve named
anchors. That is targeted work on skills the contract itself names, not the
catalog-wide trigger manufacturing the spec's Assumptions rule out; the remaining
37 skills keep their honest `coverage-gap` reporting.

**Files**

- Create: `skills/create-cli/evals/trigger-cases.json`
- Create: `skills/secure-code/evals/trigger-cases.json`
- Create: `skills/deep-research/evals/trigger-cases.json`
- Create: `skills/research-architect/evals/trigger-cases.json`
- Create: `skills/design-critique/evals/trigger-cases.json`
- Create: `skills/web-design-guidelines/evals/trigger-cases.json`
- Create: `skills/obsidian-markdown/evals/trigger-cases.json`
- Create: `skills/session-retro/evals/trigger-cases.json`
- Create: `skills/gh-commit-push-pr/evals/trigger-cases.json`
- Create: `skills/vercel-deploy/evals/trigger-cases.json`
- Create: `skills/skill-creator/evals/trigger-cases.json`
- Create: `skills/skill-standardizer/evals/trigger-cases.json`
- Create: `scripts/profiles/routing.py`
- Modify: `skills/skill-evals/scripts/run_trigger_evals.py`
- Test: `tests/test_profiles_routing.py`

**Dependencies**

Task 4, Task 5

**Assumptions Verified**

- **`--skills` filters foreign entries out of the competitor set.**
  `run_trigger_evals.py:183` ends `build_skill_index` with
  `return {name: data for name, data in corpus.items() if name in selected}`.
  IDF is corpus-wide (line 167), but the *scored* dict is the selected subset
  only — so a foreign entry can influence weighting yet **can never win a
  ranking**. EV-CON-03 ("fails when a foreign description defeats a required
  positive or collision assertion") is therefore unreachable with `--skills` set
  to resolved members alone. This is the cut.
- `run_trigger_evals.py:416-417` accepts `--skills-root` and `--skills`;
  line 423 resolves `repo_root` as `Path(__file__).resolve().parents[3]`, so
  `routing.py` passes an absolute `--skills-root` rather than relying on it.
- Exactly three skills declare `evals/trigger-cases.json` today (`blind-spots`,
  `test-strategy`, `verify-before-complete`); `research-architect`, `write-plan`,
  and `write-spec` have `evals/` with `behavioral-scenarios.md` only. **None of
  the twelve SC-02 anchors is among them.**
- Existing fixtures use `{description, cases: [{id, type, prompt, ...}]}`
  (`skills/test-strategy/evals/trigger-cases.json`), which the new fixtures match.

**Implementation Steps**

1. Author a `trigger-cases.json` for each of the twelve anchors: at least one
   positive case and one negative-or-sibling-collision case each, written against
   the skill's real intent. Where two anchors are adjacent (`design-critique` /
   `web-design-guidelines`, `deep-research` / `research-architect`,
   `skill-creator` / `skill-standardizer`), make the negative case a sibling
   collision between exactly that pair — the highest-value assertion available.
2. In `routing.py`, pass `--skills` as **resolved members ∪ observed foreign and
   bundled entries at that target**, so competitors can actually win. Compute
   coverage over the *selected* subset separately, so widening the competitor set
   cannot inflate the coverage ratio.
3. Assemble an absolute `--skills-root` pointing at the observed target root and
   parse the runner's JSON.
4. Add `--report-coverage` to `run_trigger_evals.py`, emitting
   `{included_skill_count, skills_with_fixtures, assertions_executed,
   assertion_outcomes, collision_candidates}`. Additive; existing flags and exit
   semantics are unchanged, which `tests/test_run_trigger_evals.py` keeps pinned.
5. Report coverage separately from pass/fail as
   `skills_with_fixtures / included_skill_count` over the selected set, so
   installing skills purely to create runtime data lowers coverage.
6. Emit a named `coverage-gap` per anchorless overlay member — now expected to be
   empty for anchors and non-empty for the rest of the catalog.

**Verification**

- Run: `.venv/bin/python -m pytest tests/test_profiles_routing.py tests/test_run_trigger_evals.py -q`
- Expect: all pass.
- Run: `.venv/bin/python skills/skill-evals/scripts/run_trigger_evals.py --from-triggers --skills-root skills`
- Expect: exit 0 — the twelve new fixtures self-route without collisions.
- Run: `.venv/bin/python skills/skill-evals/scripts/check_skill_versions.py --base origin/main --no-untracked`
- Expect: exit 0. Adding `evals/trigger-cases.json` to twelve skills is a
  release-relevant change, so each needs a SemVer bump and a CHANGELOG entry.

**Test Discovery Verified**

- Runner/discovery evidence: `tests/test_run_trigger_evals.py` already exists and
  is collected by `pytest tests/`; `tests/test_profiles_routing.py` matches the
  same `tests/test_*.py` pattern.
- Literal proof: `.venv/bin/python -m pytest tests/test_profiles_routing.py -q`

**Done When**

- **All twelve SC-02 anchors** declare a fixture with ≥ 1 positive and ≥ 1
  negative-or-collision case, and every capability overlay reports both assertion
  kinds for both of its anchors with **zero** `coverage-gap` entries for anchors
  (SC-10).
- **A foreign competitor can win.** A test asserts that with `--skills` set to
  members ∪ foreign, a foreign fixture skill outranks a selected member on some
  prompt; the same run with members-only cannot produce that outcome. This pins
  the `build_skill_index:183` cut (SC-10, EV-CON-03).
- A foreign description that defeats a required positive or collision assertion
  makes the run **fail**, and the identical run passes once that competitor is
  removed — so the failure is attributable (EV-CON-03).
- Coverage is a separate ratio over the selected subset, and adding an unselected
  skill to the target **does not raise** it (SC-10).
- Non-anchor coverage gaps are still reported honestly and non-empty; a run
  reporting zero gaps across the whole catalog fails, because that would mean the
  gap detector is blind (SC-10, the zero rule).
### Task 7: Cross-machine comparability

**Objective**

Make "both machines hold the same thing" a checkable claim against two
independently produced evidence files, with no remote mutation.

**Files**

- Create: `scripts/profiles/compare.py`
- Test: `tests/test_profiles_compare.py`

**Dependencies**

Task 5

**Implementation Steps**

1. Implement `compare(evidence_a, evidence_b)` consuming two `evidence` JSON
   documents produced independently (spec Out of Scope forbids remote
   orchestration).
2. Assert agreement on: profile identity, canonical revision, resolved dojo skill
   names, versions, and content identities.
3. Report as **explicit differences, not drift**: foreign entries, harness and
   model versions, budget policy identity, and budget outcome.
4. Refuse to claim agreement when either side is incomplete, audit-only, or
   unsupported — return `agreement: indeterminate` with the reason
   (EV-REC-02).
5. Exit 0 on agreement, 2 on disagreement or indeterminate, 1 on unreadable
   input.

**Verification**

- Run: `.venv/bin/python -m pytest tests/test_profiles_compare.py -q`
- Expect: all pass.
- Run (live, read-only): generate evidence on this host, copy the mini's evidence
  file in over `scp`, then
  `.venv/bin/python scripts/profiles/compare.py macbook.json mini.json`
- Expect: `agreement: true` on the 31 canonical names and content identities,
  with `microsoft-foundry` listed under explicit differences only if the two
  hosts' foreign sets differ (they currently do not).

**Test Discovery Verified**

- Runner/discovery evidence: as Task 1.
- Literal proof: `.venv/bin/python -m pytest tests/test_profiles_compare.py -q`

**Done When**

- Two evidence files agreeing on **all 31 canonical dojo names, versions, and
  content identities** report `agreement: true`; flipping a single content
  identity flips it to `false` with that skill named — so agreement is not a
  default (SC-11).
- A harness-version or foreign-entry difference is reported as an **explicit
  difference** and does **not** set `agreement: false` (SC-11).
- A partial or unsupported result on either side yields
  `agreement: indeterminate`, never `true` — asserted with a multi-target
  fixture where one target is an unsupported harness (SC-11, EV-REC-02).
- `compare` performs no writes and takes no network action; asserted by running
  it against read-only fixture copies (spec Out of Scope).

---

### Task 8: The `dojo profiles verify --all` entrypoint

**Objective**

Make the contract's literal observable invocation work.

**Files**

- Create: `bin/dojo`
- Create: `scripts/profiles/cli.py`
- Test: `tests/test_profiles_cli.py`

**Dependencies**

Task 5, Task 6, Task 7

**Research Context**

- No `dojo` executable exists (`which dojo` → not found) and there is no
  `pyproject.toml` or console-script mechanism, so a shell wrapper on `PATH` is
  the thinnest way to satisfy "the exact invocation must work" without
  introducing packaging.
- `skills/skill-standardizer/scripts/sync.py:178-182` already uses the exact exit
  convention the spec requires (0 clean, 1 errors, 2 dry-run with issues), so the
  codes are a repo convention rather than an invention.

**Implementation Steps**

1. Write `bin/dojo` as a POSIX `sh` wrapper that resolves its own directory,
   locates the repo root, selects `.venv/bin/python` when present and `python3`
   otherwise, and execs `scripts/profiles/cli.py` for the `profiles` subcommand.
   Any other subcommand exits 2 with a usage message so the namespace stays open.
2. Implement `cli.py` with `profiles verify` supporting `--all` (validate every
   definition; evaluate deployability only for currently observed or explicitly
   requested targets), `--selection`, `--target` (repeatable), `--json`, and
   `--policy`.
3. Wire exit codes: 0 only for a full conformant evaluation; 2 for evaluated
   drift, unsupported policy, or nonconformance; 1 when evaluation cannot finish.
4. Ensure `--all` validates all 8 definitions but does **not** fail unrelated
   conformant targets because the unapplied `full` definition exists (spec
   Evaluation).
5. Make `bin/dojo` executable and document the `PATH` addition in Task 16.

**Verification**

- Run: `PATH="$PWD/bin:$PATH" dojo profiles verify --all`
- Expect: exit 0 or 2 with a whole-catalog report; **never** exit 0 alongside
  `partial: true`.
- Run: `PATH="$PWD/bin:$PATH" dojo profiles verify --all --json | .venv/bin/python -m json.tool > /dev/null && echo OK`
- Expect: `OK`
- Run: `.venv/bin/python -m pytest tests/test_profiles_cli.py -q`
- Expect: all pass.

**Test Discovery Verified**

- Runner/discovery evidence: as Task 1.
- Literal proof: `.venv/bin/python -m pytest tests/test_profiles_cli.py -q`

**Done When**

- The literal string `dojo profiles verify --all` runs end to end with `bin` on
  `PATH` and emits a `partial: false` report naming **all 8** profiles (SC-06,
  spec Contract).
- Exit codes are asserted individually: 0 on a conformant fixture, 2 on a drifted
  fixture, 2 on an unsupported-policy fixture, 1 on an unreadable-target fixture
  (spec Contract).
- Running `--all` against a fixture with one conformant target and an unapplied
  `full` definition exits 0 — the `full` definition alone does not fail it (spec
  Evaluation).
- `--json` output is byte-identical across two consecutive runs (SC-06).
- The CLI holds no mutation authority: a test asserts the module namespace
  exposes no writer and that a recursive hash of every target fixture is
  unchanged after `verify --all` (SC-12, spec Authority "Verifier").

---

### Task 9: Audit-only automation and the CI gate

**Objective**

Prove that no scheduled, session-start, or CI path can apply, remove, relink, or
widen installed skill state, and add the phase 1 gate to CI.

**Files**

- Modify: `.github/workflows/skill-contract-pilot.yml`
- Test: `tests/test_profiles_automation_authority.py`

**Dependencies**

Task 8

**Assumptions Verified**

- `hooks/session-start-skill-drift.sh:27` invokes
  `audit.py --global-policy prefer-primary-link --format json` and pipes it to
  `hooks/skill_drift_state.py`. `audit.py` imports only `build_audit_report`,
  `print_json`, `resolve_context`, `summarize_report`, `write_json` (line 10
  region) — **not** `apply_actions` — so the hook has no mutation path today.
  This task pins that rather than assuming it stays true.
- `hooks/post-tool-use-regen-manifest.sh` invokes `gen_skill_docs.py`,
  `generate_skills_manifest.py`, and `gen_catalog.py`; none writes to a skills
  root outside the repo.
- `.github/workflows/skill-contract-pilot.yml` runs
  `gen_harness_adapters.py --check --skip-symlinks`, and `--skip-symlinks` skips
  the symlink phase at `scripts/gen_harness_adapters.py:262`, so CI has never
  created the whole-catalog links.

**Implementation Steps**

1. Add a ninth CI step, "Verify distribution profiles", running
   `PATH="$PWD/bin:$PATH" dojo profiles verify --all` with `--json` written to an
   artifact. CI has no Codex binary and no global roots, so the probe is
   unavailable: definition validation must still run and exit 0, with every
   target reported `unsupported: no probe available` rather than the run failing.
   Assert that distinction explicitly — a green CI step that silently evaluated
   nothing is the degenerate pass this plan exists to avoid.
2. Add the fixture-backed evaluation as a second command in the same step so the
   gate is non-degenerate in CI: `dojo profiles verify --target
   tests/fixtures/profiles/catalog --selection core,engineering`.
3. Write `tests/test_profiles_automation_authority.py` asserting, by static
   inspection of the shell sources and the imported symbols: no hook script
   references `sync.py`, `--apply`, `install-skill-from-github.py`, or any
   profiles apply entrypoint; `audit.py` does not import `apply_actions`; the CI
   workflow contains no `--apply` and no `gen_harness_adapters.py` invocation
   without `--skip-symlinks`.
4. Add a runtime assertion: run every hook script against a fixture HOME and
   assert a recursive hash of the fixture's skills roots is byte-identical
   before and after.

**Verification**

- Run: `.venv/bin/python -m pytest tests/test_profiles_automation_authority.py -q`
- Expect: all pass.
- Run (negative control for the detector): temporarily append `--apply` to a copy
  of a hook script in `tmp_path` and re-run the static check against the copy.
- Expect: the check **fails** — proving it can see a violation, so a clean result
  is a measurement rather than a broken detector.
- Run (full suite): `.venv/bin/python -m pytest tests/ -q`
- Expect: **≥ 309 passed** (the current baseline) plus the new tests, 0 failed.

**Test Discovery Verified**

- Runner/discovery evidence: as Task 1; the CI step "Run regression tests"
  already runs `python -m pytest tests/ -q`.
- Literal proof: `.venv/bin/python -m pytest tests/test_profiles_automation_authority.py -q`

**Done When**

- The static check flags a violation when one is injected and passes on the real
  tree — both directions asserted, so a pass is not a blind zero (SC-12,
  the zero rule).
- Running all hook scripts against a fixture HOME leaves its skills roots
  byte-identical (SC-12, EV-NEG-03).
- CI runs `dojo profiles verify --all` and a **non-degenerate** fixture
  evaluation, driven by the stored probe fixtures rather than a live probe, whose
  report names ≥ 10 included skills — so the gate cannot pass on an empty catalog
  (spec Evaluation).
- CI distinguishes `unsupported: no probe available` (expected, exit 0 for
  definition validation) from a silent zero-target evaluation; a test asserts the
  fixture-backed step reports `state: unprofiled` for its target rather than
  skipping it (SC-01, SC-12).
- The full suite stays green at **≥ 309 + new** tests.

---

### Task 10: Adjudicate the budget disagreement

**Objective**

Use the verifier to settle the 56%/85% versus 50%/75% conflict the spec
deliberately left open, and record the outcome as a dated measurement.

**Files**

- Modify: `docs/project/BACKLOG.md`
- Create: `docs/measurements/2026-07-31-codex-listing-adjudication.md`

**Dependencies**

Task 8

**Assumptions Verified**

- `docs/project/BACKLOG.md:92-125` holds the entry "Harness adapters promote the
  whole catalog to project scope, blowing the skill-listing budget", status
  `in-progress`, whose "Scope corrected 2026-07-29" paragraph already records the
  unverified-budget caveat this task resolves. It is the correct entry to update
  rather than a new one.

**Implementation Steps**

1. Run `dojo profiles verify --all --json` against the live `global-agents` and
   `global-codex` targets and against the `full` composition.
2. Reproduce both historical estimators in a one-off analysis: the one that
   scored name + description only, and the one that included the
   `(file: {path})` suffix. The ops audit addendum already identifies the ~8%
   gap between them as the path term; confirm or refute that as the sole cause.
3. Write the measurement note: the verifier's figure, the two prior figures, the
   identified cause of the divergence, and which prior pass was wrong and why.
   State every figure as a dated measurement with its estimator named.
4. Update the BACKLOG entry: mark the unverified-budget caveat resolved, cite the
   measurement note, and record that figures are now computed at verify time.

**Verification**

- Run: `PATH="$PWD/bin:$PATH" dojo profiles verify --all --json > /tmp/claude-501/-Users-dg-mac-mini-Dev/7ac27985-a9c5-4069-9fd8-34f35192fd7e/scratchpad/live.json && .venv/bin/python -m json.tool /tmp/claude-501/-Users-dg-mac-mini-Dev/7ac27985-a9c5-4069-9fd8-34f35192fd7e/scratchpad/live.json > /dev/null && echo OK`
- Expect: `OK`
- Run: `.venv/bin/python scripts/check_links.py`
- Expect: exit 0 — the new note is linked and no dangling reference is introduced.

**Done When**

- The note names the verifier's computed utilization for the curated set and for
  `full`, each with its date, policy identity, and the render mode chosen — and
  **quotes no figure as a constant**; the note explicitly states the figure is
  recomputed at verify time (spec Assumptions).
- The two historical estimators are reproduced and the divergence is attributed
  to a named cause, with the incorrect pass identified. "Both were approximately
  right" does not satisfy this (spec Problem: adjudicating them is the point).
- `docs/project/BACKLOG.md`'s unverified-budget caveat is marked resolved with a
  pointer to the note.
- `scripts/check_links.py` exits 0.

---

**— End of Phase 1. Phase 1 is independently shippable here: profile definitions
exist, `dojo profiles verify --all` works, CI gates it, and nothing has gained
mutation authority. This also unblocks ops register D6, which needs a declaration
of intended membership to compare against. —**

---

### Task 11: Realization identity, target locking, and conflict detection

**Objective**

Build the primitives the applicator needs *before* it exists: decide when a
request is an idempotent replay, hold an exclusive per-target lock, and detect a
stale observation. These are a dependency of activation, not a follow-on to it —
an applicator that acquires its lock after staging has already raced.

**Files**

- Create: `scripts/profiles/conflict.py`
- Test: `tests/test_profiles_concurrency.py`

**Dependencies**

Task 2, Task 8

**Research Context**

- `resolve.realization_identity` (Task 2, step 4) binds profile identity,
  canonical revision, target identity, harness/model version, and budget-policy
  identity. That five-field binding is what makes "the same request" decidable,
  so this module consumes it rather than defining its own notion of sameness.
- `skill_standardizer_lib.py` has no locking of any kind: `apply_actions`
  (line 1090) mutates immediately with no exclusion, so two concurrent syncs
  today resolve by last-writer-wins. That is the behavior the spec's Authority
  section forbids and this task replaces.

**Implementation Steps**

1. Implement `is_idempotent_replay(requested_identity, target)` — true only when
   the requested realization identity equals the target's recorded identity
   **and** the observed state still matches the record. A matching record with
   diverged state is not a replay.
2. Implement `acquire_target_lock(target)` using `O_CREAT | O_EXCL` on
   `<target>/.dojo-profiles/lock`, holding the owning pid and realization id. It
   does **not** block and does **not** steal: a second holder raises
   `LockHeld` immediately.
3. Implement `assert_fresh_observation(planned_observation, target)`, re-reading
   the target and raising `StaleObservation` when anything changed since
   planning. Last-writer-wins is not offered as an option.
4. Classify a differing canonical revision, profile definition, composition, or
   policy identity as a **distinct request** rather than a replay — a direct
   consequence of step 1 using the five-field identity.
5. Write `tests/test_profiles_concurrency.py` covering replay, lock contention,
   staleness, and the distinct-request classification. Concurrency is exercised
   with two real processes, not two calls in one interpreter, so the `O_EXCL`
   boundary is actually tested.

**Verification**

- Run: `.venv/bin/python -m pytest tests/test_profiles_concurrency.py -q`
- Expect: all pass, including the two-process lock-contention test.

**Test Discovery Verified**

- Runner/discovery evidence: as Task 1 — `pytest tests/` collects `tests/test_*.py`.
- Literal proof: `.venv/bin/python -m pytest tests/test_profiles_concurrency.py -q`

**Done When**

- `is_idempotent_replay` returns true for an identical five-field identity over
  unchanged state, and false when **any one** of the five fields differs —
  asserted field by field, so a partial identity check cannot pass (SC-08,
  EV-CON-01, spec Authority "Retry and concurrency").
- A matching recorded identity over **changed** observed state is **not** a
  replay (SC-08).
- Two separate processes contending for one target: exactly one acquires;
  the loser raises `LockHeld` immediately, performs no writes, and leaves a
  byte-identical tree (EV-CON-01).
- `assert_fresh_observation` raises `StaleObservation` when the target is mutated
  between planning and the check, and the test proves it does **not** raise on an
  unchanged target — both directions, so a pass is not a blind zero.

---

### Task 12: The staged applicator

**Objective**

Apply a resolved profile to a named target with a crash-safe boundary: prepared
state is never active, activation is the single observable transition, and the
predecessor stays recoverable.

**Files**

- Create: `scripts/profiles/apply.py`
- Test: `tests/test_profiles_apply.py`

**Dependencies**

Task 8, Task 11

**Assumptions Verified**

- `skills/skill-standardizer/scripts/skill_standardizer_lib.py:1025`
  (`_backup_destination`) calls `shutil.move(str(dest), str(backup_path))` at
  line 1043, and `apply_actions` (line 1113) then calls `_replace_with_copy` at
  line 1133. Between those two calls the destination does not exist: the prior
  realization is **not active**, only recoverable. Verified by reading both
  functions.
- `apply_actions` iterates actions one at a time (line 1113) with per-action
  `try/except` (line 1160) that records the error and **continues** to the next
  action, so a mid-run failure leaves a mixed set. EV-REC-01 and EV-REC-03 forbid
  exactly this, which is why this task adds a new applicator rather than
  extending that loop. `apply_actions` is not modified.
- `_replace_with_copy` (line 1047) and `hash_directory` (line 176) are reusable
  as-is and are imported rather than reimplemented.

**Implementation Steps**

1. **Stage outside the skills root, on the same filesystem.** Build the new
   realization under `<root_parent>/.dojo-profiles/staging/<realization_id>/` —
   e.g. `~/.agents/.dojo-profiles/`, a sibling of `~/.agents/skills`, **not** a
   child of it. Staging inside the skills root would place a second full set of
   `SKILL.md` files where a harness enumerates skills; if the harness does not
   skip the dot-directory, the catalog would momentarily double and blow the very
   budget this contract exists to protect. A sibling directory keeps the rename
   intra-filesystem (so activation stays atomic) while putting staged content
   permanently out of any listing. `scan_root` also skips dot-prefixed entries
   (`skill_standardizer_lib.py:211`), so the standardizer cannot see it either.
2. **Activation is a two-rename swap, and the window is named, not denied.**
   `os.rename` cannot replace a non-empty directory, so activation is: rename the
   live realization to `predecessors/<realization_id>/`, then rename staging into
   the live path. Define **the first rename as the activation boundary**. Before
   it, the prior realization is active (EV-REC-01). A crash *between* the two
   renames leaves the target absent and the predecessor intact at a known path —
   `verify` reports nonconformant with an exact recoverable predecessor, which is
   what EV-REC-03 permits for an interruption during activation. It never reports
   a mixed set as conformant.
3. Record the predecessor manifest — `{name, physical_path, is_symlink,
   link_target, content_hash}` per entry — and `fsync` it **before** the first
   rename, so the recovery path is durable even if the process dies inside the
   swap. The manifest is what makes restoration exact rather than approximate;
   the renamed tree is the payload.
4. Require an explicit profile composition **and** an explicit target. Refuse a
   bare invocation, a `full` target, an unresolved selection, an over-budget
   result, an unsupported policy, a dirty selected source, or a missing canonical
   member — each before any staging begins (SC-07, SC-08).
5. Show the resolved profile, exact targets, budget result, and the planned
   additions, replacements, deactivations, and link changes before mutating (spec
   Authority "Profile applicator").
6. Touch only dojo-managed entries within the named targets. Foreign,
   harness-bundled, plugin-cache, and unrelated files are never read for write
   and never modified; assert this with a sentinel file placed outside the
   managed set.
7. Implement `restore --realization <id>` returning the target to its recorded
   predecessor, and make a second restoration of the same id a no-op.
8. Multi-target requests evaluate every target first; a target whose harness is
   unsupported is preserved untouched and reported separately, and the run never
   claims cross-machine agreement for a partial result (EV-REC-02).
9. Wire Task 11's primitives in this order, which is the order that makes them
   effective: `acquire_target_lock` **before** planning, `is_idempotent_replay`
   before staging (a replay returns exit 0 having written nothing), and
   `assert_fresh_observation` immediately **before** the activation rename. A
   lock taken after staging, or a freshness check taken before staging, would
   both leave the race open.
10. **The lock is a shared resource, not this tool's private one.** Export
   `acquire_target_lock` as the precondition every guarded writer must take
   (Task 14 wires `sync.py` and the installer to the same lock). A lock only
   `dojo profiles apply` respects protects nothing — `sync.py --apply` would
   still race it.

**Verification**

- Run: `.venv/bin/python -m pytest tests/test_profiles_apply.py -q`
- Expect: all pass, including the four interruption tests below.
- Run: `.venv/bin/python -m pytest tests/test_profiles_apply.py tests/test_profiles_concurrency.py -q`
- Expect: all pass — the end-to-end replay and contention cases exercise
  Task 11's primitives through the applicator, not only in isolation.
- Run (interruption simulation): each interruption test injects a fault at a
  named phase boundary via monkeypatch, then re-runs `dojo profiles verify` over
  the resulting tree and asserts the verdict.

**Test Discovery Verified**

- Runner/discovery evidence: as Task 1.
- Literal proof: `.venv/bin/python -m pytest tests/test_profiles_apply.py -q`

**Done When**

- **Staged content is never inside a skills root.** A test asserts that at every
  point during an apply, enumerating the target skills root returns **exactly**
  the prior member set (before the first rename) or exactly the new member set
  (after the second) — never a union of both. A staging directory placed inside
  the root would fail this, which is the point of asserting it (SC-04, SC-07).
- **Interruption after stage, before activate** leaves the prior realization
  **active** — `verify` reports the target conformant to its *previous* profile,
  not merely recoverable (EV-REC-01). This is the assertion the existing
  `apply_actions` cannot satisfy.
- **Interruption between the two renames** leaves the predecessor intact at
  `predecessors/<id>` with a durable manifest, and `verify` returns exit 2 with
  `conformant: false` plus a named recovery command. The test asserts the
  predecessor tree hash equals its pre-apply value exactly (EV-REC-03, EV-REC-04).
- **Interruption during activate** yields either the full new realization or an
  explicit nonconformant result with the predecessor recoverable; a mixed set is
  never reported conformant. The test asserts the mixed intermediate tree
  produces exit 2 and `conformant: false` (EV-REC-01, EV-REC-03).
- **Two-target request, A activates and B is interrupted mid-replacement:** A
  verifies conformant; B is intact-predecessor, fully-new, or explicitly
  nonconformant-with-recoverable-predecessor. No other B state passes
  (EV-REC-03).
- **Restore** returns a nonconformant target to its recorded predecessor
  identity; foreign entries are byte-identical throughout; a second restore of
  the same id changes nothing (EV-REC-04).
- A sentinel file outside the managed set and a fixture foreign skill are
  byte-identical before and after every successful application, and canonical
  skill content and plugin caches are unmodified (SC-07, EV-NEG-03).
- Each of the seven refusal conditions in step 4 leaves active target state
  **byte-identical**, asserted by a recursive tree hash per condition (SC-08,
  EV-NEG-01, EV-NEG-02, EV-NEG-04).
- **End-to-end replay:** a second `apply` of the same realization identity to
  unchanged state produces **zero** staged trees, **zero** predecessor records,
  **zero** writes, and exits 0 (EV-CON-01).
- **End-to-end contention:** two concurrent `apply` invocations for **different**
  profile identities against one target allow **at most one** activation; the
  loser exits 2 with `conflict: lock-held` and leaves a byte-identical tree
  (EV-CON-01, SC-08).
- **Stale observation:** a target mutated between planning and activation aborts
  with `conflict: stale-observation` and no writes; last-writer-wins never
  occurs (SC-08).

---

### Task 13: Profile-aware `gen_harness_adapters.py`

**Objective**

Close the primary re-widening path: the documented adapter refresh must not
create or restore a whole-catalog link.

**Files**

- Modify: `scripts/gen_harness_adapters.py`
- Test: `tests/test_gen_harness_adapters.py`

**Dependencies**

Task 12

**Assumptions Verified**

- `scripts/gen_harness_adapters.py:261-269` is the exact cut: inside
  `if not args.skip_symlinks:` it loops `HARNESS_DIRS` (line 36:
  `.claude`, `.agents`, `.agent`) and calls `ensure_symlink(link, write)` for
  `repo_root / harness / "skills"`, where `SYMLINK_TARGET` is `"../skills"`
  (line 37) — one directory link exposing all 49 canonical skills at project
  scope.
- `ensure_symlink` at line 111 replaces a wrong or broken symlink (line 124) and
  refuses a real directory with a message (line 130), so the refusal idiom and
  its message style already exist and should be matched.
- Lines 291–298 do the same for `commands/*.md` into `.claude/commands`
  (`COMMANDS_LINK_DIR`, line 44), which is the selected *command surface* SC-05
  names — it must be profile-bounded too, not just the skills link.
- `--skip-symlinks` (line 241) gates both phases, which is why CI has never
  created these links and why the new refusal cannot break CI.

**Implementation Steps**

1. Add `--profile <composition>` and read a target's active realization record
   (`<target>/.dojo-profiles/realization.json`) when present.
2. Against a **profile-managed** target: preserve the selected realization.
   Replace the whole-catalog directory link with per-skill symlinks for the
   resolved members only, and link only the resolved members' `commands/*.md`.
   Prune managed links for names outside the profile; never touch a foreign or
   hand-authored file (the existing guards at lines 175–186 and 201–216 already
   distinguish managed from foreign links and are reused unchanged).
3. Against an **unprofiled** target with **no** `--profile`: refuse to create the
   whole-catalog directory link, exit non-zero, and emit the exact
   `dojo profiles apply` command that would resolve it. Leave existing state
   byte-identical — this is a refusal, not a removal.
4. Leave `--check` read-only and leave `--skip-symlinks` behavior unchanged so
   the CI step and the committed sidecar path are untouched.
5. Extend `tests/test_gen_harness_adapters.py` in its existing style
   (`load_module` + `_invoke` with `--repo-root` pointed at `tmp_path`).

**Verification**

- Run: `.venv/bin/python -m pytest tests/test_gen_harness_adapters.py -q`
- Expect: all existing tests still pass plus the new refusal and
  preservation tests.
- Run: `.venv/bin/python scripts/gen_harness_adapters.py --check --skip-symlinks`
- Expect: exit 0 — the CI invocation is unaffected.

**Test Discovery Verified**

- Runner/discovery evidence: `tests/test_gen_harness_adapters.py` is already
  collected by `pytest tests/`; this task extends it rather than adding a path.
- Literal proof: `.venv/bin/python -m pytest tests/test_gen_harness_adapters.py -q`

**Done When**

- Run without `--profile` against an **unprofiled** target: exits non-zero,
  creates **no** `{.claude,.agents,.agent}/skills` link, and leaves the tree
  byte-identical (SC-13, EV-NEG-05).
- Run without `--profile` against a **profile-managed** target: exits non-zero
  and leaves the selected realization byte-identical — it does not "helpfully"
  refresh it (SC-13, EV-NEG-05).
- Run **with** the selected profile against a profile-managed target: the
  resulting member set equals the resolved membership exactly — no additions, no
  removals — asserted by set equality, not by a count (SC-13, EV-NEG-05,
  EV-LEG-01's "a subsequent documented adapter refresh preserves that
  membership").
- The linked command surface contains commands from resolved members **only**
  (SC-05).
- `--check --skip-symlinks` still exits 0 and the committed sidecar behavior is
  unchanged, so CI is unaffected.

---

### Task 14: Profile-aware standardizer and installer

**Objective**

Close the remaining two re-widening paths — the one that installs the whole
canonical catalog globally, and the one that adds a single unselected skill.

**Files**

- Modify: `skills/skill-standardizer/scripts/skill_standardizer_lib.py`
- Modify: `skills/skill-standardizer/scripts/sync.py`
- Modify: `skills/skill-standardizer/scripts/audit.py`
- Modify: `skills/skill-installer/scripts/install-skill-from-github.py`
- Modify: `hooks/skill_drift_state.py`
- Modify: `skills/skill-standardizer/SKILL.md`
- Modify: `skills/skill-standardizer/commands/standardize-skills.md`
- Modify: `skills/skill-standardizer/CHANGELOG.md`
- Create: `skills/skill-installer/CHANGELOG.md` (absent today; `bump_skill_version.py` creates it, per `docs/system/OPERATIONS.md:120`)
- Test: `skills/skill-standardizer/scripts/test_skill_standardizer.py`
- Test: `tests/test_skill_drift_state.py`
- Test: `tests/test_profiles_entrypoint_guards.py`

**Dependencies**

Task 12

**Assumptions Verified**

- `skill_standardizer_lib.py:649` is the widening branch:
  `if enforce_mirror and not only_existing:` iterates `global-*` inventories and
  proposes creating each canonical skill missing there. This is the exact cut —
  it must be bounded by resolved membership when a profile applies.
- **`--only-existing` is NOT membership-neutral — an earlier revision of this
  plan asserted that it was, and it is false.** `only_existing` appears at
  exactly three sites: the parameter (line 347), the per-skill drift loop
  (line 570), and the `enforce_mirror` guard (line 649). The deprecated-alias
  handling at lines ~455–495 and ~895–940 is **ungated**: `replace_deprecated_skill`
  (lines 485, 937) writes a destination name that need not already exist, and
  `remove_deprecated_skill` (lines 462, 912) deletes an entry.
  `DEPRECATED_SKILL_REPLACEMENTS` (line 27) is live and non-empty
  (`json-canvas`→`obsidian-canvas`, `imagegen`→`gpt-imagen`). So
  `--only-existing` **can** add and remove members via the alias path and needs a
  guard like the others — not merely a neutrality test. A neutrality fixture with
  no deprecated alias in it is **vacuous**: it exercises only the line-570 filter
  and would pass against the unguarded alias path.
- `sync.py:140-151` passes `enforce_mirror`, `only_existing`, and
  `selected_skills` into `build_audit_report`, so a `--profile` argument threads
  through the existing signature without restructuring the call.
- `audit.py:127` makes the same call; both must be updated together or the
  report and the applier disagree.
- `install-skill-from-github.py:255-257` (`_default_dest`) resolves to
  `~/.{claude,codex,agents}/skills` and `:184-188` (`_copy_skill`) copies into
  it, raising only when the destination already exists. Nothing prevents adding
  an unselected dojo skill to a profile-managed root.
- `skills/skill-standardizer/SKILL.md:156-169` and
  `commands/standardize-skills.md:29-32` document `--enforce-mirror --apply` as a
  runbook, so the documentation is part of the entrypoint under SC-13.
- `skills/skill-evals/scripts/check_skill_versions.py` requires a SemVer bump
  plus a matching `CHANGELOG.md` entry for release-relevant skill changes
  (`docs/system/OPERATIONS.md:106-116`), which is why both CHANGELOGs are in
  `Files`.
- **`build_audit_report` has a second consumer besides `sync.py`.**
  `hooks/skill_drift_state.py:67-69` reads `report["issues"]` and keeps only
  entries whose `code == "CONTENT_DRIFT"`. Adding a profile-scoped `unexpected`
  classification would therefore be **silently invisible** to the SessionStart
  drift notice — a new issue code it filters out. This is why the notifier and
  its test are in `Files`: the change is not confined to `sync.py`.

**Implementation Steps**

1. Add a `profile_members: set[str] | None` parameter to `build_audit_report`.
   When set, bound the line-649 branch to those members and report any global
   entry outside the set as `unexpected`, not as something to sync.
2. Add `--profile <composition>` to both `sync.py` and `audit.py`, resolving it
   through `scripts/profiles/resolve.py`.
3. Make `sync.py --enforce-mirror --apply` **refuse** when the target carries an
   active realization record and no `--profile` is given, and refuse against an
   unprofiled global root without `--profile`. Exit 2, no writes, and emit the
   `dojo profiles apply` command that would resolve it.
4. **Guard the deprecated-alias path.** Bound `replace_deprecated_skill` and
   `remove_deprecated_skill` by resolved membership exactly as the line-649
   branch is bounded, so `--only-existing` cannot add or delete a member through
   the alias route against a profile-managed target.
5. In `install-skill-from-github.py`, refuse when the destination root carries an
   active realization record and the skill being installed is not a resolved
   member, unless `--profile` names a composition that includes it. Foreign
   installs into an unprofiled root are unaffected.
6. **Take Task 11's `acquire_target_lock` in every guarded writer** — `sync.py
   --apply` and the installer — not only in `dojo profiles apply`. A lock one
   writer respects protects nothing against the others.
7. Teach `hooks/skill_drift_state.py` the new profile-scoped codes
   (`UNEXPECTED_MEMBER`, `MISSING_MEMBER`) alongside `CONTENT_DRIFT`, so the
   SessionStart notice reports membership divergence rather than filtering it
   out. Keep it read-only and keep its debounce semantics unchanged.
8. Update `SKILL.md` and `commands/standardize-skills.md` so the documented
   runbooks carry `--profile`, and bump both skills' versions with matching
   CHANGELOG entries.

**Verification**

- Run: `.venv/bin/python skills/skill-standardizer/scripts/test_skill_standardizer.py`
- Expect: exit 0 — this suite ships beside the skill and is run as its own CI
  step (`docs/system/OPERATIONS.md:212-219`), so `pytest tests/` does **not**
  collect it and it must be invoked directly.
- Run: `.venv/bin/python -m pytest tests/test_profiles_entrypoint_guards.py tests/test_skill_drift_state.py -q`
- Expect: all pass, including the pre-existing drift-state cases.
- Run: `.venv/bin/python skills/skill-evals/scripts/check_skill_versions.py --base origin/main --no-untracked`
- Expect: exit 0 — both modified skills carry a bump and a changelog entry.

**Test Discovery Verified**

- Runner/discovery evidence: two distinct runners are involved.
  `tests/test_profiles_entrypoint_guards.py` is collected by `pytest tests/`.
  `skills/skill-standardizer/scripts/test_skill_standardizer.py` is **not**
  collected by `pytest tests/` (confirmed by the CI workflow's separate
  "Run skill-standardizer regression tests" step and by
  `docs/system/OPERATIONS.md:212-219`); it must be invoked directly.
  `tests/test_skill_drift_state.py` already exists and is collected, so the
  notifier change lands with regression coverage in place.
- Literal proof: `.venv/bin/python skills/skill-standardizer/scripts/test_skill_standardizer.py`
  and `.venv/bin/python -m pytest tests/test_profiles_entrypoint_guards.py tests/test_skill_drift_state.py -q`

**Done When**

- `sync.py --enforce-mirror --apply` without `--profile`, against both an
  unprofiled and a profile-managed global root, exits 2 and leaves the root
  **byte-identical** (SC-13, EV-NEG-05).
- `sync.py --enforce-mirror --apply --profile core,engineering` against a
  profile-managed root produces a member set **exactly equal** to the resolved
  membership (SC-13).
- **`--only-existing` cannot change membership via the alias path.** The fixture
  **contains a live deprecated alias** (`json-canvas` or `imagegen`) installed in
  the target; the guarded run adds and removes **zero** members, and a test
  asserts the *unguarded* code path would have changed membership on that same
  fixture. A fixture without a deprecated alias does not satisfy this — it
  exercises only the line-570 filter (SC-13).
- **One lock, all writers:** a contention test pairing `sync.py --apply` against
  a concurrent `dojo profiles apply` on one target allows **at most one** writer;
  the loser exits 2 and leaves a byte-identical tree (SC-08, SC-13).
- `install-skill-from-github.py` refuses to add a non-member dojo skill to a
  profile-managed root and leaves it byte-identical; installing a **foreign**
  skill into an unprofiled root still succeeds, so the guard is scoped rather
  than blanket (SC-13, SC-07).
- `check_skill_versions.py --base origin/main` exits 0.
- The standardizer's own suite exits 0 with its pre-existing cases intact.
- The SessionStart drift notice reports a profile-scoped `UNEXPECTED_MEMBER`
  issue rather than filtering it out: a fixture with **1** unexpected member
  produces a notice naming that member, and a conformant fixture produces no
  notice — both directions asserted, so silence is a measurement (SC-12).

---

### Task 15: Legacy migration

**Objective**

Turn the four detected legacy topologies into explicit, recoverable migrations —
and keep the whole-catalog link from becoming an implicit `full` profile.

**Files**

- Create: `scripts/profiles/migrate.py`
- Test: `tests/test_profiles_migration.py`

**Dependencies**

Task 12, Task 13, Task 14

**Research Context**

- Task 5 already detects all four SC-09 topologies without mutation:
  whole-catalog directory link, intersection-only installation, concrete
  secondary copy, and version-skewed managed content. This task consumes that
  detection; it does not re-derive it.
- `scripts/profiles/apply.py`'s stage → activate → commit boundary (Task 12) is
  the mechanism migration reuses. `migrate.py` is a thin planner that maps a
  detected legacy topology onto an apply request; it defines no second mutation
  path, so it inherits Task 12's recovery guarantees rather than restating them.

**Implementation Steps**

1. Add `dojo profiles migrate --target <t> --selection <s>`, which refuses
   without both an explicit selection and an explicit target.
2. Reuse the Task 12 predecessor record and staged activation verbatim so
   migration is recoverable on the same terms.
3. For a whole-catalog directory link: record the predecessor, then replace it
   with per-skill links for the resolved members only. Never treat the detected
   full-canonical membership as an implicit `full` profile
   (recorded decision 3).
4. For an intersection-only installation with a stale concrete secondary copy:
   yield the selected names at canonical identities, relinking the secondary,
   and change no foreign entry.
5. Any migration that cannot yield the exact selected profile reports the target
   nonconformant with a recovery path — it never yields a partial result labelled
   conformant.

**Verification**

- Run: `.venv/bin/python -m pytest tests/test_profiles_migration.py -q`
- Expect: all pass.
- Run (end-to-end, fixture): migrate the whole-catalog fixture, then
  `PATH="$PWD/bin:$PATH" dojo profiles verify --target <fixture>`
- Expect: exit 0 and `conformant: true` with a member set equal to the resolved
  membership.

**Test Discovery Verified**

- Runner/discovery evidence: as Task 1.
- Literal proof: `.venv/bin/python -m pytest tests/test_profiles_migration.py -q`

**Done When**

- Audit **before** migration leaves the fixture byte-identical; only an explicit
  `migrate` changes it (SC-09, EV-LEG-01, EV-LEG-02).
- After migrating the whole-catalog fixture, the member set equals the resolved
  membership exactly, the predecessor is recoverable, and a subsequent
  `gen_harness_adapters.py --profile <same>` preserves that membership — asserted
  by set equality before and after the refresh (SC-09, SC-13, EV-LEG-01).
- The intersection-only fixture migrates to the selected names at canonical
  content identities with **zero** changes to its ≥ 3 foreign entries, asserted
  by per-entry hash equality (SC-09, SC-11, EV-LEG-02).
- A migration that cannot reach the exact selected profile reports the target
  nonconformant with a named recovery command, and **zero** partial results are
  labelled conformant (SC-08, SC-09).

---

### Task 16: Documentation and register closure

**Objective**

Bring the doc set in line with shipped behavior, per this repo's "keep docs
current" agreement, and close the ops register entries phase 1 unblocked.

**Files**

- Modify: `docs/system/OPERATIONS.md`
- Modify: `docs/system/ARCHITECTURE.md`
- Modify: `README.md`
- Modify: `docs/project/BACKLOG.md`
- Modify: `docs/project/ROADMAP.md`

**Dependencies**

Task 15

**Assumptions Verified**

- `docs/system/OPERATIONS.md:140-152` documents "Regenerate harness adapters"
  including the three symlink invocations Task 13 changes, and lines 229-245
  list the nine CI commands Task 9 extends to ten.
- `docs/system/ARCHITECTURE.md:73` describes `gen_harness_adapters.py` as
  emitting sidecars and linking commands; it does not mention profiles.
- `README.md:31-40` steps 4 and 5 are the documented invocations of the two
  entrypoints Tasks 13 and 14 change; step 5's example installs from
  `--repo davisbuilds/dojo`, which is the re-widening demonstration.
- `docs/project/BACKLOG.md:92` (adapters/budget, `in-progress`) and the
  cross-machine drift entry that follows it are the two entries this work closes.

**Implementation Steps**

1. Add a "Distribution profiles" section to `OPERATIONS.md` covering
   `dojo profiles verify --all`, `apply`, `migrate`, `restore`, the `PATH`
   requirement for `bin/dojo`, the exit-code contract, and the audit-only rule
   for Claude Code targets.
2. Update the CI list in `OPERATIONS.md` from nine commands to ten.
3. Update `ARCHITECTURE.md`'s generator description and directory map for
   `profiles/`, `scripts/profiles/`, and `bin/`.
4. Update `README.md` step 4 to the profile-aware invocation and step 5 to note
   the installer's guard against profile-managed roots.
5. Move both completed BACKLOG entries into `ROADMAP.md`'s timeline per the
   repo's backlog-hygiene convention (backlog is future-only), leaving BACKLOG
   entries only for anything genuinely deferred.
6. Note in the handoff report — not in a repo file — that ops register D6 is
   unblocked by phase 1 and R20 can be closed; the register lives in a separate
   repo and this plan does not modify it.

**Verification**

- Run: `.venv/bin/python scripts/check_links.py`
- Expect: exit 0.
- Run: `.venv/bin/python scripts/slop_scan.py`
- Expect: exit 0.
- Run: `.venv/bin/python -m pytest tests/ -q`
- Expect: **≥ 309 passed** plus all tests added by this plan, 0 failed.
- Run: `.venv/bin/python skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict`
- Expect: exit 0 (the repo's documented pre-push gate).

**Done When**

- `OPERATIONS.md` documents all four profile subcommands and lists **ten** CI
  commands.
- `README.md` steps 4 and 5 no longer instruct an action the code now refuses —
  verified by running the literal commands they contain and observing they
  succeed.
- Both closed BACKLOG entries appear in `ROADMAP.md` and no longer sit in
  `BACKLOG.md` as `in-progress`.
- `check_links.py`, `slop_scan.py`, and the strict contract validator all exit 0.

## Risks And Mitigations

- **Risk:** Codex's render-mode choice (absolute paths versus the alias table,
  `render.rs:184`) depends on path lengths at the observed target, so the
  verifier's cost can diverge from the harness's if it models only one mode.
  **Signal:** Task 3's calibration undercount exceeds 5% against Task 0's
  capture, or a captured listing shows a `### Skill roots` block the model did
  not predict.
  **Mitigation:** compute both modes and take the lower, mirroring
  `aliased_render_is_better`; record the chosen mode in evidence. The live dojo
  probe renders in alias mode (`r2/imagegen/SKILL.md`), so the alias branch is
  the one exercised first and must not be the untested path.

- **Risk:** Codex changes its listing format, budget percentage, or estimator in
  a future release, invalidating a policy that still reads as authoritative.
  **Signal:** `probe_codex.py verify` reports a fingerprint diff, or the
  calibration test starts failing on unchanged fixtures.
  **Mitigation:** the policy record binds harness version, model, context window,
  and vendor revision; any diff makes the policy stale and the target audit-only
  (EV-LEG-03). This is designed-for, not merely detected.

- **Risk:** the applicator's staged activation relies on a directory rename being
  atomic. On a target where staging and the live path straddle a filesystem
  boundary, the rename degrades to a copy and reopens the mixed-state window
  EV-REC-01 forbids.
  **Signal:** `os.rename` raises `EXDEV` during activation.
  **Mitigation:** stage in a sibling of the skills root under the same parent
  (`<root_parent>/.dojo-profiles/staging/`) so the rename is intra-filesystem
  without putting staged `SKILL.md` files anywhere a harness enumerates; treat
  `EXDEV` as a hard refusal before any mutation rather than falling back to a
  copy.

- **Risk:** the profiles package couples to `skill_standardizer_lib` internals
  (`scan_root`, `hash_directory`, `_replace_with_copy`), two of which are
  underscore-private. A refactor there could break profiles silently.
  **Signal:** `tests/test_profiles_observe.py` or `test_profiles_apply.py` fails
  after an unrelated standardizer change.
  **Mitigation:** confine the coupling to one import helper; the standardizer's
  own suite and the profiles suite both run in CI, so a break surfaces in the
  same pipeline rather than at use time.

- **Risk:** `codex debug prompt-input` is a debug surface, not a stability
  contract; its JSON shape or the `<skills_instructions>` block format can change
  between Codex releases.
  **Signal:** the parser recovers zero entries, or recovers entries but zero
  namespaced plugin entries, against a working directory known to have both.
  **Mitigation:** Task 0's parser asserts both floors on every run, so a format
  change fails loudly instead of returning a confident zero. Stored fixtures pin
  the shape for hermetic tests; the live probe re-runs on demand, so there is no
  stale-artifact risk to manage. If the block cannot be parsed, the target is
  `unsupported` — never silently backfilled from the filesystem.

## Verification Matrix

| Requirement | Proof command | Expected signal |
| --- | --- | --- |
| Probe parses the real listing, plugin entries included | `.venv/bin/python -m pytest tests/test_profiles_probe.py -q` | Namespaced plugin entries recovered; counts derived, never hardcoded |
| Profile definitions valid; `full` tracks the catalog | `.venv/bin/python -m pytest tests/test_profiles_definitions.py -q` | 8 profiles; `full` count == `len(skills.json.skills)` |
| Composition order has no semantic effect | `.venv/bin/python -m pytest tests/test_profiles_resolve.py -q` | 720 permutations → 1 identity |
| Budget arithmetic matches vendor source | `.venv/bin/python -m pytest tests/test_profiles_budget.py -q -k vendor_parity` | Pass |
| Cost comes from source, not truncated listing | `.venv/bin/python -m pytest tests/test_profiles_budget.py -q -k truncation` | Demand matches source-derived figure; truncation ⇒ nonconformant |
| SC-03 fit proof | `.venv/bin/python -m pytest tests/test_profiles_budget.py -q -k core_plus_one_overlay` | `core` + 1 overlay + 3 foreign is deployable |
| 90% boundary is exact | `.venv/bin/python -m pytest tests/test_profiles_budget.py -q -k boundary` | 8900 ok, 9000 ok, 9100 rejected |
| Detectors see known cases; duplicates counted | `.venv/bin/python -m pytest tests/test_profiles_observe.py -q` | At least one each of foreign/bundled/plugin/project-scope; duplicate demand exceeds de-duplicated |
| Evidence is byte-identical and whole | `.venv/bin/python -m pytest tests/test_profiles_evidence.py -q` | Equal SHA-256 on repeat; 16 fields |
| Twelve anchor fixtures exist and self-route | `.venv/bin/python skills/skill-evals/scripts/run_trigger_evals.py --from-triggers --skills-root skills` | Exit 0 |
| Foreign competitors can actually win | `.venv/bin/python -m pytest tests/test_profiles_routing.py -q` | Foreign outranks a member with members ∪ foreign; impossible with members-only |
| Cross-machine agreement is checkable | `.venv/bin/python -m pytest tests/test_profiles_compare.py -q` | 31 names agree; flip one → `false` |
| The contract's literal invocation works | `PATH="$PWD/bin:$PATH" dojo profiles verify --all` | Exit 0 or 2, `partial: false`, 8 profiles |
| Automation has no mutation authority | `.venv/bin/python -m pytest tests/test_profiles_automation_authority.py -q` | Detector flags injected violation, passes clean tree |
| Budget disagreement adjudicated | `PATH="$PWD/bin:$PATH" dojo profiles verify --all --json` | Computed figure + named cause of divergence |
| Interruption never yields conformant mixed state | `.venv/bin/python -m pytest tests/test_profiles_apply.py -q` | Pre-activate → prior active; mid-activate → exit 2 |
| Replay is idempotent; conflicts do not race | `.venv/bin/python -m pytest tests/test_profiles_concurrency.py -q` | 0 backups on replay; ≤ 1 activation on conflict |
| Adapter refresh cannot re-widen | `.venv/bin/python -m pytest tests/test_gen_harness_adapters.py -q` | No-profile run: non-zero, tree byte-identical |
| Standardizer and installer cannot re-widen | `.venv/bin/python skills/skill-standardizer/scripts/test_skill_standardizer.py` and `.venv/bin/python -m pytest tests/test_profiles_entrypoint_guards.py -q` | Both exit 0; `--enforce-mirror` without profile exits 2, no writes |
| Deprecated-alias path cannot change membership | `.venv/bin/python -m pytest tests/test_profiles_entrypoint_guards.py -q -k alias` | Fixture with a live deprecated alias: zero membership change |
| One lock across all writers | `.venv/bin/python -m pytest tests/test_profiles_entrypoint_guards.py -q -k contention` | `sync.py --apply` vs `dojo profiles apply`: at most one writer |
| Migration is explicit and recoverable | `.venv/bin/python -m pytest tests/test_profiles_migration.py -q` | Audit no-ops; migrate → exact membership; predecessor restorable |
| Repo gates stay green | `.venv/bin/python -m pytest tests/ -q && .venv/bin/python scripts/check_links.py && .venv/bin/python scripts/slop_scan.py && .venv/bin/python skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict` | ≥ 309 + new passed; all exit 0 |

## High-Risk Readiness

### Traceability

Every SC-01…SC-13 and every EV scenario in the spec, in both directions.

| Contract ID | Task | Proof |
| --- | --- | --- |
| SC-01 | Task 1, Task 2, Task 5 | `.venv/bin/python -m pytest tests/test_profiles_definitions.py tests/test_profiles_resolve.py -q` |
| SC-02 | Task 1, Task 2 | `.venv/bin/python -m pytest tests/test_profiles_resolve.py -q` (720 permutations → 1 identity) |
| SC-03 | Task 1, Task 3 | `.venv/bin/python -m pytest tests/test_profiles_definitions.py tests/test_profiles_budget.py -q` |
| SC-04 | Task 0, Task 3, Task 4 | `.venv/bin/python -m pytest tests/test_profiles_budget.py -q -k "boundary or vendor_parity or calibration"` |
| SC-05 | Task 4, Task 5 | `.venv/bin/python -m pytest tests/test_profiles_observe.py tests/test_profiles_evidence.py -q` |
| SC-06 | Task 5, Task 8 | `.venv/bin/python -m pytest tests/test_profiles_evidence.py -q` (SHA-256 equality) |
| SC-07 | Task 12 | `.venv/bin/python -m pytest tests/test_profiles_apply.py -q` |
| SC-08 | Task 11, Task 12, Task 15 | `.venv/bin/python -m pytest tests/test_profiles_apply.py tests/test_profiles_concurrency.py -q` |
| SC-09 | Task 5 (detect), Task 15 (migrate) | `.venv/bin/python -m pytest tests/test_profiles_migration.py -q` |
| SC-10 | Task 6 | `.venv/bin/python -m pytest tests/test_profiles_routing.py -q` |
| SC-11 | Task 7 | `.venv/bin/python -m pytest tests/test_profiles_compare.py -q` |
| SC-12 | Task 9 | `.venv/bin/python -m pytest tests/test_profiles_automation_authority.py -q` |
| SC-13 | Task 13, Task 14 | `.venv/bin/python -m pytest tests/test_gen_harness_adapters.py tests/test_profiles_entrypoint_guards.py -q` |
| EV-NEG-01 | Task 2, Task 12 | `.venv/bin/python -m pytest tests/test_profiles_resolve.py -q -k reject` |
| EV-NEG-02 | Task 3 | `.venv/bin/python -m pytest tests/test_profiles_budget.py -q -k boundary` |
| EV-NEG-03 | Task 4, Task 9, Task 12 | `.venv/bin/python -m pytest tests/test_profiles_automation_authority.py tests/test_profiles_apply.py -q` |
| EV-NEG-04 | Task 5 | `.venv/bin/python -m pytest tests/test_profiles_evidence.py -q -k dirty` |
| EV-NEG-05 | Task 13, Task 14 | `.venv/bin/python -m pytest tests/test_gen_harness_adapters.py -q -k profile` |
| EV-REC-01 | Task 12 | `.venv/bin/python -m pytest tests/test_profiles_apply.py -q -k interrupt` |
| EV-REC-02 | Task 7, Task 12 | `.venv/bin/python -m pytest tests/test_profiles_compare.py -q -k indeterminate` |
| EV-REC-03 | Task 12 | `.venv/bin/python -m pytest tests/test_profiles_apply.py -q -k two_target` |
| EV-REC-04 | Task 12 | `.venv/bin/python -m pytest tests/test_profiles_apply.py -q -k restore` |
| EV-CON-01 | Task 11, Task 12 | `.venv/bin/python -m pytest tests/test_profiles_concurrency.py -q` |
| EV-CON-02 | Task 2, Task 5 | `.venv/bin/python -m pytest tests/test_profiles_resolve.py tests/test_profiles_evidence.py -q` |
| EV-CON-03 | Task 6 | `.venv/bin/python -m pytest tests/test_profiles_routing.py -q -k foreign` |
| EV-LEG-01 | Task 5, Task 13, Task 15 | `.venv/bin/python -m pytest tests/test_profiles_migration.py -q -k whole_catalog` |
| EV-LEG-02 | Task 5, Task 15 | `.venv/bin/python -m pytest tests/test_profiles_migration.py -q -k intersection` |
| EV-LEG-03 | Task 0, Task 3 | `.venv/bin/python -m pytest tests/test_profiles_budget.py -q -k stale_policy` |

### Capability And Authority Map

| Actor | Allowed | Forbidden | Effective-runtime proof |
| --- | --- | --- | --- |
| Canonical maintainer | Define profile membership; authorize realization changes | Impersonating a canonical revision with ambient working-tree content | `.venv/bin/python -m pytest tests/test_profiles_evidence.py -q -k dirty` — dirty selected content is audit-only |
| Verifier (`dojo profiles verify`) | Read canonical metadata, target roots, effective listings, harness versions, policy, plugin-cache metadata | Any write, including under scheduled or session-start execution | `.venv/bin/python -m pytest tests/test_profiles_cli.py -q -k readonly` — recursive tree hash unchanged after `verify --all` |
| Profile applicator (`dojo profiles apply`) | Mutate only named dojo-managed target state, after showing resolved profile, targets, budget, and planned changes | Plugin caches, foreign entries, canonical source, whole home directory, targets not named | `.venv/bin/python -m pytest tests/test_profiles_apply.py -q -k sentinel` — sentinel outside the managed set byte-identical |
| Adapter maintenance (`gen_harness_adapters.py`, `sync.py`, installer) | Refresh within the selected realization when given `--profile` | Whole-catalog links; treating `full` as an implicit default | `.venv/bin/python -m pytest tests/test_gen_harness_adapters.py -q -k refuse` — exit non-zero, tree byte-identical |
| Automation (hooks, CI, scheduled jobs) | Detect and report drift | Apply, remove, relink, or widen | `.venv/bin/python -m pytest tests/test_profiles_automation_authority.py -q` — static check plus fixture-HOME hash |
| Harness consumer | Discover the effective surface for its selected scope | Falling back to the canonical catalog when scope semantics are unsupported | `.venv/bin/python -m pytest tests/test_profiles_budget.py -q -k unsupported` — unsupported yields no deployable verdict |

### Side Effects And Failure Windows

| Effect | Before | After | Recovery |
| --- | --- | --- | --- |
| Stage new realization (Task 12) | Prior realization active | Prior realization **still active**; staged tree inert under `<root_parent>/.dojo-profiles/staging/`, outside any skills root | Delete staging; no target change (EV-REC-01) |
| Record predecessor (Task 12) | Prior realization active | Prior realization active; manifest + copy under `predecessors/<id>/` | Idempotent re-record; no target change |
| Activate (two-rename swap; boundary = first rename) | Prior realization active | New realization active | Crash between renames: predecessor intact at `predecessors/<id>`, target absent, `verify` → nonconformant + recoverable; `restore --realization <id>`. On `EXDEV`, refuse before mutating (EV-REC-01, EV-REC-03) |
| Commit record + prune staging | New realization active, record absent | New realization active, record written | Re-run commit; second run is a no-op (EV-CON-01) |
| Multi-target partial (Task 12) | Both targets prior | A new, B prior or explicitly nonconformant | Per-target restore; agreement reported `indeterminate` (EV-REC-02, EV-REC-03) |
| Migration of whole-catalog link (Task 15) | Directory link exposing all 49 | Per-skill links for resolved members | Restore predecessor link (EV-LEG-01) |
| Adapter refresh refusal (Task 13) | Any | Byte-identical | None needed — refusal is not a mutation (EV-NEG-05) |

### Evidence Lifecycle

| Evidence | Trusted producer | Created | Claim | Consumers | Freshness |
| --- | --- | --- | --- | --- | --- |
| Live probe output (`codex debug prompt-input`) | `probe_codex.py` | Task 0, re-run at every verify | "These entries are listed at this scope, with these rendered descriptions" | Task 3 truncation detector, Task 4 observation | Re-probed on demand; never cached, so it cannot go stale |
| Window/model (`codex debug models`) | `probe_codex.py models()` | Task 0, re-run at every verify | "The context window is N and the effective percent is M" | Task 3 budget derivation | Re-read at verify time |
| `prompt-input-*.json` fixtures | `probe_codex.py` | Task 0 | "This is the listing shape at capture date" | Hermetic tests only — **never** a cost or conformance input | Shape-pinning only; a verdict never rests on them |
| Source `SKILL.md` descriptions | Canonical repo at selected revision | Task 3 | "This is the untruncated description a listing would carry" | **The sole cost input**; truncation detector's left-hand side | Invalid on any canonical content change |
| `profiles/policies/codex.yaml` | Maintainer, from vendor source at `f57467275c` | Task 3 | "The authoritative limit is `window*2/100` tokens, estimator `ceil(bytes/4)`" | Budget evaluation, evidence, applicator refusal | Stale on fingerprint change or vendor revision change |
| `profiles/*.yaml` | Canonical maintainer | Task 1 | "This is the reviewed intended membership" | Resolver, verifier, applicator, all three guarded entrypoints | Any edit changes profile identity and invalidates prior evidence |
| `evidence` JSON | `dojo profiles verify` | Tasks 5, 8 | "This target conforms / drifts, at this cost against this limit" | Task 7 comparison, ops register D6 drift monitor | Invalid on change to definitions, canonical content, target state, harness version, or policy |
| `<target>/.dojo-profiles/realization.json` | Applicator | Task 12 | "This target holds this realization identity" | `gen_harness_adapters.py`, `sync.py`, installer guards; idempotence check | Invalid when observed state diverges from the recorded identity |
| Predecessor manifest + copy | Applicator | Task 12 | "This is the exact prior realization" | `restore` | Retained until a later successful commit supersedes it |

**Never placed in a pre-dispatch artifact:** the budget figure. It is known only
at verify time, so it appears in `evidence` and never in `profiles/*.yaml`.

### Consumer Closure

- **`realization.json` producers/consumers** are updated in one coherent pass
  spanning Tasks 11, 13, and 14: the applicator writes it, and all three guarded
  entrypoints read it. Between Task 12 and Task 13 the safe transitional
  invariant is that the record exists but no writer consults it — so behavior is
  exactly as it is today (whole-catalog refresh still possible), and no target is
  half-guarded. SC-13 is therefore claimed only after Task 14, never after
  Task 13 alone.
- **Profile identity consumers:** resolver (Task 2), evidence (Task 5),
  comparison (Task 7), applicator (Task 12), conflict primitives (Task 11), and the
  three entrypoint guards (Tasks 13–14). All read it through
  `resolve.profile_identity`; there is no second derivation.
- **Budget-policy identity consumers:** budget (Task 3), evidence (Task 5),
  comparison (Task 7), applicator refusal (Task 12). A policy change invalidates
  all four together because it is a component of `realization_identity`.
- **Documentation consumers** of the changed entrypoints — `README.md`,
  `docs/system/OPERATIONS.md`, `docs/system/ARCHITECTURE.md`,
  `skills/skill-standardizer/SKILL.md`,
  `skills/skill-standardizer/commands/standardize-skills.md` — are updated in
  Tasks 14 and 16. Documentation is treated as part of the entrypoint under SC-13
  because EV-NEG-05 tests "the documented adapter-maintenance entrypoint".
- **`build_audit_report` consumers:** `sync.py:140` and `audit.py:127` (both
  updated in Task 14) **and** `hooks/skill_drift_state.py:67-69`, which filters
  `issues` to `CONTENT_DRIFT` only. All three are updated in Task 14 so a new
  issue code cannot be silently dropped by the session-start notice.
- **Cleanup consumers:** staging and predecessor directories accumulate under
  `<root_parent>/.dojo-profiles/` — a sibling of the skills root, never inside
  it; Task 12 prunes staging on commit and retains predecessors until
  superseded. Both paths are added to `.gitignore` when the target is the repo
  itself. (`.gitignore:64-71` already ignores `.claude/skills`, `.agents/skills`,
  `.agent/skills`, and `.claude/commands` **as paths**, so Task 13 replacing a
  symlink with a real directory at the same path stays ignored — verified.)

### Lifecycle And Compatibility

- **Legacy state:** the four SC-09 topologies are detected read-only (Task 5)
  before any migration exists (Task 15), so phase 1 ships into a world of
  entirely unprofiled targets and reports on it without touching it.
- **Version skew:** a target realization recorded under an older policy identity
  is not silently revalidated; the policy component of `realization_identity`
  differs, making it a distinct request (Task 11).
- **Partial rollout:** a machine that has phase 1 but not phase 2 gets reporting
  with no guards — identical to today's behavior plus a report. A machine with
  Task 13 but not Task 14 has one guarded writer and two unguarded; the Consumer
  Closure note above makes SC-13 unclaimable in that window.
- **Retry:** same realization identity + unchanged state → no-op (EV-CON-01). Any
  differing component → distinct request requiring a fresh conflict check.
- **Supersession:** a new successful commit supersedes the prior predecessor
  record; `restore` targets an explicit realization id, so supersession never
  makes a recorded predecessor ambiguous.

### Execution Hooks

Reviewed for anything that could run before the intended guardrail:

- `hooks/session-start-skill-drift.sh` — runs `audit.py` at session start,
  before any profile guard is loaded. It has no mutation path today
  (`audit.py` does not import `apply_actions`); Task 9 pins this by static check
  **and** by a fixture-HOME hash, and Task 14's `--profile` addition to
  `audit.py` keeps it read-only.
- `hooks/post-tool-use-regen-manifest.sh` — runs on every `SKILL.md` write,
  regenerating `skills.json` and the catalog. Since `full` resolves against
  `skills.json` at resolve time, authoring a skill changes `full`'s membership
  mid-session. That is intended (it tracks the catalog) but it means `full`'s
  profile identity is not stable across a session in which a skill is authored;
  Task 1's `Done When` asserts the count is read at check time for exactly this
  reason.
- `hooks/stop-hook-skill-structure.sh` and `stop-hook-git-check.sh` — operate on
  the repo working tree only; no target state.
- `hooks/pre-tool-use-validate-skill.sh` — validates on write; no target state.
- CI (`.github/workflows/skill-contract-pilot.yml`) — installs deps and runs
  checks; passes `--skip-symlinks` so it has never created a whole-catalog link.
  The new gate is added there (Task 9).
- No dependency, build, or migration hook exists in this repo
  (`requirements.txt` is a plain pin list; there is no `pyproject.toml` and no
  install script), so there is no packaging-time path that could run before a
  guard.

### Capability Stop Gates

**Task 0 is the stop gate.** It probes the effective runtime rather than the
configuration:

- **Allowed operation that must succeed:** capture a live Codex listing and read
  the model context window. If it cannot, Codex is `unsupported` and the
  deployable-harness claim is reopened with the maintainer.
- **Forbidden operation against a sentinel outside implicitly writable roots:**
  Task 9 places a sentinel outside every managed root and asserts every
  automation path leaves it byte-identical; Task 12 does the same for the
  applicator.
- **Indirect paths:** `~/.codex/skills` reaches `~/.agents/skills` through
  per-skill symlinks, so a write to either surfaces in both. Task 4 records
  `link_target` for every entry precisely so an indirect path is visible in
  evidence rather than collapsed by `resolve()`.
- **Ambient configuration channels:** `AGENTS_HOME`, `CODEX_HOME`, and
  `CLAUDE_HOME` (`skill_standardizer_lib.py:15-17`) redirect every root. Tests
  set them to a fixture HOME; the applicator records the resolved roots in
  evidence so an ambient redirect cannot silently change which target was
  touched.
- **State classes in scope:** tracked, untracked, gitignored (the harness
  symlinks are gitignored), and externally stored (`~/.agents`, `~/.codex`,
  `~/.claude`). All four appear in the observation model.
- **Network authority:** only `install-skill-from-github.py` has any; Task 14
  guards its destination rather than its fetch.
- **Fingerprint:** harness version, model, context window, vendor revision, and
  policy identity. A changed fingerprint invalidates the cached capture and every
  downstream budget verdict. **Tasks 3, 4, 5, 8, and 10 depend on Task 0 and stop
  when its gate fails.**

### Readiness Review

- Deterministic validation: passed
- Adversarial critique: complete
- Closure critique: complete
- Blocking findings: none

**Adversarial critique findings, all revised and closed.**

*Round 2 — independent critique plus coordinator verification against the live
harness. The measurement foundation was wrong; structure, traceability, and the
staged-applicator decision survived unchanged.*

1. **BLOCKING — the budget instrument would have certified the failure it exists
   to catch.** Task 3 calibrated the cost model against captured listing output,
   which is **post-truncation**: Codex shortens descriptions until they fit, so a
   model calibrated on that output reports "fits" by construction. Cost is now
   computed from untruncated source `SKILL.md` frontmatter, and truncation is a
   first-class nonconformance signal that fires on live state today (Task 3).
2. **The probe I assumed impossible exists.** `codex debug prompt-input` dumps the
   model-visible prompt as JSON including the whole `<skills_instructions>` block;
   `codex debug models` returns the context window. Both verified via
   `codex debug --help`. Task 0 is rebuilt around them; the `codex exec` LLM-echo
   probe, the two-run agreement dance, and the stored-fixture staleness risk are
   all deleted, as is the "Codex is uninspectable" contract question.
3. **Every count in the plan was wrong, and one was wrong in the plan's own named
   failure mode.** Task 4 expected `observe('global-agents') == 32 1` — a
   *filesystem* count, the exact error this plan names as its second
   methodological assumption. All totals are now derived from probe output at
   check time; only non-degeneracy floors remain.
4. **Codex does not shadow by name across roots** — it lists and charges for both
   copies (32 duplicated names of 95 in a dojo session). The effective-catalog
   model now counts duplicates instead of collapsing them (Task 4).
5. **The Codex project-scope root is `.agents/skills` only**, not `.claude/skills`
   or `.agent/skills`, which narrows Task 13's cut and identifies the sole cause
   of dojo's and viral's truncation (Task 4).
6. **`--only-existing` is not membership-neutral.** The deprecated-alias path
   (lines ~455-495, ~895-940) is ungated and `DEPRECATED_SKILL_REPLACEMENTS` is
   live, so it can add and delete members. It gets a guard, and the old
   neutrality fixture was vacuous — the new one contains a live alias (Task 14).
7. **`run_trigger_evals.py --skills` filters foreign entries out of the scored
   set** (`build_skill_index:183`), making EV-CON-03 unreachable as written.
   `--skills` is now members ∪ observed foreign/bundled (Task 6).
8. **The plugin negative control pointed at a path Codex never reads.**
   `is_plugin_cache_path` hardcodes `/.claude/plugins/cache`; Codex's cache is
   `~/.codex/plugins/cache` and 2 of its entries are listed every session.
   Classification is now per-harness, and the parser anchors on the trailing
   ` (file: …)` because plugin entries render as `namespace:name` and a
   split-on-first-colon parser drops them silently (Tasks 0, 4).
9. **SC-10 was unsatisfiable as scoped** — no SC-02 anchor declares a fixture.
   Decided: author the twelve anchor fixtures (Task 6), rather than emit
   `coverage-gap` while claiming SC-10 proven.
10. **`unprofiled` is now a first-class target state** with its own verdict and
   exit code. It is phase 1's main operating mode, not an edge case (Tasks 5, 9).
11. **One lock, all writers.** Task 12's `O_EXCL` lock is a precondition of every
   guarded writer, with a `sync.py --apply` contention test (Tasks 12, 14).
12. **SC-03 / EV-NEG-02's fit proof is now a named test** — `core` + one overlay +
   three foreign entries against the live policy (Task 3).

*Round 1 — self-critique on the applicator boundary:*

13. **Staging location was a budget hazard.** Staging inside the target skills
   root would have placed a second full set of `SKILL.md` files where the harness
   enumerates skills. Moved to a sibling of the skills root (Task 12, step 1).
14. **The "single rename" activation was not achievable as written.** `os.rename`
   cannot replace a non-empty directory, so activation is a two-rename swap. The
   window is now named and the activation boundary defined (Task 12, step 2).
15. **The predecessor was recorded by moving**, reintroducing the exact defect
   this plan criticizes in `apply_actions`. The manifest is now written and
   `fsync`ed before the first rename (Task 12, step 3).
16. **`build_audit_report` had an unmapped consumer.**
   `hooks/skill_drift_state.py:67-69` filters issues to `CONTENT_DRIFT`, so new
   profile-scoped codes would have been silently dropped from the SessionStart
   notice (Task 14, Consumer Closure).

## Handoff

1. Execute in this session, task by task — Task 0 first; it is a stop gate.
2. Review the plan with a critique subagent (or `verify-before-complete` inline
   if subagents are unavailable), seeded with this plan, the spec, and the ops
   harness-decision register.
3. Open a separate execution session, or refine this plan first.

**Before execution begins**, settle the single contract question recorded under
*Assumptions And Constraints → Open decisions for the maintainer*: SC-10's
per-overlay anchor clause. Task 6 assumes the authoring answer and is written to
deliver it; the alternative is a contract revision narrowing that clause. The
three plan decisions listed beside it need no maintainer action — they are
recorded so they are visible, not because they are open.
