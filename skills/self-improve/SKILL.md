---
name: self-improve
description: Capture agent-operational lessons, recurring mistakes, and reusable workflow improvements in a dedicated learning store, compact them, and promote validated patterns into memory notes or skill candidates. Use when the user wants the agent to learn from repeated experience, keep a portable improvement log, extract reusable practices, or propose durable behavior changes without silently mutating code or canonical project docs.
---

# Self Improve

Capture self-improvement signals in a portable store, then promote only validated patterns into durable artifacts. Favor explicit capture, compaction, and reviewable proposals over implicit self-modification.

## When To Use

- The user wants the agent to remember repeated mistakes, successful fixes, or workflow improvements across sessions.
- You want a portable learning log that is separate from project documentation and can be compacted aggressively.
- A repeated pattern looks reusable enough to become a memory note or a draft skill candidate.
- You need to propose a durable behavior change, but want an explicit review artifact before any lasting mutation.

## Boundaries

- Not for updating `AGENTS.md`, `README.md`, or other project reference docs. Use `session-retro` for that.
- Not for session handoff summaries or transcript compaction. Use `compact-session` when the goal is resumability for a fresh instance.
- Not for creating a brand-new skill from scratch without prior learning artifacts. Use `skill-creator` for direct skill authoring.
- Do not silently edit code, prompts, or repo docs as part of this workflow. Promotion should produce reviewable artifacts first.

## Workflow

1. Choose the mode.
   - **Capture**: append a structured learning record.
   - **Compact**: turn raw records into a smaller summary artifact.
   - **Propose**: generate a reviewable promotion proposal from a summary.
   - **Extract**: turn a strong proposal into a draft skill candidate.

2. Capture a learning record.

```bash
python3 skills/self-improve/scripts/append_learning.py \
  --store /path/to/workspace \
  --kind learning \
  --summary "Reduced wasted reads by checking repo-local docs first" \
  --evidence "Avoided redundant context loading on the next similar task" \
  --tags context,triage
```

3. Compact the store before loading history into context.

```bash
python3 skills/self-improve/scripts/compact_learnings.py \
  --store /path/to/workspace \
  --limit 20
```

Read `summaries/latest.md` first. Only inspect raw inbox records when the summary suggests they matter.

4. Propose promotion for validated patterns.

```bash
python3 skills/self-improve/scripts/propose_promotion.py \
  --store /path/to/workspace \
  --summary-file /path/to/workspace/.self-improve/summaries/latest.md
```

Promotion targets are described in `references/promotion-policy.md`.

5. Extract a draft skill candidate only when the pattern is general, repeated, and worth reuse.

```bash
python3 skills/self-improve/scripts/extract_skill_candidate.py \
  --proposal /path/to/workspace/.self-improve/proposals/latest.md \
  --output /tmp/repeated-pattern-skill
```

## Output

- Structured learning records under a dedicated `.self-improve/` store.
- Compact summaries suitable for selective loading.
- Reviewable promotion proposals with rationale, blast radius, and verification steps.
- Draft skill candidates for repeated, reusable patterns.

## Verification

- `python3 skills/skill-creator/scripts/quick_validate.py skills/self-improve` passes.
- `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills self-improve --strict` passes.
- Capture, compaction, proposal, and extraction scripts run without crashing on a demo store.
- Trigger evals keep `self-improve` separate from `session-retro`, `compact-session`, and `skill-creator`.

## Resources

- `scripts/append_learning.py` - Append a structured learning record to the store.
- `scripts/compact_learnings.py` - Build a compact markdown summary from raw records.
- `scripts/propose_promotion.py` - Convert a summary into a reviewable promotion proposal.
- `scripts/extract_skill_candidate.py` - Render a draft skill candidate from a proposal.
- `scripts/smoke_test.sh` - Run the local validation sequence for this skill.
- `references/storage-layout.md` - Store structure and summary-first loading rules.
- `references/promotion-policy.md` - Promotion tiers and approval guidance.
- `references/adapter-patterns.md` - Optional harness adapter patterns.
- `assets/sample-prompts.md` - Prompt examples for routing and manual testing.
- `commands/self-improve.md` - Slash-style wrapper for harnesses that support command files.
