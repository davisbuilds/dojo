---
date: 2026-03-17
topic: self-improve-skill
stage: implementation-plan
status: draft
source: conversation
---

# Self-Improve Skill Implementation Plan

## Goal

Add a `self-improve` skill and supporting scaffolding that captures agent learnings in a portable, low-context workflow, promotes validated patterns into reusable artifacts, and preserves dojo's principles of extensibility, agent-agnosticism, and strict context discipline.

## Scope

### In Scope

- Create a new `skills/self-improve/` package with a trigger-ready `SKILL.md`.
- Design a portable on-disk learning workflow for errors, learnings, and improvement ideas.
- Add deterministic helper scripts and templates for capture, compaction, promotion, and skill-candidate extraction.
- Add an optional command wrapper and reference docs for harness-specific adapters without making them mandatory.
- Add validation and trigger-eval coverage so the new skill does not collide with nearby skills such as `session-retro`, `compact-session`, `writing-plans`, and `skill-creator`.
- Update the repo catalog/docs for the new skill.

### Out of Scope

- Autonomous online self-modification that edits repo files without an explicit invocation.
- Mandatory hooks that silently mutate user workspaces.
- Model-specific behavior embedded in the core skill contract.
- Training-time or RL-based recursive improvement systems.
- Packaging/distribution beyond normal repo conventions unless explicitly requested later.

## Assumptions And Constraints

- The core skill must remain useful in any filesystem-oriented harness, even if optional adapter docs mention Codex, Claude, or OpenClaw.
- Context is sacred: raw learning logs should be append-only, compactable, and not intended for routine full-file loading.
- Promotion from raw learnings to durable behavior must be gated by human or explicit agent review plus deterministic verification.
- The skill should complement, not replace, `session-retro`; session learnings for project docs and self-improve learnings for agent workflow are adjacent but distinct.
- The implementation should reuse existing repo primitives where possible: `skill-creator`, `skill-evals`, `quick_validate.py`, manifest regeneration, and plan/skill contract checks.
- File names and frontmatter must satisfy the current skill contract and repo hooks on first write.

## Task Breakdown

### Task 1: Define The Skill Contract And Scaffold

**Objective**

Create the new skill directory and author a concise `SKILL.md` that positions self-improve as a governed reflection-and-promotion workflow rather than unrestricted self-rewrite.

**Files**

- Create: `skills/self-improve/SKILL.md`
- Create: `skills/self-improve/commands/self-improve.md`
- Create: `skills/self-improve/references/storage-layout.md`
- Create: `skills/self-improve/references/promotion-policy.md`
- Create: `skills/self-improve/references/adapter-patterns.md`

**Dependencies**

None

**Implementation Steps**

1. Generate the base scaffold with `python3 skills/skill-creator/scripts/init_skill.py self-improve --path skills --resources scripts,references,assets`.
2. Write `SKILL.md` so its core workflow is: capture signal, compact/triage, propose promotion, verify, and then optionally materialize a durable artifact.
3. Define clear boundaries that exclude silent self-modification, project-doc retro capture, and generic long-form session summaries.
4. Add a single command-wrapper entrypoint that loads the skill and routes the user into the capture/promotion workflow.
5. Move detailed storage and adapter guidance into references to keep `SKILL.md` short and contract-compliant.

**Verification**

- Run: `python3 skills/skill-creator/scripts/quick_validate.py skills/self-improve`
- Expect: exit code 0 with valid frontmatter.
- Run: `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills self-improve --strict`
- Expect: strict pass with no missing anchors.

**Done When**

- The new skill has a valid scaffold and a concise, trigger-ready `SKILL.md`.
- The workflow explicitly favors governed promotion over autonomous mutation.
- Reference files carry the bulk of variant-specific detail.

### Task 2: Add Portable Learning Storage And Deterministic Capture Tools

**Objective**

Provide a portable learning-store layout and deterministic scripts that record, compact, and summarize self-improve signals without bloating context.

**Files**

- Create: `skills/self-improve/scripts/append_learning.py`
- Create: `skills/self-improve/scripts/compact_learnings.py`
- Create: `skills/self-improve/assets/learning-entry-template.json`
- Create: `skills/self-improve/assets/learning-summary-template.md`
- Modify: `skills/self-improve/references/storage-layout.md`

**Dependencies**

Task 1

**Implementation Steps**

1. Define a minimal workspace layout such as `.self-improve/inbox/`, `.self-improve/summaries/`, and `.self-improve/proposals/`.
2. Implement an append-only capture script that writes structured JSON records for errors, learnings, and improvement ideas with timestamps, tags, and evidence fields.
3. Implement a compaction script that converts raw records into smaller summary artifacts suitable for selective loading.
4. Document read discipline so agents load summaries first and only inspect raw records when a summary indicates high relevance.
5. Ensure scripts accept explicit paths so the storage location can be adapted by different harnesses.

