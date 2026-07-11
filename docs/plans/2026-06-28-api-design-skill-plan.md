---
date: 2026-06-28
topic: api-design-skill
stage: plan
status: complete
source: conversation
---

# API Design Skill Plan

## Goal

Create a contract-valid dojo skill named `api-design` that guides agents through API/interface design, review, and implementation handoff for robust public and internal contracts.

Implementation landed in commit `83bddb4` on branch `feat/api-design-skill`.

## Scope

### In Scope

- Add `skills/api-design/SKILL.md` as a workflow skill.
- Add focused reference files for HTTP APIs, non-HTTP interface contracts, event/streaming contracts, compatibility review, and implementation verification.
- Synthesize guidance from the local Addy Osmani source skill, local `~/Dev` project survey, and web research into dojo-native progressive disclosure.
- Route adjacent implementation concerns to existing skills: `write-spec`, `test-strategy`, `secure-code`, `create-cli`, and `first-principles`.
- Run strict skill validation and fix any contract failures.
- Regenerate or verify `skills.json` if local hooks do not update it automatically.
- Update relevant system documentation if the new skill changes the catalog or public behavior.

### Out of Scope

- Implement deterministic API linters or generators in the first pass.
- Add framework-specific code templates.
- Refactor existing project APIs outside dojo.
- Package or publish the skill unless explicitly requested after validation.

## Assumptions And Constraints

- The skill should be public and agent-agnostic.
- `SKILL.md` should remain concise and use references for protocol-specific depth.
- Reference files should live directly under `skills/api-design/references/`.
- The skill should improve local project work without becoming local-only; local project findings should influence scope, not appear as private project instructions.
- The existing Addy Osmani skill is source context, not text to copy wholesale.
- Commands should use repository-local validation paths and Python scripts already present in dojo.

## Task Breakdown

### Task 1: Scaffold the Skill Directory

**Objective**

Create the initial `api-design` skill structure in the dojo skills tree.

**Files**

- Create: `skills/api-design/SKILL.md`
- Create: `skills/api-design/references/http-apis.md`
- Create: `skills/api-design/references/interface-contracts.md`
- Create: `skills/api-design/references/events-streaming.md`
- Create: `skills/api-design/references/compatibility-review.md`
- Create: `skills/api-design/references/implementation-verification.md`
- Generate: `skills/api-design/agents/openai.yaml`

**Dependencies**

None

**Implementation Steps**

1. Use dojo skill naming conventions: directory and frontmatter `name` both equal `api-design`.
2. Mark the skill as `skill-type: workflow`.
3. Write a trigger-oriented `description` that includes API design, API review, endpoints, schemas, DTOs, events, webhooks/SSE, CLI JSON contracts, versioning, deprecation, and compatibility-sensitive changes.
4. Create only the reference files needed for the initial workflow; do not create placeholder assets or scripts.

**Verification**

- Run: `find skills/api-design -maxdepth 3 -type f -print | sort`
- Expect: one `SKILL.md`, five directly linked reference files, and generated `agents/openai.yaml`.

**Done When**

- The skill directory exists with no unused placeholder files.
- Frontmatter matches dojo naming and skill-type expectations.

### Task 2: Write the Core Workflow

**Objective**

Make `SKILL.md` a concise, executable API design/review workflow.

**Files**

- Modify: `skills/api-design/SKILL.md`

**Dependencies**

Task 1

**Implementation Steps**

1. Define the skill's scope and non-goals.
2. Add a surface-classification step: HTTP, event/stream, CLI/machine output, module/interface, cross-client contract, or mixed.
3. Add a consumer and compatibility analysis step: known consumers, public vs internal promises, observable behavior, migration risk, and deprecation needs.
4. Add a contract-first design step: inputs, outputs, errors, auth, side effects, idempotency, pagination/list semantics, rate limits, observability, and documentation.
5. Add a robustness review step: trust boundaries, parse/validate at edges, retry behavior, partial failure, resource limits, caching/concurrency, and sensitive-data exposure.
6. Add an output contract for the agent: API design packet, review findings, or implementation handoff.
7. Add sibling-skill routing instructions for `write-spec`, `test-strategy`, `secure-code`, `create-cli`, and `first-principles`.
8. Add a resource map explaining when to read each reference.

**Verification**

- Run: `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills api-design --strict`
- Expect: no contract errors related to scope, execution flow, output, verification, or resource references.

**Done When**

- `SKILL.md` is complete enough for an agent to run the workflow without loading every reference.
- The workflow explicitly produces a useful artifact rather than a vague checklist.

### Task 3: Write Focused References

**Objective**

Provide progressively disclosed guidance for the major API surface types and risk categories.

**Files**

- Modify: `skills/api-design/references/http-apis.md`
- Modify: `skills/api-design/references/interface-contracts.md`
- Modify: `skills/api-design/references/events-streaming.md`
- Modify: `skills/api-design/references/compatibility-review.md`
- Modify: `skills/api-design/references/implementation-verification.md`

**Dependencies**

Task 2

**Implementation Steps**

