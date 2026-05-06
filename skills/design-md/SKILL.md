---
name: design-md
description: "Read, write, lint, diff, and export DESIGN.md files using the Google @google/design.md format. Use when the user mentions DESIGN.md, design tokens, extracting a design system, linting design tokens, exporting tokens to Tailwind, DTCG, or CSS variables, or when authoring a fresh design-system reference for a project. Wraps the pinned 0.1.1 CLI through scripts/run_cli.sh."
skill-type: workflow
metadata:
  upstream:
    format: "https://github.com/google-labs-code/design.md"
    cli: "@google/design.md@0.1.1 (npm)"
    license: "Apache-2.0"
    exemplar-source: "https://styles.refero.design"
---

# design-md

Operates on DESIGN.md files — the Google Labs format that pairs a YAML token block with a Markdown rationale. The skill knows how to lint an existing file, diff two versions, export tokens to Tailwind or DTCG, and author a fresh DESIGN.md grounded in five Refero exemplars.

## When To Use

Trigger this skill when the request involves any of the following:

- The user mentions "DESIGN.md", "design tokens", "design system spec", or "@google/design.md".
- The user asks to extract a design system from existing CSS, Tailwind config, or component code into a single source of truth.
- The user wants to lint, validate, or diff a DESIGN.md file.
- The user wants to export design tokens to Tailwind v3 (`json-tailwind`), Tailwind v4 (`css-tailwind`), or W3C DTCG (`dtcg`).
- The user wants to author a fresh DESIGN.md and asks for examples or a starting point.

## When Not To Use

- Generating UI components or page layouts from scratch — DESIGN.md is a token spec, not a component library.
- Auditing visuals for taste, polish, or AI-generation tells — that is `design-critique`.
- Accessibility audits beyond contrast (axe / WCAG full-coverage). The DESIGN.md linter only checks `contrast-ratio` on declared component pairs.
- Animation, motion, or breakpoint tokens — the format does not cover them.

## Operations

The skill exposes four operations. They share one entry point: `scripts/run_cli.sh`, which pins the CLI version in a single place. Always invoke through the wrapper.

### lint

Validate a DESIGN.md file's structure, references, and contrast.

```bash
bash skills/design-md/scripts/run_cli.sh lint path/to/DESIGN.md
bash skills/design-md/scripts/run_cli.sh lint --format json path/to/DESIGN.md
cat path/to/DESIGN.md | bash skills/design-md/scripts/run_cli.sh lint -
```

Steps:

1. Run `lint` against the file. Read the JSON findings.
2. Group findings by rule. The seven rules and their meanings are in `references/format-primer.md`. Surface errors first, then warnings, then info.
3. For each finding, suggest a concrete fix:
   - `broken-ref` → fix the typo or define the missing token.
   - `contrast-ratio` → propose a darker text color or a lighter background that lands above 4.5:1.
   - `orphaned-tokens` → either reference the token from a component or remove it.
   - `section-order` → reorder the Markdown sections to match canonical order.
4. If exit code is non-zero, the file has at least one error. Do not move on to `export` or `diff` until errors clear.

### diff

Compare two DESIGN.md versions and summarize what changed.

```bash
bash skills/design-md/scripts/run_cli.sh diff path/to/old/DESIGN.md path/to/new/DESIGN.md
```

Steps:

1. Run `diff` and parse the JSON output.
2. Separate **material** changes (token values, new components, removed tokens, contrast regressions) from **cosmetic** changes (renames, prose rewrites, section reordering).
3. Report the material changes first with one-line consequences for downstream code (Tailwind config, component CSS, generated tokens).
4. Exit code `1` means regressions were detected (more errors or warnings in the new version). Call this out explicitly.

### export

Convert tokens to Tailwind or DTCG.

```bash
bash skills/design-md/scripts/run_cli.sh export --format json-tailwind path/to/DESIGN.md > tailwind.theme.json
bash skills/design-md/scripts/run_cli.sh export --format css-tailwind path/to/DESIGN.md > theme.css
bash skills/design-md/scripts/run_cli.sh export --format dtcg path/to/DESIGN.md > tokens.json
```

Format selection:

- Tailwind v3 project → `json-tailwind`. Merge into `tailwind.config.{js,ts}` under `theme.extend`.
- Tailwind v4 project → `css-tailwind`. Drop the output into the project's main stylesheet inside `@theme { ... }`.
- Style-Dictionary, Token Studio, or any DTCG-aware tool → `dtcg`.

Steps:

1. Lint first. Never export an unlinted file — broken refs land in the output as raw `{path.to.token}` strings.
2. Run `export` with the chosen format and write the output where the user's build expects it.
3. After writing, show the user the diff against any prior token file so they can review before committing.

### author

Write a fresh DESIGN.md from scratch when the project does not yet have one.

Inputs the agent should gather first:

- The product's mood and audience (technical-studio, marketing, consumer, internal tool, etc.).
- Color preferences (warm/cool, light/dark, brand hex if known).
- Typography constraints (system fonts only, custom face available, monospace required for code surfaces).
- Existing CSS / Tailwind config the system should align with.

**Before drafting — format gotchas the linter will surface loudly:**

