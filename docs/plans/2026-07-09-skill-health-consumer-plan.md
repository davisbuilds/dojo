---
date: 2026-07-09
topic: skill-health-consumer
stage: plan
status: draft
source: conversation
---

# Skill Health Consumer Plan

## Goal

Implement the contract in
`docs/specs/2026-07-09-skill-health-consumer-spec.md`: a dojo-side consumer of
AgentMonitor's `GET /api/v2/analytics/skills/health` that turns per-skill
trigger health into a deterministic, ranked skill-health report plus
BACKLOG-shaped findings for never-fired dojo skills, ranked by the trustworthy
signals (never-fired + invocation volume) with misfire shown but not ranked on,
and failing honestly when AgentMonitor is unreachable.

Every `Done When` traces to the contract's Success Criteria / verification
commands.

## Scope

In: an opt-in runtime-health dimension added to the existing
`scripts/skills_health.py` (fetch + `skills.json` join), a committed fixture,
findings output, tests. Out (per spec): widening/fixing misfire, broadening
version coverage, LLM judging, auto-editing skills, auto-running skill-evals,
persistent trend storage.

## Assumptions And Constraints

- **The consumer is an extension of `scripts/skills_health.py`, not a new
  script.** That script already exists and produces a per-skill "Skill Health
  Report" by merging two *static* signals (SKILL contract status + declared
  trigger routing). The runtime signals (never-fired, invocations, misfire)
  belong in the same per-skill view — a maintainer wants "is this skill
  well-formed?" and "does it ever fire?" together. The spec's illustrative path
  (`skills/skill-evals/scripts/<consumer>.py`) is superseded by this real seam.
- **The runtime dimension is strictly opt-in and non-breaking.** The default
  `skills_health.py` run (no new flags) must produce byte-identical output to
  today, so the existing `tests/test_skills_health.py` stays green and the
  static report keeps its zero-network, CI-safe behavior.
- Data source is the shipped envelope `{ data: SkillHealthRow[], coverage }`,
  `SkillHealthRow = { name, version, versionApproximate, invocations,
  lastInvokedAt, neverFired, misfireEligible, misfires, misfireRate }`.
- dojo catalog is `skills.json` (`{ version, skills: [{ name, description, path,
  version }] }`); the join scopes findings to dojo-owned skills.
- Determinism: same health input (via `--health-json`) → byte-identical report.
  No timestamps or environment data baked into the report body.
- Python stdlib only for HTTP (`urllib.request`, per
  `skills/skill-installer/scripts/github_utils.py`); no new dependencies.
- Misfire is near-zero on real data and under validation (AgentMonitor BACKLOG);
  it is displayed with its eligible denominator and labeled experimental, never
  a ranking input.

## Map Before You Cut

Traced ground:

- `scripts/skills_health.py` — `build_report(skills_root)` shells out to
  `validate_skill_contract.py --json` and `run_trigger_evals.py --from-triggers`,
  merges them into `{ summary, skills: [{ skill, contract_status, warnings,
  triggers_declared, triggers_failed, ... }] }`, keyed by skill name.
  `format_report(report)` renders the human view; `--json` dumps the dict.
  `main()` has `--skills-root` and `--json` only.
- The per-skill list is the join surface: runtime fields attach to each existing
  entry by `skill` name. The `summary` dict is the place for catalog-level
  runtime rollups (e.g. `never_fired`).
- `tests/test_skills_health.py` locks two behaviors:
  `test_build_report_aggregates_contract_and_triggers` and
  `test_format_report_renders_summary`. These are the regression guard — the
  no-flags path must not change.
- `skills.json` is at repo root; `REPO_ROOT` is already resolved in the script.
- HTTP seam: `urllib.request.urlopen` with a short timeout, mirroring
  `github_utils.py`; wrap failures into the honest-degradation path.

Seam decision: add an **optional enrichment pass** gated behind new flags
(`--agentmonitor-url` / `--health-json`). When neither is supplied, `build_report`
is unchanged. When supplied, a new `enrich_with_runtime_health(report, rows)`
folds runtime fields into the existing per-skill entries and summary, and a new
ranking/findings step reads those fields. This is the thinnest cut that satisfies
the contract without a parallel tool or touching the static path.

## Task Breakdown

### Task 1: Runtime health source (fetch + file), with honest failure

**Objective**: Obtain `SkillHealthRow[]` from either a live AgentMonitor or a
saved JSON file, or fail clearly.

**Files**: `scripts/skills_health.py`, `tests/test_skills_health.py`,
`skills/skill-evals/assets/sample-skill-health.json` (new fixture).

**Dependencies**: None.

