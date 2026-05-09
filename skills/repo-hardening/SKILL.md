---
name: repo-hardening
description: >-
  Audit and harden a software repo against supply-chain and workflow risks. Use when
  a user asks to audit a repo, harden CI, pin GitHub Actions, freeze installs, reduce
  bot workflow risk, review lockfile/package-manager discipline, or create repo-local
  security investigation artifacts. Supports Node, Python, GitHub Actions, GitLab CI,
  and mixed-stack repos. On-demand via /repo-audit and /repo-harden.
skill-type: workflow
compatibility: "Requires python3. Uses only Python standard library. Writes artifacts into the target repo under .repo-hardening by default."
---

# Repo Hardening

## Overview

Use this skill to run a deterministic repo inventory, write reusable hardening artifacts into the target repo, and then drive a concrete remediation pass with evidence-backed verification.

This skill's default artifact location is `.repo-hardening/`, with an optional override when the repo already has a preferred location.

## When To Use

Use this skill when:
- auditing a repo for supply-chain risk
- hardening GitHub Actions or GitLab CI
- checking lockfile and package-manager discipline
- investigating mutable refs, broad workflow permissions, raw bootstrap/download paths, or bot workflows
- creating a reusable audit packet for a repo that does not already have one
- responding to a new package incident and checking whether a repo is exposed

## Principles

- **Deterministic first**: run the inventory script before making claims.
- **Repo-local artifacts**: write findings into the target repo so future work has a durable trail.
- **Minimum viable hardening**: prefer the smallest safe change set that materially improves posture.
- **Verification before closure**: rerun the repo's native checks before claiming the repo is hardened.
- **Do not assume house style**: default to `.repo-hardening/` unless the repo already has an established security artifact location.

## Artifact Model

Default output directory in the target repo:

```text
.repo-hardening/
```

Default generated files:

- `inventory.json`
- `audit.md`
- `hardening-plan.md`

If the repo already uses a canonical location such as `security/`, you may override the output path explicitly. See `references/artifact-layout.md`.

## Audit Workflow

1. Run the deterministic inventory:

```bash
python3 skills/repo-hardening/scripts/repo_inventory.py <repo-path>
```

Optional incident-package checks:

```bash
python3 skills/repo-hardening/scripts/repo_inventory.py <repo-path> --package axios --package litellm
```

Optional output override:

```bash
python3 skills/repo-hardening/scripts/repo_inventory.py <repo-path> --out-dir security
```

2. Read the generated artifacts in the target repo:
- `inventory.json` for raw evidence
- `audit.md` for findings
- `hardening-plan.md` for prioritized work

3. Load `references/hardening-matrix.md` for stack-specific remediation choices.

4. Explain the findings in this order:
1. current exposure
2. highest-value fixes
3. residual risk

## Hardening Workflow

1. Run the inventory first if current artifacts do not exist or are stale.
2. Apply the minimum safe hardening changes for the repo's stack:
- Node: `pnpm install --frozen-lockfile` or `npm ci`, pinned `packageManager`, pinned GitHub Action SHAs
- Python: `uv sync --frozen` or hash-verified requirements installs
- GitHub Actions: explicit top-level `permissions:`, no mutable `uses:` refs
- GitLab CI: reduce fresh installs, pin reusable includes when practical
- Bot workflows: reduce write scopes and remove install-capable tool grants unless justified
- Remote bootstrap/downloads: replace `latest` and `curl | sh` style flows with pinned or verified retrieval

3. Run the repo's own checks and tests.
4. Refresh the generated artifacts so they reflect post-change state.
5. Report exactly what changed, what was verified, and what remains.

## Output Requirements

When returning results to the user:

- lead with the highest-risk findings or the highest-value fixes
- include concrete file references when discussing changes
- state what verification actually ran
- state what remains local-only, uncommitted, or unpushed

When updating the repo-local artifacts:

- keep findings concise and evidence-backed
- separate current state from planned work
- distinguish completed fixes from residual backlog

## Verification

- Run the target repo's native lint, build, and test commands before calling the hardening pass complete.
- Re-run `python3 skills/repo-hardening/scripts/repo_inventory.py <repo-path>` after changes so the repo-local artifacts reflect the post-change state.
- If workflow files changed, confirm there are no mutable `uses:` refs and no missing top-level `permissions:` blocks.
- If install paths changed, confirm the repo now uses a frozen or hash-verified form in CI.

## Boundaries

- Do not assume every repo should adopt the same package manager or CI shape.
- Do not rewrite repo history or revert unrelated local work.
- Do not claim a repo is hardened without rerunning native verification.
- Do not create or delete repo-local security directories unless the user asked; use `.repo-hardening/` by default.
- Do not silently remove bot workflows; that is a product decision unless the user asked for removal.

## Commands

- `/repo-audit`
- `/repo-harden`

## References

- `references/hardening-matrix.md`
- `references/artifact-layout.md`

## Sibling skills

Two security skills, distinguished by *scope*.

- `secure-code` — semgrep-based static scan of *application code* for vulnerabilities (injection, auth, secrets). This skill is broader (supply-chain, CI/CD, repo posture); pair them on high-stakes audits.
- `audit-skill` — security audit specifically for *agent skills* (prompt injection, exfiltration). Different artifact; use that one before installing third-party skills.
- `code-review-agents` — multi-agent review whose security agent overlaps with `secure-code`; orthogonal to repo-level hardening here.
