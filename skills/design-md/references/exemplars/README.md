# Exemplar DESIGN.md Files

Five opinionated, brand-extracted DESIGN.md files curated from [Refero](https://styles.refero.design). Each spans a different aesthetic pole so the agent has anchors to sample from when authoring or critiquing token systems.

These are stored in Refero's *Style Reference* markdown export format (the same shape Refero exposes from each style detail page). It overlaps heavily with Google's `@google/design.md` v0.1 schema but is not byte-identical — Refero's export is richer (Surfaces / Elevation / Imagery / Layout / Similar Brands sections), and it omits the YAML frontmatter that the Google CLI lints against. When using these to write a new strict-spec DESIGN.md, treat them as tasteful templates and translate to the format-primer's frontmatter shape.

## The Five

| File | Brand | Theme | Aesthetic Pole | When To Reach For It |
|---|---|---|---|---|
| [cursor.md](./cursor.md) | Cursor | light | Warm ivory technical-studio. Custom typography (CursorGothic + Berkeley Mono + Lato). Compact 8px element gaps. Multi-layered shadows. | Developer tools, IDEs, technical-but-warm SaaS, anything where you want a polished engineering-studio feel without going dark. |
| [linear.md](./linear.md) | Linear | dark | Midnight command center. Layered surfaces (#08090a → #0f1011 → #161718). Single neon-lime accent reserved for primary actions. Inter Variable + Berkeley Mono. | Productivity, project management, dashboards. Anywhere the answer to "what color should this CTA be" should be exactly one color. |
| [stripe.md](./stripe.md) | Stripe | light | Architectural blueprint on white marble. Soft sohne-var weight 300 headlines. Deep-violet (#533afd) primary action. Expressive gradients in heroes. Comfortable density. | Financial / API / infrastructure products. When you need authoritative-but-light, with room for one expressive gradient moment per page. |
| [vercel.md](./vercel.md) | Vercel | light | Near-monochrome developer-tooling. Pill-radius buttons (100px). Conic-gradient hero accent. Geist + Geist Mono. Tight 12px element gaps. | Developer platforms, infra / hosting / CI marketing pages. When the typography should carry the weight and color should mostly recede. |
| [figma.md](./figma.md) | Figma | light | Monochrome chassis for chromatic content. Stark #000/#fff baseline. Mixed border-radius dichotomy (50px nav pills vs 0px content grids). Aggressive negative tracking. | Tools whose UI must defer to user-generated content. Galleries, canvases, communities. When the chrome should disappear so the work can shine. |

## Aesthetic Pole Map

```
                  light theme
                       |
        Stripe   Cursor|Vercel
       (lush)  (warm) | (mono)
                      |
                      |
                      | Figma (mono+sharp)
   ─────────────────────────────────────
                      |
                      |
              Linear  |
              (dark)  |
                      |
                  dark theme
```

Cursor and Vercel are both light + roughly mono but differ on warmth (Cursor warm, Vercel cool). Stripe sits between them in temperature with extra color expression. Linear anchors the dark pole. Figma is the most opinionated chrome-recedes-to-content take.

## How To Use

1. **As anchors when authoring a new DESIGN.md** — pick the exemplar closest to the user's brief and customize tokens from there. Don't compose; pick one.
2. **As positive references during critique** — when `design-critique` flags a slop pattern, the exemplar named alternatives are often a more concrete fix than the catalog's prose.
3. **As a forcing function for restraint** — note that none of the five uses more than three font families, and most use one accent color for primary action. If a generated DESIGN.md sprawls, return to the exemplars.

## Format Notes

These files use Refero's export shape, not strict Google `@google/design.md` v0.1 frontmatter. See `../format-primer.md` for the strict format spec the CLI lints against.

Translation is *not* a faithful copy. The Refero exports are richer than the strict spec — they carry Surfaces, Elevation, Imagery, Layout, and Similar Brands sections that have no canonical mapping, and they list dozens of named palette tokens that go unreferenced by any component. A line-by-line lift of an exemplar's palette into the strict frontmatter will produce double-digit `orphaned-tokens` warnings on lint, because every color must be referenced from a `components.*` entry to count as "used."

When translating an exemplar, treat it as a taste anchor — sample mood, voice, and section rationale — and rebuild the palette around the components you actually plan to define. The format-primer's "Before drafting" notes in the parent `SKILL.md` walk through the specific gotchas (orphaned-tokens scope, no `borderColor` key, alpha-color resolution, inverted-theme `primary`).

## Substitutions And Sourcing

This pass pulled all five from the user-provided Refero exports on 2026-05-03. If a brand's style is later updated upstream, re-fetch and replace the file (preserve the header comment, bump the `Fetched:` date).

If a takedown request arrives or upstream removes a style, swap in another exemplar from Refero's catalog that covers the same aesthetic pole — diversity matters more than the specific brand.
