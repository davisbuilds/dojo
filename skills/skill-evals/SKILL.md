---
name: skill-evals
description: Evaluate skill quality and routing reliability with deterministic checks. Use when creating/updating skills, validating trigger behavior (explicit/implicit/contextual/negative), applying SKILL.md contract checklists, or generating cross-skill compliance reports.
compatibility: "Requires python3 and PyYAML."
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
3. Optionally run trigger evals with case fixtures.
4. Publish a markdown report with failures, warnings, and suggested fixes.

## Commands

```bash
# Contract checks (all skills)
python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --markdown docs/project/skill-contract-application-YYYY-MM-DD.md

# Trigger evals from fixture
python3 skills/skill-evals/scripts/run_trigger_evals.py --cases skills/skill-evals/assets/sample-trigger-cases.json --skills-root skills --pretty
```

## Output Contract

Provide:
- overall pass/warn/fail summary
- per-skill checklist results
- concrete remediation list (ordered by severity)

## Boundaries

- Do not treat lexical trigger scoring as a replacement for end-to-end LLM evals.
- Do not auto-edit skills unless explicitly requested.
- Keep recommendations deterministic and reproducible.

## Verification

- All assertions in the fixture file pass (exit code 0)
- No regressions in previously-passing skills
- Persisted report matches live validation output

## References

- `references/contracts.md` - input/output schemas
- `assets/sample-trigger-cases.json` - fixture for trigger tests
