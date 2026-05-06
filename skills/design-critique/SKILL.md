---
name: design-critique
description: "Audit implemented UI against a 37-pattern slop catalog and return ranked, scoped findings with named alternatives. Use when the user asks to review their UI, audit a design, check for AI-generated tells, critique the visuals, or asks 'does this look AI-generated'. Accepts pasted markup, file paths to component or CSS files, file paths to local screenshots, or — only when the user explicitly opts in — a URL plus Playwright auto-capture. Excludes accessibility/WCAG audits beyond contrast and creative UI generation; for rule-compliance / a11y / UX audits use web-design-guidelines."
skill-type: workflow
metadata:
  upstream:
    taxonomy: "https://impeccable.style/slop"
    license: "Web-published; descriptions paraphrased with attribution"
---

# design-critique

Walk a target UI category by category against the slop catalog. Record concrete findings only. Group by category, rank by severity, and close with the three highest-leverage fixes plus a one-line taste verdict.

## When To Use

Trigger this skill when the request involves any of the following:

- "Review my UI", "audit this design", "critique the visuals", "rate the polish".
- "Does this look AI-generated?", "find the slop", "where is this generic?".
- "Is this design dated?", "what should I change first?", "give me the taste pass".
- The user pastes markup, points at a component file, or shows a screenshot and asks for opinions on the look.

## When Not To Use

- Accessibility / WCAG audits beyond contrast — use a dedicated a11y tool. The slop catalog covers contrast, line length, line height, body size, and heading skips, but not full WCAG coverage.
- Generating UI components or layouts from scratch — that is a different problem.
- Reasoning about design tokens, exporting tokens, or linting a DESIGN.md — that is `design-md`.
- Performance, bundle size, or build hygiene reviews.

## Inputs

The skill accepts, in order of preference:

1. **Pasted HTML / JSX / TSX markup**, with or without surrounding CSS or Tailwind classes. Highest-fidelity input — the agent can scan for tells directly.
2. **File paths to component or stylesheet files** in the active project. The agent reads them and walks the catalog.
3. **A path to a local screenshot already on disk**. Useful when markup is unavailable; the agent reasons from rendered visuals.
4. **A URL plus explicit opt-in for Playwright capture**. Only when the user says "go ahead and capture it" or equivalent. Use the existing `playwright` skill to render and snapshot before scanning.
5. **A textual description only**. Lowest-fidelity fallback. Findings emitted from this input must carry `confidence: low` per the finding template.

If the user provides only a URL with no opt-in, ask whether to capture before proceeding. Do not silently fetch.

## Audit Playbook

1. **Load the catalog.** Read `references/slop-catalog.md` in full. The catalog is the closed set of patterns — do not introduce new ones.
2. **Load the finding template.** Read `references/finding-template.md`. Every finding must conform to its schema.
3. **Ingest the input.** Read the markup, file, screenshot, or description. If multiple inputs are given, treat the most concrete (markup or screenshot) as primary and use the rest as supporting context.
4. **Walk the catalog category by category.** Categories are: Visual Details, Typography, Color and Contrast, Layout and Space, Motion, Interaction, Responsive, General Quality. Process them in this order.
5. **For each pattern, look for the `tells`.** If you can point at a specific element, selector, file:line, or screenshot region that exhibits the tell, draft a finding using the template. If you cannot, move on. Do not speculate.
6. **Rank within each category.** Sort findings high → medium → low severity.
7. **Pick the top three highest-leverage fixes** across all categories. Leverage = improvement-to-effort ratio, not raw severity. Often a single `high` finding with a one-line fix beats three `medium` findings requiring a rewrite.
8. **Write the verdict.** One honest, specific line characterizing the overall taste level.
9. **Surface coverage status in two distinct buckets.** Patterns split into:
   - `Checked — no finding`: patterns walked with the given input and definitively ruled out (e.g., "no `text-align: justify` declaration found anywhere"). These prove the catalog was walked completely.
   - `Unverifiable`: patterns whose `tells` could not be operationalized against the given input (e.g., "bounce-elastic-easing requires a rendered view; markup-only input cannot confirm"). These tell the user what to revisit if they want fuller coverage.
   Listing one without the other under-serves the user. Do not collapse both into a single "coverage gaps" block.

## Output Shape

```markdown
# Design Critique: <target name or path>

## Findings by Category

### Color and Contrast
- **pattern-id:** ai-color-palette
  **where:** ...
  **evidence:** ...
  **severity:** high
  **recommended-fix:** ...
  **pattern-match-strength:** full
  **confidence:** high

### Layout and Space
- **pattern-id:** identical-card-grids
  ...

## Top three highest-leverage fixes

1. <pattern-id> — <one-line fix>
2. <pattern-id> — <one-line fix>
3. <pattern-id> — <one-line fix>

## Verdict

<one specific line>

## Checked — no finding

- <pattern-id> — <one-line "checked X, found Y, rule does not fire">

## Unverifiable

- <pattern-id> — <why this input form can't reach the tell, what input would unlock it>
```

Categories with zero findings are omitted. If the entire surface produces zero findings, say so explicitly in the verdict.

## Guardrails

- The catalog is closed. New patterns are added by editing `references/slop-catalog.md`, not by inventing them in a finding.
- Severity is inherited from the catalog. Prominence shows up in the top-three summary, not as severity inflation.
- Findings need evidence the user can re-read. "This feels generic" is not a finding. "`grid-cols-3 gap-6` repeating the same icon-heading-paragraph card four times in `app/page.tsx:24-72`" is.
- The skill is read-only. It produces a critique; it does not edit code unless the user explicitly asks for the fixes to be applied as a follow-up step.

## References

- `references/slop-catalog.md` — 37 patterns across 8 categories with the five-field schema (id, name, tells, why-it-fails, alternative, severity).
- `references/finding-template.md` — the structured shape every finding must conform to.

## Sibling skills

The four design skills compose into a pipeline: **spec → build → review**. Hand off when the request crosses an axis.

- `frontend-design` — generative UI builder. Run this skill against `frontend-design` output to catch slop tells before handoff.
- `design-md` — DESIGN.md token spec; the source of truth for tokens lives there, not here. A taste critique does not edit token files.
- `web-design-guidelines` — accessibility / UX rule-compliance review against Vercel WIG. Runs *in parallel* to a taste audit, not in place of it; the two cover non-overlapping rule sets.
