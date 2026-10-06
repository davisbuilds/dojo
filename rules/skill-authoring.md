# Skill authoring rules

Standing conventions for adding or changing a skill. Packaging requirements
are enforced by `skills/skill-evals/scripts/validate_skill_contract.py`; the
design judgments below require review. See `docs/system/skill-contract-v1.md`
for the packaging contract and `docs/system/SKILL-BEST-PRACTICES.md` for the
authoring and retirement guidance.

## Frontmatter

- `name`: hyphen-case, ≤64 chars, matches the directory name.
- `description`: ≤1024 chars, no angle brackets, and trigger-ready — say both
  what the skill does and when to use it ("Use when…", "Triggers on…").
- `version`: SemVer release; bump and update the skill changelog for release-relevant changes.
- `skill-type`: declare `workflow` or `reference`.
- `triggers` (optional): literal trigger phrases that should route to the skill.
  Use natural requests; treat lexical collisions as diagnostics, not a reason
  to add keywords that broaden actual discovery.

## Body (design review)

Explain relevant scope, boundaries, useful outcomes, verification, and how to
reach needed resources. Fit the structure to the capability; no named sections
or numbered workflow are required. The validator's opt-in heading/resource hints
are fallible prompts for review, not semantic checks or release gates.

## Economy

- Keep instructions relevant; move optional detail to references when it helps
  selection. Line count is an advisory placement signal, not a length mandate.
- Add only what the agent does not already know. Context is shared and finite.
- Identify the capability, preference, or consequential failure that justifies
  an instruction. Prefer narrowing or removing obsolete process over adding
  exceptions; preserve actual authority and consumer requirements. A shorter
  file or frequently invoked skill is not by itself evidence of value.

## Scope and composition

- Follow the user's requested scope and existing authorization. Reading a skill
  does not authorize a repair, publication, or other additional action.
- Distinguish completing a requested workflow from consulting guidance during
  another task. A sibling reference supplies relevant advice; it does not
  recursively activate that sibling's workflow, deliverables, or handoffs.
- Escalate for an unresolved material decision, dependency, or verification
  problem, not file count or domain overlap. Reuse accepted decisions and fresh
  evidence instead of requiring duplicate artifacts.
- Require evidence for consequential claims; make sequence, templates, report
  formats, and conversational checkpoints optional unless a concrete consumer
  or risk requires them. Preserve authority, privacy, compatibility, recovery,
  and applicable behavioral verification requirements.
- State these boundaries in installed skills as well as authoring guidance.
  Follow higher-priority harness loading rules; do not suggest that a skill body
  can override them. Consultation need not expand the user's deliverable.

## Before you finish

- Run the strict contract: `validate_skill_contract.py --skills-root skills --strict`.
- If you declared `triggers`, run `run_trigger_evals.py --from-triggers`.
- Regenerate derived artifacts (`gen_skill_docs.py`, `gen_harness_adapters.py`,
  `gen_catalog.py`) or let the hooks do it, then confirm `--check` is clean.
