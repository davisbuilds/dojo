---
date: 2026-06-16
topic: authoring-multiharness-pipeline
stage: spec
status: draft
source: conversation
---

# Authoring + Multi-Harness Pipeline Spec

## Goal

Make SKILL.md frontmatter the single source of truth behind one generation pipeline that (a) adds explicit, eval-backed `triggers:` and opt-in shared-fragment composition for authoring leverage, then (b) emits per-skill harness sidecars with a CI-enforced compliance check so dojo's "agent-agnostic" claim is genuinely backed across all skills.

## Scope

### In Scope

- Explicit `triggers:` frontmatter field: validation, manifest inclusion, and wiring into `run_trigger_evals.py`.
- Opt-in shared-fragment composition: a Python `gen` step expanding declared includes into `SKILL.md` with an `<!-- AUTO-GENERATED -->` marker and a regenerate command; hand-written skills remain untouched.
- Per-skill harness sidecars generated from frontmatter for the target harness set: Claude Code (`.claude/`), generic agents (`.agents/` + `.agent/`), and Codex (`openai.yaml`-style).
- Adapter-compliance `--check` that fails CI on sidecar drift; backfill across all current skills.
- Resolution of the currently half-populated `.claude/skills`, `.agents/skills`, `.agent/skills` directories.
- Documentation updates to `docs/system/skill-contract-v1.md`, `docs/system/ARCHITECTURE.md`, `docs/system/OPERATIONS.md`, and `spec/agent-skills-spec.md`.

### Out of Scope (deferred to a later pass)

- Published discoverability catalog/site (dimillian pattern).
- `skills-health` runtime report (ECC pattern).
- Behavioral eval tier that drives a real agent (gstack pattern).
- slop-scan CI and a separate `rules/` tier.
- Additional harnesses beyond the three named (OpenCode, Cursor, Gemini, Qwen, etc.).
- gstack-style full `.tmpl`-per-skill mandatory templating.

## Assumptions And Constraints

- dojo skills are small, hand-tuned, and curated; templating must be **opt-in** and must not fight curation. Skills that do not declare a template are never rewritten by the pipeline.
- `triggers:` is a **recommended** (warn-not-fail) field, consistent with how `skill-type` is treated; it is added to the frontmatter whitelist so it stops being a hard validation failure.
- The generation step is Python (matches `scripts/generate_skills_manifest.py`); no new runtime/toolchain is introduced.
- Hooks already enforce validation-on-write, manifest regen, and stop-time structure checks; new pipeline outputs must integrate with that pipeline rather than bypass it.
- `quick_validate.py` (run by `pre-tool-use-validate-skill.sh`) enforces an `ALLOWED_PROPERTIES` whitelist — any new frontmatter key must be added there or writes will be blocked.
- Target harness set is fixed for this pass: `.claude/`, `.agents/`, `.agent/`, Codex.
- Sidecars are **generated artifacts**, not hand-edited; the compliance check treats hand-edits as drift.

## Task Breakdown

### Task 1: Lock the contract surface (Phase 0)

**Objective**

Define, in docs and the spec, the new optional `triggers:` field and the per-skill harness sidecar format/location, before any code changes — so the contract leads implementation.

**Files**

- Modify: `docs/system/skill-contract-v1.md`
- Modify: `spec/agent-skills-spec.md`
- Modify: `docs/system/ARCHITECTURE.md`

**Dependencies**

None

**Implementation Steps**

1. In `skill-contract-v1.md`, add `triggers` as a recommended frontmatter field (array of literal trigger phrases) with a short rationale and example; document its relationship to `description_trigger_ready`.
2. Specify the harness sidecar contract: canonical source = SKILL.md frontmatter; generated targets and the chosen sidecar shape per harness; mark sidecars as generated artifacts.
3. Update `ARCHITECTURE.md` (frontmatter spec, manifest/validation pipeline, directory map) to reflect `triggers:`, the `gen` step, and harness sidecars.
4. Note the deferred items (Phase 3) so scope is explicit.

**Verification**

- Run: `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict`
- Expect: still passes (docs-only change; no skill regressions).

**Done When**

- `triggers:` and the sidecar contract are specified in all three docs.
- No code or skill behavior changed yet.

### Task 2: Accept and surface `triggers:` frontmatter (Phase 1)

**Objective**

Make `triggers:` a first-class, non-rejected frontmatter field across validation and the manifest.

**Files**

- Modify: `skills/skill-creator/scripts/quick_validate.py`
- Modify: `skills/skill-evals/scripts/validate_skill_contract.py`
- Modify: `scripts/generate_skills_manifest.py`
- Test: `tests/test_generate_skills_manifest.py`

**Dependencies**

Task 1

