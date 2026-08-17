## 2.5.0 - 2026-08-16

- High-risk readiness: add the "prove the handoff" obligations (identity is not capture, "idempotent" is not recovery, enforcement cannot activate before its declaration/recovery/operator topology) and seed the critique to attack each. Make high-risk ID enforcement incrementally adoptable — a legacy id-less plan tracing an id-less spec uses named contract surfaces, while a partial-ID plan (or one inventing IDs against an id-less spec) still fails rather than downgrading.

## 2.4.0 - 2026-08-16

- Advise (non-blocking) when a task invokes a known-external binary (tmux/git/npm/docker/codex/claude/gh) without a Behavior Measured block, and when a Done When bullet is degenerate — an "only X" partition with a single branch, or an "every declared …" assertion over a possibly-empty collection. Add the degeneracy gate ("assert each bullet against a case you believe is false") and the enumeration-is-not-the-invariant / cross-runner-seam guidance. Guard discover_repo_root against a deleted cwd (no longer crashes under Python 3.14).

## 2.3.1 - 2026-08-14

- Anchor runnable script commands to <skill-dir> so they resolve outside a dojo checkout

## 2.3.0 - 2026-08-12

- Add a Behavior Measured block for steps depending on tools the repo does not own — evidence is a command and its output, not a citation — and loosen Assumptions Verified to state the claim and evidence appropriate to it.

## 2.2.0 - 2026-08-10

- Assumptions are dated observations that must be re-verified before the task consuming them; capability gates must prove fidelity to the surface a user touches, not just working mechanism.

## 2.1.0 - 2026-07-27

- Resolve consumer-repository paths correctly and plan pinned acceptance gates
  across the full defect or property class.

## 2.0.0 - 2026-07-22

- Require current-schema plans to identify the producing agent in frontmatter
  while preserving validation compatibility for legacy plans.
- Preserve the detailed optional critique-subagent handoff for routine plans
  while making critique closure mandatory only for high-risk plans.
- Add a conditional high-risk plan-readiness contract with linked-spec
  traceability, authority/evidence maps, consumer closure, failure windows,
  empirical capability gates, and critique closure.
- Extend deterministic validation for high-risk structure while preserving the
  lean routine planning path.

## 1.1.0

- Add target-specific evidence for existing-code tasks, resolve-now planning,
  irreducible-risk triage, and test-discovery proof when tests change.
- Add advisory-only validator nudges for missing grounding and test-discovery
  markers, with pytest regression coverage.
