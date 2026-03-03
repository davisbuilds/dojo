---
date: 2026-03-02
topic: fetchmd-deep-research-integration
stage: implementation-plan
status: draft
source: conversation
---

# Fetchmd Deep Research Integration Implementation Plan

## Goal

Integrate `fetchmd` into the `deep-research` pipeline as a conditional URL-to-markdown ingest stage that reduces context load and preserves agent-level fallback to regular web search when ingest fails.

## Scope

### In Scope

- Add a deterministic ingest stage that calls `fetchmd --json` for candidate URLs.
- Normalize fetchmd output into `findings` records consumable by `evidence_filter.py`.
- Enforce per-URL context caps so ingest reduces context instead of inflating it.
- Extend pipeline metadata so agents can route targeted fallback search for failed URLs.
- Update `deep-research` contracts and skill docs to describe conditional ingest + fallback flow.
- Regenerate runtime skill manifest so repository `fetchmd` skill is discoverable.

### Out of Scope

- No `--render`/Puppeteer path in this integration pass.
- No in-script HTTP fallback implementation in Python.
- No replacement of existing depth routing or evidence scoring logic.
- No change to non-`deep-research` skills beyond manifest/documentation updates required for discoverability.

## Assumptions And Constraints

- Assumption: `fetchmd` is available on PATH in target environments, or the agent can detect absence and fallback.
- Assumption: upstream retrieval still provides candidate URLs (this integration improves ingest quality, not discovery).
- Constraint: fallback must stay at agent orchestration layer, not embedded in pipeline scripts.
- Constraint: output must remain deterministic and JSON-contract-based for composability.
- Constraint: no `--render` support in this pass to avoid adding Puppeteer dependency and browser-side security variance.
- First-principles decision: optimize for robust interfaces between stages (discover -> ingest -> filter -> synthesize) over one-script autonomy; this keeps failure handling explicit and testable.
- Trade-off accepted: less "single command does everything" convenience in exchange for clearer responsibilities and lower maintenance risk.

## Task Breakdown

### Task 1: Define Ingest Contract And Pipeline Interface

**Objective**

Define the minimal interface for conditional fetchmd ingest, including input shape, output shape, and agent-level fallback signals.

**Files**

- Modify: `skills/deep-research/references/contracts.md`
- Modify: `skills/deep-research/assets/sample-input.json`

**Dependencies**

None

**Implementation Steps**

1. Add `urls` and `retrieval` fields to the deep-research input contract (`retrieval.prefer_fetchmd`, `retrieval.max_tokens_per_url`, `retrieval.max_urls_for_ingest`).
2. Define ingest output metadata contract (`fetchmd_attempted`, `fetchmd_succeeded`, `fetchmd_failed`, `failed_urls` with reason categories).
3. Add sample-input variants showing both success path and fallback-required path.

**Verification**

- Run: `python3 -m json.tool skills/deep-research/assets/sample-input.json >/dev/null`
- Expect: exit code `0` and valid JSON.
- Run: `rg -n "retrieval|failed_urls|max_tokens_per_url" skills/deep-research/references/contracts.md`
- Expect: new contract fields are present.

**Done When**

- Contract clearly distinguishes ingest responsibilities vs agent fallback responsibilities.
- Sample input demonstrates conditional fetchmd usage and fallback metadata fields.

### Task 2: Implement Fetchmd URL Ingest Script

**Objective**

Create a script that converts URL candidates to compact findings via `fetchmd --json` with context caps and explicit failure reasons.

**Files**

- Create: `skills/deep-research/scripts/url_ingest.py`

**Dependencies**

- Task 1

**Implementation Steps**

1. Build CLI accepting JSON input (`--input` or stdin) and output (`--output` or stdout), mirroring existing deep-research scripts.
2. Read `urls` and retrieval config; enforce defaults and hard bounds for URLs processed and tokens retained per URL.
3. For each URL, run `fetchmd --json <url>` via subprocess, parse JSON, normalize to findings fields (`title`, `url`, `summary`, `content`, `source_type`, `published_at` when available).
4. Record per-URL failure reasons (`missing_fetchmd`, `nonzero_exit`, `invalid_json`, `empty_markdown`, `security_block`, `timeout_or_network`, `unknown_error`) without stopping the batch.
5. Emit deterministic JSON with `findings` plus ingest metadata for downstream pipeline and agent fallback routing.

**Verification**

- Run: `python3 skills/deep-research/scripts/url_ingest.py --help`
- Expect: help text renders and exit code `0`.
- Run: `python3 skills/deep-research/scripts/url_ingest.py --input /tmp/ingest-input.json --pretty`
- Expect: output includes `findings` and `ingest_meta` keys, even when some URLs fail.

**Done When**

- Script never crashes the whole run because one URL fails.
- Output is always valid JSON object with stable fields for downstream consumption.
- Token cap is applied to retained content per URL.

### Task 3: Wire Ingest Stage Into run_pipeline

**Objective**

Integrate ingest stage into the existing pipeline so fetchmd runs conditionally before filtering, while preserving current behavior when ingest is not requested.

**Files**

- Modify: `skills/deep-research/scripts/run_pipeline.py`

**Dependencies**

- Task 2

**Implementation Steps**

1. Add script path resolution for `url_ingest.py` and validate existence similarly to existing script checks.
2. Add pipeline branch: if `retrieval.prefer_fetchmd` is true and `urls` exists, run ingest stage before filter stage.
3. Merge ingest findings into payload for `evidence_filter.py` (append or initialize `findings`).
4. Include ingest metadata in top-level pipeline output under `meta` (including failed URLs for agent fallback).
5. Keep backward compatibility: if no ingest config is provided, pipeline behavior is unchanged.