**Implementation Steps**

1. Add `triggers` to `ALLOWED_PROPERTIES` in `quick_validate.py`; if present, validate it is a list of non-empty strings.
2. In `validate_skill_contract.py`, add a recommended `triggers_present` check (warn-not-fail) that, when `triggers` exists, asserts it is a non-empty list of strings.
3. In `generate_skills_manifest.py`, include `triggers` in the manifest entry when present (mirroring the `license`/`allowed-tools` optional-field pattern).
4. Add a manifest-generator test asserting `triggers` round-trips into `skills.json`.

**Verification**

- Run: `python3 -m pytest tests/test_generate_skills_manifest.py -q`
- Expect: new test passes.
- Run: `python3 skills/skill-creator/scripts/quick_validate.py skills/brainstorming/SKILL.md` after adding a `triggers:` block to a scratch copy.
- Expect: no "Unexpected key" error.

**Done When**

- A skill may declare `triggers:` without validation failure.
- `triggers` appears in `skills.json` when present.

### Task 3: Wire declared triggers into trigger evals (Phase 1)

**Objective**

Make `run_trigger_evals.py` assert against *declared* `triggers:` so trigger quality is measured against authored intent, not only inferred from the description.

**Files**

- Modify: `skills/skill-evals/scripts/run_trigger_evals.py`
- Test: add/extend a trigger-eval fixture under `skills/skill-evals/`

**Dependencies**

Task 2

**Implementation Steps**

1. Load each skill's `triggers:` (when present) as labeled positive routing phrases.
2. Assert each declared trigger routes to its own skill above the existing scoring threshold; report collisions where a declared trigger scores another skill higher.
3. Preserve current behavior for skills without `triggers:` (description-inferred path) for backward compatibility.
4. Add a small fixture proving a declared trigger that collides with another skill is flagged.

**Verification**

- Run: `python3 skills/skill-evals/scripts/run_trigger_evals.py` (or its `--json` mode)
- Expect: declared triggers are evaluated; the collision fixture is reported.

**Done When**

- Declared `triggers:` are evaluated for self-routing and collisions.
- Skills without `triggers:` behave as before.

### Task 4: Opt-in shared-fragment composition (`gen`) (Phase 1)

**Objective**

Provide a Python generation step that expands declared shared fragments into `SKILL.md`, idempotently, only for skills that opt in.

**Files**

- Create: `scripts/gen_skill_docs.py`
- Create: `skills/_fragments/` (shared include fragments)
- Modify: `hooks/post-tool-use-regen-manifest.sh` (or a sibling hook) to run `gen` before manifest regen
- Test: `tests/test_gen_skill_docs.py`

**Dependencies**

Task 2

**Implementation Steps**

1. Define an opt-in mechanism: a skill declares includes (e.g. a `template`/`includes` marker) or carries `<!-- INCLUDE: name -->` anchors; skills with neither are left byte-for-byte untouched.
2. Implement `gen_skill_docs.py` to expand includes from `skills/_fragments/`, write the result between an `<!-- AUTO-GENERATED ... do not edit between markers -->` block, and be idempotent (re-running produces no diff).
3. Add a `--check` mode that exits non-zero if any opted-in skill is stale (generated output differs from committed file).
4. Wire generation into the hook pipeline so edits to a fragment or opted-in skill regenerate before manifest regen.
5. Add tests for: expansion correctness, idempotency, non-opted-in skills untouched, `--check` drift detection.

**Verification**

- Run: `python3 -m pytest tests/test_gen_skill_docs.py -q`
- Expect: all pass, including idempotency and untouched-skill cases.
- Run: `python3 scripts/gen_skill_docs.py --check`
- Expect: exit 0 on a clean tree.

**Done When**

- Opted-in skills compile deterministically and idempotently.
- Non-opted-in skills are never modified.
- `--check` catches staleness.

### Task 5: Generate per-skill harness sidecars (Phase 2)

**Objective**

Emit harness sidecars for every skill from frontmatter for the target set: `.claude/`, `.agents/`, `.agent/`, Codex.

**Files**

- Create: `scripts/gen_harness_adapters.py`
- Modify: `.claude/skills/`, `.agents/skills/`, `.agent/skills/` (generated outputs)
- Test: `tests/test_gen_harness_adapters.py`

**Dependencies**

Task 2

**Implementation Steps**

1. Define the sidecar shape per harness (Codex: an `openai.yaml`-style interface file with display name, short description, default invocation prompt derived from `name`/`description`/`triggers`).
2. Implement `gen_harness_adapters.py` to produce all sidecars from frontmatter; outputs carry a generated-artifact marker.
3. Make generation deterministic and idempotent; add `--check` for drift.
4. Add tests: a sample skill produces expected sidecars for each harness; idempotency holds.

