---
name: deep-research
description: Answer questions through direct web research and source-backed analysis. Use for current information, evidence-based comparisons, due diligence, literature investigations, or a focused answer with citations and practical implications.
skill-type: workflow
compatibility: Web research requires retrieval access. Optional structured-finding helpers require python3.
version: 3.0.0
---

# Deep Research

Investigate the question at the depth its uncertainty and consequences warrant.
Deliver a supported answer that is useful to the user, with a clear account of
what the evidence does and does not establish.

## When To Use

Use for direct source-backed research, from a focused comparison to a substantial
investigation. Reuse the user's brief or accepted scope; there is no separate
commissioning requirement for complex or high-stakes questions.

## Boundaries

Use `research-architect` when the requested deliverable is a portable research
prompt, a multi-app run design, or assessment and synthesis of reports produced
elsewhere. Consulting either skill does not import the other's artifacts.
Simple static facts and tasks fully answered by supplied material do not need a
research workflow.

## Workflow

### Research around the uncertainty

Start with the question and intended use, using context already available. Ask
when an unresolved scope choice would materially change the investigation;
otherwise proceed with a reasonable, stated interpretation. Keep a coherent
focus and prioritize the uncertainties that could change the answer. The brief
can remain in the conversation unless a later consumer needs a file.

Choose retrieval methods that can answer those uncertainties. Follow relevant
leads, inspect original sources, and refine the search as the evidence develops.
An official interface claim, an empirical outcome, and a user's experience may
need different source types. Use primary sources for claims about what a study,
product, standard, or implementation actually says or does. Secondary sources
can supply leads, interpretation, and criticism; follow important attributions
back to their origin.

Allocate effort by information value and the cost of being wrong. Seek opposing
evidence and alternative explanations when the claim is contested, incentives
may distort reporting, or a recommendation depends on a fragile assumption.
Do not add counterarguments for symmetry or broaden into adjacent topics merely
to fill a report.

There are no required search counts, parallel tracks, or citation quotas. Stop
when the central question is supported well enough for its intended use, when
further retrieval is unlikely to resolve the remaining gaps, or at the user's
budget limit. Explain gaps that constrain the answer and the next observation
that could resolve them; do not call an exhausted search proof of absence.

### Judge evidence at the claim level

Inspect the source behind consequential claims. Check the actual passage,
measurement conditions, dates or versions when material, and whether its scope
fits the claim. A result in another population or environment may be suggestive
without supporting the proposed application.

Distinguish measured outcomes, author claims, inference, and forecasts. Trace
source lineage before counting corroboration: syndication, multiple summaries,
and model agreement can all repeat one original claim. A reputable domain is a
provenance clue, not proof that every page or statement is reliable.

Record access limitations honestly. A search snippet, inaccessible full text,
or repository README is not equivalent to inspecting the underlying evidence or
implementation. Quote or characterize only what was actually retrieved. Carry
material contradictions forward when the evidence cannot resolve them.

## Output

Answer the question directly, citing sources near the claims they support. Match
the structure and detail to the user's use: compare options when a choice is
needed, explain implications when learning is the goal, and recommend a next
step only when warranted. Avoid turning every inquiry into a build plan.

## Verification

Before delivering, check that the central conclusion follows from applicable
evidence, important numbers and attributions retain their original meaning, and
limitations could not silently reverse the recommendation. Separate supported
findings from inference and unresolved questions. State the limits of any
verification; a confidence label cannot replace an explanation.

Save a report or evidence record when requested or useful for continuation. No
fixed packet schema, self-report, or postmortem is required for ordinary research.
Research does not authorize implementation, publication, or promotion of a
finding into standing instructions.

## Optional structured-finding helpers

For an existing JSON collection of findings, the bundled scripts can suggest a
depth tier and rank/deduplicate the supplied records:

```bash
python3 <skill-dir>/scripts/run_pipeline.py --input findings.json --pretty
```

This command performs **no web retrieval or claim verification**. Its legacy
search ranges are estimates, not minimum work or completion criteria. Its
relevance, credibility, novelty, and recency scores are heuristics, not evidence
verdicts. Filtering can omit a decisive exception or contrary finding. Preserve
the original input and inspect relevant exclusions; supported evidence may be
used regardless of which output bucket it occupies.

Use these tools only when their structured triage helps. They are not a required
step before synthesis. See [contracts and limitations](references/contracts.md)
for their JSON interfaces and [the command wrapper](commands/deep-research.md)
for flags. The example at `assets/sample-input.json` illustrates the input shape,
not a validated research result.
