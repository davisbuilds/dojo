---
date: 2026-07-09
topic: skill-health-consumer
stage: plan
status: complete
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

In: a new runtime-health module invoked opt-in by the existing
`scripts/skills_health.py` (fetch + dojo-scoped join), a committed fixture,
findings output, tests. Out (per spec): widening/fixing misfire, broadening
version coverage, LLM judging, auto-editing skills, auto-running skill-evals,
persistent trend storage, and version-drift reporting (deferred — see Open note
in the spec).

## Assumptions And Constraints

- **Runtime logic lives in a new module `scripts/skill_health_runtime.py`,
  imported by `scripts/skills_health.py` and invoked only when runtime flags are
  passed.** This keeps network/fetch/validation/enrichment/findings out of the
  lean, network-free static aggregator (and its regression-guard test), while
  preserving one command for the maintainer. The static path imports the module
  but never calls it unless asked; a bare import performs no network I/O.
- **The default `skills_health.py` run (no runtime flags) is byte-identical to
  today**, so the existing `tests/test_skills_health.py` stays green and the
  static report keeps its zero-network, CI-safe behavior.
- **dojo-scoping is inherent in the existing report.** `build_report` lists
  exactly the skills under `skills/` (the contract validator globs
  `skills_root/*/SKILL.md`), so the report's skill set *is* dojo's catalog. The
  runtime join matches health rows by name against that set; a health row whose
  name is not in the report is non-dojo and ignored. No separate `skills.json`
  load is required.
- Data source is the shipped envelope `{ data: SkillHealthRow[], coverage }`,
  `SkillHealthRow = { name, version, versionApproximate, invocations,
  lastInvokedAt, neverFired, misfireEligible, misfires, misfireRate }`.
- Determinism: same health input (via `--health-json`) → byte-identical report.
  No timestamps or host data baked into the report body.
- Python stdlib only for HTTP (`urllib.request`); no new dependencies.
- Misfire is near-zero on real data and under validation upstream; it is
  displayed with its eligible denominator, labeled experimental, and never a
  ranking input.

## Map Before You Cut

Traced ground:

- `scripts/skills_health.py` — `build_report(skills_root)` shells out to
  `validate_skill_contract.py --json` and `run_trigger_evals.py --from-triggers`,
  merges them into `{ summary, skills: [{ skill, contract_status, warnings,
  triggers_declared, triggers_failed, ... }] }`, keyed by skill name (no
  `version` field). `format_report(report)` builds a line list and returns
  `"\n".join(...)`. `main()` (lines 120-141) has `--skills-root` and `--json`
  only, and wraps `build_report` in a `try/except (RuntimeError,
  JSONDecodeError)` → `print(..., file=sys.stderr); return 1`.
- `validate_skill_contract.py` `collect_skills` globs `skills_root/*/SKILL.md`
  (line 390) and emits no `version` field — confirming both that the report
  equals the dojo catalog and that version-drift cannot be computed from existing
  report data. Version-drift is therefore **out of v1** (would need a separate
  version source; deferred).
- `tests/test_skills_health.py` locks
  `test_build_report_aggregates_contract_and_triggers` and
  `test_format_report_renders_summary`. These are the regression guard.
- HTTP seam: adapt the stdlib pattern in
  `skills/skill-installer/scripts/github_utils.py:16`
  (`urllib.request.urlopen(req)`), adding a short `timeout`.
- Output modes are text (default) and `--json` (there is no markdown mode;
  `docs/system/OPERATIONS.md:136` documents exactly these two). The report's
  human text *is* the report; no `--format` flag is introduced.

Seam decision: a new `scripts/skill_health_runtime.py` owns fetch, envelope
validation, enrichment, ranking, and findings. `skills_health.py` gains the
runtime flags and calls the module only when they are set, then renders the
enriched report. Rejected alternatives: (a) a fully separate CLI — loses the
one-command "is this skill healthy?" UX that motivates phase 2; (b) inlining
everything into `skills_health.py` — couples network/mocking into the lean
static aggregator and its single regression-guard test. The module split gets
the UX of (b) with the isolation of (a).

## Task Breakdown

### Task 1: Runtime health source module (fetch + file), honest failure