**Verification**

- Run: `python3 -m pytest tests/test_gen_harness_adapters.py -q`
- Expect: pass.
- Run: `python3 scripts/gen_harness_adapters.py --check`
- Expect: exit 0 after generation.

**Done When**

- Every skill yields valid sidecars for all four targets.
- Regeneration is a no-op on a clean tree.

### Task 6: Adapter-compliance check in CI (Phase 2)

**Objective**

Fail CI when harness sidecars (or opted-in generated SKILL.md) drift from source.

**Files**

- Modify: `.github/workflows/skill-contract-pilot.yml` (add a compliance step)
- Modify: `hooks/` (stop-time or pre-push gate invoking the `--check` modes), as appropriate
- Modify: `docs/system/OPERATIONS.md`

**Dependencies**

Tasks 4, 5

**Implementation Steps**

1. Add a CI step running `gen_skill_docs.py --check` and `gen_harness_adapters.py --check`.
2. Add the same checks to the local pre-push/stop gate alongside `validate_skill_contract.py`.
3. Document the regenerate + check commands in `OPERATIONS.md`.
4. Verify failure path with a deliberately drifted fixture.

**Verification**

- Run (negative): hand-edit one sidecar, then `python3 scripts/gen_harness_adapters.py --check`
- Expect: exit non-zero naming the drifted skill.
- Run (positive): regenerate, re-run `--check`
- Expect: exit 0.

**Done When**

- CI and the local gate fail on drift and pass when synced.
- Commands are documented.

### Task 7: Backfill all skills and resolve harness dirs (Phase 2)

**Objective**

Generate sidecars for all current skills and reconcile the half-populated harness directories so the agnostic claim holds repo-wide.

**Files**

- Modify: all skill sidecar outputs under `.claude/skills/`, `.agents/skills/`, `.agent/skills/`
- Modify: `README.md` and `docs/system/ARCHITECTURE.md` (state the now-backed multi-harness support)

**Dependencies**

Tasks 5, 6

**Implementation Steps**

1. Run `gen_harness_adapters.py` across all skills; commit the generated tree.
2. Confirm the previously half-populated dirs now cover every skill (no more two-skill subset).
3. Update README/ARCHITECTURE to describe the backed multi-harness model and how to regenerate.

**Verification**

- Run: `python3 scripts/gen_harness_adapters.py --check`
- Expect: exit 0 with full coverage.
- Run: compare skill count in `skills/` against sidecar count per harness dir.
- Expect: equal counts.

**Done When**

- Every skill has sidecars in all four targets.
- `--check` is green; docs match reality.

## Risks And Mitigations

- Risk: templating erodes dojo's hand-curated quality.
  Mitigation: opt-in only; non-opted-in skills are byte-for-byte untouched, enforced by a test.
- Risk: `triggers:` rejected by the pre-write hook, blocking authoring.
  Mitigation: Task 2 adds it to `ALLOWED_PROPERTIES` before any skill declares it.
- Risk: generated sidecars create noisy, hard-to-review diffs.
  Mitigation: deterministic + idempotent generation; `--check` proves no spurious drift; outputs carry generated-artifact markers.
- Risk: scope creep into ECC/gstack-scale tooling.
  Mitigation: Phase 3 items explicitly out of scope; four-harness cap fixed for this pass.
- Risk: hook recursion (gen triggering writes that trigger hooks).
  Mitigation: generation writes only between markers and is idempotent, so a second pass yields no change and terminates.

## Verification Matrix

| Requirement | Proof command | Expected signal |
| --- | --- | --- |
| Contract docs updated, no regressions | `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict` | Exit 0 |
| `triggers:` accepted + in manifest | `python3 -m pytest tests/test_generate_skills_manifest.py -q` | Pass |
| Declared triggers evaluated | `python3 skills/skill-evals/scripts/run_trigger_evals.py --json` | Triggers scored; collisions reported |
| Composition idempotent + opt-in | `python3 -m pytest tests/test_gen_skill_docs.py -q` | Pass |
| Composition staleness caught | `python3 scripts/gen_skill_docs.py --check` | Exit 0 clean / non-zero on drift |
| Sidecars generated for all harnesses | `python3 -m pytest tests/test_gen_harness_adapters.py -q` | Pass |
| Sidecar drift fails CI/gate | `python3 scripts/gen_harness_adapters.py --check` | Exit 0 synced / non-zero drifted |
| Full backfill coverage | sidecar count per harness == skill count | Equal counts |

## Handoff

1. Execute in this session, task by task (starting Phase 0 / Task 1 now).
2. Open a separate execution session.
3. Refine this spec before implementation.
