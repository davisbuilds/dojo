# Skill authoring rules

Always-follow conventions for adding or changing a skill. The deterministic form
of these is enforced by `skills/skill-evals/scripts/validate_skill_contract.py`;
see `docs/system/skill-contract-v1.md` for the full contract.

## Frontmatter

- `name`: hyphen-case, ≤64 chars, matches the directory name.
- `description`: ≤1024 chars, no angle brackets, and trigger-ready — say both
  what the skill does and when to use it ("Use when…", "Triggers on…").
- `skill-type`: declare `workflow` or `reference`.
- `triggers` (optional): literal trigger phrases that should route to the skill.
  Echo the skill's name/description vocabulary so the trigger evals can confirm
  self-routing without collisions.

## Body (contract anchors)

- Scope anchor: a "When to use" / "Prerequisites" section.
- Boundaries anchor: explicit non-goals ("Not for…", "Skip when…").
- Verification anchor: quality / success criteria.
- Resource map: if the skill bundles `scripts/`, `references/`, `assets/`, or
  `commands/`, point to them from the body.
- `workflow` skills also need an execution anchor (Workflow/Process/Steps) and
  an output contract.

## Economy

- Keep SKILL.md under ~500 lines; push detail into `references/`.
- Add only what the agent does not already know. Context is shared and finite.

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
