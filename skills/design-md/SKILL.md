---
name: design-md
description: "Read, write, lint, diff, and export DESIGN.md files using the Google @google/design.md format. Use when the user mentions DESIGN.md, design tokens, extracting a design system, linting design tokens, exporting tokens to Tailwind, DTCG, or CSS variables, or when authoring a fresh design-system reference for a project."
skill-type: workflow
metadata:
  upstream:
    format: "https://github.com/google-labs-code/design.md"
    cli: "@google/design.md@0.4.0 (npm)"
    license: "Apache-2.0"
    exemplar-source: "https://styles.refero.design"
version: 2.0.0
---

# DESIGN.md

Work with Google's YAML design tokens and Markdown rationale using the pinned
CLI. Preserve the existing product's design intent and the consuming code's
contracts. A token reference is useful when it serves that work; it is not a
prerequisite for building every UI.

## Use the pinned interface

Substitute the directory this skill was loaded from for `<skill-dir>`. The wrapper
requires Node.js 18+ and npm's `npx`; first use may download the pinned package.
It forwards arguments and exit status without changing the caller's directory.

```bash
bash <skill-dir>/scripts/run_cli.sh lint --format json path/to/DESIGN.md
bash <skill-dir>/scripts/run_cli.sh diff path/to/old/DESIGN.md path/to/new/DESIGN.md
bash <skill-dir>/scripts/run_cli.sh spec --rules-only --format json
```

For stdin, put the `-` after the option terminator. The published 0.4.0 parser
rejects a bare positional `-` without it:

```bash
bash <skill-dir>/scripts/run_cli.sh lint --format json -- - < path/to/DESIGN.md
```

Read `references/format-primer.md` when authoring tokens or interpreting unfamiliar
schema, diagnostics, or export behavior. Use actual diagnostics from the pinned
release; a new field or unfamiliar error is reason to inspect the tool, not to
invent syntax.

## Author or revise faithfully

Reuse the product brief, existing CSS/components, and settled design choices.
Ask only about missing choices that materially change the result. Capture the
actual tokens and useful rationale; there is no minimum component count or
required exemplar selection. Use `omitted` for intentionally absent token groups
where appropriate. Don't invent components or delete valid tokens solely to
silence an advisory warning.

Keep supported CSS colors such as `rgba()` and `oklch()` in the source rather than
flattening them onto an assumed background. **Export is not lossless:** verified
0.4.0 CSS-variable output normalizes colors to sRGB hex, including alpha. Inspect
the chosen format's output before replacing existing styles, especially for
wide-gamut palettes and transparency.

`references/exemplars/README.md` indexes optional Refero taste references. They
have separate provenance and are not Google-format fixtures: use their visual
rationale where helpful, translate only what the product needs, and lint the
resulting DESIGN.md. Do not lint the exemplars as a release gate or rewrite them
as a side effect of ordinary use.

## Interpret lint and diff

- `lint` exits 0 with no errors, 1 with validation errors, and 2 for input-read
  failures. Warnings can remain at exit 0. A failed invocation or unreadable input
  is not a design finding; inspect stderr and parsed output.
- `diff` reports added/removed/modified tokens and changes in diagnostic counts.
  Exit 1 means the error or warning count increased; 0 does not mean identical
  designs or no visual regression. Equal counts can hide different findings.
  Read the changed tokens and relevant lint findings, and account for consumers.
- Contrast lint checks declared component color pairs. It does not establish
  accessibility or visual correctness in the rendered application.

Resolve errors relevant to the requested validity claim. Explain consequential
warnings and limitations without requiring a report template, blanket warning
cleanup, or approval for each ordinary correction. Investigation can finish with
findings; it does not require rewriting the design first.

## Export for the consumer

```bash
bash <skill-dir>/scripts/run_cli.sh export --format json-tailwind path/to/DESIGN.md
bash <skill-dir>/scripts/run_cli.sh export --format css-tailwind path/to/DESIGN.md
bash <skill-dir>/scripts/run_cli.sh export --format dtcg path/to/DESIGN.md
bash <skill-dir>/scripts/run_cli.sh export --format css-vars --prefix app path/to/DESIGN.md
```

Use `json-tailwind` (alias `tailwind`) for Tailwind v3, `css-tailwind` for v4,
`dtcg` for a compatible token consumer, or `css-vars` for a plain `:root` stylesheet.
The optional `--prefix` applies to `css-vars` names.

**Export success only means serialization succeeded.** Version 0.4.0 can emit
output and exit 0 despite source lint errors. Keep lint evidence separate when
claiming valid tokens. A requested diagnostic export may still be useful; label
its unresolved input problems rather than refusing to investigate.

Before integrating output, check relevant lint findings, exported names/values,
and the consuming build or styles. Write to a temporary destination first when
an existing artifact would otherwise be truncated by a failing command. Preserve
unrelated configuration when merging tokens. Do not silently introduce Tailwind
or another dependency merely to consume the export.

## Deliver and maintain

Return the requested file, export, or findings with relevant verification and
material limitations. Consult `frontend-design`, `design-critique`, or
`web-design-guidelines` for the specific build, taste, or accessibility question;
this does not require a spec/build/review pipeline or additional artifacts.

When updating the pin, reconcile the wrapper, metadata, primer, and actual package
behavior together. Dojo's opt-in integration tests use the published CLI against
small original fixtures, not the Refero exemplars. From a Dojo checkout:

```bash
DOJO_TEST_DESIGN_MD_CLI=1 uv run --locked pytest tests/test_design_md_cli.py -q
```

This needs Node/npm and may populate the npm cache; the default Python suite skips
these network-dependent checks. Reuse fresh results for the same pin. Passing
fixtures establish those contracts, not general design quality or agent efficacy.
