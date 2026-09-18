---
name: workflows:brainstorm
description: Explore requirements and approaches through collaborative dialogue before planning implementation.
argument-hint: "[feature idea or problem to explore]"
---

# Brainstorm A Feature Or Improvement

This command invokes the canonical `brainstorming` skill. Load its guidance and
use the user's request and `#$ARGUMENTS` as context; ask for the missing goal only
if neither supplies it.

## Flow

- Ground the discussion in available project context. If the direction is
  already clear, skip unnecessary questions and continue within existing scope.
- Ask about material unresolved decisions; group independent questions when
  useful. Compare meaningful alternatives and explain the recommendation.
- Summarize the direction and open questions conversationally. Save or update
  `docs/design/YYYY-MM-DD-<topic>-design.md` only when requested, project-required,
  or useful for downstream work. Saved summaries use resolved `author:` metadata
  and the canonical skill's scaffold as appropriate.
- Consult relevant sibling guidance without inheriting its entire workflow.
  Recommend a further workflow only when a material unresolved need warrants it.

A discussion-only request ends with discussion. Continue implementation only
when it is already authorized and the direction is settled. Do not ask permission
to skip ceremony, require a handoff menu, or turn this command into an automatic
spec/plan pipeline.