**Verification**

- Run: `python3 skills/self-improve/scripts/append_learning.py --help`
- Expect: usage text renders without error.
- Run: `python3 skills/self-improve/scripts/append_learning.py --store /tmp/self-improve-demo --kind learning --summary "Prompted a better file selection pattern" --evidence "Reduced unnecessary reads"`
- Expect: a new structured record is written under the demo store.
- Run: `python3 skills/self-improve/scripts/compact_learnings.py --store /tmp/self-improve-demo`
- Expect: summary artifact is generated and references the captured record.

**Done When**

- Raw learnings are stored in a structured, append-only format.
- Compaction exists so the workflow does not require loading full history into context.
- The storage contract is portable and does not assume a single harness runtime.

### Task 3: Build Promotion And Skill-Candidate Extraction Scaffolding

**Objective**

Turn validated learnings into governed promotion artifacts, including candidate skill scaffolds for patterns that recur and generalize.

**Files**

- Create: `skills/self-improve/scripts/propose_promotion.py`
- Create: `skills/self-improve/scripts/extract_skill_candidate.py`
- Create: `skills/self-improve/assets/promotion-proposal-template.md`
- Create: `skills/self-improve/assets/skill-candidate-template.md`
- Modify: `skills/self-improve/references/promotion-policy.md`

**Dependencies**

Task 2

**Implementation Steps**

1. Define promotion tiers such as `discard`, `keep-local`, `promote-to-memory`, and `promote-to-skill-candidate`.
2. Implement a proposal generator that turns summarized learnings into a reviewable proposal with rationale, evidence, blast radius, and required verification.
3. Implement a skill-candidate extractor that renders a draft `SKILL.md` scaffold or proposal packet from repeated validated patterns instead of directly editing live skills.
4. Document promotion gates that require explicit review plus repo validation commands before a proposal can affect durable behavior.
5. Keep the output generic so another harness could consume the same proposal artifacts even if it uses different hooks or memory files.

**Verification**

- Run: `python3 skills/self-improve/scripts/propose_promotion.py --help`
- Expect: usage text renders without error.
- Run: `python3 skills/self-improve/scripts/propose_promotion.py --store /tmp/self-improve-demo --summary-file /tmp/self-improve-demo/.self-improve/summaries/latest.md`
- Expect: proposal artifact is written under `.self-improve/proposals/`.
- Run: `python3 skills/self-improve/scripts/extract_skill_candidate.py --proposal /tmp/self-improve-demo/.self-improve/proposals/latest.md --output /tmp/self-improve-demo/self-improve-candidate`
- Expect: candidate scaffold is rendered without mutating repo skills.

**Done When**

- Promotion is mediated by explicit proposal artifacts rather than hidden mutation.
- Reusable patterns can be converted into skill candidates.
- The workflow stays extensible and portable across harnesses.

### Task 4: Add Optional Adapter Guidance And Command-Level Ergonomics

**Objective**

Provide optional harness-specific guidance and command ergonomics without compromising the agent-agnostic core contract.

**Files**

- Modify: `skills/self-improve/commands/self-improve.md`
- Modify: `skills/self-improve/references/adapter-patterns.md`
- Create: `skills/self-improve/assets/adapter-examples/README.md`

**Dependencies**

Task 3

**Implementation Steps**

1. Document adapter patterns for platforms that can inject workspace memory or run hooks, but keep them explicitly optional.
2. Separate portable concepts from harness-specific examples so the core skill never depends on OpenClaw, Codex, Claude, or any repo-local hook runner.
3. Show how to wire the store path, compaction cadence, and promotion approval step into different harnesses using small examples.
4. Keep command-wrapper instructions thin and route all durable policy back to `SKILL.md` and the references.

**Verification**

- Run: `rg -n \"OpenClaw|Codex|Claude|hook\" skills/self-improve`
- Expect: platform-specific mentions appear only in optional adapter docs or examples, not as hard requirements in the core workflow.
- Run: `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills self-improve --strict`
- Expect: strict pass after adapter guidance is added.

**Done When**

- The skill is agent-agnostic at its core.
- Adapter guidance exists for extensibility but is clearly optional.
- Command ergonomics do not introduce hidden platform coupling.

### Task 5: Add Trigger Evals And Negative Controls

**Objective**

Protect routing quality and behavioral boundaries with deterministic evals that distinguish self-improve from adjacent workflow skills.

**Files**

- Modify: `skills/skill-evals/assets/trigger-collision-cases-expanded.json`
- Create: `skills/self-improve/assets/sample-prompts.md`
- Create: `skills/self-improve/scripts/smoke_test.sh`

**Dependencies**

Task 4

**Implementation Steps**

