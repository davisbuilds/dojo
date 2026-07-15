---
name: skill-evals
description: Evaluate skill quality and routing reliability with deterministic checks. Use when creating/updating skills, validating trigger behavior (explicit/implicit/contextual/negative), applying SKILL.md contract checklists, or generating cross-skill compliance reports.
skill-type: workflow
compatibility: "Requires python3 and PyYAML."
version: 1.2.0
---

# Skill Evals

Deterministic evaluation harness for skill quality.

## When To Use

Use this skill when you need to:
- test whether skills trigger in the right situations
- run a repo-wide SKILL.md contract checklist
- compare skills before/after edits
- generate a compliance report for maintainers

## Workflow

1. Define a target set (`--skills`) or evaluate all skills.
2. Run contract validation.
3. Run release-version validation for changed skills when evaluating a branch.
4. Optionally run trigger evals with case fixtures.
5. Publish a markdown report with failures, warnings, and suggested fixes.

## Commands

```bash
# Contract checks (all skills)
python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --markdown docs/project/skill-contract-application-YYYY-MM-DD.md

# Version bump checks (changed skills)
python3 skills/skill-evals/scripts/check_skill_versions.py --base origin/main

# Perform the bump the check requires: update SKILL.md version + prepend a CHANGELOG heading
python3 skills/skill-evals/scripts/bump_skill_version.py skills/<name> patch -m "What changed."

# Trigger evals from fixture
python3 skills/skill-evals/scripts/run_trigger_evals.py --cases skills/skill-evals/assets/sample-trigger-cases.json --skills-root skills --pretty

# Trigger evals from declared `triggers:` frontmatter (self-routing + collision check)
python3 skills/skill-evals/scripts/run_trigger_evals.py --from-triggers --skills-root skills --pretty
```

## Output Contract

Provide:
- overall pass/warn/fail summary
- per-skill checklist results
- concrete remediation list (ordered by severity)

## Boundaries

- Do not treat lexical trigger scoring as a replacement for end-to-end LLM evals. Scoring is TF-IDF cosine over stemmed tokens — a deterministic proxy for routing, not a real agent. `scripts/behavioral_evals.py` is the real-agent backstop.
- `--cases` asserts by ranking (default): the top-scoring skill must be an expected `trigger`, and each `avoid` skill must score below it; a case with an empty `trigger` must keep every `avoid` under the match-nothing floor. Pass `--threshold` for the older absolute-score model.
- A fixture case may set `"known_hard": true` for a genuine lexical-ceiling collision (e.g. a prompt naming a competing skill's core verb). It is reported under `known_hard_*` and excluded from `failed`, so it stays visible without a fake pass or deletion.
- `--from-triggers` still asserts each declared `triggers:` phrase self-routes to its owner without being tied or beaten; phrases should echo the skill's name/description vocabulary.
- Do not auto-edit skills unless explicitly requested.
- Keep recommendations deterministic and reproducible.

## Verification

- All assertions in the fixture file pass (exit code 0)
- Changed skills either are part of the first unversioned baseline or have a version bump plus changelog entry
- No regressions in previously-passing skills
- Persisted report matches live validation output

## References

- `references/contracts.md` - input/output schemas
- `assets/sample-trigger-cases.json` - fixture for trigger tests

## Sibling skills

Part of the skill-management toolchain.

- `skill-creator` / `template` — upstream authoring. Validate after edits land here.
- `audit-skill` — security review (prompt injection, exfiltration). Orthogonal to contract validation; this skill checks structure, that one checks safety.
- `skill-standardizer` — keep skill copies aligned across mirrors after validation passes.
