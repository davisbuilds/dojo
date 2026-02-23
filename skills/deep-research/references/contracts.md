# Deep Research Contracts

This file defines the JSON contracts for `depth_router.py` and `evidence_filter.py`.

## `depth_router.py`

### Input

```json
{
  "research_brief": "string",
  "task_type": "optional string",
  "override_depth": "optional: quick|standard|deep",
  "high_stakes": "optional boolean",
  "requires_current_info": "optional boolean",
  "multi_entity_comparison": "optional boolean",
  "unknown_scope": "optional boolean",
  "task_context": {
    "high_stakes": "optional boolean",
    "requires_current_info": "optional boolean",
    "multi_entity_comparison": "optional boolean",
    "unknown_scope": "optional boolean"
  }
}
```

### Output

```json
{
  "selected_depth": "quick|standard|deep",
  "override_applied": "boolean",
  "score": "integer (-1 when override is used)",
  "task_type": "string",
  "reasons": ["string"],
  "budgets": {
    "searches": {"min": "int", "max": "int"},
    "tracks": {"min": "int", "max": "int"},
    "findings": {"target_kept": "int", "max_kept": "int"},
    "stop_rules": ["string"]
  }
}
```

Example:

```bash
python3 skills/deep-research/scripts/run_pipeline.py \
  --input skills/deep-research/assets/sample-input.json \
  --pretty
```

## `evidence_filter.py`

### Input

```json
{
  "research_brief": "string",
  "depth": "optional: quick|standard|deep",
  "selected_depth": "optional fallback when depth is omitted",
  "max_findings": "optional integer",
  "min_score": "optional float threshold override",
  "now": "optional datetime/date string",
  "findings": [
    {
      "title": "string",
      "url": "string",
      "summary": "optional string",
      "snippet": "optional string",
      "content": "optional string",
      "notes": "optional string",
      "excerpt": "optional string",
      "source_type": "official|primary|academic|government|news|analysis|blog|forum|social|unknown",
      "published_at": "optional date/datetime string",
      "domain": "optional string"
    }
  ]
}
```

### Output

```json
{
  "research_brief": "string",
  "depth": "quick|standard|deep",
  "key_findings": [
    {
      "citation_id": "[1]",
      "title": "string",
      "url": "string",
      "summary": "string",
      "relevance": "float 0-1",
      "credibility": "float 0-1",
      "novelty": "float 0-1",
      "recency": "float 0-1",
      "score": "float 0-1"
    }
  ],
  "citations": [
    {
      "id": "[1]",
      "title": "string",
      "url": "string",
      "domain": "string"
    }
  ],
  "discarded_context": [
    {
      "title": "string",
      "url": "string",
      "reason": "invalid_item|missing_content|off_topic|duplicate_url|duplicate_semantic|low_score|over_budget",
      "score": "float"
    }
  ],
  "confidence_gaps": ["string"],
  "next_queries": ["string"],
  "stats": {
    "input_findings": "int",
    "retained_findings": "int",
    "discarded_findings": "int",
    "distinct_domains": "int",
    "threshold": "float"
  }
}
```

## Composable Usage Pattern

1. Build `research_brief`.
2. Route depth with `depth_router.py`.
3. Execute search loop using returned budgets.
4. Normalize findings into the expected list shape.
5. Run `evidence_filter.py`.
6. Synthesize final response from `key_findings` and `citations` only.

## Notes

- `evidence_filter.py` is deterministic and rule-based; it does not call an LLM.
- If claim quality is critical, use this output as a pre-synthesis gate and run a final claim check afterward.

## `run_pipeline.py`

### Input

Same shape as the combination of both tools:
- routing fields consumed by `depth_router.py`
- optional `findings` array consumed by `evidence_filter.py`

CLI flags:
- `--override-depth quick|standard|deep`
- `--max-findings <n>`
- `--depth-only`

### Output

```json
{
  "depth_plan": { "...depth_router output..." },
  "research_packet": { "...evidence_filter output or null..." },
  "meta": {
    "depth_only": "boolean",
    "filter_stage_executed": "boolean",
    "requires_findings_for_filter_stage": "boolean",
    "note": "optional string when filter stage is skipped"
  }
}
```
