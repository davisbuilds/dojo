# skill-evals Contracts

## `validate_skill_contract.py`

### CLI

```bash
python3 skills/skill-evals/scripts/validate_skill_contract.py \
  --skills-root skills \
  --markdown docs/project/skill-contract-application-YYYY-MM-DD.md
```

### Output shape (JSON mode)

```json
{
  "summary": {
    "total": 0,
    "pass": 0,
    "warn": 0,
    "fail": 0,
    "strict": false
  },
  "skills": [
    {
      "skill": "deep-research",
      "path": "skills/deep-research/SKILL.md",
      "status": "pass|warn|fail",
      "line_count": 0,
      "checks": {
        "frontmatter_valid": { "status": "pass|fail", "required": true, "message": "..." }
      }
    }
  ]
}
```

## `run_trigger_evals.py`

### Input shape

```json
{
  "cases": [
    {
      "id": "dr-implicit-1",
      "type": "implicit|explicit|contextual|negative",
      "prompt": "Need source-backed latest analysis with citations",
      "expected": {
        "trigger": ["deep-research"],
        "avoid": ["gpt-imagen"]
      }
    }
  ]
}
```

### Output shape (JSON mode)

```json
{
  "summary": {
    "cases": 0,
    "assertions": 0,
    "passed": 0,
    "failed": 0
  },
  "skills": [
    {
      "skill": "deep-research",
      "tp": 0,
      "fp": 0,
      "tn": 0,
      "fn": 0,
      "precision": 0,
      "recall": 0,
      "f1": 0
    }
  ],
  "assertions": [
    {
      "case_id": "dr-implicit-1",
      "skill": "deep-research",
      "expected": true,
      "predicted": true,
      "score": 0.0,
      "passed": true,
      "type": "implicit"
    }
  ]
}
```
