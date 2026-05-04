# Finding Template

A finding is the unit of output for `design-critique`. Two agents reading the same input and the same slop catalog should produce structurally identical findings. This template defines the shape.

## Schema

Every finding has six required fields:

- **`pattern-id`** — the slug from `slop-catalog.md` (e.g. `side-tab-accent-border`, `low-contrast-text`). Always reference an existing pattern; never invent new ones in a finding.
- **`where`** — the location. Prefer specificity:
  - File path with line range: `app/page.tsx:42-58`.
  - DOM/CSS selector: `.feature-grid > .card`.
  - Screenshot region: `screenshot.png — top-right card cluster, ~y=120-280`.
  - Worst case: a clear textual description anchored to a visible element.
- **`evidence`** — the offending snippet, computed style, or coordinate. One to three lines. This is what the user re-reads to confirm the finding is real.
- **`severity`** — `low` | `medium` | `high`. Inherit the severity from the pattern in the catalog. Do not soften or harden it on a hunch.
- **`recommended-fix`** — concrete and actionable. Cite the pattern's `alternative` field and translate it to the target stack (Tailwind class, CSS rule, JSX change). Avoid generic advice like "improve hierarchy" — name the change.
- **`confidence`** — `high` (you can see the offending element directly), `medium` (strong inference from markup or styles, but no rendered view), `low` (inferred from a description; no markup or screenshot). Findings below `medium` confidence should be rare and clearly labelled.

## Concrete Output Shape

```markdown
- **pattern-id:** side-tab-accent-border
  **where:** components/FeatureCard.tsx:18 (rendered on /pricing)
  **evidence:** `border-l-4 border-l-violet-500` on every card; visible in screenshot top row.
  **severity:** high
  **recommended-fix:** Drop the left-border accent. Replace with a small label chip above the card title using the existing `Badge` component, or tint the card background with `bg-violet-50` for category cards only.
  **confidence:** high
```

## Rules

1. **One observation per finding.** If a single element triggers two patterns (e.g. low contrast *and* tight line height), emit two findings.
2. **No speculation.** If the catalog asks for a `tell` you cannot verify in the input you have, do not emit the finding. Note the gap in the closing summary instead.
3. **No catalog drift.** If you find an issue that does not match any pattern in `slop-catalog.md`, mention it under a separate `Notes` section after the findings, but do not invent a `pattern-id`. The catalog is the closed set for this skill.
4. **Severity follows the catalog.** A `medium` pattern stays `medium` even if it appears prominently. Prominence shows up in the top-three summary, not in inflated severity.
5. **Group by category in the final report.** Within a category, sort findings by severity (high → medium → low). Categories that produced zero findings are omitted from the report.

## Top-Three Summary

After the grouped findings, close with a section titled **Top three highest-leverage fixes**. Pick the three findings whose fix would most improve the overall surface, not the three highest-severity findings. Often these are different — a single `high` finding tied to a one-line CSS change beats three `medium` findings tied to a layout rewrite.

End with a single-line **Verdict** characterizing the overall taste level (e.g., "Polished, with two AI-generated tells in the marketing hero." / "Generic templated landing page; identical-card-grids and ai-color-palette are the dominant signals."). Keep it honest and specific.
