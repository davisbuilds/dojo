## 3.0.0 - 2026-07-12

- Replace self-declared credibility scoring with URL-derived hostname policy
  from a conservative, explainable registry.
- Treat `source_type` only as a known-domain tiebreaker or an unknown-domain
  downgrade; it can no longer promote an unknown host above neutral.
- Derive hostnames from URLs instead of trusting caller-supplied `domain`, and
  emit registry, authority, document-class, consistency, and rationale fields.
- Seed exact rules for scholarly repositories/publishers and selected
  university repository, research-center, news, and root hosts; keep unlisted
  university subdomains neutral.

## 2.0.0

- Narrow trigger semantics to direct, answer-seeking web research
  (stakes-based split): prompt engineering, commissioning multi-model or
  external deep-research runs, and report verification now route to
  `research-architect`, with this skill as its local execution backend.
- Add `research-architect` to sibling skills and to the skip list.
- Add accessibility-honesty quality rule: never silently substitute
  lower-grade sources for an unreachable priority source class; record the
  gap instead.
- Add `self_report` to the output contract (optional on quick runs, expected
  on standard/deep) — agent-composed at synthesis, feeds research-architect
  postmortems.
