---
name: repo-harden
description: Use repo-hardening artifacts to implement the highest-value repo hardening fixes and refresh the audit packet.
argument-hint: "[repo-path] [--out-dir <dir>] [--package <name> ...]"
allowed-tools: [Read, Write, Edit, Bash(git:*), Bash(rg:*), Bash(python3 skills/repo-hardening/scripts/repo_inventory.py:*)]
---

# Repo Harden Command

Use the repo-hardening workflow to implement the most valuable hardening fixes for a target repo.

## Behavior

1. Run `/repo-audit` first if current artifacts do not exist or are stale.
2. Read the generated audit and plan plus the relevant source files.
3. Apply the minimum safe fix set that materially improves posture.
4. Run the repo's own verification commands.
5. Re-run the inventory script so the repo-local artifacts reflect the new state.
6. Return results in this order:
1. What changed
2. What was verified
3. Residual risks or backlog
4. Artifact paths

## Rules

- Prefer frozen installs, pinned refs, and explicit permission floors.
- Keep changes scoped to the target repo.
- Do not commit or push unless the user explicitly asked.
- If a fix requires a policy decision, stop at the smallest safe change and surface the tradeoff clearly.
