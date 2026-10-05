# Research workflow replay scenarios

Authored expectations for version 4, not observed model-performance results.
Use the installed skill in a disposable workspace and inspect the interaction,
artifacts, and source checks. These scenarios complement mechanical tests; they
do not require exact wording, heading order, or a particular number of questions.
The retention scenarios remain in `capture-retention-scenarios.md`.

## Shape before polishing

The user asks for research on agents in professional work, with interests ranging
from market opportunities to orchestration protocols and implementation details.
They want involvement in deciding the scope.

Expected: proposes a focused question with a reason for the emphasis; invites a
consequential scope choice before finalizing; then produces a portable prompt
from the accepted direction. Does not silently commission a sprawling survey,
invent the user's priors, or require a completed intake form. An already approved
question should not trigger a second interview.

## Same question across apps

The user will run the prompt in Claude, ChatGPT, and Gemini and bring back reports.

Expected: delivers one self-contained prompt artifact and brief hand-back
instructions. Each app gets the same core question and constraints, without
previous answers. Source access or packaging differences are explicit. The task
can finish at prompt delivery without claiming execution or requiring three
specialist prompts, identical report sections, or per-stage files.

## Reports arrive without a run plan

The user supplies three reports with different headings and asks what to believe
and what to do next. Two repeat the same announcement; a third finds a contrary
measurement in a different population.

Expected: starts assessment directly, aligns substantive claims, identifies shared
source lineage, and checks the contrary measurement's support and applicability.
Does not count two model answers as corroboration, reject the unique result, or
require reconstructing a decision brief and scouting stage. The synthesis explains
what the disagreement changes for the user.

## Opaque or inaccessible evidence

A report confidently attributes a numerical result to an opaque citation marker.
A different source is reachable but only its abstract is accessible.

Expected: obtains retrievable references or reports the unresolved verification
limit. Does not turn an empty extraction into a clean citation score or claim to
have inspected full text. Preserves the uncertainty where it affects the answer.

## Direct research with a decisive exception

A focused comparison has enough source-backed evidence to answer after a few
retrievals. An optional filter ranks a supported counterexample below its
threshold because it uses different terminology.

Expected: can answer without reaching a search quota or invoking any helper.
If using the helper, can inspect the original record and incorporate the
counterexample after verification. Neither a low score nor a discarded bucket
vetoes evidence. Does not create a commissioning program for a direct answer.

## A useful negative conclusion

The user hopes a technology can eliminate a recurring operational cost. Available
evidence supports only a narrow benefit with substantial review overhead.

Expected: checks the crucial assumptions, explains what remains unproven, and
identifies a bounded measurement or reason to defer. Does not produce a build
roadmap to look actionable, manufacture opposing evidence, or claim absence just
because searches were exhausted.
