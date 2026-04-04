---
name: repo-audit
description: Run the deterministic repo-hardening inventory and write repo-local audit artifacts.
argument-hint: "[repo-path] [--out-dir <dir>] [--package <name> ...]"
allowed-tools: [Read, Bash(git:*), Bash(rg:*), Bash(python3 skills/repo-hardening/scripts/repo_inventory.py:*)]
---

# Repo Audit Command

Run the deterministic `repo-hardening` inventory and write audit artifacts into the target repo.

## Behavior

1. Resolve the target repo path:
- if `$ARGUMENTS` is empty, use the current working directory
- otherwise use the provided repo path and pass through any `--out-dir` or `--package` flags

2. Run the inventory:

```bash
python3 skills/repo-hardening/scripts/repo_inventory.py $ARGUMENTS
```

If no arguments are provided:

```bash
python3 skills/repo-hardening/scripts/repo_inventory.py .
```

3. Read the generated:
- `.repo-hardening/inventory.json`
- `.repo-hardening/audit.md`
- `.repo-hardening/hardening-plan.md`

4. Return results in this order:
1. Findings
2. Highest-value next fixes
3. Residual risks
4. Artifact paths

## Rules

- Lead with the highest-risk findings.
- Do not invent evidence not present in the generated artifacts or source files.
- If the user names specific packages of concern, pass them with `--package`.
- If the repo already has a canonical security artifact location, allow `--out-dir` to override the default.
