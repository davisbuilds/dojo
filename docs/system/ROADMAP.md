# Skills Roadmap

Actionable improvement backlog for the skills catalog. Extracted from the [skills analysis](../skills-analysis-2026-3-07.md) (2026-03-07), updated 2026-03-08.

## Cross-Cutting Findings

### Verbosity Issues

| Skill | Status | Notes |
|-------|--------|-------|
| ~~obsidian-bases~~ | Done | 678→259 lines, function catalog extracted to `references/functions.md` |
| ~~obsidian-markdown~~ | Done | 647→284 lines, removed standard Markdown syntax |
| ~~compound-docs~~ | Done | 527→119 lines, stripped XML ceremony and redundant sections |
| ~~obsidian-canvas~~ | Done | 675→192 lines, examples extracted to `references/examples.md` |
| first-principles | Open | ~200 lines of abstract methodology without concrete examples |
| agent-native-architecture | Open | 14 reference files -- some overlap between architecture-patterns.md and agent-execution-patterns.md |

### Overly Strict Language

| Skill | Example | Status |
|-------|---------|--------|
| ~~compound-docs~~ | "STRICT ENFORCEMENT", 7-step mandatory workflow | Done -- rewritten without XML ceremony |
| verify-before-complete | "Iron Law", "NEVER claim completion" | Keep -- appropriate for its purpose |
| brainstorming | "MUST use this before any creative work" | Open -- too broad for simple changes |
| autonomous-engineering | Chains 7+ skills sequentially | Open -- fragile, one failure cascades |

**Guidance:** Use "should" over "MUST" for advisory skills; reserve "MUST" for safety-critical behaviors.

### Gaps and Missing Skills

| Gap | Description | Suggested Skill |
|-----|-------------|----------------|
| Testing | No skill for test strategy, test generation, or coverage analysis | `test-strategy` |
| Database | No skill for schema design, migration planning, or query optimization | `db-design` |
| API Design | No skill for REST/GraphQL API design patterns | `api-design` |
| Documentation | No skill for README generation, API docs, or changelog management | `docs-generator` |
| Accessibility | Mentioned in web-design-guidelines but no dedicated skill | `a11y-audit` |
| Performance Profiling | vercel-react-best-practices covers React perf but no general profiling | `perf-profiler` |
| Dependency Management | No skill for auditing, updating, or managing dependencies | `dep-audit` |

### Duplicate/Overlapping Concerns

1. **gh-fix-issue + gh-triage-issues**: Both bundle `fetch_issue.sh` separately. Should share a common script.
2. **gpt-imagen + gemini-imagen**: Same workflow pattern with different APIs. Could share a common skill layer with provider-specific scripts.
3. **code-review-agents**: dhh-rails-reviewer and kieran-rails-reviewer overlap in domain. Consider merging or clearly differentiating.
4. **vercel-deploy + vercel-preview-logs**: Could be one skill with deploy + diagnose commands.
5. **obsidian-markdown + obsidian-bases + obsidian-canvas**: Three separate reference skills. Already trimmed and disambiguated; merging is low priority since trigger routing works (f1 1.00 for all three).

### Resource Distribution

| Resource Type | Count | Skills With | Skills Without |
|---------------|-------|-------------|----------------|
| Scripts | 30+ | 16 skills | 28 skills |
| References | 40+ | 20 skills | 24 skills |
| Templates/Assets | 20+ | 11 skills | 33 skills |
| Commands | 15+ | 10 skills | 34 skills |

Many skills are instruction-only with no supporting resources. The highest-rated skills consistently have scripts, references, and templates.

## Priority Improvements

### High Impact

1. ~~**Add engineering principles to first-principles**~~ -- Done, added YAGNI/KISS/DRY/SOLID lenses and tension resolution table
2. ~~**Add test strategy skill**~~ -- Done, see `test-strategy`
3. **Merge Vercel deploy skills** -- Combine vercel-deploy and vercel-preview-logs into one skill with deploy + diagnose commands
4. ~~**Deduplicate fetch_issue.sh**~~ -- Done, unified to `scripts/fetch_issue.sh` with symlinks

### Medium Impact

5. **Bring gemini-imagen to parity with gpt-imagen** -- Add sample prompts, use-case taxonomy
6. **Add auto-detection to code-review-agents** -- Select relevant reviewers based on tech stack
7. **Bundle guidelines in web-design-guidelines** -- Don't depend on external URL fetch
8. ~~**Upgrade template**~~ -- Done, added commented guidance for all contract sections + authoring checklist
9. ~~**Soften brainstorming language**~~ -- Done, XML hard-gate removed, boundaries added

### Low Impact

10. **Add caching to deep-research** -- Avoid re-researching previously answered questions
11. **Add rule testing to hookify** -- Let users validate rules before activation
12. **Add example plans to writing-plans** -- Show what good plans look like
13. **Consolidate agent-native-architecture references** -- Reduce overlap between architecture-patterns.md and agent-execution-patterns.md
14. **LLM-based trigger scoring** -- Add semantic scoring tier for the 10 accepted lexical-limit pairs

## Completed

| Item | What Changed |
|------|-------------|
| Trim Obsidian skills | obsidian-markdown 647→284, obsidian-bases 678→259, obsidian-canvas 675→192 |
| Soften compound-docs | 527→119 lines, removed XML tags and redundant sections |
| Strict contract enforcement | 45/45 pass, 0 warnings, CI enforces full catalog |
| Trigger collision fixes | 78.6%→92.9%, discriminating name tokens, expanded stopwords |
| Expanded trigger fixtures | 12→34 cases across 12 skill clusters |
| Rescore all skills | 23 skills bumped, 1 new entry (skill-evals), measured evidence |
| Rename json-canvas | → obsidian-canvas, updated all references |
| Extract system docs | Best practices, roadmap, contract extracted from analysis doc |
| Add test-strategy skill | Methodology skill with verification checklist, 45th skill |
| Soften brainstorming | Removed XML hard-gate, added Boundaries/Verification/Resources |
| Enhance first-principles | Added engineering principles, tension resolution table, verification (110→141 lines) |
| Deduplicate fetch_issue.sh | Unified to `scripts/fetch_issue.sh`, symlinked from both skills |
| Upgrade template | Commented scaffold with all contract sections + authoring checklist (35→78 lines) |