**Objective**: Load `SkillHealthRow[]` from a live AgentMonitor or a saved JSON
file, or fail with a clear typed error.

**Files**: `scripts/skill_health_runtime.py` (new),
`tests/test_skill_health_runtime.py` (new),
`skills/skill-evals/assets/sample-skill-health.json` (new fixture).

**Dependencies**: None.

**Implementation Steps**:
1. In the new module, add `load_health_rows(*, url: str | None, path: str | None)
   -> list[dict]`: `path` set → read + `json.loads` the file; else `url` →
   `urllib.request.urlopen(url, timeout=5)` and parse. Validate the envelope:
   top-level `data` is a list whose items are dicts containing at least `name`,
   `invocations`, `neverFired`. On connection error, timeout, non-JSON, missing
   `data`, or item-shape mismatch, raise `RuntimeError` with a specific message.
   Return the `data` list.
2. Commit `sample-skill-health.json`: a `{ data: [...], coverage: {...} }`
   envelope with rows for (a) a never-fired dojo skill, (b) a heavily-used dojo
   skill, (c) a dojo skill with misfire data (`misfires`/`misfireEligible`
   non-zero), (d) a rarely-fired dojo skill (invocations 1-2), (e) a skill name
   absent from dojo's `skills/`. Use real dojo skill names for (a)-(d) so the
   join tests are faithful.
3. Tests in `tests/test_skill_health_runtime.py`:
   `test_load_health_rows_from_file`,
   `test_load_health_rows_url_error_raises` (patch `urlopen` to raise →
   `RuntimeError`), `test_load_health_rows_malformed_shape_raises`.

**Verification**: `python3 -m pytest tests/test_skill_health_runtime.py -q -k
load_health_rows` — all three pass.

**Done When**: rows load from file and URL; unreachable/malformed sources raise a
clear `RuntimeError` (contract clause 4).

**Assumptions Verified**: stdlib `urllib.request.urlopen` is the repo's HTTP
approach, adapted from `skills/skill-installer/scripts/github_utils.py:16` (which
calls `urlopen(req)` without a timeout; the timeout is a deliberate addition).
Envelope shape confirmed against `agentmonitor/src/api/v2/types.ts`
`SkillHealthRow`.

### Task 2: Dojo-scoped enrichment of the per-skill report

**Objective**: Fold runtime fields into the existing per-skill entries and
summary, scoped to dojo skills, without touching the static path.

**Files**: `scripts/skill_health_runtime.py`, `tests/test_skill_health_runtime.py`.

**Dependencies**: Task 1.

**Implementation Steps**:
1. Add `enrich_report(report: dict, rows: list[dict]) -> dict` in the module:
   index `rows` by `name`; for each existing per-skill entry (keyed by `skill`),
   attach `invocations`, `never_fired`, `last_invoked_at`, `misfire_rate`,
   `misfire_eligible`, `misfires`. Rows whose `name` is not an existing report
   entry (non-dojo) are ignored. Skills with no matching row get
   `invocations: 0, never_fired: None` (unknown — no runtime data), distinct from
   an explicit `never_fired: True` row.
2. Add runtime rollups to `summary` only within this function: `never_fired`
   (count of dojo skills with `never_fired is True`), `invoked` (count with
   `invocations > 0`), and `runtime_source` (the origin string). Return the same
   dict object mutated in place.
3. Do not import or call this from the static path; `skills_health.py` calls it
   only when runtime flags are set (Task 3). The no-runtime dict is therefore
   untouched.

**Verification**: `python3 -m pytest tests/test_skill_health_runtime.py -q -k
enrich` — asserts a never-fired dojo skill gains `never_fired=True`, the non-dojo
row (e) is absent from the enriched report, and a dojo skill with no row gets
`never_fired=None`.

**Done When**: runtime fields attach by name to dojo skills only; non-dojo rows
are ignored (contract clause 1; honest scoping).

**Assumptions Verified**: per-skill entries are keyed by `skill` and the summary
is a plain dict (`scripts/skills_health.py` `build_report`, lines 57-83); report
skill set equals dojo catalog (`validate_skill_contract.py:390`).

### Task 3: Wire runtime into the CLI + ranking/render (misfire experimental)

