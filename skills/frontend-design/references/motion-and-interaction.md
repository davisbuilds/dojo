# Motion that survives interaction

Use this when implementing or repairing transitions, animated controls, overlays,
or gesture feedback. Start with the project's motion tokens and component
primitives. The examples are choices for a particular interaction, not a required
sequence, animation library, or aesthetic.

## Choose the behavior before the curve

Repeated actions need immediate acknowledgment. A command palette used constantly
may work best with instant opening; an occasional panel can use a short transition
to explain where it came from. Keyboard input is not itself a reason to ban motion.
Keep the action available while decoration plays, and avoid repeatedly animating
content people are trying to read.

For a small control, roughly 120–200 ms is a useful starting range; a larger panel
may need longer to remain legible. These are tuning suggestions, not acceptance
thresholds. Evaluate normal speed and rapid repetition on the actual component.
An ease-out entrance can make feedback visible quickly; an exit may need a
different curve or duration. Anchor a popover's transform origin to its trigger,
including when positioning flips sides near the viewport edge.

Prefer a CSS transition for a directly retargetable state such as hover or
expansion. Use keyframes for a defined sequence, and a programmatic animation or
an existing motion library when cancellation, gestures, or layout coordination
requires it. A spring can preserve velocity through interruption; it does not
repair incorrect component state. Reuse the component library's focus, dismissal,
and presence behavior instead of replacing it to obtain an effect.

## Failure to remedy

| Observed behavior | Investigate | Useful repair |
| --- | --- | --- |
| A hover target flickers as the pointer stays still | The animated transform moves the hit area out from under the pointer | Keep a stable interactive wrapper; animate its visual child. Gate hover-specific effects with `(hover: hover)` where appropriate, and preserve focus and press feedback. |
| Rapid open–close–open snaps or ends closed | A new animation restarts from a fixed keyframe, or an old completion callback commits stale state | Retarget from the current presentation. Cancel or supersede prior work; only the completion belonging to the current requested state may remove/hide the element. Exercise reversal before completion. |
| An invisible exiting panel still intercepts clicks or retains focus | Opacity changes presentation without changing interaction or focus ownership | Keep semantic state, focus restoration, and pointer behavior consistent with the component's close contract. A visual exit must not leave an invisible active overlay. Avoid placing focus inside content you are making inert. |
| Reduced motion leaves a spinner, locked button, or never-removed panel | Cleanup or business completion waits exclusively for an animation event | Complete the state change explicitly when motion is skipped. Cancellation and zero-duration paths must also settle; don't merely set every duration to a tiny value to manufacture an event. |
| An expanding section overlaps content or jumps at the end | A transform changes appearance but does not reserve layout space | Use the layout change the interaction needs, or an existing measured/layout animation. If animating height, account for content changes and retarget from the current size; do not assume a fixed pixel endpoint fits every locale. |
| A smooth isolated demo stutters in the real screen | Paint-heavy effects, large layers, or synchronous work competes with the animation | Profile the affected flow. Prefer transform/opacity when they express the change, but verify paint/layout and frame behavior in browser tooling. Avoid blanket `will-change` and claims that a property or library guarantees GPU execution. |

CSS `transitionend` is not a universal completion signal: canceling the transition
or removing it can prevent the event, and zero duration/delay produces none.
When listening, distinguish the intended target/property from bubbled descendant
or other-property events. With Web Animations, cancellation rejects the current
`finished` promise; handle the expected cancellation and guard stale completions.
See [transition events](https://developer.mozilla.org/en-US/docs/Web/API/Element/transitionend_event)
and [animation cancellation](https://developer.mozilla.org/en-US/docs/Web/API/Animation/cancel).

## Inspect the affected transition

Use the project's existing browser tooling or animation inspector. Sample during
motion: an auto-waiting click or screenshot can finish after a short transition.
When inspecting native animation objects, distinguish running, paused, and
forwards-filled finished effects; an inventory is not a count of moving elements.

Confirm the inspection surface can observe a known animation before interpreting
an empty result. Native `getAnimations()` covers CSS transitions, CSS animations,
and Web Animations, but not arbitrary requestAnimationFrame drawing, canvas/video
motion, or effects that have already disappeared. Restricted evaluation surfaces
may omit the API entirely. An inventory cannot measure frame rate, prove
compositor placement, or establish motion quality. See
[API coverage](https://developer.mozilla.org/en-US/docs/Web/API/Element/getAnimations)
and [rendering considerations](https://web.dev/articles/animations-and-performance/).

## Check the transition, including no-motion behavior

Use the existing browser tooling to exercise the actual action, reversal, and
completion. Check the resulting visible and semantic state. Where supported,
emulate reduced motion in a separate test context, then confirm that
`matchMedia('(prefers-reduced-motion: reduce)').matches` is true **and** that the
action still completes with appropriate focus and recovery. A matching media query alone does
not establish that the application honors it. Include a preference change during
motion when the implementation subscribes to changes.

Keep necessary state feedback when reducing motion; removal of spatial travel,
a gentler fade, or immediate replacement may suit different interactions. Use
slow playback to diagnose paths and normal playback to judge responsiveness.
For gestures, desktop emulation does not establish physical touch behavior.
Record only the relevant evidence and unresolved limits; no universal motion
score, second reviewer, or mandatory report is needed.
