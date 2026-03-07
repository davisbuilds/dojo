# Skills Analysis (2026-03-07)

Comprehensive analysis of all 44 skills in `dojo/skills/`. Each skill is rated 1-10 across multiple dimensions, with specific findings on verbosity, gaps, and improvement areas.

## Scoring Criteria

| Dimension | Weight | What It Measures |
|-----------|--------|-----------------|
| Instruction Quality | 25% | Clarity, structure, actionability of SKILL.md |
| Resource Bundling | 20% | Scripts, references, assets, templates |
| Trigger Design | 15% | Description accuracy, activation specificity |
| Edge Case Handling | 15% | Error paths, fallbacks, boundary conditions |
| Practical Utility | 15% | Real-world value, frequency of use |
| Conciseness | 10% | Signal-to-noise ratio, context window efficiency |

---

## Rankings Overview

| Rank | Skill | Score | Tier | Category |
|------|-------|-------|------|----------|
| 1 | vercel-react-best-practices | 9.5 | S | Knowledge |
| 2 | vercel-react-native-skills | 9.5 | S | Knowledge |
| 3 | code-review-agents | 9 | S | Multi-Agent |
| 4 | skill-creator | 9 | S | Meta/Process |
| 5 | gpt-imagen | 9 | S | Tool |
| 6 | agent-native-architecture | 9 | S | Knowledge |
| 7 | secure-code | 8.5 | A | Security |
| 8 | audit-skill | 8.5 | A | Security |
| 9 | hookify | 8.5 | A | Tool |
| 10 | deep-research | 8.5 | A | Workflow |
| 11 | frontend-design | 8 | A | Creative |
| 12 | gh-triage-issues | 8 | A | GitHub |
| 13 | gh-review-pr | 8 | A | GitHub |
| 14 | verify-before-complete | 8 | A | Behavioral |
| 15 | algorithmic-art | 8 | A | Creative |
| 16 | vercel-composition-patterns | 8 | A | Knowledge |
| 17 | writing-plans | 7.5 | B | Process |
| 18 | brainstorming | 7.5 | B | Process |
| 19 | gh-fix-issue | 7 | B | GitHub |
| 20 | compound-docs | 7 | B | Process |
| 21 | playwright | 7 | B | Tool |
| 22 | create-cli | 7 | B | Design |
| 23 | compact-session | 7 | B | Process |
| 24 | gh-commit-push-pr | 7 | B | GitHub |
| 25 | skill-standardizer | 7 | B | Meta |
| 26 | theme-factory | 7 | B | Creative |
| 27 | obsidian-markdown | 6.5 | B | Knowledge |
| 28 | obsidian-bases | 6.5 | B | Knowledge |
| 29 | json-canvas | 6.5 | B | Knowledge |
| 30 | local-review | 6.5 | B | Workflow |
| 31 | autonomous-engineering | 6.5 | B | Workflow |
| 32 | screenshot | 6.5 | B | Tool |
| 33 | gemini-imagen | 6 | C | Tool |
| 34 | session-retro | 6 | C | Process |
| 35 | skill-installer | 6 | C | Meta |
| 36 | vercel-deploy | 6 | C | DevOps |
| 37 | vercel-preview-logs | 6 | C | DevOps |
| 38 | web-design-guidelines | 5.5 | C | Knowledge |
| 39 | fetchmd | 5 | C | Utility |
| 40 | markdown-converter | 5 | C | Utility |
| 41 | find-skills | 5 | C | Meta |
| 42 | first-principles | 4.5 | D | Behavioral |
| 43 | template | 2 | D | Meta |

**Note:** Rankings above reflect the pre-implementation snapshot from 2026-03-07. Post-analysis implementation updates are tracked in the revision section at the end of this document.

---

## Tier S (9-10): Best-in-Class

### vercel-react-best-practices -- 9.5/10
**Files:** 59 | **Category:** Knowledge

57 individually-filed rules across 8 categories (async/waterfalls, bundle optimization, server-side, client-side, re-renders, rendering, JS performance, advanced patterns). Each rule has incorrect/correct examples with impact metrics. The AGENTS.md is ~800 lines of well-organized, priority-ranked guidance.

- **Strengths:** Highest rule density of any skill. Every rule is self-contained with before/after code. Priority tiers (CRITICAL > HIGH > MEDIUM > LOW) make it actionable. Covers the full React/Next.js performance surface.
- **Weaknesses:** No scripts for automated detection. No integration with linting tools. The sheer volume (59 files) is a lot of context if loaded entirely.
- **Verbosity:** Appropriate -- each rule file is focused and concise.
- **Gaps:** Could benefit from a `scripts/detect_violations.py` that scans for anti-patterns.

