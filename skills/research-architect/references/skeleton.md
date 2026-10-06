# Portable research prompt composition

Use this as a drafting aid, not a required block protocol. The old filename is
retained for existing links. Shape the question with the user first; fill the
prompt from actual context and agreed priorities.

A useful prompt usually communicates:

- **Question and purpose:** the central uncertainty and what understanding or
  decision the research should support.
- **Context and scope:** relevant user constraints, definitions, time horizon,
  included populations or systems, and deliberate exclusions. Label beliefs and
  hypotheses. Say whether named examples are illustrative or exhaustive.
- **Priority questions:** what deserves depth and what can remain unresolved.
  If output space is constrained, preserve the central analysis rather than
  giving every subtopic a shallow paragraph.
- **Evidence needs:** source types that can answer this particular question,
  consequential claims to check, and plausible alternative explanations. State
  seed sources as leads with retrievable identifiers, not endorsed conclusions.
- **Useful output:** the answer and implications the user needs, with enough
  citations, assumptions, and limitations to evaluate it. Add a table, schema,
  artifact inspection, or detailed bibliography only when it serves that use.

Not all prompts need these headings. A short focused prompt may express the same
information in prose. A complex question may need substantial context without
benefiting from more procedural commands.

## Calibrate the evidence request

For contested empirical claims, ask what the evidence actually establishes, how
it was measured, and which alternative explanations remain. Check source
incentives and lineage where they affect the claim. Seek contrary evidence when
it could change the conclusion; do not demand a negative example in every
section or manufacture balance when the evidence is strong.

For design decisions, distinguish demonstrated behavior from a proposed design.
Request direct artifact inspection when the claim depends on implementation,
and specify which interfaces or constraints matter. Metadata, documentation,
and an inaccessible repository are not interchangeable with inspected code.

For comparisons, require like-for-like definitions where possible. Evidence in
one population, scale, jurisdiction, or operating environment may not transfer.
Ask for the consequence of that mismatch rather than a generic caveat.

For emerging topics, distinguish observed deployments, vendor claims, forecasts,
and speculation. Dates and product versions matter when the conclusion depends
on them. If access prevents answering a priority question, report what remains
unknown; do not infer absence from failed retrieval.

These are optional lenses. Select the ones that protect this inquiry from a
concrete error rather than pasting every instruction into every prompt.

## Example: one focused inquiry

> Research whether a small professional-services firm can reduce the human time
> needed to process routine client-document intake using current AI agents,
> while preserving its error-detection and client-confidentiality requirements.
>
> I am a technical solo builder deciding whether to pilot this workflow with a
> partner firm. I can build integrations, but I do not yet have work samples or
> measured baseline timings. Treat expected savings as hypotheses. Focus on
> intake, classification, missing-document follow-up, and routing for review;
> exclude substantive professional advice and acquisition financing.
>
> Prioritize which steps have checkable outputs, where exceptions consume human
> attention, and what evidence would distinguish saved effort from effort merely
> shifted into review. Compare documented deployments with relevant evaluations
> or failure evidence, tracing headline numbers to their original source and
> measurement conditions. Identify where evidence from another domain does not
> transfer. Do not estimate this firm's ROI without the missing operating data.
>
> Give me a grounded judgment on whether a pilot is warranted, the workflow
> boundary most worth testing, and the observations that would justify expanding,
> revising, or stopping it. Link the sources supporting important claims and
> distinguish measured results from assumptions. If the public evidence is too
> weak to choose a workflow confidently, identify the work samples or baseline
> measurements that would resolve the choice.

This is an illustrative prompt, not research findings or a recommendation to
build that product. Adapt to the user's question; don't substitute the example's
commercial purpose for curiosity, scientific inquiry, or another legitimate goal.

## Same-question multi-app runs

Send the same final prompt and relevant attachments to each selected app. Keep
private notes and earlier answers out of those independent runs. There is no
need to demand identical report headings: the synthesis can align claims and
questions across different structures.

Record material prompt, access, or timing differences with the returned reports.
Preserve the prompt that actually ran. If changing a pending run in light of an
earlier result is useful, do so deliberately and describe it as a follow-up,
rather than treating it as an independent same-question comparison.
