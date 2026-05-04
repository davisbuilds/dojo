---
date: 2026-05-05
topic: design-systems-layer
stage: smoke-test
status: complete
plan: docs/plans/2026-05-03-design-systems-layer-implementation.md
---

# Design Systems Layer Smoke Test

Validation run for the `design-md` and `design-critique` skills against `/Users/dg-mac-mini/Dev/habits-ai-website` — a static HTML/CSS marketing site with no existing DESIGN.md. Each skill was exercised by a fresh `general-purpose` subagent on `claude-sonnet-4-6`, given only the skill files and the target paths. The subagents had no prior session context, so any ambiguity they hit is real ambiguity in the skill bodies, not contamination from the authoring conversation.

Both runs produced usable output — the skills work. The friction below is what to fix in the deferred remediation pass, not blocker-level breakage in v1.

## What worked

- The audit playbook in `design-critique` produced 14 concrete, file:line-anchored findings plus explicit "checked, no finding" entries for several patterns. The catalog's five-field schema held up under real input.
- The `author` operation in `design-md` produced a syntactically valid DESIGN.md draft that linted with 0 errors. The agent picked Linear as the closest aesthetic anchor on its own — the exemplar README's pole descriptions were enough signal.
- `run_cli.sh` worked end-to-end for both stdin and path-based input. The pinned 0.1.1 version returned the expected lint output shape.
- Both subagents hit the format-primer / slop-catalog references at the right moments; progressive disclosure routed correctly.

## What surfaced as friction

### `design-md`

**`orphaned-tokens` is structurally hostile to semantic color systems.** Of 10 lint findings, 9 were `orphaned-tokens` warnings on tokens the agent considered legitimately part of the system: muted-text opacity ladder, border tokens, hover-state colors, link/link-hover. The DESIGN.md frontmatter has no way to declare "this token is used by global body text" without fabricating a fake component. The skill gives no warning before the author starts that any palette token not paired 1:1 with a component slot will fire. **Fix:** add a "before authoring" note to the playbook; consider whether the format-primer should recommend a `prose` or `surface` component pattern as a sink for global tokens.

**No `borderColor` key on components.** Valid component property keys are `backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`. Border tokens have nowhere to land. Any palette entry intended for borders is permanently orphaned. **Fix:** flag this in `format-primer.md` so authors don't waste time trying to wire border tokens through.

**Hover-state pattern is lose-lose.** Either raw hover values inline (named tokens become orphaned) or hover-color tokens with separate hover-component entries (verbose). The primer's "Variants live as separate top-level entries" line doesn't acknowledge the trade-off.

**`rgba()` source CSS is silently unsupported.** The agent had to manually resolve every alpha value to its solid-on-canvas equivalent. Primer's Color row says hex only; the playbook doesn't tell the author to do the resolution.

**Inverted theme color semantics are uncovered.** `primary: "#FFFFFF"` is semantically odd but required to satisfy `missing-primary`. The skill assumes a brand-color world; dark-theme-first sites where the CTA fill is white have no canonical pattern.

**"At least three components: button, surface, text style" is ambiguous.** "Text style" reads as a typography token, not a component — the agent declined to fabricate a `prose-body` component and absorbed the orphaned warnings as a result. Playbook should disambiguate.

**Exemplar-to-spec gap is understated.** The exemplars README says "translate to the format-primer's frontmatter shape" but doesn't warn that a faithful full-palette lift from a Refero exemplar will produce double-digit `orphaned-tokens` warnings. The playbook fix from `design-md` Task 4 now distinguishes "voice anchor" from "structural template," but the README itself still soft-pedals the gap.

**Stdin vs. temp file for lint isn't disambiguated.** Both forms are shown; for in-context drafts the agent picked temp-file to avoid awkward heredoc piping. Cleaner guidance: stdin for one-shot drafts, temp file for iterative work.

### `design-critique`

**`pattern-match-strength` and `confidence` are conflated.** The finding template's `confidence` field covers input fidelity ("can I see the rendered output"); the agent kept hitting findings where match strength was the issue ("two primary CTAs in different sections, not adjacent — does this fire?"). It overloaded `confidence: medium` to cover both axes. **Fix:** add a `pattern-match-strength` field (`full` / `partial` / `borderline`) separate from `confidence`.

