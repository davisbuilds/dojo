---
name: agent-native-architecture
description: Build applications where agents are first-class citizens. Use this skill when designing autonomous agents, creating MCP tools, implementing self-modifying systems, or building apps where features are outcomes achieved by agents operating in a loop.
skill-type: reference
version: 2.0.0
---

## When To Use

- Designing a new agent-native system from scratch
- Adding agent capabilities (MCP tools, system prompts) to an existing app
- Reviewing architecture for parity, granularity, or composability gaps
- Refactoring traditional code toward prompt-native patterns

## Output

- Architecture plan addressing the checklist (parity, granularity, composability, emergent capability)
- Tool inventory with CRUD completeness assessment
- System prompt draft or refinement
- Identified gaps and recommended next steps

## Why Now

Software agents work reliably now. AI coding agents have demonstrated that an LLM with access to bash and file tools, operating in a loop until an objective is achieved, can accomplish complex multi-step tasks autonomously.

The surprising discovery: **a really good coding agent is actually a really good general-purpose agent.** The same architecture that lets a coding agent refactor a codebase can let an agent organize your files, manage your reading list, or automate your workflows.

Agent SDKs make this accessible. You can build applications where features aren't code you write—they're outcomes you describe, achieved by an agent with tools, operating in a loop until the outcome is reached.

This opens up a new field: software that works the way coding agents work, applied to categories far beyond coding.

## Core Principles

Five principles, in dependency order. Each is stated here; the reasoning and
worked examples are in `references/core-principles.md`, which you should read
before applying any of them to a real design.

1. **Parity** — whatever the user can do through the UI, the agent should be
   able to achieve through tools. Foundational: without it nothing else matters.
2. **Granularity** — tools should be small enough to compose and large enough to
   be meaningful on their own.
3. **Composability** — capability comes from combining tools, not from adding a
   tool per use case.
4. **Emergent Capability** — a well-composed toolset does things nobody designed
   a path for.
5. **Improvement Over Time** — the system should get better as the model does,
   without a rewrite.

## Routing

Ask which aspect the user needs, then read the matching reference before
applying anything. One topic per row; the numbered menu and the routing table
that used to duplicate each other are merged here.

| Aspect | Read |
|---|---|
| Design a new agent-native system | [architecture-patterns.md](./references/architecture-patterns.md), then the checklist below |
| Files, workspace, filesystem as interface | [files-universal-interface.md](./references/files-universal-interface.md), [shared-workspace-architecture.md](./references/shared-workspace-architecture.md) |
| Tool design, MCP, primitives, CRUD completeness | [mcp-tool-design.md](./references/mcp-tool-design.md) |
| When to add domain tools vs stay primitive | [from-primitives-to-domain-tools.md](./references/from-primitives-to-domain-tools.md) |
| Execution, completion signals, context limits | [agent-execution-patterns.md](./references/agent-execution-patterns.md) |
| System prompts, judgment criteria | [system-prompt-design.md](./references/system-prompt-design.md) |
| Injecting runtime app state | [dynamic-context-injection.md](./references/dynamic-context-injection.md) |
| Action parity, capability mapping | [action-parity-discipline.md](./references/action-parity-discipline.md) |
| Letting agents evolve themselves safely | [self-modification.md](./references/self-modification.md) |
| Product design, progressive disclosure, approvals | [product-implications.md](./references/product-implications.md) |
| Mobile: iOS storage, background, checkpoint/resume | [mobile-patterns.md](./references/mobile-patterns.md) |
| Testing for capability and parity | [agent-native-testing.md](./references/agent-native-testing.md) |
| Refactoring existing code toward agent-native | [refactoring-to-prompt-native.md](./references/refactoring-to-prompt-native.md) |

## Architecture Review Checklist

When designing an agent-native system, verify these **before implementation**:

### Core Principles
- [ ] **Parity:** Every UI action has a corresponding agent capability
- [ ] **Granularity:** Tools are primitives; features are prompt-defined outcomes
- [ ] **Composability:** New features can be added via prompts alone
- [ ] **Emergent Capability:** Agent can handle open-ended requests in your domain

### Tool Design
- [ ] **Dynamic vs Static:** For external APIs where agent should have full access, use Dynamic Capability Discovery
- [ ] **CRUD Completeness:** Every entity has create, read, update, AND delete
- [ ] **Primitives not Workflows:** Tools enable capability, don't encode business logic
- [ ] **API as Validator:** Use `z.string()` inputs when the API validates, not `z.enum()`

### Files & Workspace
- [ ] **Shared Workspace:** Agent and user work in same data space
- [ ] **context.md Pattern:** Agent reads/updates context file for accumulated knowledge
- [ ] **File Organization:** Entity-scoped directories with consistent naming

### Agent Execution
- [ ] **Completion Signals:** Agent has explicit `complete_task` tool (not heuristic detection)
- [ ] **Partial Completion:** Multi-step tasks track progress for resume
- [ ] **Context Limits:** Designed for bounded context from the start

### Context Injection
- [ ] **Available Resources:** System prompt includes what exists (files, data, types)
- [ ] **Available Capabilities:** System prompt documents tools with user vocabulary
- [ ] **Dynamic Context:** Context refreshes for long sessions (or provide `refresh_context` tool)