### vercel-react-native-skills -- 9.5/10
**Files:** 39 | **Category:** Knowledge

37 rules covering list performance, animation, navigation, UI patterns, state management, rendering, monorepo config, and design systems. Same high-quality before/after pattern as the web counterpart.

- **Strengths:** Comprehensive mobile coverage. FlashList/LegendList guidance is practical and current. GPU-animation rules prevent common perf traps. React Compiler compatibility rules are forward-looking.
- **Weaknesses:** Slightly less comprehensive than the web version. Some rules are very short (2-3 lines of guidance).
- **Gaps:** No Expo Router-specific rules. No testing patterns for React Native.

### code-review-agents -- 9/10
**Files:** 20 | **Category:** Multi-Agent

16 specialized review agents covering architecture, language-specific conventions (Rails, Python, TypeScript), data integrity, migrations, schema drift, performance, security, frontend race conditions, code simplicity, and deployment verification. Plus `/agent-native-audit` orchestration and `/heal-skill` repair command.

- **Strengths:** Broadest agent coverage of any skill. Each agent has a clear, non-overlapping concern. The orchestration command runs 8 agents in parallel with scored principles. Domain-specific agents (schema-drift-detector, data-migration-expert) are genuinely novel.
- **Weaknesses:** Heavy -- 20 files is a lot to load. Some agents (dhh-rails-reviewer, kieran-rails-reviewer) overlap in domain. No mechanism to select only relevant agents for a given codebase.
- **Gaps:** No front-end-specific reviewer beyond race conditions (e.g., accessibility, responsive design). No auto-detection of which agents are relevant based on project tech stack.

### skill-creator -- 9/10
**Files:** 9 | **Category:** Meta/Process

The meta-skill. 4 scripts (init, validate, package, generate OpenAI YAML), 3 reference docs (output patterns, workflows, OpenAI metadata). Clear 6-step creation process with progressive disclosure.

- **Strengths:** End-to-end workflow from ideation to distribution. The validator is real and enforced by hooks. Reference docs cover workflow and output patterns well.
- **Weaknesses:** No example skills bundled. `init_skill.py` creates placeholders but doesn't scaffold meaningful content.
- **Gaps:** A `--type` flag for different skill archetypes (workflow, knowledge, tool) would accelerate creation.

### gpt-imagen -- 9/10
**Files:** 12 | **Category:** Tool

Comprehensive image generation/editing via OpenAI API. Decision tree (generate vs. edit vs. batch), structured prompt augmentation, use-case taxonomy (8 generate types + 8 edit types), 50+ sample prompts, CLI reference, prompting best practices.

- **Strengths:** Most thoroughly documented tool skill. The sample-prompts.md is immediately usable. Use-case taxonomy prevents generic prompting. Draft-iterate-final workflow is well-structured.
- **Weaknesses:** Depends on external API key. The `codex-network.md` reference suggests environment-specific friction.
- **Gaps:** No local/offline fallback. No cost estimation guidance.

### agent-native-architecture -- 9/10
**Files:** 16 | **Category:** Knowledge

14 reference documents covering agent architecture from first principles. Core concepts: Parity, Granularity, Composability, Emergent Capability, Improvement Over Time. Covers MCP tool design, system prompt design, self-modification, mobile patterns, and refactoring guides.

- **Strengths:** Deepest conceptual skill in the repo. Reference docs are individually high-quality and well-cross-referenced. Addresses a genuinely novel domain (agent-native design) with rigorous thinking.
- **Weaknesses:** Heavy reading load -- 14 reference files is substantial. No scripts or automation. Purely advisory.
- **Verbosity:** Some reference files could be condensed. `architecture-patterns.md` and `agent-execution-patterns.md` have overlapping concepts.
- **Gaps:** No validation tool to check if a codebase follows agent-native principles. No starter templates.

---

## Tier A (8-8.5): Strong

### secure-code -- 8.5/10
**Files:** 11 | **Category:** Security

Semgrep-based SAST scanning with two commands: `/scan` (standard security scan) and `/trifecta-check` (detects co-occurrence of private data + untrusted input + external comms). Includes setup script, finding parser, custom Semgrep rules, and remediation guides.

- **Strengths:** The "lethal trifecta" concept is original and well-explained with real-world exploit examples. Remediation guide covers 10+ vulnerability classes. Custom Semgrep rule authoring reference is practical.
- **Weaknesses:** Requires semgrep installation. Python scripts add dependency overhead.
- **Gaps:** No CI integration example. No language-specific rule sets beyond the trifecta.

### audit-skill -- 8.5/10
**Files:** 13 | **Category:** Security

Three-layer deterministic security audit: structural validation (25%), instruction scanning for prompt injection/exfiltration (35%), and code analysis with SAST (40%). Produces A-F trust scores.

