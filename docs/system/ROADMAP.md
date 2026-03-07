# Skills Roadmap

Actionable improvement backlog for the skills catalog. Extracted from the [skills analysis](../skills-analysis-2026-3-07.md) (2026-03-07).

## Cross-Cutting Findings

### Verbosity Issues

| Skill | Lines | Problem |
|-------|-------|---------|
| obsidian-bases | 652 | Function catalog belongs in external docs, not context window |
| obsidian-markdown | 621 | Standard Markdown syntax is redundant -- agent already knows it |
| first-principles | ~200 | Abstract methodology without concrete examples |
| compound-docs | ~150 | 7-step process with redundant validation gates |
| agent-native-architecture | 14 refs | Reference sprawl -- some files overlap |

**Recommendation:** The Obsidian skills together consume ~1,300 lines of context for what is essentially syntax reference. Trim to Obsidian-specific extensions only and cut 60%+ of content.

### Overly Strict Language

| Skill | Example | Impact |
|-------|---------|--------|
| compound-docs | "STRICT ENFORCEMENT", 7-step mandatory workflow | Discourages casual documentation |
| verify-before-complete | "Iron Law", "NEVER claim completion" | Appropriate for its purpose |
| brainstorming | "MUST use this before any creative work" | Too broad -- simple changes don't need brainstorming |
| autonomous-engineering | Chains 7+ skills sequentially | Fragile -- one failure cascades |

**Recommendation:** Use "should" over "MUST" for advisory skills; reserve "MUST" for safety-critical behaviors.

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
5. **obsidian-markdown + obsidian-bases + json-canvas**: Three Obsidian-related reference skills. Could consolidate into one `obsidian` skill.

### Resource Distribution

| Resource Type | Count | Skills With | Skills Without |
|---------------|-------|-------------|----------------|
| Scripts | 30+ | 16 skills | 28 skills |
| References | 40+ | 18 skills | 26 skills |
| Templates/Assets | 20+ | 11 skills | 33 skills |
| Commands | 15+ | 10 skills | 34 skills |

Many skills are instruction-only with no supporting resources. The highest-rated skills consistently have scripts, references, and templates.

## Priority Improvements

### High Impact

1. **Trim Obsidian skills** -- Cut 60%+ of obsidian-markdown and obsidian-bases by removing standard syntax the agent already knows
2. **Add worked examples to first-principles** -- Transform from abstract methodology to concrete decision tool
3. **Merge Vercel deploy skills** -- Combine vercel-deploy and vercel-preview-logs
4. **Add test strategy skill** -- Most common gap across all projects
5. **Deduplicate fetch_issue.sh** -- Share between gh-fix-issue and gh-triage-issues

### Medium Impact

6. **Soften compound-docs enforcement** -- Reduce 7 steps to 4, soften mandatory language
7. **Bring gemini-imagen to parity with gpt-imagen** -- Add sample prompts, use-case taxonomy
8. **Add auto-detection to code-review-agents** -- Select relevant reviewers based on tech stack
9. **Bundle guidelines in web-design-guidelines** -- Don't depend on external URL fetch
10. **Upgrade template** -- Add commented examples and variant templates

### Low Impact

11. **Add caching to deep-research** -- Avoid re-researching previously answered questions
12. **Add rule testing to hookify** -- Let users validate rules before activation
13. **Add example plans to writing-plans** -- Show what good plans look like
14. **Merge Obsidian skills** -- One `obsidian` skill with markdown, bases, and canvas sub-references
