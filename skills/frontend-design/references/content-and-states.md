# Interfaces with real content

Use this reference when implementing data-driven cards, lists, forms, or panels,
or when an interface works with demo content but fails with real input. Choose
the cases relevant to the changed surface; this is a set of diagnostic examples,
not a required audit of every screen.

## Exercise the input boundary

Trace a displayed value back to its props, fixture, response, or stored record.
Use plausible values and actual schema limits. A short form limit may not cover
records created through imports or another API. If there is no known bound,
describe that uncertainty and choose a believable long value.

Feed examples through that boundary using the project's existing story, fixture,
or test route. Preserve the rendering code for the initial reproduction. Changing
rendered text in DevTools can explore a layout, but skips parsing, formatting,
escaping, conditional rendering, and search behavior. It cannot verify those paths.
Keep fixtures isolated from production data. A new demo toggle is useful only if
someone needs it; the existing test tooling may already make the state reachable.

## Failure to remedy

| Input or transition | Look for | Choose a remedy based on the task |
| --- | --- | --- |
| A long title, identifier, or URL beside an action | The action leaves the container; text forces the whole page wider | Inspect the shrinking boundary: a flex text child may need `min-inline-size: 0`, a grid track `minmax(0, 1fr)`. Let indispensable actions keep their size. Apply `overflow-wrap: anywhere` to text that may break, rather than clipping the whole row. |
| Similar filenames or records that differ near the end | Ellipsis makes distinct choices look identical | Keep the distinguishing part visible, wrap where reading matters, or provide an accessible full-value detail/copy action. A hover-only tooltip or `title` attribute is insufficient for touch and keyboard access. |
| Missing optional metadata; a short name; a missing or failed image | Orphan separators, blank rows, broken-image icons, displaced controls | Render separators with their content. Give media a stable box and an intentional fallback; prevent an image-error fallback loop. Decide whether omission or reserved space better preserves comparison. |
| Zero, one, and the pagination boundary | False empty states, wrong plurals, an empty next page, controls that cannot recover | Distinguish no records from no matches and failed loading. Keep clearing filters or retrying reachable. Use the product's localization rules; test page-size and page-size-plus-one when pagination exists. |
| A count changes from 99 to 100; an amount is zero, negative, or unavailable | Layout jumps; missing values appear as zero; precision disappears | Use the existing locale/number formatter and explicit missing-value semantics. Tabular numerals help align changing digits but do not reserve space for an extra digit. Preserve precision where people compare amounts. |
| `Research & Development`, literal `&amp;`, or markup-like text | Entities appear on screen; search finds a transformed value; content becomes HTML | Check each serialization and rendering boundary separately. Encode for the destination context. For JSON inside an HTML script data block, HTML entities are not decoded; escape `<` as a JSON Unicode escape to protect the script boundary, then parse normally. Render user text as text or escape it at the final HTML boundary. |
| Loading becomes success, empty, or error; retry follows failure | Stale rows look current, skeletons jump, focus disappears, retry repeats an action | Exercise the transition, not just each final screenshot. Keep the user's input and a reachable recovery action; distinguish stale data if it remains visible. Check the actual action and resulting state before claiming recovery. |

Test content at its real container width: a component in a sidebar can fail even
when the page is wide. Include relevant narrow viewports, text enlargement, or
supported locales. Browser zoom and increased root font size exercise different
behaviors; name which one you checked. Supported RTL layouts need inspection of
action order and mixed-direction identifiers, not just translated labels.

## Readability and interaction together

Wrapping is useful when people need the full value. Clamping can suit a preview,
provided its full content remains reachable. Avoid solving overflow by hiding
the information or action the user needs. Check keyboard focus and touch access
after a layout repair; a visible control can still be unreachable under an overlay.

Large lists deserve a realistic quantity for the product, including its existing
pagination or virtualization. Observe responsiveness before adding either.
Preserve an ordinary-content case alongside the failing input so the repair does
not silently damage the common layout.

## Evidence and scope

Drive the affected flow in the rendered application. For a layout finding,
inspect the screenshot and relevant geometry; for search, recovery, or selection,
perform the action and check the resulting content. Report a source-based
hypothesis as such when a browser check is blocked.

Reuse the project's launch and cleanup instructions. If repeated work reveals a
missing verification recipe, a tested project-local instruction may help; this
reference does not require creating one. Preserve useful evidence outside scratch
state that cleanup removes. A demonstrated repair establishes that case, not a
general claim that this skill improves agent performance.

## Sources and adaptation

The content-edge examples and layout remedies adapt Emil Kowalski's
[`break-ui` and its catalog](https://github.com/emilkowalski/skills/tree/2d228630ba1446365f614a108cb8252f1feda202/skills/break-ui),
under the MIT license. Dojo rewrites and narrows the guidance: cases are selected
for the task, existing fixtures are preferred, and no toggle, report format, or
new approval step is required. The serialization example comes from exercising
Dojo's own catalog generator. See [third-party notices](../THIRD_PARTY_NOTICES.md).
