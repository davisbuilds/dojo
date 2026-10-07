---
name: agent-native-design
description: Design software for agent consumers and delegated work. Use when shaping agent-facing capabilities, delegated responsibilities, cross-agent coordination, human control of agent-driven experiences, or products with agents as primary consumers.
skill-type: reference
version: 3.1.0
---

# Agent-Native Design

Help agents achieve useful outcomes through an environment they can understand,
act within, and obtain evidence from. Choose where agent judgment adds value and
where the system should supply dependable operations. Increasing capability
should create room for better choices without dissolving the product's contracts.

## When to use

Use for a design decision about agents as software consumers or participants:
exposing an existing service, delegating a recurring responsibility, coordinating
across agents, or conceiving a product around agent use. Apply the relevant lens
to the current question; these are overlapping design problems, not maturity stages.

| Design problem | What needs deciding | Reference, when that detail matters |
| --- | --- | --- |
| Software agents can use | How an agent discovers capabilities, obtains context, acts, and checks the result | [Agent-facing interfaces](references/agent-facing-interfaces.md) |
| Software that delegates work | What discretion is delegated, who owns state, and how work survives failure or changes of intent | [Delegated work](references/delegated-work.md) |
| Products for agent consumers | What the agent consumes, who benefits or pays, and how people understand and steer the service | [Product and human agency](references/product-and-human-agency.md) |

A service can be useful to agents without containing an agent. A delegated task
can use one reliable operation without an autonomous loop. A product can combine
conventional code, agent judgment, and existing services.

## Design lenses

Use the lenses that expose a consequential decision or gap. Do not turn them into
an exhaustive checklist for every change.

- **Intent and discretion.** Separate the desired outcome from the choices the
  agent may make. Reuse settled requirements. Distinguish a proposed action from
  permission to execute it, especially when another agent supplied the request.
- **Context and discovery.** Make relevant resources, capabilities, and limitations
  findable at the point of use. Preserve source, freshness, and access boundaries;
  missing information should remain distinguishable from a negative finding.
- **Action and authority.** Choose useful operation boundaries. A domain operation
  can enforce an atomic transition that raw CRUD cannot. Keep authorization,
  accounting rules, and other enforceable invariants in the executing system;
  prompts can express preferences and guide judgment within those boundaries.
- **Evidence and completion.** Give agents ways to inspect outcomes as well as
  perform actions. Separate accepted, running, completed, and verified where the
  distinction matters. Evidence should identify its target, scope, and limitations;
  an agent's completion message alone does not establish an external effect.
- **Continuity and control.** For work that outlives a call or session, make its
  owner, committed effects, and remaining work recoverable. Let people revise
  intent and intervene without reconstructing every tool call.
- **Capability growth.** Leave choices open where stronger agents can improve
  them. Keep stable contracts around identity, authority, state, and evidence.
  Revisit model-specific scaffolding using observed behavior; fewer constraints,
  more tools, or more autonomy do not by themselves establish a better product.

## Boundaries

This skill informs the requested design, review, or implementation. It does not
require a new architecture document, tool inventory, prompt draft, or approval
round. Read only the references that help resolve the actual question.

Universal UI parity, full CRUD, primitive-only tools, shared filesystem access,
and prompt-only feature development are not goals. Support the outcomes the
product intends to delegate, including deliberate read-only or human-only roles.
Parity is useful when equivalent outcomes are promised; it does not confer the
human user's full authority on an agent.

Do not replace working business logic with prompts merely to make the system
more agent-native. Introduce judgment where variability warrants it, and retain
code where it provides needed correctness, efficiency, or transactional behavior.
A model upgrade, another agent, or a new protocol is a choice to justify against
the task, not a required component.

For ordinary endpoint schemas, CLI syntax, framework setup, or a generic UI
review, use the existing project conventions and relevant narrow guidance. An
agent being involved in the work does not make every change an agent-native
design exercise. Consultation of other guidance adds no automatic deliverables.

## Output

Improve the existing answer, design, or implementation with the decisions that
matter, their reasons, and any unresolved dependency. Save a separate artifact
only when requested or useful to its consumer. Keep design expectations distinct
from behavior observed in the target system.

## Verification

Select evidence for the claim: an agent can discover and complete the intended
job; a result can be checked against authoritative state; an interruption or
changed instruction has the promised recovery behavior; or an agent-facing
service reduces the beneficiary's work. Exercise relevant failure and authority
boundaries as well as success. A tool appearing in a registry, a valid response,
or an agent reporting success proves only that narrower fact.

For existing products, prefer a bounded change and comparison on representative
work before broad architectural replacement. A successful demo establishes
feasibility in that setting, not dependable operation or customer demand.
