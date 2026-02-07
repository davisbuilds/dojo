# Autonomous Engineering Skills

Commands for fully autonomous feature development workflows from the compound-engineering plugin.

## Commands

| Command | Description |
|---------|-------------|
| `lfg` | Full autonomous engineering workflow (sequential) |
| `slfg` | Full autonomous engineering workflow with swarm mode for parallel execution |

## LFG Workflow

The `/lfg` command runs a complete feature development cycle:

1. **Plan** - Create implementation plan from feature description
2. **Deepen** - Enhance plan with research and best practices
3. **Work** - Execute the implementation
4. **Review** - Multi-agent code review
5. **Resolve** - Fix any issues found in review
6. **Test** - Run browser tests on affected pages
7. **Video** - Record feature walkthrough and add to PR

## SLFG (Swarm LFG)

The `/slfg` variant uses swarm mode for parallel execution:

- Work phase uses parallel Task agents
- Review and browser testing run in parallel
- Faster completion for large features

## Source

These commands are extracted from the compound-engineering plugin v2.30.0.
