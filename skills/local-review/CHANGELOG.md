# Changelog

## 1.1.1 - 2026-07-31

- Drop the `gh-review-pr` and `code-review-agents` siblings, retired 2026-07-31.
  The "post PR reviews to GitHub" boundary now points at the `gh` CLI or the
  harness's own review command rather than a skill that no longer exists.

## 1.1.0

- Added deep review context collection, branch-base fallback, stricter flag validation, and clearer helper path guidance.
