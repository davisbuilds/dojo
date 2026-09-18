# Vision

Dojo makes reusable agent capabilities portable, reliable, and easy to evolve.
This is a decision framework, not a release plan.

## Why This Exists

A skill earns its place by adding something useful to a capable agent: specialized
knowledge, working tools, local conventions, user preferences, or safeguards for
failures that matter. The relevant baseline is the agent with its actual tools,
harness instructions, and repository context, not an unassisted model.

As models and harnesses improve, the useful content of a skill can change.
Dojo should make it easy to shorten, narrow, relocate, or retire guidance that
no longer helps. A smaller catalog can be progress. Capability growth is a
reason to revisit instructions, not proof that a particular safeguard is obsolete.

## Guiding Principles

1. **Add value beyond the baseline.** Spend context on information, capabilities,
   and preferences the agent would otherwise lack. Generic methodology needs
   a specific reason to remain.
2. **Preserve room for judgment.** State the desired outcome, constraints, and
   relevant evidence. Prescribe a sequence only when order protects a real
   dependency, consumer contract, or fragile operation.
3. **Preserve user intent and authority.** Consultation must not expand the task,
   imply new permissions, or require redundant approval. Investigation, design,
   and implementation have different completion conditions.
4. **Compose without cascading.** Let a primary task consult narrow guidance
   without inheriting every sibling's workflow and deliverables. Escalate for
   unresolved decisions or concrete risk, not file count or domain overlap.
5. **Make artifacts serve consumers.** Save decisions when requested, required by
   the project, or useful for coordination and later execution. Reuse accepted
   contracts and fresh evidence. Thinking carefully does not require publishing
   a document for every stage.
6. **Protect meaningful invariants.** Preserve authority, privacy, compatibility,
   recovery, and evidence for consequential claims. Use scripts and validators
   for enforceable properties; distinguish structural checks from proof that
   behavior is correct. Presentation preferences are not safety invariants.
7. **Keep discovery and context economical.** Use precise triggers, appropriate
   distribution scope, and progressive disclosure. Account for attention,
   unnecessary stops, and maintenance as well as tokens.
8. **Stay portable and honest.** Keep model-specific assumptions and platform
   details explicit and revisitable. Distinguish observed results, design
   expectations, and unknowns; do not promise equal effectiveness on every model.

## Future State

Dojo is a maintained set of useful capabilities whose scope can change with the
agents using them:

- Skills are discoverable, versioned, and safely distributable across harnesses.
- Tools and specialized references remain available without prescribing an
  entire methodology for every task.
- Workflow depth follows uncertainty, dependencies, reversibility, and the
  consequence of error. Formal contracts and plans remain available when needed.
- Authoring, validation, and distribution agree about what a skill requires.
- Feedback supports both adding useful capability and removing obsolete process.

## Decision Rubric

When adding or revising guidance, ask:

- What decision or outcome does this improve over the agent's existing context?
- What would be lost if the instruction were removed or made advisory?
- Does a constraint protect an actual boundary or merely enforce a preferred style?
- Can an existing tool, reference, repository rule, or accepted artifact do the job?
- What evidence would justify keeping, narrowing, or retiring it later?

Use judgment proportional to the change. Repair an obvious scope conflict
without commissioning an experiment. Claims that a skill improves model outcomes
need behavioral evidence appropriate to that claim. Invocation frequency,
structural validity, and shorter text alone do not establish value.

## Non-Goals

- Maximizing the number of skills, instructions, or generated artifacts.
- Teaching generic competence by default or freezing today's reasoning process
  into tomorrow's agents.
- Trading away safety or user preferences because a model appears more capable.
- Building a new approval or evaluation bureaucracy for every small revision.

## Success Indicators

Tasks produce useful, verified outcomes with fewer unnecessary interruptions and
duplicate artifacts. Required boundaries remain intact. Contributors can explain
what each skill adds, and can remove outdated guidance without fighting templates
or validators. Catalog and harness changes are reflected honestly in evidence
and documentation.

## Relationship to Other Docs

- [SKILL-BEST-PRACTICES.md](../system/SKILL-BEST-PRACTICES.md) translates this direction into authoring and maintenance guidance.
- [ROADMAP.md](./ROADMAP.md) records shipped changes and current work.
- [BACKLOG.md](./BACKLOG.md) tracks unresolved friction and follow-ups.
- [ARCHITECTURE.md](../system/ARCHITECTURE.md) describes the operating model.
- [GIT_HISTORY_POLICY.md](./GIT_HISTORY_POLICY.md) defines history hygiene.
