---
name: skill-evals
description: Check skill packaging, release versions, and lexical routing fixtures, and choose evidence appropriate to a skill-quality claim. Use when validating a skill edit, investigating trigger collisions, or assessing what an evaluation establishes.
skill-type: workflow
compatibility: "Requires python3 and PyYAML; repository checks need a Dojo checkout."
version: 2.0.0
---

# Skill Evals

Choose the check that answers the question. Packaging validity, discoverability,
and useful task outcomes are different claims; one cannot substitute for another.

## Evidence and limits

| Question | Available evidence | What it does not establish |
| --- | --- | --- |
| Is the bundle valid and releasable? | Metadata/schema checks, version/changelog checks, generated-artifact checks, relevant script tests | Correct advice, safe execution, or useful results |
| Are descriptions lexically distinguishable? | `run_trigger_evals.py` fixtures or declared phrases | Actual harness discovery, invocation, or improved task outcomes |
| Which skill does a model say it would choose? | Repository `scripts/behavioral_evals.py`, explicitly opted into | The harness actually loaded the body, or the task was performed well |
| Does this revision improve work? | Representative task runs with a suitable baseline, inspected outputs and execution evidence | General benefit beyond the observed tasks, models, and harnesses |

Select targets and checks from the change and uncertainty. Report their scope,
failures, exclusions, and limits. A concise answer is enough unless a saved report
has a consumer. Do not repair, launch paid runs, or synchronize installations
merely because an evaluation identified a concern; stay within the user's scope.

## Repository checks

Run these from the Dojo checkout; these are repository tool paths, not paths
assumed to exist in a consuming project's working directory.

```bash
# Metadata gates. --json exposes each result; --authoring-hints adds prose hints.
python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict

# Release-relevant changes need a version bump and matching changelog heading.
python3 skills/skill-evals/scripts/check_skill_versions.py --base origin/main

# Helper when a release bump is part of the authorized edit.
python3 skills/skill-evals/scripts/bump_skill_version.py skills/<name> patch -m "What changed."

# Lexical routing diagnostics, not a real harness invocation.
python3 skills/skill-evals/scripts/run_trigger_evals.py --cases skills/skill-evals/assets/sample-trigger-cases.json --skills-root skills --pretty
python3 skills/skill-evals/scripts/run_trigger_evals.py --from-triggers --skills-root skills --pretty
```

Use `--skills name,other-name` on the contract checker for a focused inspection.
`--markdown <path>` saves an optional report. Strict mode enforces catalog
metadata. `--authoring-hints` opts into prose headings, trigger wording, resource
navigation, and length heuristics; these never become failures. Review substance
before acting on a warning. A recognized
heading is not evidence that the section is useful or even complete.

## Routing diagnostics

The lexical scorer uses TF-IDF over stemmed tokens. In fixture mode the winner
must be an expected `trigger`; each `avoid` must rank below it. An empty `trigger`
requires all `avoid` skills below the match-nothing floor. `--threshold` retains
the older absolute-score mode. Declared phrases must self-route without a tie.

Use natural requests and meaningful near misses. Inspect confusion against the
actual catalog, not only a handpicked competing pair. Do not stuff descriptions
with keywords merely to satisfy this proxy. `known_hard` cases are visible but
excluded from gating failures; report that exclusion rather than claiming all
cases passed. Schema details and example fixtures are in `references/contracts.md`
and `assets/sample-trigger-cases.json`.

## Outcome evidence

When a behavioral comparison is warranted, define success from the user's task
before looking at candidate outputs. Distinguish revision effect (old vs. new)
from marginal value (with vs. without the skill) and discovery (whether it loads).
Preserve the same task inputs, model, harness, tools, and relevant instructions;
freeze full bundles including resources and check what the executor actually
received. Compare correctness and meaningful boundaries as well as unnecessary
steps, user interruptions, time, and cost. Avoid grading obedience to incidental
wording or your own preferred headings.

Use repeats when variability could change the conclusion; retain unseen cases
for confirmation after tuning. Separate grounded source repairs from claims of
measured improvement. A smoke run supplies diagnostic evidence, not a universal
quality score. Reuse an appropriate existing runner or harness toolkit; this
skill does not require a new benchmark or launch one automatically.

Deliver what the evidence establishes and what remains untested. Security review
belongs to `audit-skill` when that is the question; deployment drift belongs to
`skill-standardizer`. Neither workflow follows automatically from validation.
