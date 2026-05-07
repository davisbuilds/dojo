# Slop Catalog

A flat reference of 37 design anti-patterns that mark interfaces as careless, dated, or AI-generated. Used by `design-critique` to scan a target UI category by category and produce ranked findings.

## Attribution

The taxonomy and pattern set are paraphrased from impeccable.style/slop. Names are preserved; descriptions, alternatives, and severity ratings are written in our own words. We do not vendor the impeccable CLI or its six-category Create / Evaluate / Refine / Simplify / Harden / System workflow framing — only the slop anti-pattern catalog.

## How To Use

Read the catalog top to bottom once before scanning. For each pattern, look at the target UI for the `tells`. Record a finding **only when there is a concrete observation** tied to a specific element, selector, file path, or screenshot region — never speculate. Group findings under their category heading. Within each category, rank by `severity` (high → medium → low). Close with a short summary of the top three highest-leverage fixes. Each finding's `alternative` field is the recommended replacement to point the user toward.

Severity rubric:

- **high** — dates the work badly, harms usability or accessibility, or is a strong AI-generated tell.
- **medium** — meaningfully reduces polish or signals carelessness without breaking the experience.
- **low** — minor refinement; worth noting but rarely the highest-leverage fix.

## Field Schema

Every entry has five fields:

- `id` — short slug used to reference the pattern from a finding.
- `name` — the pattern's canonical name.
- `tells` — what to look for in the target UI.
- `why-it-fails` — the underlying mistake the pattern reveals.
- `alternative` — the recommended replacement.
- `severity` — `low` | `medium` | `high`.

---

## Visual Details

### border-accent-rounded

- **name:** Border accent on rounded element
- **tells:** A thick colored border wrapping a card that also has a noticeable border-radius.
- **why-it-fails:** The hard border fights the soft radius; the two treatments cancel each other out and the card reads as indecisive.
- **alternative:** Commit to one — drop the border and lean on the radius plus a fill, or drop the radius and let the border do the framing.
- **severity:** medium

### glassmorphism-everywhere

- **name:** Glassmorphism everywhere
- **tells:** Frosted-glass blur, translucent fills, and glow-borders applied to surfaces that have nothing stacked behind them.
- **why-it-fails:** The effect implies layering that does not exist; it is decoration cosplaying as depth.
- **alternative:** Reserve glass and blur for surfaces that genuinely sit over rich content (sticky toolbars over scrolling feeds, modal scrims over busy dashboards). Everywhere else, use opaque fills.
- **severity:** high

### modal-reflex

- **name:** Reaching for modals by reflex
- **tells:** Routine actions — confirms, edits, filters, settings — open in a centered modal dialog by default.
- **why-it-fails:** Modals interrupt flow, hide context, and trap focus. Defaulting to them is the lazy answer to "where should this UI live?".
- **alternative:** Inline edits, side panels, popovers anchored to the trigger, or a dedicated route. Save modals for truly blocking decisions.
- **severity:** medium

### generic-rounded-shadow

- **name:** Rounded rectangles with generic drop shadows
- **tells:** Every surface is the same softly rounded rectangle with the same diffuse shadow underneath.
- **why-it-fails:** Reads as the default output of an AI generator. Nothing earns visual weight because every container has the same treatment.
- **alternative:** Pick a stronger, more specific shape language — sharper corners, asymmetric radii, hairline borders, or layered fills. Reserve shadow for elements that are actually elevated.
- **severity:** medium

### side-tab-accent-border

- **name:** Side-tab accent border
- **tells:** A thick colored stripe along one edge (usually the left) of a card or callout.
- **why-it-fails:** This is one of the strongest tells of an AI-generated UI; the pattern shows up across every default theme.
- **alternative:** Use a subtle background tint, an inline icon, or a small label chip to convey category. Drop the stripe.
- **severity:** high

### sparklines-as-decoration

- **name:** Sparklines as decoration
- **tells:** Tiny line charts dropped into stat tiles or card corners with no scale, axis, or interaction.
- **why-it-fails:** The data is too small to read but takes up real estate, signalling "we have analytics" without delivering any.
- **alternative:** Either give the data a real chart with scale and tooltips, or remove the visualization and lean on the number.
- **severity:** medium

## Typography

### flat-type-hierarchy

- **name:** Flat type hierarchy
- **tells:** Heading and body sizes within a few pixels of each other (px-based CSS), or with a size *ratio* below 1.25× between adjacent levels (rem / `clamp()` CSS). The page reads as one undifferentiated wall of text.
- **why-it-fails:** Without a clear size step, the eye cannot scan or anchor; everything competes for the same level of attention.
- **alternative:** Use fewer sizes with a stronger ratio (1.25× minimum, 1.333× or 1.5× for display-driven layouts). Pair size with weight and color shifts.
- **severity:** high

