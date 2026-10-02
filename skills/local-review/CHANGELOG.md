## 2.0.0 - 2026-10-02

- Rebuild review guidance around actionable introduced defects, concrete affected paths, counterevidence, and concise priority-tagged comments.
- Consolidate `error-handling-review` and `type-design-review` into optional references; remove syntax-based severity and type scorecards. Existing installs migrate through Skill Standardizer.
- Allow tracing unchanged consumers while keeping findings scoped to the requested revision; remove file-count escalation and fixed report sections.
- Fix working-mode collection to include staged changes and deletion-only targets; remove marker scans against unrelated working-tree bytes.
- Document the inspected public Codex native-review implementation and the limits of prompt parity. Add authored replay cases, without claiming behavioral evaluation results.

## 1.1.5 - 2026-09-23

- Align the completion-evidence sibling pointer with its conditional scope; no automatic extra gate after a local review.

## 1.1.4 - 2026-08-17

- Cross-reference the error-handling-review and type-design-review specialist lenses in Sibling skills.

## 1.1.3 - 2026-08-14

- Anchor runnable script commands to <skill-dir> so they resolve outside a dojo checkout

## 1.1.2 - 2026-08-01

- Drop the git-context-collection mechanic from the description; output contract and triggers unchanged.

# Changelog

## 1.1.1 - 2026-07-31

- Drop the `gh-review-pr` and `code-review-agents` siblings, retired 2026-07-31.
  The "post PR reviews to GitHub" boundary now points at the `gh` CLI or the
  harness's own review command rather than a skill that no longer exists.

## 1.1.0

- Added deep review context collection, branch-base fallback, stricter flag validation, and clearer helper path guidance.