**Objective**: Add opt-in runtime flags to `skills_health.py`, wire loading +
enrichment into `main()` with honest failure, and render a ranked runtime
section.

**Files**: `scripts/skills_health.py`, `tests/test_skills_health.py`,
`tests/test_skill_health_runtime.py`.

**Dependencies**: Task 2.

**Implementation Steps**:
1. In `skills_health.py`, add flags: `--runtime` (bool), `--health-json <path>`,
   `--agentmonitor-url <url>` (default `None`). Runtime is active when any of the
   three is supplied; if only `--runtime` is given, use
   `http://127.0.0.1:3141/api/v2/analytics/skills/health`. (No silent no-op: a
   bare `--agentmonitor-url` activates runtime.)
2. In `main()`, after `build_report`, if runtime is active:
   `rows = load_health_rows(...)` then `enrich_report(report, rows)`, both inside
   a `try/except RuntimeError` that prints to stderr and `return 1` **before**
   any report is printed — a requested-but-failed runtime load yields no partial
   report (contract clause 4). When inactive, control flow is unchanged.
3. Add a "Runtime health" section to `format_report`, rendered only when
   `summary` carries `runtime_source`. Ranking within the section:
   **never-fired dojo skills first** (alphabetical), then a **rarely-fired band**
   (`0 < invocations < 3`, alphabetical), then the rest by **invocations
   ascending** (under-used surfaced first), ties broken by name. Render misfire
   per skill as `misfire N/M (experimental)` from `misfires`/`misfire_eligible`,
   or `misfire —` when `misfire_eligible == 0`; misfire is never in the sort key.
   The `--json` branch emits the enriched dict unchanged.

**Verification**:
- `python3 -m pytest tests/test_skills_health.py -q` — existing two tests green;
  a new `test_default_run_is_byte_identical` golden-compares the no-flags
  `format_report` and `--json` dict against a captured baseline.
- `python3 -m pytest tests/test_skill_health_runtime.py -q -k "rank or render or
  main"` — `test_never_fired_sorts_first`, `test_misfire_does_not_affect_rank`
  (swap misfire values in the fixture → identical order),
  `test_json_includes_runtime_fields` (`--json --health-json fixture` → enriched
  keys present), `test_runtime_load_failure_exits_nonzero_no_report`.

**Done When**: runtime is opt-in and non-breaking; report ranks by never-fired +
volume; misfire is visible, labeled experimental, and rank-inert; failed runtime
load exits non-zero with no report; same input → identical output (contract
clauses 2, 4, 5).

**Assumptions Verified**: `main()` already guards `build_report` with
`try/except → return 1` (`scripts/skills_health.py:133-137`), so the runtime
guard mirrors an existing pattern; `format_report` returns `"\n".join(lines)`,
so an additive section is safe.

### Task 4: Findings output for never-fired dojo skills

**Objective**: Emit paste-ready, BACKLOG-shaped findings for never-fired dojo
skills; keep a maintainer in the loop.

**Files**: `scripts/skills_health.py`, `scripts/skill_health_runtime.py`,
`tests/test_skill_health_runtime.py`.

**Dependencies**: Task 3.

**Implementation Steps**:
1. Add `render_findings(report) -> str` in the module: for each dojo skill with
   `never_fired is True`, a `BACKLOG.md`-shaped block — `#### <skill> never
   fires` + `noted` status + **What** / **Why it matters** / **Sketch** bullets
   (dojo convention). Include a fixed caveat line that never-fired is relative to
   the queried range (static disclaimer string; not read from `coverage`).
2. Add a `--findings` flag to `skills_health.py` that prints the block to stdout
   instead of the report; requires runtime to be active. It writes nothing to any
   file and does not invoke `skill-evals`.
3. Findings order is alphabetical by skill for determinism.

