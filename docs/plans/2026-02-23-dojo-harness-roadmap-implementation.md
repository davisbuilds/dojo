---
date: 2026-02-23
topic: dojo-harness-roadmap
stage: implementation-plan
status: migrated
source: conversation
---

# Dojo Harness Roadmap Implementation Plan

## Goal

Evolve `dojo` from a skills/hooks repository into a modular harness runtime with deterministic execution, policy controls, traceability, and guarded self-improvement gates.

## Scope

### In Scope

- Phased runtime buildout from contracts through improvement loop.
- Deterministic tests, policy checks, replay, eval gates, and migration decision artifacts.
- Explicit repo split decision criteria and migration prep tasking.

### Out of Scope

- Hosted SaaS control plane.
- Unreviewed autonomous production patching.
- Provider-specific lock-in for core runtime contracts.

## Assumptions And Constraints

- Runtime should remain deterministic and test-driven at each phase.
- Safety and verification gates block progression between phases.
- Repo split remains conditional on objective thresholds.

## Task Breakdown

### Task 1: Define core harness contracts

**Objective**

Establish runtime data contracts and schema tests before implementing orchestration behavior.

**Files**

- Create: `harness/contracts.py`
- Create: `harness/types.py`
- Create: `tests/harness/test_contracts.py`
- Modify: `README.md`

**Dependencies**

None

**Implementation Steps**

1. Define core request/result/policy/trace types.
2. Write tests for required-field and schema validation behavior.
3. Keep implementation minimal until tests pass.

**Verification**

- Run: `pytest tests/harness/test_contracts.py -q`
- Expect: PASS.

**Done When**

- Core contracts compile and tests pass.
- README references the new contract boundary.

### Task 2: Implement deterministic runner loop

**Objective**

Add bounded-turn execution flow with deterministic provider behavior for reproducible tests.

**Files**

- Create: `harness/runner.py`
- Create: `harness/providers/fake_provider.py`
- Create: `tests/harness/test_runner_deterministic.py`
- Modify: `README.md`

**Dependencies**

Task 1

**Implementation Steps**

1. Build runner loop with max-turn limit and tool callback interface.
2. Add fake provider for scripted model behavior.
3. Add deterministic seed handling and test coverage.

**Verification**

- Run: `pytest tests/harness/test_runner_deterministic.py -q`
- Expect: PASS.

**Done When**

- Deterministic execution path is reproducible under test.
- Termination behavior is covered by tests.

### Task 3: Add permission engine and policy modes

**Objective**

Introduce policy enforcement (`ask`, `auto`, `yolo`) with per-tool overrides and deny-by-default support.

**Files**

- Create: `harness/policy/engine.py`
- Create: `harness/policy/config.py`
- Create: `tests/harness/test_policy_engine.py`
- Modify: `AGENTS.md`

**Dependencies**

Task 2

**Implementation Steps**

1. Implement `PolicyEngine.decide(...)` contract.
2. Add configuration loading and mode interpretation.
3. Add tests for mode behavior and override precedence.

**Verification**

- Run: `pytest tests/harness/test_policy_engine.py -q`
- Expect: PASS.

**Done When**

- Policy mode decisions are deterministic and tested.
- Deny-by-default path is enforced where expected.

### Task 4: Add trace sink and replay tooling

**Objective**

Capture append-only runtime traces and support replay for deterministic debugging.

**Files**

- Create: `harness/tracing/sink.py`
- Create: `harness/tracing/replay.py`
- Create: `scripts/harness_replay.py`
- Create: `tests/harness/test_trace_replay.py`

**Dependencies**

Task 3

**Implementation Steps**

1. Implement JSONL trace append sink keyed by run ID.
2. Implement replay loader and deterministic sequence reconstruction.
3. Add tests for event order and replay equivalence.

**Verification**

- Run: `pytest tests/harness/test_trace_replay.py -q`
- Expect: PASS.

**Done When**

- Trace persistence and replay produce consistent event streams.
- Replay script is runnable in local workflows.

### Task 5: Introduce eval harness and CI merge gate

**Objective**

Require repeatable eval outcomes before merge through local and CI workflows.

**Files**

- Create: `harness/evals/runner.py`
- Create: `harness/evals/cases/smoke.yaml`
- Create: `tests/harness/test_eval_runner.py`
- Create: `.github/workflows/harness-evals.yml`
- Modify: `CONTRIBUTING.md`

**Dependencies**

Task 4

**Implementation Steps**

1. Implement eval case loading and suite execution.
2. Emit deterministic pass/fail reports.
3. Add CI workflow gate for eval command.

**Verification**

- Run: `pytest tests/harness/test_eval_runner.py -q`
- Expect: PASS.
- Run: `python3 -m harness.evals.runner --suite harness/evals/cases/smoke.yaml`
- Expect: exits 0 for baseline.

**Done When**

- Eval runner passes tests.
- CI gate is defined and aligned with local command.

### Task 6: Add session store and compaction

**Objective**

Provide durable session history with compaction to control context growth.

**Files**

- Create: `harness/session/store.py`
- Create: `harness/session/compaction.py`
- Create: `tests/harness/test_session_store.py`
- Create: `tests/harness/test_compaction.py`

**Dependencies**

Task 5

**Implementation Steps**

1. Build SQLite-backed session and message storage.
2. Add compaction strategy preserving recent turns + synthetic summary.
3. Validate isolation and compaction correctness via tests.

**Verification**

- Run: `pytest tests/harness/test_session_store.py tests/harness/test_compaction.py -q`
- Expect: PASS.