### UI Integration
- [ ] **Agent → UI:** Agent changes reflect in UI (shared service, file watching, or event bus)
- [ ] **No Silent Actions:** Agent writes trigger UI updates immediately
- [ ] **Capability Discovery:** Users can learn what agent can do

### Mobile (if applicable)
- [ ] **Checkpoint/Resume:** Handle iOS app suspension gracefully
- [ ] **iCloud Storage:** iCloud-first with local fallback for multi-device sync
- [ ] **Cost Awareness:** Model tier selection (Haiku/Sonnet/Opus)

**When designing architecture, explicitly address each checkbox in your plan.**

## Quick Start: Build an Agent-Native Feature

**Step 1: Define atomic tools**
```typescript
const tools = [
  tool("read_file", "Read any file", { path: z.string() }, ...),
  tool("write_file", "Write any file", { path: z.string(), content: z.string() }, ...),
  tool("list_files", "List directory", { path: z.string() }, ...),
  tool("complete_task", "Signal task completion", { summary: z.string() }, ...),
];
```

**Step 2: Write behavior in the system prompt**
```markdown
## Your Responsibilities
When asked to organize content, you should:
1. Read existing files to understand the structure
2. Analyze what organization makes sense
3. Create/move files using your tools
4. Use your judgment about layout and formatting
5. Call complete_task when you're done

You decide the structure. Make it good.
```

**Step 3: Let the agent work in a loop**
```typescript
const result = await agent.run({
  prompt: userMessage,
  tools: tools,
  systemPrompt: systemPrompt,
  // Agent loops until it calls complete_task
});
```

## Reference Files

- `references/core-principles.md` — the five principles in full, with examples.
- `references/anti-patterns.md` — designs that look agent-native and are not.

All references in `references/`:

**Core Patterns:**
- [architecture-patterns.md](./references/architecture-patterns.md) - Event-driven, unified orchestrator, agent-to-UI
- [files-universal-interface.md](./references/files-universal-interface.md) - Why files, organization patterns, context.md
- [mcp-tool-design.md](./references/mcp-tool-design.md) - Tool design, dynamic capability discovery, CRUD
- [from-primitives-to-domain-tools.md](./references/from-primitives-to-domain-tools.md) - When to add domain tools, graduating to code
- [agent-execution-patterns.md](./references/agent-execution-patterns.md) - Completion signals, partial completion, context limits
- [system-prompt-design.md](./references/system-prompt-design.md) - Features as prompts, judgment criteria

**Agent-Native Disciplines:**
- [dynamic-context-injection.md](./references/dynamic-context-injection.md) - Runtime context, what to inject
- [action-parity-discipline.md](./references/action-parity-discipline.md) - Capability mapping, parity workflow
- [shared-workspace-architecture.md](./references/shared-workspace-architecture.md) - Shared data space, UI integration
- [product-implications.md](./references/product-implications.md) - Progressive disclosure, latent demand, approval
- [agent-native-testing.md](./references/agent-native-testing.md) - Testing outcomes, parity tests

**Platform-Specific:**
- [mobile-patterns.md](./references/mobile-patterns.md) - iOS storage, checkpoint/resume, cost awareness
- [self-modification.md](./references/self-modification.md) - Git-based evolution, guardrails
- [refactoring-to-prompt-native.md](./references/refactoring-to-prompt-native.md) - Migrating existing code

## Anti-Patterns

Designs that look agent-native but are not — chat bolted onto a CRUD app,
one tool per screen, agent-only side doors that drift from the UI. The full
catalogue, with the failure each one produces, is in
`references/anti-patterns.md`. Read it when reviewing an existing design
rather than when building a new one.

## Success Criteria

You've built an agent-native application when:

### Architecture
- [ ] The agent can achieve anything users can achieve through the UI (parity)
- [ ] Tools are atomic primitives; domain tools are shortcuts, not gates (granularity)
- [ ] New features can be added by writing new prompts (composability)
- [ ] The agent can accomplish tasks you didn't explicitly design for (emergent capability)
- [ ] Changing behavior means editing prompts, not refactoring code

### Implementation
- [ ] System prompt includes dynamic context about app state
- [ ] Every UI action has a corresponding agent tool (action parity)
- [ ] Agent tools are documented in system prompt with user vocabulary
- [ ] Agent and user work in the same data space (shared workspace)
- [ ] Agent actions are immediately reflected in the UI
- [ ] Every entity has full CRUD (Create, Read, Update, Delete)
- [ ] Agents explicitly signal completion (no heuristic detection)
- [ ] context.md or equivalent for accumulated knowledge

### Product
- [ ] Simple requests work immediately with no learning curve
- [ ] Power users can push the system in unexpected directions
- [ ] You're learning what users want by observing what they ask the agent to do
- [ ] Approval requirements match stakes and reversibility

### Mobile (if applicable)
- [ ] Checkpoint/resume handles app interruption
- [ ] iCloud-first storage with local fallback
- [ ] Background execution uses available time wisely
- [ ] Model tier matched to task complexity

---

### The Ultimate Test

**Describe an outcome to the agent that's within your application's domain but that you didn't build a specific feature for.**

Can it figure out how to accomplish it, operating in a loop until it succeeds?

If yes, you've built something agent-native.

If it says "I don't have a feature for that"—your architecture is still too constrained.
