---
name: self-improve
description: Capture, compact, or promote agent-operational learnings using the self-improve skill.
argument-hint: "capture|compact|propose|extract [flags]"
allowed-tools: [Read, Bash(python3 skills/self-improve/scripts/append_learning.py:*), Bash(python3 skills/self-improve/scripts/compact_learnings.py:*), Bash(python3 skills/self-improve/scripts/propose_promotion.py:*), Bash(python3 skills/self-improve/scripts/extract_skill_candidate.py:*)]
---

# Self Improve Command

Use this wrapper to run the canonical self-improvement workflow from `skills/self-improve`.

## Behavior

1. Load `skills/self-improve/SKILL.md`.
2. Route the first argument as a subcommand:
   - `capture` -> `append_learning.py`
   - `compact` -> `compact_learnings.py`
   - `propose` -> `propose_promotion.py`
   - `extract` -> `extract_skill_candidate.py`
3. Require an explicit store or proposal path rather than inferring hidden workspace state.
4. Report the created artifact path after each successful command.

## Example Invocations

```bash
/self-improve capture --store /repo --kind learning --summary "Use summary-first reads" --evidence "Lower context cost"
/self-improve compact --store /repo --limit 15
/self-improve propose --store /repo --summary-file /repo/.self-improve/summaries/latest.md
/self-improve extract --proposal /repo/.self-improve/proposals/latest.md --output /tmp/context-discipline-skill
```

## Output Rules

- Do not claim that behavior changed permanently unless a proposal or candidate artifact was actually created.
- Do not mutate project docs or repo code from this wrapper.
- Base durable promotion claims on the generated proposal, not on raw inbox records alone.