**Done When**

- Session persistence is stable under test.
- Compaction behavior is deterministic and loss-bounded.

### Task 7: Add sandbox adapter and security audit checks

**Objective**

Enforce safe sandbox policy combinations and add static audit tooling.

**Files**

- Create: `harness/sandbox/adapter.py`
- Create: `harness/sandbox/docker_adapter.py`
- Create: `scripts/harness_security_audit.py`
- Create: `tests/harness/test_sandbox_policy.py`
- Modify: `docs/OPERATIONS.md`

**Dependencies**

Task 6

**Implementation Steps**

1. Define sandbox adapter abstraction and local no-op mode.
2. Add policy validation for mode/mount combinations.
3. Add static security audit CLI and docs.

**Verification**

- Run: `pytest tests/harness/test_sandbox_policy.py -q`
- Expect: PASS.
- Run: `python3 scripts/harness_security_audit.py --config .agents/settings.json`
- Expect: command runs and reports findings without crashing.

**Done When**

- Invalid sandbox policy combinations are rejected.
- Security audit tooling is documented and testable.

### Task 8: Add multi-agent queueing and handoffs

**Objective**

Support safe multi-agent orchestration with per-lane serialization and validated handoff payloads.

**Files**

- Create: `harness/orchestration/queue.py`
- Create: `harness/orchestration/handoff.py`
- Create: `tests/harness/test_queue_serialization.py`
- Create: `tests/harness/test_handoffs.py`
- Modify: `docs/ARCHITECTURE.md`

**Dependencies**

Task 7

**Implementation Steps**

1. Implement lane-keyed queueing model with global concurrency control.
2. Add handoff payload validation and state transfer checks.
3. Add tests for per-session ordering and cross-session concurrency.

**Verification**

- Run: `pytest tests/harness/test_queue_serialization.py tests/harness/test_handoffs.py -q`
- Expect: PASS.

**Done When**

- Queue/handoff behavior is deterministic and race-tested.
- Architecture doc reflects orchestration semantics.

### Task 9: Build guarded self-improvement pipeline

**Objective**

Add an offline, gated recursive improvement loop with mandatory eval checks and rollback paths.

**Files**

- Create: `harness/improvement/pipeline.py`
- Create: `harness/improvement/proposals.py`
- Create: `harness/improvement/canary.py`
- Create: `harness/evals/cases/regression.yaml`
- Create: `tests/harness/test_improvement_pipeline.py`
- Modify: `docs/ROADMAP.md`

**Dependencies**

Task 8

**Implementation Steps**

1. Implement collect -> propose -> eval -> canary/rollback stages.
2. Add regression suite requirements for promotion.
3. Add tests for failure ingestion, gating, and rollback behavior.

**Verification**

- Run: `pytest tests/harness/test_improvement_pipeline.py -q`
- Expect: PASS.
- Run: `python3 -m harness.improvement.pipeline --dry-run`
- Expect: exits 0 and prints staged outcomes.

**Done When**

- Improvement pipeline is test-covered and guarded by eval requirements.
- Dry-run pipeline produces deterministic stage output.

### Task 10: Execute split-decision and migration planning

**Objective**

Apply objective split thresholds and publish a documented repo strategy decision.

**Files**

- Create: `docs/plans/2026-02-23-dojo-harness-split-plan.md`
- Create: `docs/archive/harness-migration-checklist.md`
- Modify: `README.md`
- Modify: `docs/ARCHITECTURE.md`

**Dependencies**

Task 9

**Implementation Steps**

1. Evaluate split thresholds (LOC, release cadence, dependency divergence, external API adoption).
2. If thresholds are met, document move/keep boundaries and migration choreography.
3. If thresholds are not met, document defer decision and next review checkpoint.

**Verification**

- Run: `rg --files harness | wc -l`
- Expect: objective inventory value captured.
- Run: `git log --oneline -- harness | head -n 20`
- Expect: activity history available for release-cadence assessment.
- Run: `python3 skills/writing-plans/scripts/validate_plan.py docs/plans/2026-02-23-dojo-harness-roadmap-implementation.md --strict-filename`
- Expect: PASS.

**Done When**

- Split decision criteria and outcome are documented.
- Migration checklist exists for the chosen direction.

## Risks And Mitigations

- Risk: runtime complexity grows before quality gates stabilize.
  Mitigation: enforce phase order and require passing verification before progressing.
- Risk: policy/sandbox behavior introduces unsafe execution paths.
  Mitigation: explicit deny-by-default policy tests and security audit tooling.
- Risk: premature repo split increases overhead.
  Mitigation: apply objective thresholds and document defer conditions.

## Verification Matrix

| Requirement | Proof command | Expected signal |
| --- | --- | --- |
| Plan schema compliance | `python3 skills/writing-plans/scripts/validate_plan.py docs/plans/2026-02-23-dojo-harness-roadmap-implementation.md --strict-filename` | PASS |
| Phase 0 contract and runner tests pass | `pytest tests/harness/test_contracts.py tests/harness/test_runner_deterministic.py -q` | PASS |
| Safety policy and sandbox checks pass | `pytest tests/harness/test_policy_engine.py tests/harness/test_sandbox_policy.py -q` | PASS |
| Eval gate wiring is functional | `python3 -m harness.evals.runner --suite harness/evals/cases/smoke.yaml` | Exit code 0 |

## Handoff

1. Execute tasks sequentially by phase in this session.
2. Open a separate execution session if isolated long-running work is preferred.
3. Refine scope/thresholds before implementation begins.