**Implementation Steps**:
1. Add `load_health_rows(source)` that accepts either a URL or a file path:
   file path → parse JSON; URL → `urllib.request.urlopen(url, timeout=…)` then
   parse. Validate the envelope shape (`data` is a list of objects with the
   expected keys); on connection error, timeout, non-JSON, or shape mismatch,
   raise a typed error (`RuntimeError`) with a clear message.
2. Add `--agentmonitor-url` (default `http://127.0.0.1:3141`) and `--health-json
   <path>` flags; `--health-json` wins when both are usable. Add a
   `--runtime`/enable signal so the default run stays static-only (e.g. runtime
   enrichment activates only when `--health-json` is given or `--runtime` is
   passed; a bare default run does not touch the network).
3. Commit `sample-skill-health.json`: a hand-built envelope covering a never-fired
   dojo skill, a heavily-used skill, a skill with misfire data, a skill absent
   from `skills.json`, and a version-drift case.

**Verification**: `python3 -m pytest tests/test_skills_health.py -q -k
"load_health"` — passes for file parse, URL-error → RuntimeError, and
malformed-shape → RuntimeError.

**Done When**: health rows load from a file and from a URL; unreachable/malformed
sources raise a clear typed error (contract clause 4).

**Assumptions Verified**: stdlib `urllib.request.urlopen` is the established HTTP
pattern (`skills/skill-installer/scripts/github_utils.py:15`); shipped envelope
shape confirmed against `src/api/v2/types.ts` `SkillHealthRow`.

### Task 2: Join runtime health onto the per-skill report

**Objective**: Fold runtime fields into the existing per-skill entries and
summary, scoped to the dojo catalog, without altering the static path.

**Files**: `scripts/skills_health.py`, `tests/test_skills_health.py`.

**Dependencies**: Task 1.

**Implementation Steps**:
1. Add `enrich_with_runtime_health(report, rows)`: index `rows` by `name`; for
   each existing per-skill entry, attach `invocations`, `never_fired`,
   `last_invoked_at`, `misfire_rate`, `misfire_eligible`, and a
   `version_drift` flag (AgentMonitor `version` vs the skill's `skills.json`
   version, when both known). Skills in `rows` but absent from the report's
   catalog (not dojo-owned) are ignored for dojo-scoped output.
2. Extend `summary` with runtime rollups: `never_fired`, `invoked`, and
   `runtime_source` (the origin, for the reader) — but only when enrichment ran.
3. Guarantee the no-enrichment path returns the original dict unchanged (guard
   by only adding keys inside the enrichment branch).

**Verification**: `python3 -m pytest tests/test_skills_health.py -q` — existing
two tests unchanged/green; new test asserts a never-fired dojo skill gains
`never_fired=True`, a non-dojo skill is excluded, and the no-flags report dict is
byte-identical to pre-change (golden compare).

**Done When**: runtime fields attach by name for dojo skills only; the static
report is provably unchanged when enrichment is off (contract: honest scoping +
non-breaking).

**Assumptions Verified**: per-skill entries are keyed by `skill` name and the
summary is a plain dict (`scripts/skills_health.py` `build_report`); `skills.json`
entries expose `name` + `version`.

### Task 3: Ranking + rendering (never-fired & volume; misfire experimental)

**Objective**: Rank and render the enriched report by trustworthy signals, with
misfire shown but not ranked on.

**Files**: `scripts/skills_health.py`, `tests/test_skills_health.py`.

**Dependencies**: Task 2.

**Implementation Steps**:
1. Add a runtime section to `format_report` (only when enrichment ran): a
   "Runtime health" block listing never-fired dojo skills first, then skills
   ordered by invocation volume, with a rarely-fired band (invocations below a
   small threshold) called out distinctly from never-fired.
2. Render misfire per skill as `misfire: X/Y (experimental)` using
   `misfires`/`misfireEligible`; never use it in the sort key. Show `—` when
   `misfireEligible == 0`.
3. Keep the ranking deterministic: ties broken by skill name; identical health
   input → identical output.

**Verification**: `python3 -m pytest tests/test_skills_health.py -q -k
"rank or render"` — asserts never-fired skills sort first, misfire value does
not move rank (swap misfire in fixture → same order), and two runs on the same
fixture are byte-identical.

**Done When**: report ranks by never-fired + volume, misfire is visibly
experimental and rank-inert, output is reproducible (contract clauses 2, 5;
success criteria on ranking + reproducibility).

**Assumptions Verified**: `format_report` builds a line list and returns
`"\n".join(...)` (`scripts/skills_health.py`), so a bounded runtime section is
additive.

### Task 4: Findings output for never-fired dojo skills

**Objective**: Emit paste-ready, BACKLOG-shaped findings for never-fired dojo
skills, keeping a maintainer in the loop.

