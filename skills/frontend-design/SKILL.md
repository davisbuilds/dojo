---
name: frontend-design
description: Build or refine frontend interfaces with intentional visual design. Use when creating a page or component, shaping a UI's visual direction, or improving its layout, hierarchy, and interaction states. For critique without implementation, use design-critique.
skill-type: workflow
license: Complete terms in LICENSE.txt
version: 2.2.0
---

# Frontend Design

Build interfaces that serve the product and feel deliberately designed. Start
from the user's task, audience, existing interface, and requested scope. Visual
novelty is useful when it supports the brief; familiarity and consistency can be
exactly the right design choice.

## Establish the direction

Inspect the relevant screens, components, styles, and product guidance before
choosing a direction. Preserve established tokens and interaction conventions
when extending an application. Ask about missing choices only when they would
materially change the result; a settled brief does not need another design phase.

For a new visual direction, connect choices to the content and intended use:
what should people notice, understand, and do? An expressive landing page and a
dense monitoring interface have different needs. Describe the important choices
briefly when that helps the user assess them; no separate design artifact is
required.

Typography, color, spacing, density, and motion should work together. There are
no banned font families, colors, or layouts. Repetition can support comparison,
and a restrained system font can suit an operational product. Avoid decoration
that competes with the information or action the screen exists to provide.

## Implement the experience

Use the project's stack and existing components. Add abstractions or dependencies
when the requested behavior warrants them, not to achieve a preferred aesthetic.
Match scope to the task: a small component change should not silently restyle its
surroundings.

Treat the relevant states as part of the design: realistic content, loading,
empty results, errors, selection, focus, and constrained viewports. Choose the
states that can change the user's ability to complete the task. Preserve keyboard
operation, semantic controls, legible contrast, and reduced-motion behavior as
applicable; decorative polish does not compensate for an unusable interaction.

Use motion to communicate state or continuity, or when the brief calls for it.
Do not add entrance effects, textures, custom cursors, or asymmetry by default.
Check that visual changes preserve the application's data and action semantics.

## Check what was built

For a meaningful visual or interaction change, inspect the rendered result and
exercise the affected flow using the project's browser tooling. Compare relevant
states and viewport sizes against the intended outcome. Source inspection and a
successful build cannot establish visual quality or usability.

Reuse applicable verification and follow project instructions. If a rendered
check is blocked, state what remains unobserved rather than claiming the design
is verified. Return the implementation, relevant evidence, and any material
limitations; no mandatory sibling review or fixed checklist report is required.

## Optional references

- `references/motion-and-interaction.md` covers interrupted transitions, exit
  cleanup, reduced motion, and rendering tradeoffs. Use it when implementing or
  repairing animated interactions.

- `references/content-and-states.md` connects realistic content and state failures
  to remedies when building data-driven interfaces or repairing layouts that fail
  beyond demo data. Use the examples relevant to the affected surface.
- `references/anti-patterns.md` offers questions for spotting design choices that
  are disconnected from the task. These are prompts for judgment, not bans.
- `references/color-palettes.md` and `references/font-pairings.md` offer starting
  material when a new visual direction is needed. Existing product choices take
  precedence; examples are not prevalidated accessibility or performance claims.
- Consult `design-md` for actual DESIGN.md tooling or token-format work, and
  `design-critique` when a critique would resolve a design question. Consulting a
  reference does not require its entire workflow.
