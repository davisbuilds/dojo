# Report assessment and synthesis

Accept reports directly; the user does not need a prior run plan or commissioning
artifacts. Use the original question and relevant context when available. If a
missing detail changes the recommendation, resolve it or state the assumption.

## Check what carries the conclusion

Build a working view of the important claims, their supporting sources, and the
reasoning that connects them to the answer. This can stay in working notes unless
an evidence table would help the reader or later verification.

Prioritize verification by consequence and uncertainty: decision-driving numbers,
source attributions, disputed specifics, surprising results, and claims that
require direct artifact inspection. Check whether the cited source supports the
exact claim, whether the relevant passage was actually retrieved, and whether
the population, environment, version, or measurement fits the proposed use.
A live URL does not establish support; support alone does not establish that a
recommendation transfers to the user.

When access fails, say what could not be checked and what that limits. An opaque
export is not evidence of fabricated citations, and an empty citation sample is
not a clean bill of health. Obtain usable links or map them manually before
making citation-quality claims. Distinguish no evidence found from evidence that
an effect or capability is absent.

## Compare reports through their evidence

Align answers to the substantive questions, regardless of heading order. Trace
apparently independent citations to their upstream studies, announcements, or
datasets. Several models repeating one vendor claim add no independent empirical
support. Conversely, a finding present in only one report may be valuable;
verify it according to its importance, not its vote count.

Separate factual contradictions from different definitions, time frames,
applicability judgments, or recommendations under different preferences. Resolve
what the sources can resolve. Preserve remaining disagreement, explain what
would change the decision, and avoid averaging incompatible estimates.

A fresh synthesis session can reduce attachment to an earlier answer. Give it
the question, relevant context, reports, and available evidence without telling
it which report to favor. It still needs source checks; independence is not a
substitute for verification.

## Optional citation worksheet

For a long report or repeatable verification record:

```bash
python3 <skill-dir>/scripts/score_report.py worksheet report.md > worksheet.json
# Retrieve the sampled sources, then fill support verdicts and applicability.
python3 <skill-dir>/scripts/score_report.py score worksheet.json
```

The script extracts claim/citation pairs, samples them, and calculates rates from
verdicts supplied by the reviewer. It does not fetch sources or judge truth.
A claim with several citations has several pairs; one supporting citation must
not hide another that contradicts it. Inspect the extraction and add checks for
important uncited claims or claims the sampler missed.

The default sample favors quantitative and source-attribution claims, informed
by dated failures in this catalog's run records. It is not a representative
estimate of the whole report's accuracy. Report denominators, extraction limits,
and unchecked consequential claims with any rates. If `citation_coverage.status`
is `opaque` or `absent`, do not interpret a hit rate. Self-reported confidence and
worksheet scores do not establish recommendation quality.

## Deliver the useful answer

Lead with the answer to the user's question and explain the evidence that matters
for it. Cite original sources where retrievable and distinguish checked findings,
reasonable inference, and unresolved claims. A report-only comparison is valid
when that is the requested scope, but label its external verification limit.

State implications for the user's constraints: a decision, a bounded next step,
a change in understanding, or a reason to defer action. Preserve source and
reasoning detail needed to revisit important conclusions; omit repeated summaries
and peripheral findings that do not help. A combined report should improve the
answer, not concatenate the inputs or manufacture certainty.