1. In `http-apis.md`, cover resource design, methods/statuses, structured errors, pagination, filtering/sorting, idempotency, rate limits, auth, OpenAPI, and observability.
2. In `interface-contracts.md`, cover typed boundaries, DTO separation, parse-don't-validate boundary handling, branded/semantic IDs, enum evolution, stable CLI JSON schemas, stdout/stderr/exit-code contracts, and hard-to-misuse signatures.
3. In `events-streaming.md`, cover event names, schema versioning, ordering, replay, idempotent handlers, delivery semantics, SSE/webhooks, backpressure, and consumer failure modes.
4. In `compatibility-review.md`, cover Hyrum's Law, additive evolution, breaking-change taxonomy, versioning strategy, deprecation notices, migrations, consumer-driven contracts, and doc/test drift.
5. In `implementation-verification.md`, cover request-level integration tests, schema/contract tests, negative paths, auth/authorization tests, idempotency/retry tests, rate-limit tests, observability checks, and docs synchronization.
6. Include short source notes or links where they add authority without bloating the files.

**Verification**

- Run: `rg -n "http-apis|interface-contracts|events-streaming|compatibility-review|implementation-verification" skills/api-design/SKILL.md`
- Expect: every reference file is directly discoverable from `SKILL.md`.
- Run: `wc -l skills/api-design/references/*.md`
- Expect: references are focused, not oversized; any file longer than 100 lines has a small table of contents.

**Done When**

- Each reference is usable independently for its surface/risk category.
- No reference duplicates the entire `SKILL.md` workflow.

### Task 4: Validate And Refresh Generated Artifacts

**Objective**

Confirm the new skill passes dojo's contract and runtime inventory expectations.

**Files**

- Modify if generated by hooks or scripts: `skills.json`
- Generate if required by local generator: `skills/api-design/agents/openai.yaml`

**Dependencies**

Tasks 1-3

**Implementation Steps**

1. Run strict validation for the new skill.
2. If validation reports manifest drift or generated sidecar drift, run the appropriate dojo generator rather than hand-editing generated files.
3. Re-run validation after generated artifacts update.
4. Inspect `git status --short` to confirm the changed file set is coherent.

**Verification**

- Run: `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills api-design --strict`
- Expect: validation passes.
- Run: `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict`
- Expect: full skill tree still passes, or any unrelated failures are identified clearly.
- Run: `git status --short`
- Expect: only the new skill, generated inventory/sidecars, and intentional doc updates are changed.

**Done When**

- The new skill validates in isolation.
- Full-tree validation is clean or any unrelated pre-existing failure is documented.
- Generated artifacts are updated by generators, not manual edits.

### Task 5: Update System Catalog Documentation

**Objective**

Keep dojo's public documentation current after adding the skill.

**Files**

- Modify: `docs/system/FEATURES.md`
- Modify if needed: `docs/project/ROADMAP.md`

**Dependencies**

Task 4

**Implementation Steps**

1. Add `api-design` to the appropriate feature category in `docs/system/FEATURES.md`.
2. Remove or adjust any roadmap item that the new skill completes, if present.
3. Keep the docs update minimal and factual.

**Verification**

- Run: `rg -n "api-design|API" docs/system/FEATURES.md docs/project/ROADMAP.md`
- Expect: catalog mentions the new skill and roadmap does not contradict shipped behavior.

**Done When**

- System docs reflect the new skill without broad unrelated edits.

## Risks And Mitigations

- Risk: The skill becomes too broad and vague.
  Mitigation: Keep `SKILL.md` workflow-driven and move protocol detail into focused references.
- Risk: The skill duplicates existing `write-spec`, `test-strategy`, `secure-code`, or `create-cli` behavior.
  Mitigation: Add explicit routing boundaries and handoff points instead of reimplementing those workflows.
- Risk: References become generic API advice that agents already know.
  Mitigation: Emphasize non-obvious contract risks: consumers, compatibility, observable behavior, idempotency, schema drift, and verification.
- Risk: Validation fails due to missing output or verification anchors.
  Mitigation: Run strict validation early after `SKILL.md` is drafted and fix contract issues before polishing references.

## Verification Matrix

| Requirement | Proof command | Expected signal |
| --- | --- | --- |
| New skill exists with intended files | `find skills/api-design -maxdepth 3 -type f -print | sort` | `SKILL.md` plus five reference files plus generated `agents/openai.yaml` |
| New skill passes strict contract | `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills api-design --strict` | zero validation errors |
| Full skill tree remains valid | `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict` | zero validation errors or documented unrelated failures |
| References are discoverable | `rg -n "references/(http-apis|interface-contracts|events-streaming|compatibility-review|implementation-verification)\\.md" skills/api-design/SKILL.md` | all five references linked |
| Documentation catalog is current | `rg -n "api-design" docs/system/FEATURES.md` | catalog entry exists |
| Changed file set is coherent | `git status --short` | only intentional skill, generated, and doc files changed |

## Handoff

1. Execute in this session, task by task.
2. Refine the spec before implementation.
3. Defer implementation and keep the plan/spec as the scoped artifact.
