# Deep Research Contracts

These optional helpers triage an existing collection; none performs retrieval or
claim verification. Each output includes `assessment_scope: "heuristic_triage"`
and `sources_verified: false`. Depth ranges and scores are advisory, not a
quality gate. Preserve the original input: discarded records do not retain all
source content needed for reassessment.

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
  "assessment_scope": "heuristic_triage",
  "sources_verified": false,
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
python3 <skill-dir>/scripts/run_pipeline.py \
  --input <skill-dir>/assets/sample-input.json \
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
      "domain": "optional compatibility field; scoring always derives the hostname from url"
    }
  ]
}
```

### Output

```json
{
  "assessment_scope": "heuristic_triage",
  "sources_verified": false,
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
      "credibility_reason": "string",
      "credibility_registry_id": "string|null",
      "credibility_authority": "string",
      "credibility_document_class": "string",
      "source_type_consistency": "compatible|mismatch|unverified",
      "priority_source": "boolean",
      "novelty": "float 0-1",
      "recency": "float 0-1",
      "score": "float 0-1",
      "retention_reason": "score_threshold|verified_priority_source_below_threshold"
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
    "priority_sources_retained_below_threshold": "int",
    "distinct_domains": "int",
    "threshold": "float"
  }
}
```

## Optional usage

Use `depth_router.py` when a rough tier estimate is useful, and
`evidence_filter.py` when ranking a supplied JSON collection helps triage it.
`run_pipeline.py` composes the two. The `budgets` key retains legacy numeric
ranges for interface compatibility; neither their minimum nor maximum is an
instruction to the researcher. Caller-selected filtering limits still control
how many records the helper emits, not what evidence may inform the answer.

Inspect consequential retained and excluded findings against their sources.
Lexical overlap can miss relevant counterexamples, deduplication can collapse
distinct claims, and domain priors cannot establish page-level support. Use
supported evidence from either bucket. The original input remains the source
for excluded content. The helper's `confidence_gaps` and `next_queries` are
heuristic suggestions, not a complete coverage assessment.

## Notes

- `evidence_filter.py` is deterministic and rule-based; it does not call an LLM.
- Credibility is a provenance prior derived from the URL hostname and
  `credibility-registry.json`, not a claim-quality verdict. Exact registry hosts
  plus rules explicitly declaring owned subdomains and the controlled `.gov`
  namespace can raise the neutral prior; self-declared `source_type` cannot
  raise an unknown host. University and publisher entries carry
  document-class-specific ceilings.
- A relevant registry-verified priority source can survive an aggregate score
  below the configured threshold. The finding records
  `verified_priority_source_below_threshold`, and the packet adds a confidence
  gap so synthesis verifies page-level support. Off-topic, duplicate, and
  over-budget rules still apply. Caller-provided `source_type` consistency is
  diagnostic and affects only the credibility tiebreak; it does not gate this
  verified-host retention.

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
  "assessment_scope": "heuristic_triage",
  "sources_verified": false,
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
