# Frontend Anti-Patterns: The AI Slop Catalog

Patterns that instantly signal "an AI made this." Each anti-pattern includes what to do instead.

---

## Typography

### The Inter/Roboto Default
**Pattern**: Using Inter, Roboto, or system-ui for everything. Safe, invisible, forgettable.
**Instead**: Pick a font with personality. Even switching to Outfit, DM Sans, or Figtree (all clean sans-serifs) adds warmth. For headings, use something with character: Fraunces, Syne, Bricolage Grotesque.

### The Uniform Weight
**Pattern**: All text at font-weight 400 or 500. No hierarchy through weight variation.
**Instead**: Use weight contrast. 800+ for headings, 300 for large display text, 400 for body. The spread between weights creates visual tension.

### The 16px Everywhere
**Pattern**: All body text at 16px, headings at predictable increments (24, 32, 48).
**Instead**: Use a modular scale (1.25x, 1.414x, or 1.618x ratio). Let some text be surprisingly large (hero text at 80-120px) or surprisingly small (labels at 11-12px). Contrast in scale creates drama.

---

## Color

### The Purple Gradient Hero
**Pattern**: Linear gradient from purple (#7c3aed) to blue (#3b82f6) on a white background. The single most overproduced AI color choice.
**Instead**: If you want a gradient, make it unexpected: dark olive to warm gold, burnt sienna to dusty rose, near-black to dark teal. Or skip gradients entirely and use a bold flat color.

### The Gray-on-White
**Pattern**: #6b7280 text on #ffffff background. Every surface white, every text gray. Technically readable, emotionally dead.
**Instead**: Tint your neutrals. Warm grays (#8c7a6b), blue-grays (#4a6d80), or green-grays (#6b7a66) feel intentional. Use off-white backgrounds (#faf9f6, #f5f0e8) instead of pure white.

### The Blue Primary
**Pattern**: #3b82f6 or similar "safe blue" as the primary accent on everything. Links, buttons, active states, all the same blue.
**Instead**: Choose a color that relates to the content. A cooking site could use terracotta. A finance tool could use deep green. A music app could use coral. Blue is only right if it means something.

### The Rainbow Dashboard
**Pattern**: Charts and cards each in different random saturated colors (red, blue, green, yellow, purple) with no palette relationship.
**Instead**: Use tints/shades of 2-3 colors max. A blue palette: #1a3a5c, #2d6fa8, #6ba3d6, #a8d0f0. Vary lightness, not hue.

---

## Layout

### The Centered Card Grid
**Pattern**: Perfectly centered heading, subtitle, 3 equal-width cards in a row, each with icon-title-text-button structure. Repeated identically.
**Instead**: Try asymmetric layouts. Make one card span two columns. Use a masonry grid. Let some content bleed off-edge. Overlap elements. Break the predictable rhythm.

### The Hero-Features-CTA Sandwich
**Pattern**: Full-width hero with gradient bg and centered text -> 3-4 feature cards -> CTA section. Every landing page, every time.
**Instead**: Open with something unexpected: a bold statement in giant type, an interactive element, a scrolling marquee, a split-screen comparison. Structure should match content, not a template.

### The Equal Padding
**Pattern**: 24px padding on everything. Every card, every section, every container. Uniform spacing throughout.
**Instead**: Vary spacing intentionally. Sections can breathe with 80-120px vertical padding. Cards can be tight (16px) or airy (40px). The ratio between spacings creates rhythm and hierarchy.

---

## Components

### The Rounded-Everything
**Pattern**: border-radius: 8px (or 12px, or 16px) on every single element. Cards, buttons, inputs, images, badges -- all the same radius.
**Instead**: Mix radiuses with intent. Buttons at 6px, cards at 2px, avatars at 50%. Or go sharp (0px) on some elements. The variation signals design thought.

### The Shadow-Lifted Card
**Pattern**: box-shadow: 0 4px 6px rgba(0,0,0,0.1) on every card. The "floating paper" look, applied uniformly.
**Instead**: Use shadows sparingly and with variation. Subtle: 0 1px 2px. Dramatic: 0 25px 50px -12px. Or skip shadows entirely and use borders, background color differences, or negative space to create separation.

### The Generic Icon Set
**Pattern**: Heroicons or Lucide icons used at 24x24 for everything. Every feature has its own generic icon. Icon + heading + paragraph repeated 3-6 times.
**Instead**: Use fewer icons, or none. Replace with numbers, letters, custom illustrations, or typographic elements. If using icons, consider a distinctive set (Phosphor, Tabler) or mix weights (thin for decoration, bold for interaction).

---

## Motion

### The Fade-In-Up Cascade
**Pattern**: Every element fades in and slides up 20px with staggered delays. The universal "AI animation."
**Instead**: Vary your entrance animations. Some elements can scale in, others can slide from the side, some can simply appear instantly. Use different easings (spring, bounce, sharp). Or animate one thing dramatically and leave the rest static.

### The Hover Scale
**Pattern**: transform: scale(1.05) on hover for every interactive element. Cards, buttons, links -- all grow identically.
**Instead**: Use hover effects that match the element. Buttons: background color shift or subtle inset shadow. Cards: border color change or image zoom within the card. Links: underline animation or color transition.

---

## Overall

### The "Clean and Modern" Sameness
**Pattern**: Describes itself as "clean and modern" but looks identical to every other "clean and modern" page. No distinctive character.
**Instead**: "Clean" is a baseline, not an aesthetic. Layer a point of view on top. Clean + brutalist. Clean + editorial. Clean + playful. The modifier is what makes it memorable.

### The Gratuitous Glassmorphism
**Pattern**: backdrop-filter: blur(10px) with semi-transparent white backgrounds on everything. Glass cards, glass navbars, glass modals.
**Instead**: Use glassmorphism only when depth and layering serve the content (e.g., overlay on a hero image). One glass element is a design choice; ten is a crutch.
