---
name: deep-research
description: Triage an existing JSON collection of research findings with advisory depth estimates and heuristic ranking; does not retrieve or verify sources.
argument-hint: "--input <path> [--output <path>] [--override-depth quick|standard|deep] [--max-findings <n>] [--depth-only]"
---

# Deep Research Command

This wrapper retains the structured-helper interface. For a natural-language
research question, use the `deep-research` skill's research guidance directly.

## Behavior

Resolve `<skill-dir>` to this installed skill's absolute directory, then run:

```bash
python3 <skill-dir>/scripts/run_pipeline.py $ARGUMENTS
```

The command estimates a depth tier and optionally filters supplied findings.
It does not search, fetch cited pages, or establish whether a claim is supported.
Use `references/contracts.md` for the input and output schema.

- `depth_plan` contains advisory estimates; its search ranges are not quotas.
- `research_packet` contains ranked findings, exclusions, and heuristic gaps.
  It is `null` when filtering was skipped; report that state accurately.
- `meta` identifies which helpers ran and the limits of the output.

Retain the input. Inspect relevant exclusions and verify important claims before
using this packet to answer the user. A low score is not a reason to ignore a
supported counterexample; a high score is not a reason to trust an unsupported
claim. Do not present heuristic `confidence_gaps` as a complete uncertainty audit.

## Examples

```bash
# Advisory depth estimate only
/deep-research --input /tmp/research.json --depth-only --pretty

# Rank supplied findings; preserve the source input
/deep-research --input /tmp/research.json --output /tmp/research.packet.json --pretty

# Override tier and retained-record count for this triage
/deep-research --input /tmp/research.json --override-depth deep --max-findings 18 --pretty
```