**Px-vs-ratio operationalization gap.** Patterns like `flat-type-hierarchy` ("font sizes within a few pixels of each other"), `tight-line-height`, and `tiny-body-text` are written for px-based CSS. Modern fluid typography uses `clamp()` and `rem`. The agent had to translate the tells to ratio criteria on its own. **Fix:** add ratio fallbacks per typography pattern in the catalog.

**Same-DOM-multi-pattern overlap is undefined.** When `identical-card-grids` fires on a feature grid AND `icon-tile-stacked` fires on each cell, is that one finding or two? The finding template's "one observation per finding" rule doesn't say whether "element" means a single DOM node or a semantic unit. Agent emitted both with a manual rationale.

**No distinction between "checked, no finding" and "unverifiable from this input."** Both end up in the single `Coverage gaps` block. The agent split it on its own and explicitly recommended separate `Checked — no finding` and `Unverifiable — requires screenshot or live render` sub-sections.

**`every-button-primary` scope is undefined.** "Next to each other" — same DOM parent? Same section? Same viewport? The agent guessed (same surface) and emitted a partial-match finding for two CTAs in different sections.

**Negative-finding output is verbose by default.** When the agent walks the catalog and finds nothing, the natural impulse is to document the check. The output shape doesn't authorize that, so the agent improvised "No finding" entries inside the Findings block. Either authorize them or split them out.

**Copy-rewrite scope is ambiguous on `redundant-information`.** The finding template asks for a concrete `recommended-fix`; the skill's read-only guardrail says no edits. For copy-level findings, the agent had to invent a replacement string with no template guidance on whether that's allowed.

## Cross-cutting observations

- **Both skills produced more "I had to make a judgment call" moments than expected.** Most concentrate on edge cases (alpha colors, partial pattern matches, distributed findings), not on the happy path. The skills work; the friction is at the boundaries.
- **The format-primer is mostly self-sufficient as a reference, but the lint-rule table needs a follow-up column.** "What components / tokens does this rule actually inspect?" — `contrast-ratio` skipping `transparent` backgrounds, `orphaned-tokens` not knowing about non-component surfaces — would prevent half the friction above.
- **Subagent runs are a useful smoke-test pattern.** A fresh agent reading only the skill body produces friction that an authoring agent cannot see. Worth reusing for future skill v1 launches.

## Items to fold into the deferred remediation pass

These join the existing "Deferred Follow-Up Work" list in `docs/plans/2026-05-03-design-systems-layer-implementation.md`:

1. `design-md`: add a "before authoring" warning about `orphaned-tokens` behavior. Decide whether the format-primer should recommend a `prose`-style sink component or document the friction as inherent to the format.
2. `design-md`: clarify "text style" in step 4 of the author playbook (component-with-typography-ref vs. typography token).
3. `design-md`: add an alpha-color resolution step to the author playbook ("when source CSS uses `rgba()`, resolve to hex on the canvas color before tokenizing").
4. `design-md`: document the inverted-theme color semantics case (white-CTA-on-black) so authors don't get blocked by `missing-primary`.
5. `design-md`: tighten exemplar README to spell out the orphaned-token risk on full-palette lifts.
6. `design-md`: pick stdin or temp-file as the recommended draft-lint flow and say so in the playbook.
7. `design-md`: extend the format-primer lint-rule table with a "what this rule inspects / skips" column, especially for `contrast-ratio` and `orphaned-tokens`.
8. `design-critique`: split `confidence` (input fidelity) from `pattern-match-strength` (full / partial / borderline) in the finding template.
9. `design-critique`: add ratio-based criteria to typography patterns (`flat-type-hierarchy`, `tight-line-height`, `tiny-body-text`) so they operationalize against rem/clamp CSS without a screenshot.
10. `design-critique`: define scope for `every-button-primary` (same DOM parent / same section / same viewport).
11. `design-critique`: add explicit guidance for same-DOM-multi-pattern overlaps (grid-level + cell-level findings).
12. `design-critique`: split the `Coverage gaps` output section into `Checked — no finding` and `Unverifiable — requires screenshot`.
13. `design-critique`: state explicitly whether `redundant-information` findings may include drafted replacement copy.