**Verification**: `python3 -m pytest tests/test_skill_health_runtime.py -q -k
findings` — `test_findings_emits_backlog_block_for_never_fired` (block present
with What/Why/Sketch for the fixture's never-fired skill) and
`test_findings_writes_no_file` (assert `docs/project/BACKLOG.md` mtime/content
unchanged across the run).

**Done When**: findings emit for never-fired dojo skills in BACKLOG-ready shape;
nothing is auto-written (contract clause 3; scope: no auto-filing).

**Assumptions Verified**: dojo BACKLOG item shape (What / Why it matters / Sketch
+ `noted`/`in-progress`/`dropped`) from `docs/project/BACKLOG.md` header.

### Task 5: Docs + lifecycle

**Objective**: Document the runtime dimension and update lifecycle frontmatter.

**Files**: `docs/system/OPERATIONS.md`,
`docs/specs/2026-07-09-skill-health-consumer-spec.md`,
`docs/plans/2026-07-09-skill-health-consumer-plan.md`.

**Dependencies**: Task 4.

**Implementation Steps**:
1. Extend the existing "Skill health report" section
   (`docs/system/OPERATIONS.md:136`) with the new flags (`--runtime`,
   `--health-json`, `--agentmonitor-url`, `--findings`), the AgentMonitor
   endpoint + default URL as the optional runtime source, and a note that the
   default run is unchanged and network-free.
2. Flip spec + plan `status:` to `complete` when landed.

**Verification**: `python3 scripts/skills_health.py --help` lists the new flags;
`rg -n "agentmonitor|--runtime|skills/health" docs/system/OPERATIONS.md` returns
hits.

**Done When**: docs match shipped behavior; lifecycle frontmatter current.

## Risks And Mitigations

- **Regressing the static report** → runtime logic is in a separate module the
  static path never calls unless flagged; `test_default_run_is_byte_identical`
  golden-compares both text and `--json` output; the existing two tests remain.
- **Network coupling in a previously-offline tool** → the module import does no
  I/O; only explicit `--runtime`/`--health-json`/`--agentmonitor-url` triggers a
  fetch, and an unreachable AgentMonitor is a handled `RuntimeError` → exit 1
  with no report.
- **Misfire creeping into ranking** → `test_misfire_does_not_affect_rank` swaps
  fixture misfire values and asserts identical ordering; misfire is render-only.
- **Non-determinism** → no timestamps/host data in the report body; same
  `--health-json` input asserted byte-identical.
- **Name-join drift** (AgentMonitor names vs dojo skill dirs) → non-dojo rows are
  ignored; this is the intended scoping, tested via fixture row (e).

## Verification Matrix

| Requirement | Proof command | Expected signal |
| --- | --- | --- |
| Load from file/URL, honest failure (clause 4) | `python3 -m pytest tests/test_skill_health_runtime.py -q -k load_health_rows` | file parse ok; URL-error and malformed-shape raise RuntimeError |
| Dojo-scoped enrichment, non-dojo ignored (clause 1) | `python3 -m pytest tests/test_skill_health_runtime.py -q -k enrich` | never-fired dojo skill enriched; non-dojo row absent; unmatched dojo skill `never_fired=None` |
| Static path unchanged (non-breaking) | `python3 -m pytest tests/test_skills_health.py -q` | existing 2 tests green; `test_default_run_is_byte_identical` passes (text + `--json`) |
| Rank by never-fired + volume, misfire rank-inert, honest failure (clauses 2,4,5) | `python3 -m pytest tests/test_skill_health_runtime.py -q -k "rank or render or main"` | never-fired first; misfire swap → same order; `--json` carries runtime keys; failed load → exit 1, no report |
| Findings for never-fired, no auto-write (clause 3) | `python3 -m pytest tests/test_skill_health_runtime.py -q -k findings` | BACKLOG-shaped block emitted; `BACKLOG.md` untouched |
| Live smoke (not a gate) | `python3 scripts/skills_health.py --runtime` against local AgentMonitor | report with runtime section, or clean exit-1 failure if down |
| Repo gate | `python3 -m pytest tests/ -q` | all pass (new tests discovered under `tests/`) |

## Handoff

Execute tasks 1 → 5 in a dojo session; each is independently verifiable and the
existing `tests/test_skills_health.py` (plus the new byte-identical guard) protects
the static path throughout. After Task 5, the feedback loop is closed end to end:
AgentMonitor measures, this consumer surfaces never-fired/heavy-use signal and
proposes BACKLOG findings a maintainer acts on. Misfire-signal widening
(AgentMonitor) remains the natural follow-up before misfire becomes a ranking
input; version-drift reporting is a deferred enhancement needing a dojo-side
version source.
