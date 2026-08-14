## 2.3.3 - 2026-08-14

- Anchor runnable script commands to <skill-dir> so they resolve outside a dojo checkout

## 2.3.2 - 2026-08-01

- Trim internal depth/filtering mechanics from the description; triggers and research-architect hand-off unchanged.

## 2.3.1 - 2026-07-31

- Trim the description from 558 to 370 chars by removing the tier-routing and packet-contents detail. The research-architect routing note is preserved verbatim.

## 2.3.0 - 2026-07-27

- Recognize verified first-party model, harness, protocol, and agent-framework documentation through owned root/subdomain rules; retain relevant priority sources below the aggregate score threshold with an explicit advisory, independent of missing or mismatched caller source-type labels.

## 2.2.0 - 2026-07-24

- Credibility registry gains on-chain explorers (Etherscan/Polygonscan/Basescan/Arbiscan), Dune, and code hosts (GitHub, raw.githubusercontent, GitLab) with ceilings reflecting what each class can establish; previously these landed as unknown domains at the neutral floor, biasing market and tooling research against its own primary sources. Documents that registry credibility is a reliability prior only, not a currency signal.

## 2.1.0 - 2026-07-12

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