- **Strengths:** Unique and valuable -- no other skill audits other skills. Three-layer architecture is well-designed. Scoring weights are thoughtful. Offline-only (no cloud APIs).
- **Weaknesses:** Pass condition (score >= 70, no CRITICAL) could be too lenient for high-security contexts. Python dependencies required.
- **Gaps:** No remediation automation (just reports findings). No integration with skill-creator pipeline.

### hookify -- 8.5/10
**Files:** 20 | **Category:** Tool

Dynamic guard rails from markdown rule files. Harness-agnostic (Claude Code, Agents SDK, generic stdin/stdout). 4 example rules, 4 commands, conversation analyzer agent, writing rules reference.

- **Strengths:** Genuinely novel concept -- guard rails as markdown files. No restart needed for rule changes. Example rules are practical (dangerous rm, sensitive files, require tests). The conversation-analyzer agent for discovering needed hooks is clever.
- **Weaknesses:** 20 files is heavy for what is conceptually simple. The writing-rules reference could be condensed.
- **Verbosity:** The SKILL.md is well-structured but the supporting material is spread across many small files.
- **Gaps:** No rule testing framework. No built-in rule library beyond 4 examples.

### deep-research -- 8.5/10
**Files:** 10 | **Category:** Workflow

Web research with tiered depth (quick: 3-6 searches, standard: 8-20, deep: 20-80). Deterministic filtering via Python scripts scoring relevance/credibility/novelty/recency. Structured output with citations, confidence gaps, and next queries.

- **Strengths:** The depth routing is smart -- avoids over-researching simple questions. Evidence filtering with deduplication is rigorous. Output format with "discarded context" and "confidence gaps" is unusually thoughtful.
- **Weaknesses:** Python dependencies. The filtering heuristics may need tuning per domain.
- **Gaps:** No caching of previous research. No domain-specific tuning profiles.

### frontend-design -- 8/10
**Files:** 10 | **Category:** Creative

*Significantly improved since the previous analysis (was 6/10).* Now includes font pairings reference (11 pairings by aesthetic), color palettes (11 palettes with CSS vars), anti-patterns catalog ("AI slop" gallery), 4 component templates (brutalist hero, editorial hero, asymmetric cards, minimal nav), and a scaffold script.

- **Strengths:** The anti-patterns reference is the strongest piece -- explicitly names and corrects common AI design mistakes. Font pairings organized by aesthetic direction (brutalist, luxury, playful, etc.) are immediately actionable. Component templates provide concrete starting points.
- **Weaknesses:** Only 4 component templates. The scaffold script is Python but most frontend work is JS/TS.
- **Gaps:** No dark mode guidance. No responsive design patterns. No accessibility checklist integration.

### gh-triage-issues -- 8/10
**Files:** 5 | **Category:** GitHub

3 scripts (fetch issue, find duplicates, list labels), batch mode, 11-step workflow with priority assessment. Handles security issues, first-time contributors, and contentious issues.

- **Strengths:** Best GitHub skill. Duplicate detection is smart. Batch mode for bulk triage is practical. Priority signals are concrete.
- **Weaknesses:** No labeling taxonomy reference.
- **Gaps:** No integration with project boards or milestones.

### gh-review-pr -- 8/10
**Files:** 3 | **Category:** GitHub

Structured review workflow with fetch script pulling metadata, CI status, reviews, and diff. Analysis covers code quality, security, style, and architecture.

- **Strengths:** The APPROVE/REQUEST_CHANGES/COMMENT decision framework is clear. Depth adapts to PR size.
- **Weaknesses:** No security checklist reference. No automated metrics.
- **Gaps:** Could integrate with secure-code skill for automated SAST on PR diffs.

### verify-before-complete -- 8/10
**Files:** 1 | **Category:** Behavioral

Pure instruction skill -- no scripts or assets. Enforces evidence-based completion claims with verification levels (quick/standard/high-risk), freshness rules, and anti-patterns list.

- **Strengths:** The only skill that fundamentally changes agent behavior. Well-crafted failure tables and rationalization prevention. Drawn from real failure patterns.
- **Weaknesses:** No automation to enforce compliance. Relies entirely on the agent following instructions.
- **Gaps:** A verification script that auto-detects project type and suggests commands would make this more concrete.

### algorithmic-art -- 8/10
**Files:** 3 | **Category:** Creative

Two-phase creative process: philosophical manifesto then p5.js implementation. Templates for interactive viewer with parameter controls and seed navigation.

- **Strengths:** The creative philosophy is distinctive. Seeded randomness ensures reproducibility. Viewer template is production-quality.
- **Weaknesses:** Only p5.js -- no other creative frameworks. No example gallery.
- **Gaps:** Could include style-specific templates (particle systems, L-systems, cellular automata).

