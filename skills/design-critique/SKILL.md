---
name: design-critique
description: Review an interface's visual hierarchy, usability, interaction states, and product fit. Use when asked to critique a UI, assess polish or accessibility concerns, identify generic design choices, or recommend what to improve. Return grounded findings and concrete alternatives; use frontend-design to implement changes.
skill-type: workflow
version: 2.0.1
---

# Design Critique

Judge how well an interface serves its intended users and tasks. Preserve useful
product conventions and distinguish consequential problems from optional taste
preferences. A familiar font, card grid, or color does not establish poor design
or AI authorship.

## Ground the review

Use the brief, existing product, and requested scope to identify what the user
needs to understand or accomplish. For visual judgments, prefer the rendered
interface or supplied screenshots. Read source to explain causes and locate
changes; markup alone is not the highest-fidelity view of the experience.

A request to review a supplied URL normally includes ordinary inspection of that
page using available browser tools. Follow access and action boundaries: reviewing
a flow does not authorize submissions, purchases, destructive actions, or changes
to shared data. Ask only when necessary access or a consequential action is
unresolved, not for another permission to look at the requested surface.

A screenshot can establish visible layout, not keyboard behavior or hidden states.
Source can reveal likely defects without proving how the running interface behaves.
When rendering or interaction is unavailable, give the useful supported findings
and identify the consequential evidence gaps.

## Follow the important questions

Choose depth from the task and evidence, rather than walking a fixed catalog:

- Does the hierarchy make the important information and actions easy to find?
- Do grouping, density, navigation, and language support the actual workflow?
- Are loading, empty, error, selected, and disabled states understandable where
  they matter? Does realistic or long content expose layout failures?
- Can the relevant flow work at its intended viewport sizes and with keyboard
  input? Are focus, names, semantics, contrast, and motion appropriate?
- Does the visual language fit the product and remain coherent with its other
  screens? Is decoration helping the experience or competing with it?

Use the project's accessibility checks or other suitable tools for claims they
can establish. Automated checks complement rendered and interaction evidence;
passing a scanner does not establish complete accessibility compliance. A formal
standards audit needs its stated scope and evidence, beyond this critique.

`references/slop-catalog.md` is optional inspiration for recurring design smells.
Its examples are not exhaustive, findings need not match a pattern, and alternatives
must fit the product. Do not assign severity from the appearance of a pattern.

## Return useful findings

For each finding, show the affected element or state, what you observed, why it
matters to the user, and a concrete improvement. Use a screenshot region, route,
selector, or source location as appropriate. Separate observed behavior from an
inference and name the evidence needed when that distinction changes the advice.

Prioritize by actual impact, reach, and the purpose of the review. Consolidate
observations that share a cause or fix. Offer a small number of alternatives when
there is a meaningful tradeoff; avoid prescribing a redesign to fix a local issue.
`references/finding-template.md` has an optional example, not a required schema.

Report the most useful findings first, with relevant coverage limits. No finding
quota, fixed top three, exhaustive no-finding inventory, or taste verdict is
required. A review can conclude that no meaningful change is warranted.

Critique alone does not authorize edits. If the user also requested fixes, apply
them within that scope and check the result. Consult `frontend-design` for the
implementation question or `design-md` for token-format work when useful; neither
is a mandatory next step.
