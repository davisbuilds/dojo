# DESIGN.md Format Primer

Reference for **@google/design.md 0.4.0**, format `version: alpha`. Use the wrapper
in the parent skill for commands. This describes the published package checked
on 2026-10-07, including observed limits where upstream prose differs.

## File shape and scope

YAML frontmatter holds exportable tokens; Markdown `##` sections explain the
system's intent. A small color-only design can intentionally omit other groups:

```markdown
---
version: alpha
name: example
colors:
  primary: "oklch(60% 0.15 250)"
  overlay: "rgba(0, 0, 0, 0.5)"
omitted:
  - typography
  - section: spacing
    reason: "Layout spacing belongs to the consuming application."
  - rounded
  - components
---

## Overview

A color palette shared by existing components.

## Colors

Preserve the source colors; inspect normalization in exported formats.
```

There is no minimum component count. The Refero exemplars are taste references,
not schema templates or validation fixtures.

## Recognized token fields

| Key | Meaning |
| --- | --- |
| `version`, `name`, `description` | Format marker and descriptive metadata. |
| `colors` | Named CSS colors; quote values in YAML. |
| `typography` | Named objects with `fontFamily`, `fontSize`, `fontWeight`, `lineHeight`, `letterSpacing`, `fontFeature`, `fontVariation`. |
| `spacing`, `rounded` | Named scales; dimensions use px, em, or rem; spacing also accepts numbers. |
| `components` | Named property bags using `backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`. |
| `omitted` | Intentionally absent groups: `colors`, `typography`, `spacing`, `rounded`, `components`. Each entry is a group name or `{section, reason}`. |

Token groups are optional. Omissions suppress applicable missing-group
findings; they do not disable validation of tokens that are present. Unknown or
redundant omission declarations have their own diagnostics. Do not use omissions
to hide actual requirements or errors.

Colors accept hex, named colors, rgb/rgba, hsl/hsla, hwb, oklch/oklab, lch/lab,
and color-mix. Parsing support does not imply lossless round trips: despite the
upstream spec's preservation claim, the verified CSS-variable exporter reads
resolved sRGB hex. The fixture's `rgba(0, 0, 0, 0.5)` becomes `#00000080` and
`oklch(60% 0.15 250)` becomes `#2784d5`. Keep the original source values and check
whether normalization or gamut conversion is acceptable to the consumer.

Typography fields are optional; `lineHeight` may be a unitless multiplier or a
dimension. Support in the source model does not guarantee every exporter retains
every property; inspect the output used by the application.

References use `{path.to.token}`. Component typography may reference a composite
token such as `{typography.body}`. Unsupported component properties (for example,
`borderColor`) are not a way to extend the schema; inspect their diagnostics.
Keep unsupported design concerns in prose or their existing implementation.

```yaml
components:
  button:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.body}"
```

This fragment assumes those referenced tokens are defined. Model state variants
as named component entries when useful; there is no nested variants schema.

## Markdown sections

Recognized sections should occur in this relative order; irrelevant sections can
be absent:

1. Overview (alias: Brand & Style)
2. Colors
3. Typography
4. Layout (alias: Layout & Spacing)
5. Elevation & Depth (alias: Elevation)
6. Shapes
7. Components
8. Do's and Don'ts

Keep richer design rationale where it helps, but do not assume arbitrary prose or
unknown token maps are included in exports. Motion, breakpoints, and theme-switching
behavior need their existing implementation or prose reference.

## Diagnostics and exit behavior

`spec --rules-only --format json` lists these registered rules. Individual
findings may use more specific IDs or severities; parser/model errors can also
appear, so this table is not an exhaustive list of possible finding IDs.

| Registered rule | Default severity | Scope |
| --- | --- | --- |
| `broken-ref` | error | Broken/circular references and unknown component sub-tokens. |
| `missing-primary` | warning | Colors without a `primary` entry. |
| `contrast-ratio` | warning | Resolved component background/text pairs below the implemented 4.5:1 threshold. |
| `orphaned-tokens` | warning | Unreferenced tokens under the rule's usage heuristics. |
| `token-summary` | info | Counts of defined tokens. |
| `missing-sections` | info | Absent spacing/rounded groups unless intentionally omitted. |
| `missing-typography` | warning | Colors without typography unless intentionally omitted. |
| `section-order` | warning | Recognized Markdown sections out of order. |
| `unknown-key` | warning | Top-level keys resembling misspelled schema keys. |
| `token-like-ignored` | warning | Token-like maps outside the recognized export schema. |
| `omitted-rules` | info | Emits `declared-omission` (info), `unknown-omission` or `redundant-omission` (warnings). |

The contrast rule does not implement a separate large-text 3:1 threshold or
validate the rendered page's compositing, focus states, or accessibility. An
unreferenced token may still have a real CSS consumer outside this file; investigate
before deleting it or inventing a component solely to silence a warning.

| Operation | Exit interpretation |
| --- | --- |
| `lint` | 0: no errors, possibly warnings; 1: validation errors; 2: input-read failure. Inspect stderr for invocation failures. |
| `diff` | 1: error or warning count increased; 0: counts did not increase, even if token values or individual findings changed; 2: input-read failure. |
| `export` | 0: output produced, even with lint errors; 1: invalid format/emitter failure; 2: input-read failure. |

Diff JSON exposes `tokens.<group>.added`, `.removed`, and `.modified`, plus
before/after diagnostic summaries and count deltas. It is not a visual comparison.
For stdin use `lint --format json -- -`; the bare `-` documented upstream is
rejected by the published argument parser.

## Export formats

| Format | Consumer and output |
| --- | --- |
| `json-tailwind` (alias `tailwind`) | Tailwind v3 theme configuration JSON. |
| `css-tailwind` | Tailwind v4 `@theme` CSS. |
| `dtcg` | DTCG JSON; verify compatibility with the actual consuming tool. |
| `css-vars` | Plain `:root` CSS variables; optional `--prefix app` produces names such as `--app-color-primary`. |

Exports derive from parsed tokens, not Markdown rationale. Check the lint result
separately, and validate exported values and names in the consuming application.
An emitted artifact is not proof of source validity or fidelity.

## Provenance and refresh

- [Upstream specification](https://github.com/google-labs-code/design.md/blob/9bf8eae67128b6cc55ad9bf86665767deb4c11cd/docs/spec.md)
- [Exporter implementation](https://github.com/google-labs-code/design.md/blob/9bf8eae67128b6cc55ad9bf86665767deb4c11cd/packages/cli/src/commands/export.ts)
- Published npm 0.4.0 reports the same `gitHead`; local integration tests verify
  selected behaviors through the wrapper. Google source is Apache-2.0; Refero
  exemplars retain their separate provenance.

When changing the pin, check `spec` and real fixture outputs rather than updating
version strings alone. Reconcile this reference with observed package behavior.
