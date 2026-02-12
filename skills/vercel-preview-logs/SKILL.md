---
name: vercel-preview-logs
description: Inspect Vercel preview deployments and retrieve build/runtime logs for failed or unhealthy previews. Use when the user asks to check Vercel preview errors, inspect deployment logs, debug failed builds, or correlate PR/commit deployments with log output.
---

# Vercel Preview Logs

Use this skill to close the deploy-debug loop by fetching real Vercel preview logs from CLI and summarizing actionable failures.

## When to Use

Trigger this skill for requests like:
- "check Vercel preview logs"
- "why did this preview deployment fail?"
- "inspect deployment <url/id>"
- "find logs for this PR/commit/branch deployment"

## Prerequisites

- `vc` (Vercel CLI) is installed.
- Auth is available via `VERCEL_TOKEN` (preferred) or existing CLI login.
- If sandbox blocks network or home-directory writes, rerun with `sandbox_permissions=require_escalated`.

## Wrapper Script

Use the bundled wrapper for all commands:

```bash
bash skills/vercel-preview-logs/scripts/vc_safe.sh <vc-subcommand> [args...]
```

What it does:
- sets `VERCEL_DISABLE_AUTO_UPDATE=1`
- sets `NO_UPDATE_NOTIFIER=1`
- sets `XDG_CACHE_HOME` to `/tmp` by default
- uses `-Q /tmp/.vercel-global` so CLI does not need to write in `~/Library/...`

## Core Workflow

1. Identify the deployment

If URL/ID is provided:
```bash
bash skills/vercel-preview-logs/scripts/vc_safe.sh inspect <url-or-id> --format=json -t "$VERCEL_TOKEN"
```

If not provided, list recent deployments for the linked project:
```bash
bash skills/vercel-preview-logs/scripts/vc_safe.sh list --format=json --status ERROR,BUILDING,READY -t "$VERCEL_TOKEN"
```

Optional filters:
```bash
bash skills/vercel-preview-logs/scripts/vc_safe.sh list --format=json -m githubCommitRef=<branch> -t "$VERCEL_TOKEN"
bash skills/vercel-preview-logs/scripts/vc_safe.sh list --format=json -m githubCommitSha=<sha> -t "$VERCEL_TOKEN"
```

2. Fetch build logs

```bash
bash skills/vercel-preview-logs/scripts/vc_safe.sh inspect <url-or-id> --logs -t "$VERCEL_TOKEN"
```

3. Fetch runtime logs (for READY deployments)

```bash
bash skills/vercel-preview-logs/scripts/vc_safe.sh logs <url-or-id> --format=json -t "$VERCEL_TOKEN"
```

## Output Requirements

Report:
- deployment URL/ID and state (`READY`, `ERROR`, etc.)
- the first concrete failure signal (file path, line, stack frame, or command)
- likely root cause in one sentence
- minimal fix recommendation with exact file(s)

If multiple failures exist, prioritize:
1. compile/type errors
2. missing env/config
3. runtime exceptions

## Notes

- This skill focuses on inspection and diagnosis, not deploying.
- If user asks to create/redeploy previews, use `vercel-deploy`.
