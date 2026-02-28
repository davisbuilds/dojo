# Vision

This document defines the long-term direction for Dojo as an agent-skills system.
It is not a release plan. It is the decision framework we use when tradeoffs are unclear.

## Why This Exists

Dojo should make specialized agent behavior portable, reliable, and easy to evolve without locking users into a single model vendor or harness.

## Guiding Principles

1. **Context Is Sacred**
   Context window is finite and shared. We optimize for signal density, progressive disclosure, and minimal cognitive load.
2. **Agent Agnosticism by Default**
   Skills should work across agent runtimes whenever possible. Platform-specific metadata is optional add-on, not the core contract.
3. **Extensibility Over Forking**
   Prefer composable skill structure (`commands/`, `scripts/`, `references/`, `assets/`) and clear interfaces so contributors extend behavior without cloning entire systems.
4. **Determinism for Fragile Workflows**
   High-risk operations should be script-backed, validated, and repeatable. Free-form instructions are for flexible tasks, not safety-critical paths.
5. **Progressive Disclosure**
   Load only what is needed when it is needed: metadata first, then skill body, then references/assets on demand.
6. **Policy as Code**
   Quality and safety requirements belong in hooks, validators, and machine-readable manifests, not only in prose docs.
7. **Fast Feedback, Honest State**
   The system should surface invalid structure, drift, and unsafe changes early, and block completion when repository state is inconsistent.
8. **Human-Readable and Machine-Operable**
   Every major artifact should be understandable to humans and consumable by automation.

## Future State (Target)

In the future, Dojo is the default way teams define and operate reusable agent capabilities:

- A stable, vendor-neutral skill contract is implemented across multiple harnesses.
- Skills are versioned, testable, and safely distributable with explicit compatibility and changelogs.
- Installation, updates, and drift detection are one-command workflows for local and shared registries.
- Security posture is measurable (validation, static analysis, trust scoring) before installation or execution.
- Teams can discover, evaluate, and compose skills quickly without sacrificing governance.
- Documentation, manifests, and hooks stay in sync automatically.

## Decision Rubric

When choosing between alternatives, prefer the option that:

1. Preserves context efficiency.
2. Increases cross-agent portability.
3. Reduces hidden complexity and one-off glue.
4. Improves verifiability (tests, checks, deterministic scripts).
5. Keeps contributor onboarding and extension simple.

## Non-Goals

- Building a single-agent optimization layer that cannot transfer to other runtimes.
- Maximizing feature count at the expense of clarity, trust, or maintainability.
- Relying on manual process where enforceable automation is practical.

## Success Indicators

- New skills are added with minimal custom scaffolding and pass validation immediately.
- Skill behavior remains consistent across supported agent harnesses.
- Repo hooks prevent malformed skills, stale manifests, and invalid plan artifacts from landing.
- Contributors can understand and modify the system without reverse engineering implicit conventions.
- Teams treat Dojo artifacts as durable infrastructure, not one-off prompt files.

## Relationship to Other Docs

- [ROADMAP.md](./ROADMAP.md) describes current priorities and sequencing.
- [ARCHITECTURE.md](../system/ARCHITECTURE.md) describes the operating model and technical structure.
- [GIT_HISTORY_POLICY.md](./GIT_HISTORY_POLICY.md) defines history hygiene and collaboration constraints.
