# DESIGN.md Format Primer

A self-contained reference for the `@google/design.md` format. Read this before authoring, linting, or diffing a DESIGN.md so the agent knows the schema, the canonical section order, and what the linter actually checks.

Pinned to CLI version **0.1.1** (format `version: alpha`). The format is under active development; if `run_cli.sh` errors with unfamiliar fields or the lint output mentions rules not listed here, regenerate this primer (see Maintenance section in `SKILL.md`).

## File Shape

A DESIGN.md is a two-layer document:

1. **YAML frontmatter** — machine-readable tokens, delimited by `---`. This is what the linter parses and what `export` converts to other formats.
2. **Markdown body** — human-readable rationale in `##` sections. The linter validates section order but not prose content.

Minimal valid file:

```markdown
---
version: alpha
name: example
colors:
  primary: "#1A1C1E"
  on-primary: "#FFFFFF"
typography:
  body:
    fontFamily: "Inter"
    fontSize: 16px
    lineHeight: 1.5
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
---

## Overview

Short prose describing the system's intent.
```

## Frontmatter Schema

| Key | Required | Notes |
|-----|----------|-------|
| `version` | optional | Currently `alpha`. Omit and the CLI assumes alpha. |
| `name` | recommended | System identifier; surfaces in tooling. |
| `description` | optional | One-line summary. |
| `colors` | optional | Map of token name → `Color`. |
| `typography` | optional | Map of token name → `Typography` object. |
| `rounded` | optional | Map of scale level → `Dimension`. |
| `spacing` | optional | Map of scale level → `Dimension` or number. |
| `components` | optional | Map of component name → property bag. |

All token sections are optional individually, but combinations trigger warnings (colors without typography, colors without a `primary`, etc. — see Linting Rules).

## Token Types

| Type | Format | Examples |
|------|--------|----------|
| `Color` | `#` + hex sRGB | `"#1A1C1E"`, `"#FFFFFF"` |
| `Dimension` | number + unit (`px`, `em`, `rem`) | `48px`, `1.5rem`, `-0.02em` |
| `Token Reference` | `{path.to.token}` resolved against the same file | `{colors.primary}`, `{rounded.sm}` |
| `Typography` | object with `fontFamily`, `fontSize`, `fontWeight`, `lineHeight`, `letterSpacing`, `fontFeature`, `fontVariation` | See below |

### Typography Object

```yaml
typography:
  display-lg:
    fontFamily: "Söhne, system-ui, sans-serif"
    fontSize: 48px
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: -0.02em
```

All inner fields are optional but at least `fontFamily` and `fontSize` should be present for the typography token to be useful.

## Component Tokens

Component entries map a component name to a property bag. Variants (hover, active, pressed, disabled) live as separate top-level entries with related names — there is no nested variants block.

```yaml
components:
  button-primary:
    backgroundColor: "{colors.tertiary}"
    textColor: "{colors.on-tertiary}"
    rounded: "{rounded.sm}"
    padding: 12px
  button-primary-hover:
    backgroundColor: "{colors.tertiary-container}"
    textColor: "{colors.on-tertiary-container}"
```

Valid component property keys: `backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`. Anything else is silently ignored.

Component values may be raw scalars (`12px`, `"#000000"`) or token references (`"{colors.primary}"`). Prefer references — they are what makes the file a system rather than a list of values.

## Section Order

The Markdown body uses `##` headings in this canonical order. Sections may be omitted, but their **relative order** must be preserved or the linter emits a `section-order` warning.

1. `Overview` (alias: `Brand & Style`)
2. `Colors`
3. `Typography`
4. `Layout` (alias: `Layout & Spacing`)
5. `Elevation & Depth` (alias: `Elevation`)
6. `Shapes`
7. `Components`
8. `Do's and Don'ts`

The exemplars in `references/exemplars/` follow this order — use them as a template when authoring a new DESIGN.md.

## Linting Rules

The linter runs seven rules. Each emits a finding at a fixed severity:

| Rule | Severity | What it catches |
|------|----------|-----------------|
| `broken-ref` | error | A `{path.to.token}` reference that does not resolve. |
| `missing-primary` | warning | Colors defined but no `primary` color present. |
| `contrast-ratio` | warning | A component pairs `backgroundColor` and `textColor` whose ratio falls below WCAG AA (4.5:1 normal, 3:1 large). |
| `orphaned-tokens` | warning | Color tokens never referenced by any component. |
| `missing-typography` | warning | Colors defined but no typography section. |
| `section-order` | warning | Markdown sections appear out of canonical order. |
| `token-summary` | info | Count of tokens per section. |
| `missing-sections` | info | Optional sections absent despite related tokens being present. |

Only `broken-ref` is an error; the rest are advisory. The CLI exit code is `0` when there are no errors, `1` when at least one error is present.

## Export Formats

`export` accepts three `--format` values:

- `json-tailwind` (alias `tailwind`) — Tailwind v3 `theme.extend` JSON object.
- `css-tailwind` — Tailwind v4 `@theme { ... }` block with CSS custom properties.
- `dtcg` — W3C Design Tokens Community Group `tokens.json`.

All three are deterministic transforms of the frontmatter; the Markdown body is ignored.

## What This Format Does Not Cover

- No animation, motion, or easing tokens.
- No grid or breakpoint tokens.
- No light/dark theme switching — a DESIGN.md is one theme. Author two files for two themes.
- No semantic role tokens beyond what the user names (e.g., `colors.primary`, `colors.on-primary`).

When the user needs any of the above, capture them in the Markdown body as prose rationale rather than trying to fit them into the frontmatter.

## Maintenance Notes

- The format is `version: alpha`. Field names and rule sets may change between minor releases.
- The pinned CLI version is set in `scripts/run_cli.sh` (`DESIGN_MD_VERSION`).
- When bumping that version, re-fetch the upstream README and the `npx @google/design.md spec --rules-only` output and reconcile any drift in this primer.