### icon-tile-stacked

- **name:** Icon tile stacked above heading
- **tells:** A small rounded-square tile containing a stroke icon, sitting directly above a feature heading and short paragraph, repeated three or four times across.
- **why-it-fails:** This is the single most generated marketing-page pattern; every starter template emits the same shape.
- **alternative:** Place the icon inline with the heading, integrate it into the layout grid, or replace it with a representative image, screenshot, or numeral.
- **severity:** medium

### monospace-as-technical

- **name:** Monospace as "technical" shorthand
- **tells:** Body copy, navigation, or marketing headlines rendered in a monospace face purely to signal "this is for developers".
- **why-it-fails:** It is a stereotype substituting for a real type decision; the typography is doing performative work, not communicative work.
- **alternative:** Choose a body face for its actual reading qualities and reserve monospace for code, data, and identifiers — places where character alignment matters.
- **severity:** medium

### overused-font

- **name:** Overused font
- **tells:** Inter, Roboto, Geist, Fraunces, or other faces that have saturated the design template ecosystem.
- **why-it-fails:** The face no longer carries any voice; it reads as "default" rather than as an intentional choice.
- **alternative:** Pick a less-saturated alternative with comparable quality — Söhne, Switzer, Mona Sans, GT America, Aeonik, or a self-hosted custom face.
- **severity:** low

### single-font-everywhere

- **name:** Single font for everything
- **tells:** One family at one weight covering headings, body, captions, numerals, and labels.
- **why-it-fails:** Type contributes nothing to hierarchy; everything sits on the same visual register.
- **alternative:** Pair a display face with a refined body face, or use the same family across multiple weights and styles to create voice contrast.
- **severity:** medium

### all-caps-body

- **name:** All-caps body text
- **tells:** Sentences or paragraphs rendered entirely in uppercase letters.
- **why-it-fails:** Readers parse words by their shape silhouette; uppercase erases that silhouette and forces letter-by-letter reading.
- **alternative:** Reserve uppercase for short labels, eyebrow tags, and section markers. Use sentence case for anything longer than three words.
- **severity:** high

## Color And Contrast

### ai-color-palette

- **name:** AI color palette
- **tells:** Purple-to-violet gradients, cyan accents on dark navy, the same teal-to-magenta sweep that ships with every default template.
- **why-it-fails:** This palette family is the single most recognizable AI-generated UI tell; it instantly dates the work to "machine output, 2024–2026".
- **alternative:** Develop a palette from a real source — brand artifact, photograph, paint chip, archival reference — and constrain to two or three hues with intentional neutrals.
- **severity:** high

### dark-mode-glow-accents

- **name:** Dark mode with glowing accents
- **tells:** Dark backgrounds plus colored box-shadow halos on buttons, cards, and headlines.
- **why-it-fails:** The glow is decorative, not functional; it implies emission without any underlying lighting model and reads as "cool mode" rather than considered design.
- **alternative:** Use subtle highlights, hairline borders, or true ambient lighting cues (gradients that imply a light source). Drop the unmotivated halo.
- **severity:** medium

### dark-mode-for-safety

- **name:** Defaulting to dark mode for "safety"
- **tells:** A dark theme chosen as the default because "it always looks polished" rather than because the content benefits.
- **why-it-fails:** Dark mode is a deliberate choice with real tradeoffs (long-form reading, photographic content, brightness in daylight). Defaulting to it is a retreat from making that choice.
- **alternative:** Pick light or dark based on the actual use context. If unsure, default to light and offer dark as an opt-in.
- **severity:** medium

### gradient-text

- **name:** Gradient text
- **tells:** Headlines or callouts with a multi-stop gradient applied to the glyphs.
- **why-it-fails:** The gradient is decorative, fights legibility, and is one of the most-shipped templated effects.
- **alternative:** Use a single solid color. If you need emphasis, use weight, scale, or a contrasting accent on a single word.
- **severity:** medium

### gray-on-colored

- **name:** Gray text on colored background
- **tells:** Mid-gray copy placed over a saturated or pastel surface.
- **why-it-fails:** The contrast collapses below readability thresholds; the text becomes ambient noise.
- **alternative:** Use a darker tint of the background hue, near-black, or near-white. Verify with a contrast checker against the actual surface color.
- **severity:** medium

### pure-black-background