### vercel-composition-patterns -- 8/10
**Files:** 10 | **Category:** Knowledge

8 rules across 4 categories: Component Architecture, State Management, Implementation Patterns, React 19 APIs. Focuses on avoiding boolean prop proliferation through composition.

- **Strengths:** Practical, opinionated, and current (includes React 19 changes). Each rule has clear before/after examples. The boolean-props-to-composition refactoring guidance is widely applicable.
- **Weaknesses:** Narrower scope than the other Vercel skills. Only 8 rules.
- **Gaps:** No compound component starter templates. No migration guide from class-based patterns.

---

## Tier B (6.5-7.5): Solid

### writing-plans -- 7.5/10
Implementation plans with YAML frontmatter, 10-30 minute task granularity, verification commands per task, and validation script. Routes to brainstorming or first-principles when requirements are unclear.

- **Strengths:** Validation script catches plan issues before handoff. Three handoff modes (execute, separate session, refine). Task granularity guidance is practical.
- **Weaknesses:** Template is somewhat rigid. No example plans bundled.
- **Gaps:** No integration with project management tools.

### brainstorming -- 7.5/10
4-phase process: assess clarity, understand intent (one question at a time), explore approaches, capture design summary. Hard-gate prevents premature implementation.

- **Strengths:** The one-question-at-a-time discipline prevents overwhelming users. Hard-gate on design approval is valuable. Skill coordination routing is smart.
- **Weaknesses:** No design document template despite recommending one be written.
- **Verbosity:** The platform-mapping reference adds complexity for uncertain value.
- **Gaps:** No question bank organized by domain.

### gh-fix-issue -- 7/10
10-step workflow from issue fetch to PR creation. Handles closed issues, existing PRs, fork-required repos.

- **Strengths:** End-to-end automation. Edge case handling is thorough.
- **Weaknesses:** Duplicates `fetch_issue.sh` with gh-triage-issues.
- **Gaps:** No PR template reference. No test auto-detection.

### compound-docs -- 7/10
Captures solved problems as categorized documentation with YAML frontmatter. 7-step workflow with enum-validated problem types.

- **Strengths:** Decision gates for promoting to critical patterns and skills are smart. YAML schema validation ensures consistency. Category-based filing aids retrieval.
- **Weaknesses:** Relatively heavy process for documenting a solution (7 steps). The enforcement language is very strict.
- **Verbosity:** Could be condensed -- the 7-step workflow has redundant validation steps.
- **Gaps:** No search/retrieval tooling for existing docs.

### playwright -- 7/10
CLI-first browser automation with wrapper script, CLI reference, and workflow guides.

- **Strengths:** Practical workflow guide (open > snapshot > interact > re-snapshot). Wrapper script handles environment setup.
- **Weaknesses:** Depends on npx availability. Guardrails section is brief.
- **Gaps:** No example test scripts. No integration with verify-before-complete for UI verification.

### create-cli -- 7/10
CLI surface area design before implementation. Excellent cli-guidelines.md reference condensed from clig.dev.

- **Strengths:** The guidelines reference is genuinely excellent (240 lines, 16 areas). Spec template is practical.
- **Weaknesses:** No example specs. No generation scripts.
- **Gaps:** Example specs would dramatically improve usability.

### compact-session -- 7/10
Session summaries with 9-section structure, template, and 2 examples.

- **Strengths:** Examples illustrate different session types. Section structure optimizes for resumability.
- **Weaknesses:** No auto-generation from git/conversation context.
- **Gaps:** More example types needed (refactoring, debugging, multi-day work).

### gh-commit-push-pr -- 7/10
*Improved since previous analysis (was 4/10).* Now has conventions reference (branch naming, commit format), PR templates (minimal/standard/detailed), and a prepare_commit script.

- **Strengths:** Three PR template tiers are practical. Branch naming conventions are clear.
- **Weaknesses:** Still relatively thin compared to other GitHub skills.
- **Gaps:** No error recovery guidance for push failures.

### skill-standardizer -- 7/10
Canonicalizes skills across repo, global, and local directories. Discovers, audits drift, and syncs with safety.

- **Strengths:** Solves a real problem (skill copy drift). 8+ drift types detected. Safe sync with backups.
- **Weaknesses:** Complex mental model (canonical vs. global vs. local). Scripts are Python-heavy.
- **Gaps:** No scheduled/automatic drift detection.

### theme-factory -- 7/10
10 curated themes with JSON + markdown definitions, CSS generation script, preview script, and HTML template.

- **Strengths:** *Improved since previous analysis* -- now has machine-readable JSON, CSS generation, and preview capabilities. PDF showcase is a nice touch.
- **Weaknesses:** Themes are visual-design focused but lack code framework integration.
- **Gaps:** No Tailwind CSS output. No dark/light mode variants per theme.

