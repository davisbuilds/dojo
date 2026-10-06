# Trying a skill on real work

Use this when a substantive change needs behavioral evidence or the user requests
a comparison. It is an optional method, not a prerequisite for every edit. A
harness's existing evaluator can execute it; Dojo does not require a second runner.

## Choose the uncertainty

An invocation problem needs a discovery test. An incorrect result needs task
execution. A script defect may need only a deterministic regression test. Dojo's
lexical fixture scorer and model-selection probe answer narrower questions than
native discovery or task success.

Choose realistic inputs that expose the suspected weakness and define success
from the user's intended result. Include a consequential boundary or near miss
where relevant. Do not score whether the output reproduces your headings, exact
phrasing, or a prescribed reasoning sequence unless a consumer requires them.
For subjective work, inspect the artifact with the user instead of inventing
objective-looking scores.

## Make the comparison interpretable

- Old versus new tests revision effect. Skill versus no skill tests marginal
  value. Both retain the normal harness, tools, and repository instructions.
- Snapshot complete skill bundles before editing, including referenced scripts
  and templates. Keep task inputs and execution conditions comparable. Record
  which model, harness, versions, and instructions were actually used.
- A path pointing to the old bundle is insufficient if the same session can
  discover the new global copy. Isolate discovery for the comparison, and verify
  what each executor received or loaded. Keep independent runs free of the
  author's solution and earlier outputs.
- Have executors perform the task, not recite how they would use the skill. Keep
  output artifacts and enough execution evidence to understand success, failure,
  extra work, and tool errors. Missing or failed runs are not silent passes.
- Use repeated runs when variability could change the conclusion. Small pilots
  are diagnostic. Keep fresh confirmation cases separate from cases used to
  select or tune a candidate; selecting by a “held-out” score makes it tuning
  data. Blind the comparison when evaluator expectations could bias judgment.

Use existing authorization and resource limits. This reference does not authorize
launching paid/model runs, subagents, external mutations, or changing user data.
If independent execution is unavailable, a walkthrough can still find defects;
label it as author inspection rather than an independent comparison.

## Inspect, revise, and stop

Inspect the actual outputs alongside meaningful checks: correctness, applicability,
missed boundaries, user interruptions, unnecessary artifacts or steps, time, and
cost where observable. A compact comparison in conversation is often sufficient;
a viewer or saved report is useful only when someone will use it.

Look for causes across cases. An assertion that always passes may not distinguish
the candidates; recurring helper code may belong in the bundle; generic coaching
may explain extra steps without improving results. Preserve useful discretion and
fix missing context, contracts, or tooling at their owner. Ask for user judgment
when acceptability is subjective or intent remains unclear.

Rerun affected cases after a material revision, and confirm on fresh cases before
claiming general improvement. Report mixed results and uncertainty. Keep, narrow,
revise, or retire the skill based on observed value; do not optimize indefinitely
for a small fixture set or present packaging/routing scores as task quality.