- **name:** Pure black background
- **tells:** `#000000` as the page or surface background.
- **why-it-fails:** Pure black does not exist in nature; on screens it reads as harsh, flat, and slightly cheap. It also makes every other color land more aggressively than intended.
- **alternative:** Tint the black toward the brand hue or toward a warm or cool neutral (`#0a0a0c`, `#0c0a0e`, `#0a0c0e`). The shift is small but the surface immediately reads as considered.
- **severity:** low

## Layout And Space

### everything-centered

- **name:** Everything centered
- **tells:** Every section centers its text and content; the page is a vertical column of centered blocks.
- **why-it-fails:** Center alignment removes the strong left edge readers anchor to; the page loses rhythm and reads as a slide deck.
- **alternative:** Default to left alignment. Use center for the hero or a single deliberate moment, and prefer asymmetric layouts for everything below the fold.
- **severity:** medium

### hero-metric-layout

- **name:** Hero metric layout
- **tells:** A giant number with a small label, three supporting stats below, plus a gradient backdrop.
- **why-it-fails:** This composition is everywhere on AI-generated landing pages; it has become the visual equivalent of "lorem ipsum stats".
- **alternative:** Build the hero around a real artifact — a screenshot, a quote, a product moment, an actual chart with context — instead of decorative numerals.
- **severity:** medium

### identical-card-grids

- **name:** Identical card grids
- **tells:** A 2×2 or 3×3 grid of equally sized cards, each with the same icon-heading-paragraph composition.
- **why-it-fails:** This is the single most templated layout on the web right now; it telegraphs "no editorial decisions were made about which item matters most".
- **alternative:** Vary card sizes (bento layouts), mix card content types (text-only, image-only, quote, stat), or replace the grid with a denser editorial treatment.
- **severity:** high

### monotonous-spacing

- **name:** Monotonous spacing
- **tells:** The same gap value (often 16px or 24px) between every element in the layout — within groups, between groups, between sections.
- **why-it-fails:** Spacing carries grouping information. When every gap is identical, nothing reads as related or separated.
- **alternative:** Tighten spacing within groups, expand it between groups, and use a much larger value between sections. Aim for at least three distinct spacing scales in any layout.
- **severity:** medium

### nested-cards

- **name:** Nested cards
- **tells:** A card inside a card, sometimes inside a third card. Borders, radii, and shadows compounding.
- **why-it-fails:** Each container adds visual weight without adding semantic depth; the user sees rectangles, not relationships.
- **alternative:** Flatten. Use spacing, dividers, type weight, or background tint to convey grouping. Reserve actual cards for the outermost level only.
- **severity:** medium

### everything-in-cards

- **name:** Wrapping everything in cards
- **tells:** Every paragraph, list, image, and form field sits inside its own bordered container.
- **why-it-fails:** The chrome overwhelms the content; visual noise rises and the actual information has to fight to be read.
- **alternative:** Default to no container. Add a card only when the content genuinely needs to be set apart from its surroundings (an interactive widget, an aside, a promoted item).
- **severity:** high

### line-length-too-long

- **name:** Line length too long
- **tells:** Body paragraphs running past ~80 characters per line, often the full width of a wide content column.
- **why-it-fails:** When the line is too long, the eye loses its place tracking back to the start of the next line. Reading speed drops and abandonment rises.
- **alternative:** Constrain text containers to 65–75 characters using `max-width: 65ch` or similar. For multi-column layouts, narrow each column rather than letting one column run wide.
- **severity:** high

## Motion

### bounce-elastic-easing

- **name:** Bounce or elastic easing
- **tells:** Buttons, modals, or list items animating in with overshoot-and-settle bouncy curves.
- **why-it-fails:** The aesthetic peaked years ago and now reads as dated and toy-like. Functional UI rarely benefits from physical bounce.
- **alternative:** Use `ease-out-quart`, `ease-out-expo`, or a cubic-bezier with quick-start, slow-finish behavior. Bias short and decelerating.
- **severity:** medium

### layout-property-animation

- **name:** Layout property animation
- **tells:** Transitions on `width`, `height`, `padding`, `margin`, or `top` / `left` properties.
- **why-it-fails:** These properties trigger layout on every frame, causing jank, dropped frames, and visible stutter — especially on lower-end devices.
- **alternative:** Animate `transform` and `opacity` only. For height-collapse animations, use `grid-template-rows: 0fr → 1fr` or `interpolate-size: allow-keywords`.
- **severity:** high

## Interaction

### every-button-primary

