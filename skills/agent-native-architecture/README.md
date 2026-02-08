# Agent-Native Architecture

Architecture patterns for building applications where agents are first-class citizens. Agents operate in loops to achieve outcomes, using tools as primitives rather than workflows.

## Core Principles

1. **Parity** - Whatever a user can do, an agent can do
2. **Granularity** - Build atomic tools, compose into features via prompts
3. **Composability** - Multiple agents can share tools and workspaces
4. **Emergent Capability** - Features are outcomes, not coded functions
5. **Improvement Over Time** - Agents learn and adapt through prompt evolution

## Reference Documents

| Topic | File | Description |
|-------|------|-------------|
| Action Parity | `references/action-parity-discipline.md` | Ensuring agents have same capabilities as users |
| Agent Execution | `references/agent-execution-patterns.md` | Completion signals, checkpointing, model tiers |
| Testing | `references/agent-native-testing.md` | Testing outcomes, not procedures |
| Architecture | `references/architecture-patterns.md` | Event-driven, git-based, unified orchestration |
| Context Injection | `references/dynamic-context-injection.md` | Runtime context in system prompts |
| Files | `references/files-universal-interface.md` | Files as the universal agent interface |
| Tool Evolution | `references/from-primitives-to-domain-tools.md` | When to add domain tools |
| MCP Design | `references/mcp-tool-design.md` | Tool design principles |
| Mobile | `references/mobile-patterns.md` | iOS storage, background execution, cost awareness |
| Product | `references/product-implications.md` | Progressive disclosure, latent demand, approval flows |
| Refactoring | `references/refactoring-to-prompt-native.md` | Moving logic from code to prompts |
| Self-Modification | `references/self-modification.md` | Agents that evolve their own code |
| Shared Workspace | `references/shared-workspace-architecture.md` | Agent-user collaboration patterns |
| System Prompts | `references/system-prompt-design.md` | Writing effective prompt-native prompts |

## Usage

The SKILL.md file provides an intake menu for navigating topics. Reference documents are loaded on-demand based on what aspect of agent-native architecture you're working on.

## Source

Extracted from the compound-engineering plugin (v2.30.0) for reference and adaptation.