- **`orphaned-tokens` is the dominant warning.** Every color token must be referenced by a component (`{colors.foo}` from a `components.bar.backgroundColor` or similar) or it fires `orphaned-tokens`. Plan your component set up front so muted-text tokens, border tokens, hover-state tokens, and link tokens all have a component slot to land on. Fabricating a `prose-body` component (with `textColor` + `typography` refs) is a legitimate way to anchor global text colors.
- **Components have no `borderColor` key.** Valid keys are `backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`. Border colors will be perma-orphaned no matter what; either accept the warning or document the border color in prose only and skip the token.
- **Source CSS using `rgba()` must be resolved to hex before tokenizing.** The Color type is `#`-prefix sRGB hex only. For dark themes, resolve `rgba(255,255,255,0.6)` to its solid equivalent on the canvas color (≈ `#999999` on `#000`). Document the original alpha value in the Markdown rationale if it matters.
- **Inverted themes (white CTA on black canvas) should still set `colors.primary`.** The `missing-primary` rule fires whenever colors are defined without a `primary` entry, regardless of whether `primary` is a brand color or a CTA-fill role. For dark-first sites, set `primary` to the CTA fill (often `#FFFFFF`) and document the inversion in the Overview prose.

Steps:

1. Read `references/exemplars/README.md` and pick the exemplar that anchors the closest aesthetic pole. The five exemplars cover warm-technical (Cursor), dark-geometric (Linear), clean-blue (Stripe), monochrome-minimal (Vercel), and colorful-playful (Figma).
2. Read the chosen exemplar for **voice, taste, and depth of rationale** — not for structural shape. The exemplars use Refero's Style Reference export format, which has richer prose sections and no YAML frontmatter. Treat them as taste anchors, not as structural templates.
3. Read `references/format-primer.md` for the **canonical structure** the linter expects: frontmatter schema, token types, and section order. The output must conform to the primer, not the exemplar.
4. Draft the frontmatter first. Define `colors`, `typography`, and at least three components — one interactive (a button), one surface (a card or container), and one prose role (e.g. `prose-body` with `textColor` and `typography` refs to anchor global body styles). "Text style" here means a component entry, not a typography token. Use token references rather than raw values wherever possible.
5. Draft the Markdown body in canonical section order. Each section is short — a paragraph of rationale, not an essay.
6. Lint the draft via stdin: `printf '%s' "<draft>" | bash skills/design-md/scripts/run_cli.sh lint -`. Stdin is the canonical path for in-context drafts; reserve a temp file for iterative editing across multiple turns. Resolve any errors before showing it to the user. Surface warnings as discussion points rather than fixing them silently — the orphaned-tokens warnings on global text/border/hover tokens are often the right tradeoff to accept.
7. Save the file as `DESIGN.md` at the project root unless the user specifies a different path.

## Inputs The Skill Accepts

- A path to an existing DESIGN.md file (lint, diff, export).
- Two paths for `diff`.
- A path to a project root and a description of its aesthetic for `author`.
- Pasted DESIGN.md content piped through stdin (use `-` as the file argument).

## Output Shape

For `lint` and `diff`, return a structured summary:

```
## Findings

### Errors
- broken-ref at colors.brand: undefined token referenced by components.button-primary.backgroundColor
  Fix: define `colors.brand` or change the reference to `{colors.primary}`.

### Warnings
- contrast-ratio on button-secondary: 3.1:1 (AA fails for body)
  Fix: darken textColor toward #0F172A or lighten background toward #F8FAFC.

### Info
- token-summary: 12 colors, 6 typography, 3 spacing, 8 components
```

For `export`, write the file and print the path plus a one-line summary of token counts.

For `author`, return the drafted file path plus the lint result.

## References

- `references/format-primer.md` — DESIGN.md schema, token types, linting rules, export formats.
- `references/exemplars/README.md` — index of the five Refero-sourced exemplars.
- `references/exemplars/{cursor,linear,stripe,vercel,figma}.md` — full DESIGN.md exemplars covering distinct aesthetic poles.

## Maintenance

The format is `version: alpha` and the CLI is at 0.1.1. Both may move. Two signals indicate this skill needs a refresh:

1. The user reports lint findings that mention rules not listed in `format-primer.md`.
2. `npx @google/design.md@latest --version` returns a version newer than 0.1.1 and a smoke run produces unfamiliar output.

To refresh:

1. Bump `DESIGN_MD_VERSION` in `scripts/run_cli.sh`.
2. Re-fetch the upstream README from `github.com/google-labs-code/design.md`.
3. Run `bash scripts/run_cli.sh spec --rules-only --format json` and reconcile any rule additions, removals, or severity changes against the table in `format-primer.md`.
4. Run `bash scripts/run_cli.sh lint` against each of the five exemplars to confirm none of them regressed under the new version.

## Sibling skills

The four design skills compose into a pipeline: **spec → build → review**. Hand off when the request crosses an axis.

- `frontend-design` — generative UI builder. If a fresh DESIGN.md is being authored alongside a build, draft tokens here and consume them there.
- `design-critique` — visual taste audit against a closed 37-pattern slop catalog. Orthogonal to token-spec linting; run it on the *built* UI, not on the DESIGN.md.
- `web-design-guidelines` — accessibility / UX rule-compliance review (Vercel WIG, fetched live). Orthogonal to token-spec linting.