- **name:** Every button is a primary button
- **tells:** Multiple filled, high-contrast buttons within the same scope competing for the click. **Scope** = same section (full match), or same viewport / same major page region (partial match — emit with `pattern-match-strength: partial`). Two primary CTAs with the entire page between them is partial; two primary CTAs in the same hero is full.
- **why-it-fails:** When everything is emphasized, nothing is. The user has to read every button to find the actual primary action.
- **alternative:** One primary per surface. Demote the rest to secondary (outline or filled-neutral), tertiary (ghost), or text links. The visual hierarchy should mirror the action hierarchy.
- **severity:** high

### redundant-information

- **name:** Redundant information
- **tells:** Section intros that restate the heading, labels that repeat the page title, button text that duplicates the label above it.
- **why-it-fails:** Each redundant element costs scan time without adding meaning. It is the prose equivalent of unused chrome.
- **alternative:** Cut. Make every word, label, and heading carry weight that is not already carried by another element on the same screen.
- **severity:** medium

## Responsive

### amputated-mobile

- **name:** Amputating features on mobile
- **tells:** Filters, settings, secondary actions, or whole sections hidden or disabled below a certain breakpoint.
- **why-it-fails:** Mobile is not a degraded desktop; for many users it is the only entry point. Removing functionality treats them as second-class.
- **alternative:** Adapt the layout (stack, accordion, drawer, bottom sheet) so all features remain reachable. Reserve removal for genuinely device-impossible interactions.
- **severity:** high

## General Quality

### cramped-padding

- **name:** Cramped padding
- **tells:** Text or controls pressing against the inner edge of their container with little or no breathing room.
- **why-it-fails:** Reads as unresolved or rushed; every container looks like a draft.
- **alternative:** Minimum 8px inner padding, 12–16px ideal, more for content-heavy surfaces. Increase padding with container size.
- **severity:** medium

### justified-text

- **name:** Justified text
- **tells:** Body paragraphs aligned flush to both left and right margins, often with visible "rivers" of whitespace running through them.
- **why-it-fails:** Browsers cannot hyphenate well, so the text engine stretches inter-word spaces unevenly to reach the right edge. The result is rivers, awkward gaps, and a slower read.
- **alternative:** Default to left-aligned, ragged-right text. If justification is non-negotiable for editorial reasons, enable `hyphens: auto` and test on the real content.
- **severity:** medium

### low-contrast-text

- **name:** Low contrast text
- **tells:** Body text that fails WCAG AA (under 4.5:1) or large text under 3:1 against its background.
- **why-it-fails:** Excludes users with low vision and degrades readability for everyone in bright environments. Often a side effect of pursuing a "subtle" aesthetic.
- **alternative:** Hit at least 4.5:1 for body and 3:1 for large text. Verify with a contrast tool against the actual rendered surface (including any overlays or images behind the text).
- **severity:** high

### skipped-heading-level

- **name:** Skipped heading level
- **tells:** Heading hierarchy jumping levels — `h1` to `h3`, or `h2` to `h5` — purely because the lower level happened to look right visually.
- **why-it-fails:** Screen readers expose document outline through heading levels; skipping breaks navigation for assistive-tech users. Search engines also use the outline.
- **alternative:** Keep heading levels sequential and decouple level from visual style. Use CSS classes to make an `h3` look bigger if needed, rather than promoting it to `h2`.
- **severity:** high

### tight-line-height

- **name:** Tight line height
- **tells:** Body paragraphs set with `line-height` below 1.3 (unitless or any unit). Display headings below 1.05 also qualify.
- **why-it-fails:** Lines crowd each other; ascenders and descenders nearly touch, the eye loses track of which line it is on, and reading slows.
- **alternative:** 1.5–1.7 for body text, 1.1–1.25 for display headings. Tune by face — some require more, some less.
- **severity:** medium

### tiny-body-text

- **name:** Tiny body text
- **tells:** Body copy below 14px (or its rem equivalent: below `0.875rem` assuming a 16px root). For `clamp()`-based fluid typography, the *minimum* clamp value is the criterion — `clamp(0.75rem, 1vw, 1rem)` triggers because the floor is below 14px.
- **why-it-fails:** Hard to read on standard displays, worse on high-DPI screens at typical viewing distances. Excludes users with even mild vision differences.
- **alternative:** 14px minimum, 16px ideal for body. Reserve smaller sizes for true secondary content like captions, footnotes, and metadata.
- **severity:** high

### wide-letter-spacing-body

- **name:** Wide letter spacing on body text
- **tells:** Body paragraphs with `letter-spacing` greater than 0.05em.
- **why-it-fails:** Wide tracking breaks up the visual word groupings the eye uses to read; reading speed drops noticeably even at small spacing values.
- **alternative:** Leave body text at the face's default tracking (often 0 or slightly negative). Reserve wide tracking for short uppercase labels, where it actually improves legibility.
- **severity:** low
