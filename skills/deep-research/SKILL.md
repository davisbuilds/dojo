---
name: deep-research
description: Use when a task needs direct web-backed research with controlled depth, relevance filtering, and citation-ready synthesis — the user wants the answer, not a commissioned research program. Routes work to quick, standard, or deep tiers, filters low-signal context, and returns a compact packet with key findings, citations, discarded context, confidence gaps, and next queries. For commissioning multi-model or externally-executed research programs, or verifying reports produced elsewhere, use research-architect instead — this skill is its execution backend.
skill-type: workflow
compatibility: "Requires python3. Requires network access for web research."
version: 2.0.0
---

# Deep Research

Run web research with explicit budgets, deterministic filtering, and compact evidence handoff.

## When To Use

Use this skill when the user asks for:
- up-to-date, source-backed analysis
- comparisons across multiple entities or options
- due diligence, risk, or policy-sensitive research
- long-form synthesis where irrelevant context must be pruned aggressively

Skip this skill for:
- simple static facts that do not require web retrieval
- tasks where user-provided context is already complete and verified
- engineering a research prompt/brief, planning multi-model or external DR
  runs, or verifying a report someone else produced — that is
  `research-architect`, which calls this skill as its execution backend

## Workflow

### Quick Runner

For one-command execution (route + optional filter), run:

```bash
python3 skills/deep-research/scripts/run_pipeline.py --input /path/to/research.json --pretty
```

Use `--depth-only` to return routing budgets without filtering.
For a ready-to-run example, use `assets/sample-input.json`.

### 1) Scope Gate

Before searching, produce a strict research brief:
- define objective in one paragraph
- list constraints and non-goals
- capture required source priorities (official docs, primary papers, etc.)

If scope is ambiguous, ask clarifying questions first.

### 2) Depth Routing

Use `scripts/depth_router.py` to select `quick`, `standard`, or `deep`.

```bash
python3 skills/deep-research/scripts/depth_router.py --pretty <<'JSON'
{
  "research_brief": "Compare incident response platforms for SOC teams in regulated healthcare environments.",
  "task_context": {
    "high_stakes": true,
    "requires_current_info": true,
    "multi_entity_comparison": true
  }
}
JSON
```

Routing policy:
- `quick`: 3-6 searches, single track, rapid answer
- `standard`: 8-20 searches, 2-4 tracks, one refinement pass
- `deep`: 20-80 searches, 4-8 tracks, contradiction checks and broader coverage

The user can override depth explicitly.

### 3) Research Loop

Run search rounds with this loop:
1. broad query expansion
2. targeted follow-up queries
3. gap check after each round
4. stop on saturation (no material novelty in two rounds)

Prefer primary sources first, then secondary analysis.

### 4) Evidence Distillation

After collecting raw findings, run `scripts/evidence_filter.py`.

```bash
python3 skills/deep-research/scripts/evidence_filter.py --pretty <<'JSON'
{
  "research_brief": "Compare incident response platforms for SOC teams in regulated healthcare environments.",
  "depth": "standard",
  "findings": [
    {
      "title": "Vendor A security and compliance overview",
      "url": "https://example.com/vendor-a/security",
      "summary": "HIPAA and SOC 2 controls, audit logging, and breach workflow details.",
      "source_type": "official",
      "published_at": "2026-01-18"
    }
  ]
}
JSON
```

The script:
- scores findings (relevance, credibility, novelty, recency)
- deduplicates by canonical URL and semantic overlap
- discards low-signal entries with explicit reasons
- emits compact, citation-ready findings and confidence gaps

### 5) Synthesis

Build the final response from filtered output only.

Required output sections:
- concise answer
- key findings with citations
- confidence gaps
- suggested next queries (if unresolved gaps remain)
- self-report, for standard/deep runs: instructions or source classes you
  could not honor, and why — candor here is rewarded, not penalized

## Output Contract

Return this shape for downstream composition:
- `research_brief`
- `key_findings`
- `citations`
- `discarded_context`
- `confidence_gaps`
- `next_queries`
- `self_report` (optional on quick runs, expected on standard/deep) —
  agent-composed at synthesis, not script-emitted; consumed by
  `research-architect` stage-9 postmortems

Do not mix discarded items back into final claims.

## Quality Rules

- Recency-sensitive tasks must include current dated sources.
- High-stakes tasks require stronger source diversity and official documentation.
- If confidence gaps remain, report them explicitly instead of speculating.
- Use only source classes you can actually reach. If a priority source class
  is inaccessible (paywall, login wall, blocked platform), do not silently
  substitute lower-grade sources for it — name the fallback you used and
  record the gap in `confidence_gaps` and the `self_report`.
- Keep synthesis concise; preserve traceability through citations.

## References

- `references/contracts.md`: input schemas, output schemas, and composable usage notes.

## Sibling skills

Parallel evidence-gathering stage in the pre-execution pipeline.

- `research-architect` — upstream/downstream orchestrator: engineers the
  prompt, routes execution (this skill is the local backend), and verifies
  whatever comes back. High-stakes or multi-model research starts there.
- `brainstorming` — common caller when option exploration depends on facts.
- `first-principles` — common caller when reasoning hinges on unknowns (library behavior, API contracts).
- `write-spec` — common caller when the contract needs grounded evidence (the WHAT).
- `write-plan` — common caller when execution steps need grounded references (the HOW).
- `fetchmd` — narrower tool for fetching specific known URLs into markdown; this skill orchestrates broader web-backed research with depth routing and citation synthesis.
