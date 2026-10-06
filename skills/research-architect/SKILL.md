---
name: research-architect
description: Commission and plan multi-model research runs across Claude, ChatGPT, Gemini, or other executors. Shape research questions, briefs, and portable prompts; independently verify and synthesize returned reports. Use for a research prompt, research brief, cross-app research plan, or assessment of completed reports.
skill-type: workflow
version: 4.0.0
triggers:
  - research prompt
  - research brief
  - research architect
  - commission research
  - plan a research run
  - verify this research report
compatibility: Prompts are portable across terminal agents and external research apps. Optional hygiene and citation worksheet tools require python3; source verification requires retrieval access.
---

# Research Architect

Help the user ask a question worth researching, produce a prompt they can run,
and turn returned reports into a grounded answer. Enter at either end: shaping a
new inquiry or assessing existing reports. Neither requires reconstructing a
full research program.

## When To Use

Use for commissioning research, preparing or improving a portable prompt, or
verifying and synthesizing reports.

## Boundaries

For a source-backed answer directly, use `deep-research`; complexity alone does
not require a separate commissioning workflow. Implementation and adoption remain
separate from research unless the user requested them.

## Workflow

### Shape the inquiry with the user

Start from the conversation and existing material. Establish what the user wants
to understand or decide, why it matters, and which uncertainties could change
their next move. Curiosity is a valid purpose; do not invent a business decision
to justify it.

Give the user a chance to shape the core question, scope, and emphasis while
these are still open. Offer a concrete framing and ask about consequential
choices; reuse choices already settled. Do not turn this into an intake form or
another approval gate for an accepted direction.

Prefer one coherent inquiry with a small set of supporting questions. When a
request bundles a market survey, technical design, business plan, and personal
strategy, identify the central question and defer the rest or propose separate
runs. Protect depth where it matters. Distinguish examples from exhaustive lists
and user beliefs from established facts; never invent priors to disconfirm.

### Deliver a portable prompt

The prompt artifact is a first-class deliverable. Save the final, self-contained
prompt in the user's requested location or the project's research home; provide
a paste-ready artifact when no filesystem is available. Include enough context
for an executor with no session history, with only the private context the user
intends to share on that surface. Keep internal discussion outside the prompt.

Use [prompt composition](references/skeleton.md) for an adaptable structure.
Specify the question, relevant context and boundaries, priority uncertainties,
and the output that would be useful. Add topic-specific evidence requirements
and failure modes where they earn their cost. Do not require a section roster,
source quota, skeptical persona, or machine-readable summary without a consumer.

Before delivery, read the prompt as the recipient: can it answer the intended
question using the material it will actually receive? Check for unsupported
premises, unavailable attachments, conflicting demands, and scope dilution.
A focused source probe or [critique](references/redteam-checklist.md) is useful
when a consequential premise or access assumption is uncertain; neither is a
mandatory stage.

Optional hygiene check:

```bash
python3 <skill-dir>/scripts/lint_prompt.py prompt.md --json
```

This catches empty text, possible unfilled slots, drafting debris, and potentially
unsourced background statistics. Inspect flags in context. A pass does not assess
research quality or validate the background. `--executor web|terminal` is a
compatibility label, not a different instruction budget.

### Choose execution deliberately

Default for a multi-app run: give Claude, ChatGPT, Gemini, or other selected
executors **the same core prompt independently**, then synthesize their reports
in a separate pass. Do not seed later runs with earlier conclusions. Keep the
question and substantive constraints the same; adapt packaging or attachments
only when a surface needs it, and note differences that affect comparability.
Different models may still retrieve the same underlying evidence.

Specialized sub-questions or asymmetric assignments can help when sources or
methods differ materially, but they answer a different need from independent
coverage of the same question. Make that choice explicit. Do not multiply runs
merely because several executors are available.

For external execution, provide the prompt and a short hand-back instruction:
bring back the full reports with usable source links and any access limitations.
Prompt delivery can finish the current task; do not claim research has run.
For local execution, use available research tools or `deep-research` within the
user's scope. Delegation follows host capabilities and authorization; no fixed
subagent count, search count, or paid run is implied.

### Assess and synthesize returned reports

Start directly with the reports and the user's question. Recover missing context
only when it changes the assessment. Follow [report assessment and synthesis](references/synthesis.md)
for claim checks, source lineage, applicability, and treatment of disagreements.

Use a separate synthesis pass, preferably a fresh agent/session when available
and appropriate, with the question, reports, and sources rather than a favored
conclusion. Independence is useful, but it is not proof of correctness and does
not require delegation for every report. Spend verification effort on claims
that carry the conclusion, consequential numbers, disputed specifics, and
recommendations whose assumptions may not transfer to the user's situation.

The synthesis should answer the question, explain what the evidence changes for
this user, preserve meaningful disagreement, and identify the next decision or
investigation where warranted. A useful conclusion may be that no action is
justified. Distinguish checked support, plausible inference, and unresolved
claims; do not flatten uncertainty into a single confidence score.

## Output

For commissioning, deliver the prompt artifact and only the execution context
needed to use it. For returned reports, deliver a focused assessment or synthesis
with retrievable sources for consequential claims, limitations on what was
checked, and useful implications.

## Verification

Check that the prompt preserves the agreed scope, contains no invented context,
and can stand alone on the intended surface. Check that the synthesis answers
the original question, treats model agreement separately from independent
evidence, and bases recommendations on applicable support.

## Retention

Retain prompts, reports, and evidence needed to reassess important conclusions
or resume pending work. Use existing run conventions; there is no artifact per
stage. Record a process lesson only when it is useful, dated, and supported.
Ordinary use does not update installed skills or harness memories. Historical
[postmortems](references/postmortems.md) and [executor observations](references/executor-profiles.md)
are optional background, not current capability guarantees or standing mandates.
