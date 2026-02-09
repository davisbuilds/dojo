---
name: autonomous-engineering
description: "Full autonomous engineering workflows that run a complete feature development cycle: plan, deepen, implement, review, resolve, test, and record. Use when asked to build a feature end-to-end, go autonomous, or when user says 'lfg' or 'slfg'. Includes a sequential variant (lfg) and a swarm-parallel variant (slfg) for faster execution of large features."
---

# Autonomous Engineering

End-to-end feature development workflows. Each variant chains slash commands in order to go from a feature description to a merged, reviewed, tested PR with a video walkthrough.

## Commands

### `/lfg [feature description]`

Sequential workflow — runs each phase one after another:

1. Plan implementation from feature description
2. Deepen plan with research and best practices
3. Execute the implementation
4. Multi-agent code review
5. Resolve issues found in review
6. Run browser tests on affected pages
7. Record feature walkthrough and add to PR

### `/slfg [feature description]`

Swarm-parallel variant — same phases, but parallelizes where possible:

- Work phase uses parallel Task agents
- Review and browser testing run concurrently
- Faster completion for large features

## When to Use

- User provides a feature description and wants autonomous implementation
- User says "lfg", "slfg", "build this", or "go autonomous"
- A feature is well-scoped enough to plan, implement, review, and ship in one cycle
