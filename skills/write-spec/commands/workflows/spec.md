---
name: workflows:spec
description: Write a falsifiable contract (the target) from a feature request, ticket, or approved design summary — before sequencing the build.
argument-hint: "[feature, ticket, or approved design summary]"
---

# Spec A Feature Or Change

This command requests a durable contract using the canonical `write-spec` skill.
Load it and use the conversation and `#$ARGUMENTS` as input. Ask only for material
missing decisions; resolve repository facts directly.

## Flow

- Reuse or amend an accepted contract when it already covers the target.
- State falsifiable outcomes and relevant failure/authority behavior. Resolve
  blocking contract decisions before calling the target ready.
- Save the requested artifact at `docs/specs/YYYY-MM-DD-<topic>-spec.md` or update
  the existing contract. Use `assets/spec-template.md` with resolved author
  metadata and the canonical risk classification.
- For `high`, load the high-risk reference/addendum and complete validation,
  adversarial critique, revision, and closure critique before setting
  `readiness: ready`. Use a critique subagent when supported and authorized;
  otherwise critique inline.
- Run `python3 <skill-dir>/scripts/validate_spec.py docs/specs/<filename>.md`.
  Fix schema errors and judge advisories against the actual acceptance criteria.

Report the saved artifact and meaningful readiness limits. Handoff content is
optional and describes a real next action, not a required menu. Do not start a
planning workflow merely because the spec is complete. A spec-only request does
not authorize implementation; continue further work only within existing scope.
