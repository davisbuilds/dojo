---
name: trifecta-check
description: Investigate agent prompt-injection paths across data access, untrusted content, and action authority.
argument-hint: "[agent system or target paths]"
---

# Agent authority review

This compatibility command now invokes an investigation, not a regex verdict.
Read [agent authority boundaries](../references/lethal-trifecta.md), then follow
untrusted content through model context and delegated actions to sensitive data
or effects. Include cross-file, tool, process, and service boundaries.

Identify a plausible path, the effective authority and its enforcement, existing
controls, and what remains unverified. Same-file co-occurrence is neither proof
of exploitability nor a prerequisite for risk. If the target has no agent-mediated
path, say so and address any ordinary code-security concern on its own merits.

Use secure-code's output and verification contract. No count of keywords, clean
architecture certification, or default demand to separate modules.