1. Add positive trigger cases for prompts about capturing agent learnings, proposing persistent behavior changes, or extracting a reusable skill from repeated experience.
2. Add negative controls for prompts that should route elsewhere, especially project-doc retros (`session-retro`), session handoff summaries (`compact-session`), and generic new-skill authoring (`skill-creator`).
3. Add a small smoke-test script that runs local validation commands in the expected order for maintainers.
4. Review the skill description vocabulary to minimize lexical overlap with adjacent skills.

**Verification**

- Run: `python3 skills/skill-evals/scripts/run_trigger_evals.py --cases skills/skill-evals/assets/trigger-collision-cases-expanded.json --skills-root skills --pretty`
- Expect: new self-improve cases pass and adjacent skills do not regress.
- Run: `bash skills/self-improve/scripts/smoke_test.sh`
- Expect: exits 0 after running the declared validation sequence.

**Done When**

- Trigger behavior is tested with both positive and negative cases.
- The skill does not collide materially with adjacent workflow skills.
- Maintainers have a single smoke-test entrypoint for the package.

### Task 6: Integrate The Skill Into Repo Catalog And Maintenance Docs

**Objective**

Make the new capability visible and maintainable in the repo’s canonical docs and runtime inventory.

**Files**

- Modify: `docs/system/FEATURES.md`
- Modify: `docs/system/ROADMAP.md`
- Modify: `skills.json`

**Dependencies**

Task 5

**Implementation Steps**

1. Add the new skill to the appropriate catalog section in `docs/system/FEATURES.md`.
2. Add a roadmap note for future phase work such as governed auto-promotion, canarying, or integration with a broader harness improvement pipeline.
3. Regenerate `skills.json` through the normal manifest workflow.
4. Confirm that all repo hooks triggered by skill edits pass cleanly after the full package lands.

**Verification**

- Run: `python3 scripts/generate_skills_manifest.py`
- Expect: `skills.json` updates without errors and includes `self-improve`.
- Run: `rg -n \"self-improve\" docs/system/FEATURES.md docs/system/ROADMAP.md skills.json`
- Expect: catalog, roadmap, and manifest entries are present.

**Done When**

- The new skill is discoverable in canonical docs and the runtime manifest.
- Future expansion work is documented without overcommitting the MVP.
- Repo-maintenance workflows remain green after integration.

## Risks And Mitigations

- Risk: The skill drifts into autonomous self-modification and becomes unsafe or harness-specific.
  Mitigation: Keep mutation out of the MVP, require proposal artifacts, and isolate all adapter details in optional references.
- Risk: Raw learning logs become a context sink.
  Mitigation: Use append-only structured records plus compaction summaries and document summary-first read discipline.
- Risk: Trigger overlap with `session-retro`, `compact-session`, or `skill-creator`.
  Mitigation: Add explicit negative boundaries in `SKILL.md` and corresponding trigger-eval fixtures.
- Risk: Promotion artifacts are too vague to validate or act on.
  Mitigation: Require rationale, evidence, blast radius, and concrete verification commands in the proposal template.
- Risk: The design overfits pskoett/OpenClaw conventions.
  Mitigation: Recast `.learnings/` ideas into a portable storage contract with optional adapter examples only.

## Verification Matrix

| Requirement | Proof command | Expected signal |
| --- | --- | --- |
| New skill scaffold is structurally valid | `python3 skills/skill-creator/scripts/quick_validate.py skills/self-improve` | Exit code 0 |
| New skill passes contract checks | `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills self-improve --strict` | Strict pass |
| Learning capture script works | `python3 skills/self-improve/scripts/append_learning.py --store /tmp/self-improve-demo --kind learning --summary "test" --evidence "test"` | Structured record created |
| Learning compaction works | `python3 skills/self-improve/scripts/compact_learnings.py --store /tmp/self-improve-demo` | Summary artifact created |
| Promotion proposal generation works | `python3 skills/self-improve/scripts/propose_promotion.py --store /tmp/self-improve-demo --summary-file /tmp/self-improve-demo/.self-improve/summaries/latest.md` | Proposal artifact created |
| Skill-candidate extraction works | `python3 skills/self-improve/scripts/extract_skill_candidate.py --proposal /tmp/self-improve-demo/.self-improve/proposals/latest.md --output /tmp/self-improve-demo/self-improve-candidate` | Candidate scaffold rendered |
| Trigger boundaries hold | `python3 skills/skill-evals/scripts/run_trigger_evals.py --cases skills/skill-evals/assets/trigger-collision-cases-expanded.json --skills-root skills --pretty` | Self-improve cases pass without adjacent regressions |
| Manifest integration is complete | `python3 scripts/generate_skills_manifest.py && rg -n "self-improve" docs/system/FEATURES.md docs/system/ROADMAP.md skills.json` | Manifest and docs include the new skill |

## Handoff

1. Execute this plan in this session, starting with Task 1 and Task 2.
2. Open a separate execution session dedicated to building the new skill package and eval coverage.
3. Refine this plan before implementation if you want a different balance between MVP portability and future autonomous promotion features.
