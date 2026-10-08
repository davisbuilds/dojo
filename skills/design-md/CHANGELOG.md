# Changelog

## 2.0.0 - 2026-10-07

- Upgrade the pinned CLI to 0.4.0 with CSS-variable exports, modern color inputs,
  omission declarations, and current diagnostic/exit contracts.
- Document verified export normalization and stdin argument handling rather than
  promising lossless color round trips or treating serialization as validation.
- Remove component quotas, required exemplar selection, mandatory handoffs, and
  blanket export/diff gates; retain consumer validation and source fidelity.
- Add opt-in integration checks using the real pinned package and original fixtures.

## 1.0.2 - 2026-08-14

- Anchor runnable script commands to <skill-dir>, including inline-code commands, so they resolve outside a dojo checkout


## 1.0.1 - 2026-08-01

- Drop the pinned-CLI wrapper implementation note from the description; triggers unchanged.
