---
name: deep-research
description: Run the deep-research pipeline in one command with automatic depth routing and optional evidence filtering.
argument-hint: "--input <path> [--output <path>] [--override-depth quick|standard|deep] [--max-findings <n>] [--depth-only]"
allowed-tools: [Read, Bash(python3 skills/deep-research/scripts/run_pipeline.py:*)]
---

# Deep Research Command

Use this wrapper to run the canonical deep research pipeline from `skills/deep-research`.

## Behavior

1. Load `deep-research` skill guidance from `skills/deep-research/SKILL.md`.
2. Run the pipeline script:

```bash
python3 skills/deep-research/scripts/run_pipeline.py $ARGUMENTS
```

3. Interpret output sections in this order:
1. `depth_plan`
2. `research_packet`
3. `meta`

4. If `research_packet` is `null`, report that filter stage was skipped and explain how to provide findings.

## Input Expectations

Input JSON must include:
- `research_brief`: string
- `findings`: array (required only when running full pipeline)

Optional context flags for routing:
- `high_stakes`
- `requires_current_info`
- `multi_entity_comparison`
- `unknown_scope`
- `task_context` object with same flags

## Output Rules

- Base conclusions only on `research_packet.key_findings` and `research_packet.citations`.
- Never reintroduce items from `research_packet.discarded_context` into final claims.
- If `confidence_gaps` is non-empty, report those gaps explicitly.

## Example Invocations

```bash
# Depth planning only
/deep-research --input /tmp/research.json --depth-only --pretty

# Full pipeline with automatic depth selection
/deep-research --input /tmp/research.json --output /tmp/research.packet.json --pretty

# Full pipeline with forced depth and tighter retained findings
/deep-research --input /tmp/research.json --override-depth deep --max-findings 18 --pretty
```