### obsidian-markdown -- 6.5/10
621-line comprehensive reference for Obsidian Flavored Markdown.

- **Strengths:** Exhaustive coverage of wikilinks, callouts, embeds, properties, Mermaid, and LaTeX.
- **Weaknesses:** Essentially a reference manual -- no workflows, scripts, or automation.
- **Verbosity:** **Overly verbose.** 621 lines is excessive for what is largely syntax documentation. Much of this duplicates what an agent already knows about Markdown. Could be cut to ~200 lines focusing only on Obsidian-specific extensions.
- **Gaps:** No templates for common note types. No linting or validation.

### obsidian-bases -- 6.5/10
652-line reference for Obsidian Bases (.base files) with 100+ function reference.

- **Strengths:** Complete schema documentation with 4 worked examples. The function reference is thorough.
- **Weaknesses:** Same issue as obsidian-markdown -- it's a reference manual, not a workflow.
- **Verbosity:** **Overly verbose.** 652 lines, with the function reference alone consuming hundreds of lines. Could be condensed significantly by focusing on the schema and linking to external docs for the function catalog.
- **Gaps:** No templates for common base configurations. No validation script.

### json-canvas -- 6.5/10
Complete spec for JSON Canvas files with 4 examples and validation rules.

- **Strengths:** Thorough specification. ID generation and layout guidelines are practical. Examples cover different use cases.
- **Weaknesses:** Another reference manual. No scripts or templates.
- **Verbosity:** Could be more concise by separating the spec from the examples.
- **Gaps:** No canvas generation script. No validation tool.

### local-review -- 6.5/10
Local code review without GitHub integration. Three modes (working, staged, branch).

- **Strengths:** Findings-first output structure. Risk analysis section. Multiple review targets.
- **Weaknesses:** The collect_review_context.sh script does the heavy lifting, but the SKILL.md could provide more review heuristics.
- **Gaps:** No integration with other review skills (code-review-agents, secure-code).

### autonomous-engineering -- 6.5/10
End-to-end feature development via `/lfg` (sequential) and `/slfg` (swarm/parallel).

- **Strengths:** Ambitious -- chains plan > deepen > implement > review > test > video. Swarm variant for parallel execution is novel.
- **Weaknesses:** Depends heavily on other skills existing and working. If any chained skill fails, the whole pipeline breaks.
- **Verbosity:** The README adds little beyond what the commands describe.
- **Gaps:** No error recovery or partial-completion handling. No progress tracking.

### screenshot -- 6.5/10
Cross-platform screenshot capture with macOS permission handling.

- **Strengths:** Thorough cross-platform coverage (macOS, Linux, Windows). Permission preflight for macOS is practical. Multiple capture modes (app, window, region).
- **Weaknesses:** Heavy script count (5 scripts) for a simple capability. Most agents already have screenshot tools.
- **Gaps:** No image annotation or comparison capabilities.

---

## Tier C (5-6): Adequate

### gemini-imagen -- 6/10
Image generation via Google Gemini API with 3 subcommands and resolution tiers.

- **Strengths:** Resolution tier system (1K/2K/4K). Prompt template structure.
- **Weaknesses:** Much thinner than gpt-imagen. Only 3 files vs. gpt-imagen's 12. No sample prompts reference. No use-case taxonomy.
- **Gaps:** Feels like a stripped-down gpt-imagen. Could be merged or brought to parity.

### session-retro -- 6/10
Updates AGENTS.md/CLAUDE.md with session learnings. Max 5 learnings, append-only, requires approval.

