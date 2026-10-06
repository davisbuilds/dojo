# Dojo evidence CLI pilot

Status: implemented for review, 2026-10-06.

## Purpose

Give people and agents a discoverable, read-only interface to Dojo's existing
checks and harness evidence. Reduce repeated setup and unsupported completion
claims. This is a Dojo development capability; a standalone product and a shared
cross-repository runner remain unselected.

## Two workflows

- Check a named canonical skill or its directory: packaging metadata, conservative
  Markdown resource links, and optional release changes against a Git base.
  Explicit repository checks can add generated-file consistency. Reuse the
  validators used by existing scripts and CI; do not duplicate their rules.
- Inspect a named skill: canonical and installed copies, relevant declared
  configuration and profile policy, and a fresh Codex prompt-input listing. Keep
  filesystem inventory distinct from catalog exposure and actual body loading.
  The creator rollout is the first concrete investigation.

The first harness is Codex because its existing prompt-input probe needs no model
turn. Claude's live request capture has different effects and is deferred. No
paid runs, sync, repair, configuration changes, or skill-owned script execution
occur implicitly. Running installed harness diagnostics may write their own
normal caches; this is not a sandbox or a whole-filesystem no-write guarantee.

## Interface and evidence

`bin/dojo check <skill> [--base <ref>] [--repo-checks] [--json]`

`bin/dojo inspect <skill> --harness codex [--cwd <directory>] [--json]`

The checkout containing the CLI is the default canonical repository. An explicit
`--repo` selects another trusted Dojo checkout; `--cwd` selects the harness probe
context independently. JSON has a schema version, target, revision and content
identity, per-check scope and status, evidence sources, and limitations. Exit 0
means requested checks completed without findings, 1 means findings, and 2 means
invalid input or unavailable/incomplete evidence. Skipped optional checks remain
visible. A packaging pass makes no claim about security, invocation, or quality.

Use Python and existing dependencies. Keep existing script interfaces working.
Avoid a new installation service, all-purpose command tree, aggregate trust score,
or outcome-comparison runner. Any later comparison command should reuse the
bounded ops/OpenBench pilot once its execution path is established.

## Acceptance and evaluation

Prove malformed metadata, broken local links, unchanged release versions,
unavailable probes, and duplicate/missing catalog exposure produce the promised
results. Prove valid controls succeed. Exercise the real CLI, JSON and exit codes,
and preserve target/config contents during checks. Inspect an actual creator
catalog on both hosts without implying that a new probe describes an already
running desktop session.

A natural review point is both workflows working with meaningful failure coverage,
operator documentation, and one real investigation. One cloud review pass precedes
merge/sync. Deterministic tests and author-driven use establish functionality;
usefulness to a fresh agent remains a follow-up observation, not a measured gain.

## First investigation

The initial live creator inspection found a single Dojo-managed creator exposed
by Codex after its bundled counterpart was disabled, while the profile equivalence
still declared Dojo suppressible. This is a useful diagnostic finding. Profile
reconciliation remains a separately tracked follow-up; the CLI did not repair it.