**Files**: `scripts/skills_health.py`, `tests/test_skills_health.py`.

**Dependencies**: Task 3.

**Implementation Steps**:
1. Add a `--findings` mode that prints a paste-ready `BACKLOG.md`-shaped block
   (What / Why it matters / Sketch + `noted` status, per dojo's convention) for
   each never-fired dojo skill — proposed, not written to any file.
2. Include the skill's last-invoked (or "never") and the report's caveat that
   never-fired is relative to the queried range.
3. Do not auto-append to `BACKLOG.md` and do not invoke `skill-evals`; the block
   is for a maintainer to commit or act on.

**Verification**: `python3 -m pytest tests/test_skills_health.py -q -k
"findings"` — a never-fired dojo skill in the fixture yields a findings block
matching dojo's BACKLOG item shape; no file is written (assert `BACKLOG.md`
untouched).

**Done When**: findings are emitted for never-fired dojo skills in
BACKLOG-ready shape, nothing is auto-written (contract clause 3; scope: no
auto-filing).

**Assumptions Verified**: dojo BACKLOG convention (What / Why it matters /
Sketch + `noted`/`in-progress`/`dropped`) from `docs/project/BACKLOG.md` header.

### Task 5: Docs + lifecycle

**Objective**: Document the runtime dimension and update lifecycle frontmatter.

**Files**: `skills/skill-evals/SKILL.md` (or the script's `--help`/usage docstring
and any `docs/system` reference that catalogs skill-management commands),
`docs/specs/2026-07-09-skill-health-consumer-spec.md`,
`docs/plans/2026-07-09-skill-health-consumer-plan.md`.

**Dependencies**: Task 4.

**Implementation Steps**:
1. Document the new flags (`--agentmonitor-url`, `--health-json`, `--runtime`,
   `--findings`) and the AgentMonitor dependency in the script usage docstring
   and wherever skill-management commands are catalogued.
2. Note the AgentMonitor endpoint + default URL as the runtime data source and
   that it is optional/opt-in.
3. Flip spec + plan `status:` to `complete` when landed.

**Verification**: `python3 scripts/skills_health.py --help` lists the new flags;
`rg -n "agentmonitor|skills/health" scripts/skills_health.py <doc>` returns hits.

**Done When**: docs match shipped behavior; lifecycle frontmatter current.

## Risks And Mitigations

- **Regressing the static report** → runtime enrichment is flag-gated and the
  no-flags dict is golden-compared in a test; the existing two tests are the
  guard.
- **Network coupling in a previously-offline tool** → default run never touches
  the network; `--runtime`/`--health-json` are explicit opt-in, and unreachable
  AgentMonitor is a handled error, not a partial report.
- **Misfire creeping into ranking** → a test swaps the fixture's misfire values
  and asserts identical ordering; misfire is render-only.
- **Name-join drift** (AgentMonitor names vs `skills.json`) → non-dojo names are
  ignored for findings; version disagreement is surfaced as `version_drift`, not
  silently reconciled.
- **Non-determinism** → no timestamps/host data in the report body; same
  `--health-json` input asserted byte-identical across runs.

## Verification Matrix

| Requirement | Proof command | Expected signal |
| --- | --- | --- |
| Load from file/URL, honest failure (clause 4) | `python3 -m pytest tests/test_skills_health.py -q -k load_health` | file parse ok; URL-error and malformed-shape raise RuntimeError |
| Dojo-scoped join, static path unchanged (clause 1) | `python3 -m pytest tests/test_skills_health.py -q` | existing 2 tests green; non-dojo skill excluded; no-flags dict byte-identical |
| Rank by never-fired + volume, misfire rank-inert (clause 2, 5) | `python3 -m pytest tests/test_skills_health.py -q -k "rank or render"` | never-fired first; misfire swap → same order; runs byte-identical |
| Findings for never-fired, no auto-write (clause 3) | `python3 -m pytest tests/test_skills_health.py -q -k findings` | BACKLOG-shaped block emitted; `BACKLOG.md` untouched |
| Live smoke (not a gate) | `python3 scripts/skills_health.py --runtime --format-… ` against local AgentMonitor | report over real data or clean failure if down |
| Repo gate | `python3 -m pytest tests/ -q` | all pass (new tests discovered under `tests/`) |

## Handoff

Execute tasks 1 → 5 in a dojo session; each is independently verifiable and the
existing `tests/test_skills_health.py` guards the static path throughout. After
Task 5, the feedback loop is closed end to end: AgentMonitor measures, this
consumer surfaces never-fired/heavy-use signal and proposes BACKLOG findings a
maintainer acts on. Misfire-signal widening (AgentMonitor) remains the natural
follow-up before it becomes a ranking input.
