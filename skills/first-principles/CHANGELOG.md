# Changelog

## 2.0.0 - 2026-07-31

- **Cede debugging to `diagnose`.** The description triggered on "why is this
  failing" and "root cause" while `diagnose` already claims "this is
  broken/throwing/failing" and has an actual procedural loop behind it. The
  Decision Matrix now routes "complex failure, cause unclear" to `diagnose`
  rather than claiming it. This is the narrowed trigger semantics that makes
  the release MAJOR.
- Description 587 -> 341 chars; drops the four broadest triggers ("why is this
  failing", "root cause", "help me decide", "think through this") and adds the
  `diagnose` and `brainstorming` redirects.
- Remove the Engineering Principles section (YAGNI, KISS, Separation of
  Concerns, DRY, SOLID, composition-over-inheritance). A current frontier model
  applies these without being told, and the Resolving Principle Tensions table
  survives without them since the terms need no gloss.
- Remove "Trade-Off Awareness for Code", which restated Analytical Method's
  "surface alternatives" almost verbatim, and two commonplace bullets from
  Analytical Method itself.
- Compress "When To Use" and "Boundaries" and drop "Output". The file
  previously stated its full-vs-lightweight rule four separate times across
  those sections, the Self-Check Gate, and the Decision Matrix. The contract
  requires scope and boundaries anchors on `reference` skills, so these stay --
  but Boundaries now carries the sibling routing rather than restating the
  matrix.
- **Kept deliberately: the Epistemic Framework.** Calibrating confidence,
  marking knowledge boundaries, and flagging reasoning that runs past training
  data are not things frontier models do reliably unprompted, and that section
  is the skill's strongest claim to earning a listing slot.

158 -> 126 lines.