**Verification**

- Run: `python3 skills/deep-research/scripts/run_pipeline.py --input skills/deep-research/assets/sample-input.json --pretty`
- Expect: output contains `depth_plan`, `research_packet` or skip note, and ingest metadata fields in `meta` when ingest is enabled.
- Run: `python3 skills/deep-research/scripts/run_pipeline.py --input skills/deep-research/assets/sample-input.json --depth-only --pretty`
- Expect: ingest/filter are skipped according to depth-only semantics, with clear `meta` notes.

**Done When**

- Pipeline supports both legacy flow and new ingest-enabled flow without contract breakage.
- Agent can reliably identify which URLs need fallback search from output metadata.

### Task 4: Update Skill Guidance For Operational Behavior

**Objective**

Document the integration so agents use fetchmd as a context-saving ingest stage and apply fallback consistently.

**Files**

- Modify: `skills/deep-research/SKILL.md`
- Modify: `skills/deep-research/commands/deep-research.md`

**Dependencies**

- Task 3

**Implementation Steps**

1. Update workflow section to include: search/discovery -> fetchmd ingest -> fallback for failed URLs -> evidence filter -> synthesis.
2. Add explicit rule: no `--render` in this integration path.
3. Add explicit fallback protocol: when ingest metadata reports failures, run regular web search for only failed URLs and merge results back into findings.
4. Update command wrapper examples to show ingest-enabled input shape.

**Verification**

- Run: `rg -n "fallback|fetchmd|render|failed_urls|retrieval" skills/deep-research/SKILL.md skills/deep-research/commands/deep-research.md`
- Expect: guidance includes conditional ingest and explicit no-render/fallback behavior.

**Done When**

- Skill docs remove ambiguity about where fallback happens.
- Operator guidance matches implemented pipeline behavior and contract fields.

### Task 5: Restore Skill Discoverability And Validate Plan/Runtime Artifacts

**Objective**

Ensure runtime manifest and plan quality gates are satisfied so agents can discover the fetchmd skill and safely execute the new flow.

**Files**

- Modify: `skills.json`
- Validate: `docs/plans/2026-03-02-fetchmd-deep-research-integration-implementation.md`

**Dependencies**

- Task 4

**Implementation Steps**

1. Regenerate `skills.json` from skill frontmatter so `skills/fetchmd` is represented in runtime catalog.
2. Confirm `deep-research` and `fetchmd` entries both exist in generated manifest.
3. Run writing-plans validator on this plan file and fix any schema/structure issues.

**Verification**

- Run: `python3 scripts/generate_skills_manifest.py`
- Expect: command succeeds and `skills.json` includes `"name": "fetchmd"`.
- Run: `rg -n "\"name\": \"fetchmd\"|\"name\": \"deep-research\"" skills.json`
- Expect: both entries found.
- Run: `python3 skills/writing-plans/scripts/validate_plan.py docs/plans/2026-03-02-fetchmd-deep-research-integration-implementation.md`
- Expect: `PASS` result.

**Done When**

- `skills.json` reflects committed skill directories relevant to this integration.
- Plan passes validator with no errors.

## Risks And Mitigations

- Risk: fetchmd unavailable in some environments, causing ingest failures.
  Mitigation: classify `missing_fetchmd` explicitly and preserve actionable `failed_urls` for agent fallback.
- Risk: ingest stage still bloats context if markdown is retained too aggressively.
  Mitigation: apply default hard token cap per URL plus `max_urls_for_ingest` bounds.
- Risk: agents misunderstand fallback boundary and expect script-level web retrieval.
  Mitigation: encode fallback boundary in both contracts and SKILL command guidance.
- Risk: manifest drift hides `fetchmd` skill at runtime.
  Mitigation: include manifest regeneration in completion checklist and CI/hook flow.
- Risk: scoring bias if fallback findings differ in shape from ingest findings.
  Mitigation: normalize both ingest and fallback records to the same `evidence_filter` fields before filtering.

## Verification Matrix

| Requirement | Proof command | Expected signal |
| --- | --- | --- |
| Ingest contract includes retrieval and fallback metadata fields | `rg -n "retrieval|failed_urls|max_tokens_per_url" skills/deep-research/references/contracts.md` | Fields present with clear semantics |
| URL ingest script is executable and contract-shaped | `python3 skills/deep-research/scripts/url_ingest.py --help` | Exit `0` and usage text shown |
| Pipeline conditionally runs ingest and surfaces metadata | `python3 skills/deep-research/scripts/run_pipeline.py --input skills/deep-research/assets/sample-input.json --pretty` | JSON output contains ingest-related `meta` fields when enabled |
| Agent fallback boundary is documented | `rg -n "fallback|failed_urls|no .*render|fetchmd" skills/deep-research/SKILL.md skills/deep-research/commands/deep-research.md` | Documentation states agent-level fallback and no-render policy |
| Runtime skill discoverability includes fetchmd | `python3 scripts/generate_skills_manifest.py && rg -n "\"name\": \"fetchmd\"" skills.json` | Generator succeeds and fetchmd entry exists |
| Plan quality gate passes | `python3 skills/writing-plans/scripts/validate_plan.py docs/plans/2026-03-02-fetchmd-deep-research-integration-implementation.md` | `PASS` for plan file |

## Handoff

1. Execute in this session, task by task.
2. Open a separate execution session.
3. Refine this plan before implementation.
