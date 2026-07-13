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