- **Strengths:** Strict filtering criteria (what qualifies vs. doesn't). One-line-per-learning constraint prevents bloat. Approval gate prevents unwanted changes.
- **Weaknesses:** Very simple -- 57 lines of instruction, no scripts or templates.
- **Gaps:** No auto-detection of learnable moments. No deduplication against existing docs.

### skill-installer -- 6/10
Installs skills from GitHub or curated lists into Codex/Claude directories.

- **Strengths:** Supports both curated and experimental skill lists. Fallback from download to git sparse checkout.
- **Weaknesses:** Depends on external GitHub infrastructure. No validation after install.
- **Gaps:** No update/upgrade mechanism. No dependency resolution between skills.

### vercel-deploy -- 6/10
Deploy to Vercel with preview by default, production on request.

- **Strengths:** Simple and focused. Fallback script for auth issues.
- **Weaknesses:** Thin -- most of the value is just running `vercel deploy`. The skill adds limited value beyond CLI documentation.
- **Gaps:** No rollback guidance. No environment variable management. No build configuration help.

### vercel-preview-logs -- 6/10
Inspect Vercel preview deployments for failures with root cause analysis.

- **Strengths:** Specific failure diagnosis priority (compile > env/config > runtime). Safe CLI wrapper.
- **Weaknesses:** Narrow scope. Only useful when Vercel deployments fail.
- **Gaps:** Could be merged with vercel-deploy as a single Vercel skill.

### web-design-guidelines -- 5.5/10
Fetches Web Interface Guidelines from vercel-labs and checks UI files.

- **Strengths:** Fetches fresh guidelines at review time.
- **Weaknesses:** Depends entirely on an external URL being available. No cached/bundled fallback. Very thin instructions.
- **Verbosity:** Too terse -- the opposite problem. Barely explains what guidelines are checked.
- **Gaps:** No bundled guidelines. No example output. No integration with frontend-design skill.

### fetchmd -- 5/10
Webpage-to-markdown converter via npx.

- **Strengths:** Lists features and options clearly.
- **Weaknesses:** Thin wrapper around an npm package. Minimal value-add beyond `npx @davisbuilds/fetchmd --help`.
- **Gaps:** No example workflows. No integration with deep-research.

### markdown-converter -- 5/10
Document-to-markdown via `uvx markitdown`.

- **Strengths:** Lists supported formats clearly.
- **Weaknesses:** Thin wrapper around an existing tool. Minimal value-add.
- **Gaps:** No format-specific tips. No batch conversion guidance. No error handling.

### find-skills -- 5/10
Discovers and installs skills via `npx skills`.

- **Strengths:** Lists common skill categories with example queries.
- **Weaknesses:** Thin wrapper around `npx skills`. The 4-step workflow is generic.
- **Gaps:** No curation or recommendation logic. No compatibility checking.

### first-principles -- 4.5/10
First-principles reasoning framework with self-check gate, epistemic framework, and decision matrix.

- **Strengths:** The epistemic framework (assumptions, confidence, knowledge boundaries) is conceptually sound.
- **Weaknesses:** **Overly verbose and prescriptive.** The instructions read like an academic methodology paper rather than actionable agent guidance. Phrases like "Epistemic framework", "calibrate confidence", "distinguish correlation from causation" are abstract without concrete examples. The decision matrix maps task types to analysis levels but doesn't show what the output should look like.
- **Verbosity:** High. The skill tries to change how the agent thinks rather than what it does, which is hard to enforce through instruction alone.
- **Gaps:** No worked examples showing the framework applied to a real decision. No templates for trade-off analysis or decision documents. Compare to writing-plans which has a template and validator -- this skill has neither.

### template -- 2/10
Minimal placeholder with frontmatter skeleton only.

- **Strengths:** Exists as a starting point.
- **Weaknesses:** 7 lines. Provides nothing beyond what init_skill.py generates.
- **Gaps:** Should include commented examples of each section, or variant templates by skill type.

---

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

**Recommendation:** Compound-docs and brainstorming should soften their language. A skill that demands strict compliance for every interaction creates friction. Use "should" over "MUST" for advisory skills; reserve "MUST" for safety-critical behaviors.

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
| Vercel Consolidation | vercel-deploy + vercel-preview-logs could merge | Single `vercel` skill |
| Image Gen Consolidation | gpt-imagen + gemini-imagen have overlapping patterns | Shared prompt/workflow layer |

### Duplicate/Overlapping Concerns

1. **gh-fix-issue + gh-triage-issues**: Both bundle `fetch_issue.sh` separately. Should share a common script.
2. **gpt-imagen + gemini-imagen**: Same workflow pattern (generate/edit, resolution tiers, prompt structure) with different APIs. Could share a common skill layer with provider-specific scripts.
3. **code-review-agents**: dhh-rails-reviewer and kieran-rails-reviewer overlap in domain. Consider merging or clearly differentiating (philosophy vs. patterns).
4. **vercel-deploy + vercel-preview-logs**: Could be one skill with deploy + diagnose commands.
5. **obsidian-markdown + obsidian-bases + json-canvas**: Three Obsidian-related reference skills. Could consolidate into one `obsidian` skill with sub-references.

### Resource Distribution

| Resource Type | Count | Skills With | Skills Without |
|---------------|-------|-------------|----------------|
| Scripts | 30+ | 16 skills | 28 skills |
| References | 40+ | 18 skills | 26 skills |
| Templates/Assets | 20+ | 11 skills | 33 skills |
| Commands | 15+ | 10 skills | 34 skills |

Many skills are instruction-only with no supporting resources. The highest-rated skills consistently have scripts, references, and templates.

### Quality Trends Since Previous Analysis

| Skill | Previous Score | Current Score | Change | Notes |
|-------|---------------|---------------|--------|-------|
| frontend-design | 6/10 | 8/10 | +2 | Added font pairings, color palettes, anti-patterns, component templates |
| gh-commit-push-pr | 4/10 | 7/10 | +3 | Added conventions, PR templates, prepare_commit script |
| theme-factory | 7/10 | 7/10 | 0 | Added JSON + scripts (matching previous recommendations) |
| brainstorming | 6/10 | 7.5/10 | +1.5 | Added platform mapping, improved routing |

The improvements directly match recommendations from the previous analysis, validating the feedback loop.

---

## Priority Improvements

### High Impact (address first)

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

---

## External Research Addendum (2026-03-07)

This addendum incorporates web-backed findings using the `deep-research` workflow (standard depth routing, scored/deduplicated evidence filtering), with a focus on **recent (2025-2026)** guidance and relevant arXiv literature.

### Research Brief

Identify current best practices and power-user patterns for AI agent skills (skill files, trigger design, resource bundling, orchestration), prioritizing 2025-2026 sources and supplementing with arXiv literature.

### Key Findings (Filtered Packet)

1. **Progressive disclosure + narrow scope are now converging norms**  
   OpenAI and Anthropic both formalize metadata-first loading with on-demand resource expansion, and both stress single-purpose, composable skills over broad "do-everything" bundles [1][6][9].

2. **Trigger quality is a first-class quality dimension, not a docs nicety**  
   Recent guidance emphasizes routing-style descriptions, explicit "not for" boundaries, and negative trigger examples to reduce false activations and skill collision [1][3][6][10].

3. **Eval-driven skill development is becoming the default for mature teams**  
   The strongest recent pattern is to treat skill behavior as testable: explicit/implicit/contextual trigger tests, negative controls (`should_trigger=false`), and regression tracking across traces/artifacts [4][6].

4. **Power-user pattern: deterministic vs opportunistic invocation should be explicit**  
   For high-stakes or pipeline-critical work, explicit skill invocation is recommended for determinism; for discovery-heavy workflows, implicit routing can remain enabled [1][3].

5. **Long-running agent workflows need operational scaffolding, not just better prompts**  
   The newest power-user playbooks prioritize container/session reuse, compaction checkpoints, artifact handoff conventions, and network/security constraints [3].

6. **Org-level adoption depends on governance of instruction files**  
   Instruction/skill docs are most effective when versioned in-repo, included in onboarding, and treated as governed operational assets (not ad-hoc local notes) [7].

7. **Literature trend supports skill libraries and abstraction layers, but evaluation maturity is still uneven**  
   Recent preprints point to gains from iterative skill discovery and polymorphic abstraction, while ecosystem-scale benchmarking is still emerging and security/performance ceilings remain visible [2][5][8][11].

### Implications for This Analysis

- The original report correctly emphasized **conciseness**, but external evidence suggests moving from a generic "trim verbosity" rule to a **hard design contract**:
  - single responsibility
  - explicit trigger boundary
  - negative trigger examples
  - measurable eval checks
- "Instruction-only skills" are not inherently weak; they become weak when they lack:
  - clear routing cues
  - task I/O contract
  - validation/eval loop
- Overlap issues (Vercel pairs, Obsidian trio, imaging pair) should be judged by **routing ambiguity and eval outcomes**, not only by conceptual overlap.

### Revised Priority Roadmap (Research-Aligned)

#### High Impact

1. **Create a shared `skill-evals` harness**  
   Add trigger tests (explicit/implicit/contextual + negatives), success criteria, and regression snapshots for top 15 skills [4][6].
2. **Standardize SKILL.md authoring contract across repo**  
   Enforce single-responsibility scope, trigger boundaries, "not-for" section, and concise body length targets [1][6][9].
3. **Add deterministic-invocation guidance to high-risk skills**  
   Security, deployment, and migration-adjacent skills should default to explicit invocation recommendations [1][3].
4. **Operationalize long-running workflows**  
   Codify compaction checkpoints, artifact boundary formats, and network/tool constraints in autonomous/multi-step skills [3].
5. **Keep instruction files under governance**  
   Version, review, and onboard around AGENTS/skill docs as operational interface contracts [7].

#### Medium Impact

6. **Refactor overlapping skills using trigger-collision tests before merging**  
   Prioritize merges where false activation or duplicate activation is observable in evals.
7. **Add "power-user patterns" reference pack**  
   Include templates for explicit invocation, artifact schemas, and handoff protocols.
8. **Add security/robustness checks to scripts**  
   Hard-fail unsafe defaults and add dry-run modes for script-backed skills.

#### Low Impact

9. **Explore adaptive/self-improving skill discovery experimentally**  
   Trial literature-backed patterns (iterative skill mining/polymorphic abstraction) behind flags, not as default behavior [8][11].
10. **Track ecosystem-scale benchmarks as they stabilize**  
   Revisit when benchmarking frameworks mature and peer-reviewed results accumulate [2][5].

### Confidence Gaps

- Some ecosystem guidance is still fragmented across vendor docs and fast-moving blogs.
- Several literature inputs are new arXiv preprints (valuable signals, not peer-reviewed consensus).
- Limited contradictory evidence found against progressive-disclosure + eval-driven approaches.

### Sources

[1] OpenAI, "Agent Skills (Codex docs)": https://developers.openai.com/codex/skills  
[2] "Organizing, Orchestrating, and Benchmarking Agent Skills at Ecosystem Scale" (arXiv 2603.02176): https://arxiv.org/abs/2603.02176  
[3] OpenAI, "Shell + Skills + Compaction" (2026-02-11): https://developers.openai.com/blog/skills-shell-tips  
[4] OpenAI, "Testing Agent Skills Systematically with Evals" (2026-01-22): https://developers.openai.com/blog/eval-skills  
[5] "Agent Skills for Large Language Models: Architecture, Acquisition, Security, and the Path Forward" (arXiv 2602.12430): https://arxiv.org/abs/2602.12430  
[6] Anthropic, "Skill authoring best practices": https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices  
[7] Anthropic, "Scaling agentic coding across your organization": https://resources.anthropic.com/hubfs/Scaling%20agentic%20coding%20across%20your%20organization.pdf  
[8] "SkillWeaver" (arXiv 2504.07079): https://arxiv.org/abs/2504.07079  
[9] Anthropic, "Skills overview": https://claude.com/docs/skills/overview  
[10] Anthropic, "The Complete Guide to Building Skill for Claude" (2026): https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf  
[11] "PolySkill" (arXiv 2510.15863): https://arxiv.org/abs/2510.15863  
[12] Agent Skills Specification: https://agentskills.io/specification

---

## Revision v2 (Post-Implementation, 2026-03-07)

This section records what was implemented after the original analysis so session compaction retains current operational context.

### Implemented Since Original Analysis

- Added new `skill-evals` skill with:
  - deterministic contract validator (`skills/skill-evals/scripts/validate_skill_contract.py`)
  - deterministic trigger-eval scaffold (`skills/skill-evals/scripts/run_trigger_evals.py`)
  - contracts + sample fixture (`skills/skill-evals/references/contracts.md`, `skills/skill-evals/assets/sample-trigger-cases.json`)
- Added repo-wide SKILL contract reference:
  - `docs/system/skill-contract-v1.md`
- Applied contract across all skills and generated reports:
  - `docs/project/skill-contract-application-2026-03-07.md`
  - `docs/project/skill-contract-application-2026-03-07.json`
  - `docs/project/skill-trigger-evals-sample-2026-03-07.json`
- Updated affected SKILL frontmatter/content to remove required contract failures:
  - `skills/compound-docs/SKILL.md`
  - `skills/theme-factory/SKILL.md`
  - `skills/verify-before-complete/SKILL.md`
  - `skills/writing-plans/SKILL.md`
  - `skills/template/SKILL.md`
- Regenerated `skills.json` manifest.

### Measured Outcomes

- Contract application (default mode): **44 total / 0 fail / 42 warn / 2 pass**.
- Sample trigger eval fixture: **12/12 assertions passed**.
- All skills pass `quick_validate.py` structural checks.

### Roadmap Status Update

#### Completed

1. Create shared `skill-evals` harness.
2. Standardize SKILL.md authoring contract (v1) and apply across catalog.
3. Establish baseline trigger-eval fixture and reporting artifacts.

#### Partially Completed

4. Deterministic invocation guidance exists in research roadmap, but not yet enforced uniformly in high-risk skills.
5. Governance is in place via committed contract/report artifacts, but CI enforcement gates are not yet wired.

#### Still Open (High Leverage Next)

6. Burn down warnings from contract report in priority order (scope/boundary/output/verification anchors).
7. Add strict mode path (`--strict`) to CI for selected skill subsets, then full catalog.
8. Use trigger-collision evals to drive merge decisions for overlapping skills (Vercel pair, Obsidian trio, image-gen pair).
9. Re-score rankings with `skill-evals` included and update tier table from measured evidence.

### Compaction-Safe Working Context

- Canonical contract doc: `docs/system/skill-contract-v1.md`
- Canonical compliance snapshot: `docs/project/skill-contract-application-2026-03-07.md`
- Canonical trigger baseline: `docs/project/skill-trigger-evals-sample-2026-03-07.json`
- Implementation commits:
  - `0da2084` (research-backed addendum)
  - `7892fa0` (contract/evals framework + catalog application)
