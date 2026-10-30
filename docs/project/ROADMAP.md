# Skills Roadmap

Selected direction for the catalog, guided by the [Vision](VISION.md). This is not
an exhaustive work queue or a release contract. [Backlog](BACKLOG.md) owns
unresolved candidates and revisit conditions; individual skill changelogs and Git
history own detailed shipped changes.

## Current Direction

Continue evaluating what guidance adds beyond a capable agent's existing tools,
harness instructions, and repository context. Retain useful capabilities and
safeguards; narrow or retire instructions that add ceremony without addressing a
real gap. Apply the [authoring principles](../system/SKILL-BEST-PRACTICES.md) to
selected catalog revisions rather than expanding the catalog for coverage alone.

The September pass established proportional planning, scoped consultation,
knowledge-capture ownership, and claim-specific verification/testing. That is the
basis for subsequent review, not proof of improved model performance. Empirical
comparison remains separate from structural validation and source review.

The bounded [development CLI pilot](../design/2026-10-06-dojo-cli-pilot.md)
connects existing packaging checks and effective-catalog evidence. Evaluate it
through real authoring and discovery work before expanding its command surface.

Make existing capabilities easier to try on real work. Lead consumer examples
with `skill-standardizer` for executable drift auditing and recoverable sync,
`create-cli` for specialist interface conventions, and `test-strategy` for
portable testing preferences and meaningful regression coverage. Each example
should name a concrete task and a result the user can inspect. These are useful
starting points, not a required installation set or claims of measured benefit.

The frontend content/state and optional motion references are available. The
subsequent interaction investigation used existing browser and project test
tools to reproduce and repair a defect; it did not establish a need for a bundled
inspection helper. Revisit extraction only when repeated investigation exposes
mechanics worth maintaining beyond the existing tools.

## Further Review

The [composition-audit backlog entry](BACKLOG.md#evaluate-workflow-revisions-and-extend-the-composition-audit)
identifies remaining review candidates and the evidence that would justify work.
Choosing the next skill is a prioritization decision; those candidates are not
all committed projects. Use observed friction and applicable experimental results
rather than invocation counts or document size alone.

## Standing Distribution Boundary

Distribution profiles completed their scoped contract. The shipped measurement
and drift-checking interfaces are documented in [Operations](../system/OPERATIONS.md);
[Global Skill Membership](GLOBAL-SKILL-MEMBERSHIP.md) preserves the standing choice
and its dated evidence. The program did not commit to a CLI wrapper, automated
applicator, or cross-host deployment service. Reopen those only for demonstrated
operational needs, not because an old task list included them.
