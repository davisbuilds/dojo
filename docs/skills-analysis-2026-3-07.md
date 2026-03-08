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

Rescored with measured evidence: strict contract compliance (44/44), trigger-eval f1 scores (24 skills tested), and structural improvements. See per-skill sections below for change rationale.

| Rank | Skill | Score | Prev | Tier | Category | Trigger f1 |
|------|-------|-------|------|------|----------|-----------|
| 1 | vercel-react-best-practices | 9.5 | 9.5 | S | Knowledge | — |
| 2 | vercel-react-native-skills | 9.5 | 9.5 | S | Knowledge | — |
| 3 | code-review-agents | 9 | 9 | S | Multi-Agent | — |
| 4 | skill-creator | 9 | 9 | S | Meta/Process | 1.00 |
| 5 | gpt-imagen | 9 | 9 | S | Tool | 1.00 |
| 6 | agent-native-architecture | 9 | 9 | S | Knowledge | — |
| 7 | secure-code | 8.5 | 8.5 | A | Security | 1.00 |
| 8 | audit-skill | 8.5 | 8.5 | A | Security | 1.00 |
| 9 | hookify | 8.5 | 8.5 | A | Tool | — |
| 10 | deep-research | 8.5 | 8.5 | A | Workflow | — |
| 11 | frontend-design | 8 | 8 | A | Creative | — |
| 12 | gh-triage-issues | 8 | 8 | A | GitHub | — |
| 13 | gh-review-pr | 8 | 8 | A | GitHub | 0.67 |
| 14 | verify-before-complete | 8 | 8 | A | Behavioral | — |
| 15 | algorithmic-art | 8 | 8 | A | Creative | — |
| 16 | vercel-composition-patterns | 8 | 8 | A | Knowledge | — |
| 17 | writing-plans | 8 | 7.5 | A | Process | 1.00 |
| 18 | skill-evals | 8 | new | A | Meta | — |
| 19 | brainstorming | 7.5 | 7.5 | B | Process | 0.80 |
| 20 | gh-fix-issue | 7.5 | 7 | B | GitHub | 1.00 |
| 21 | playwright | 7.5 | 7 | B | Tool | 1.00 |
| 22 | compact-session | 7.5 | 7 | B | Process | 1.00 |
| 23 | gh-commit-push-pr | 7.5 | 7 | B | GitHub | 1.00 |
| 24 | compound-docs | 7 | 7 | B | Process | — |
| 25 | create-cli | 7 | 7 | B | Design | — |
| 26 | skill-standardizer | 7 | 7 | B | Meta | — |
| 27 | theme-factory | 7 | 7 | B | Creative | — |
| 28 | obsidian-markdown | 7 | 6.5 | B | Knowledge | 1.00 |
| 29 | obsidian-bases | 7 | 6.5 | B | Knowledge | 1.00 |
| 30 | json-canvas | 7 | 6.5 | B | Knowledge | 1.00 |
| 31 | local-review | 7 | 6.5 | B | Workflow | 0.67 |
| 32 | screenshot | 7 | 6.5 | B | Tool | 1.00 |
| 33 | gemini-imagen | 7 | 6 | B | Tool | 1.00 |
| 34 | session-retro | 6.5 | 6 | B | Process | 1.00 |
| 35 | autonomous-engineering | 6.5 | 6.5 | B | Workflow | — |
| 36 | skill-installer | 6.5 | 6 | B | Meta | — |
| 37 | vercel-deploy | 6.5 | 6 | B | DevOps | 0.67 |
| 38 | vercel-preview-logs | 6.5 | 6 | B | DevOps | 0.67 |
| 39 | web-design-guidelines | 6 | 5.5 | C | Knowledge | — |
| 40 | first-principles | 5.5 | 4.5 | C | Behavioral | 0.67 |
| 41 | fetchmd | 5.5 | 5 | C | Utility | 0.50 |
| 42 | markdown-converter | 5.5 | 5 | C | Utility | 0.80 |
| 43 | find-skills | 5.5 | 5 | C | Meta | — |
| 44 | template | 4 | 2 | D | Meta | 0.67 |

**Score changes:** 20 skills unchanged, 23 skills +0.5 to +2, 1 new entry (skill-evals). No scores decreased. Trigger f1 values below 1.0 reflect accepted lexical-scorer limits, not description quality issues (see [SKILL-BEST-PRACTICES.md](system/SKILL-BEST-PRACTICES.md)).

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

### writing-plans -- 8/10 *(was 7.5)*
Implementation plans with YAML frontmatter, 10-30 minute task granularity, verification commands per task, and validation script. Routes to brainstorming or first-principles when requirements are unclear.

- **Strengths:** Validation script catches plan issues before handoff. Three handoff modes (execute, separate session, refine). Task granularity guidance is practical.
- **Weaknesses:** Template is somewhat rigid. No example plans bundled.
- **Gaps:** No integration with project management tools.
- **Score change:** +0.5 for strict contract compliance and strong trigger f1 (1.00).

### skill-evals -- 8/10 *(new)*
**Files:** 8 | **Category:** Meta

Trigger-eval framework and strict contract validator for skill quality. Fixtures test explicit, implicit, contextual, and negative triggers across 12 skill clusters. Lexical scorer with discriminating name tokens and stopword filtering.

- **Strengths:** Only skill that measures other skills quantitatively. Contract validator enforces structural quality across the full catalog. Trigger fixtures catch routing regressions. Scorer improvements (disc_name_tokens, stopwords) are reusable.
- **Weaknesses:** Lexical scorer has inherent limits — cannot distinguish semantic intent for vocabulary-overlapping pairs. No LLM-based scoring tier yet.
- **Gaps:** No automated fixture generation from skill descriptions. No historical trend tracking.

---

## Tier B (6.5-7.5): Solid

### brainstorming -- 7.5/10
4-phase process: assess clarity, understand intent (one question at a time), explore approaches, capture design summary. Hard-gate prevents premature implementation.

- **Strengths:** The one-question-at-a-time discipline prevents overwhelming users. Hard-gate on design approval is valuable. Skill coordination routing is smart.
- **Weaknesses:** No design document template despite recommending one be written.
- **Verbosity:** The platform-mapping reference adds complexity for uncertain value.
- **Gaps:** No question bank organized by domain.

### gh-fix-issue -- 7.5/10 *(was 7)*
10-step workflow from issue fetch to PR creation. Handles closed issues, existing PRs, fork-required repos.

- **Strengths:** End-to-end automation. Edge case handling is thorough. Strong trigger f1 (1.00).
- **Weaknesses:** Duplicates `fetch_issue.sh` with gh-triage-issues.
- **Gaps:** No PR template reference. No test auto-detection.
- **Score change:** +0.5 for strict contract compliance and clean trigger routing.

### compound-docs -- 7/10
Captures solved problems as categorized documentation with YAML frontmatter. 7-step workflow with enum-validated problem types.

- **Strengths:** Decision gates for promoting to critical patterns and skills are smart. YAML schema validation ensures consistency. Category-based filing aids retrieval.
- **Weaknesses:** Relatively heavy process for documenting a solution (7 steps). The enforcement language is very strict.
- **Verbosity:** Could be condensed -- the 7-step workflow has redundant validation steps.
- **Gaps:** No search/retrieval tooling for existing docs.

### playwright -- 7.5/10 *(was 7)*
CLI-first browser automation with wrapper script, CLI reference, and workflow guides.

- **Strengths:** Practical workflow guide (open > snapshot > interact > re-snapshot). Wrapper script handles environment setup. Strong trigger f1 (1.00).
- **Weaknesses:** Depends on npx availability. Guardrails section is brief.
- **Gaps:** No example test scripts. No integration with verify-before-complete for UI verification.
- **Score change:** +0.5 for strict contract compliance and clean trigger routing.

### create-cli -- 7/10
CLI surface area design before implementation. Excellent cli-guidelines.md reference condensed from clig.dev.

- **Strengths:** The guidelines reference is genuinely excellent (240 lines, 16 areas). Spec template is practical.
- **Weaknesses:** No example specs. No generation scripts.
- **Gaps:** Example specs would dramatically improve usability.

### compact-session -- 7.5/10 *(was 7)*
Session summaries with 9-section structure, template, and 2 examples.

- **Strengths:** Examples illustrate different session types. Section structure optimizes for resumability. Strong trigger f1 (1.00).
- **Weaknesses:** No auto-generation from git/conversation context.
- **Gaps:** More example types needed (refactoring, debugging, multi-day work).
- **Score change:** +0.5 for strict contract compliance and clean trigger routing.

### gh-commit-push-pr -- 7.5/10 *(was 7)*
*Improved since previous analysis (was 4/10).* Now has conventions reference (branch naming, commit format), PR templates (minimal/standard/detailed), and a prepare_commit script.

- **Strengths:** Three PR template tiers are practical. Branch naming conventions are clear. Strong trigger f1 (1.00).
- **Weaknesses:** Still relatively thin compared to other GitHub skills.
- **Gaps:** No error recovery guidance for push failures.
- **Score change:** +0.5 for strict contract compliance and clean trigger routing.

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

### obsidian-markdown -- 7/10 *(was 6.5)*
621-line comprehensive reference for Obsidian Flavored Markdown.

- **Strengths:** Exhaustive coverage of wikilinks, callouts, embeds, properties, Mermaid, and LaTeX. Clean trigger routing (f1 1.00).
- **Weaknesses:** Essentially a reference manual -- no workflows, scripts, or automation.
- **Verbosity:** **Overly verbose.** 621 lines is excessive for what is largely syntax documentation. Much of this duplicates what an agent already knows about Markdown. Could be cut to ~200 lines focusing only on Obsidian-specific extensions.
- **Gaps:** No templates for common note types. No linting or validation.
- **Score change:** +0.5 for strict contract compliance and clean trigger routing.

### obsidian-bases -- 7/10 *(was 6.5)*
652-line reference for Obsidian Bases (.base files) with 100+ function reference.

- **Strengths:** Complete schema documentation with 4 worked examples. The function reference is thorough. Clean trigger routing (f1 1.00).
- **Weaknesses:** Same issue as obsidian-markdown -- it's a reference manual, not a workflow.
- **Verbosity:** **Overly verbose.** 652 lines, with the function reference alone consuming hundreds of lines. Could be condensed significantly by focusing on the schema and linking to external docs for the function catalog.
- **Gaps:** No templates for common base configurations. No validation script.
- **Score change:** +0.5 for strict contract compliance and clean trigger routing.

### json-canvas -- 7/10 *(was 6.5)*
Complete spec for JSON Canvas files with 4 examples and validation rules.

- **Strengths:** Thorough specification. ID generation and layout guidelines are practical. Examples cover different use cases. Clean trigger routing (f1 1.00).
- **Weaknesses:** Another reference manual. No scripts or templates.
- **Verbosity:** Could be more concise by separating the spec from the examples.
- **Gaps:** No canvas generation script. No validation tool.
- **Score change:** +0.5 for strict contract compliance and clean trigger routing.

### local-review -- 7/10 *(was 6.5)*
Local code review without GitHub integration. Three modes (working, staged, branch).

- **Strengths:** Findings-first output structure. Risk analysis section. Multiple review targets.
- **Weaknesses:** The collect_review_context.sh script does the heavy lifting, but the SKILL.md could provide more review heuristics. Trigger f1 0.67 due to vocabulary overlap with gh-review-pr.
- **Gaps:** No integration with other review skills (code-review-agents, secure-code).
- **Score change:** +0.5 for strict contract compliance.

### autonomous-engineering -- 6.5/10
End-to-end feature development via `/lfg` (sequential) and `/slfg` (swarm/parallel).

- **Strengths:** Ambitious -- chains plan > deepen > implement > review > test > video. Swarm variant for parallel execution is novel.
- **Weaknesses:** Depends heavily on other skills existing and working. If any chained skill fails, the whole pipeline breaks.
- **Verbosity:** The README adds little beyond what the commands describe.
- **Gaps:** No error recovery or partial-completion handling. No progress tracking.

### screenshot -- 7/10 *(was 6.5)*
Cross-platform screenshot capture with macOS permission handling.

- **Strengths:** Thorough cross-platform coverage (macOS, Linux, Windows). Permission preflight for macOS is practical. Multiple capture modes (app, window, region). Clean trigger routing (f1 1.00).
- **Weaknesses:** Heavy script count (5 scripts) for a simple capability. Most agents already have screenshot tools.
- **Gaps:** No image annotation or comparison capabilities.
- **Score change:** +0.5 for strict contract compliance and clean trigger routing.

### gemini-imagen -- 7/10 *(was 6)*
Image generation via Google Gemini API with 3 subcommands and resolution tiers.

- **Strengths:** Resolution tier system (1K/2K/4K). Prompt template structure. Clean trigger routing (f1 1.00) — fully disambiguated from gpt-imagen after description rewrite.
- **Weaknesses:** Much thinner than gpt-imagen. Only 3 files vs. gpt-imagen's 12. No sample prompts reference. No use-case taxonomy.
- **Gaps:** Feels like a stripped-down gpt-imagen. Could be merged or brought to parity.
- **Score change:** +1 for strict contract compliance and clean trigger routing after description disambiguation.

### session-retro -- 6.5/10 *(was 6)*
Updates AGENTS.md/CLAUDE.md with session learnings. Max 5 learnings, append-only, requires approval.

- **Strengths:** Strict filtering criteria (what qualifies vs. doesn't). One-line-per-learning constraint prevents bloat. Approval gate prevents unwanted changes. Clean trigger routing (f1 1.00).
- **Weaknesses:** Very simple -- 57 lines of instruction, no scripts or templates.
- **Gaps:** No auto-detection of learnable moments. No deduplication against existing docs.
- **Score change:** +0.5 for strict contract compliance and clean trigger routing.

### skill-installer -- 6.5/10 *(was 6)*
Installs skills from GitHub or curated lists into Codex/Claude directories.

- **Strengths:** Supports both curated and experimental skill lists. Fallback from download to git sparse checkout.
- **Weaknesses:** Depends on external GitHub infrastructure. No validation after install.
- **Gaps:** No update/upgrade mechanism. No dependency resolution between skills.
- **Score change:** +0.5 for strict contract compliance.

### vercel-deploy -- 6.5/10 *(was 6)*
Deploy to Vercel with preview by default, production on request.

- **Strengths:** Simple and focused. Fallback script for auth issues. Description disambiguated from vercel-preview-logs (trigger f1 0.67 — accepted lexical limit).
- **Weaknesses:** Thin -- most of the value is just running `vercel deploy`. The skill adds limited value beyond CLI documentation.
- **Gaps:** No rollback guidance. No environment variable management. No build configuration help.
- **Score change:** +0.5 for strict contract compliance and description disambiguation.

### vercel-preview-logs -- 6.5/10 *(was 6)*
Inspect Vercel preview deployments for failures with root cause analysis.

- **Strengths:** Specific failure diagnosis priority (compile > env/config > runtime). Safe CLI wrapper. Description disambiguated from vercel-deploy (trigger f1 0.67 — accepted lexical limit).
- **Weaknesses:** Narrow scope. Only useful when Vercel deployments fail.
- **Gaps:** Could be merged with vercel-deploy as a single Vercel skill.
- **Score change:** +0.5 for strict contract compliance and description disambiguation.

---

## Tier C (5-6): Adequate

### web-design-guidelines -- 6/10 *(was 5.5)*
Fetches Web Interface Guidelines from vercel-labs and checks UI files.

- **Strengths:** Fetches fresh guidelines at review time.
- **Weaknesses:** Depends entirely on an external URL being available. No cached/bundled fallback. Very thin instructions.
- **Verbosity:** Too terse -- the opposite problem. Barely explains what guidelines are checked.
- **Gaps:** No bundled guidelines. No example output. No integration with frontend-design skill.
- **Score change:** +0.5 for strict contract compliance.

### fetchmd -- 5.5/10 *(was 5)*
Webpage-to-markdown converter via npx.

- **Strengths:** Lists features and options clearly.
- **Weaknesses:** Thin wrapper around an npm package. Minimal value-add beyond `npx @davisbuilds/fetchmd --help`.
- **Gaps:** No example workflows. No integration with deep-research.
- **Score change:** +0.5 for strict contract compliance.

### markdown-converter -- 5.5/10 *(was 5)*
Document-to-markdown via `uvx markitdown`.

- **Strengths:** Lists supported formats clearly.
- **Weaknesses:** Thin wrapper around an existing tool. Minimal value-add.
- **Gaps:** No format-specific tips. No batch conversion guidance. No error handling.
- **Score change:** +0.5 for strict contract compliance.

### find-skills -- 5.5/10 *(was 5)*
Discovers and installs skills via `npx skills`.

- **Strengths:** Lists common skill categories with example queries.
- **Weaknesses:** Thin wrapper around `npx skills`. The 4-step workflow is generic.
- **Gaps:** No curation or recommendation logic. No compatibility checking.
- **Score change:** +0.5 for strict contract compliance.

### first-principles -- 5.5/10 *(was 4.5)*
First-principles reasoning framework with self-check gate, epistemic framework, and decision matrix.

- **Strengths:** The epistemic framework (assumptions, confidence, knowledge boundaries) is conceptually sound. Trigger f1 0.67 reflects expected overlap with brainstorming (intent-based disambiguation).
- **Weaknesses:** **Overly verbose and prescriptive.** The instructions read like an academic methodology paper rather than actionable agent guidance. Phrases like "Epistemic framework", "calibrate confidence", "distinguish correlation from causation" are abstract without concrete examples. The decision matrix maps task types to analysis levels but doesn't show what the output should look like.
- **Verbosity:** High. The skill tries to change how the agent thinks rather than what it does, which is hard to enforce through instruction alone.
- **Gaps:** No worked examples showing the framework applied to a real decision. No templates for trade-off analysis or decision documents. Compare to writing-plans which has a template and validator -- this skill has neither.
- **Score change:** +1 for strict contract compliance and structural improvements (scope, boundaries, output, verification anchors added).

---

## Tier D (1-4): Needs Work

### template -- 4/10 *(was 2)*
Minimal placeholder with frontmatter skeleton only.

- **Strengths:** Exists as a starting point. Now includes scope, boundaries, output, and verification anchors.
- **Weaknesses:** Still very thin. Provides little beyond what init_skill.py generates.
- **Gaps:** Should include commented examples of each section, or variant templates by skill type.
- **Score change:** +2 for strict contract compliance (added all required anchors).

---

## Cross-Cutting Findings

Moved to dedicated system docs:

- **Findings, gaps, overlaps, and priority improvements** → [`docs/system/ROADMAP.md`](system/ROADMAP.md)
- **Research-backed best practices and sources** → [`docs/system/SKILL-BEST-PRACTICES.md`](system/SKILL-BEST-PRACTICES.md)
- **Contract specification** → [`docs/system/skill-contract-v1.md`](system/skill-contract-v1.md)

### Quality Trends Since Previous Analysis

| Skill | Previous Score | Current Score | Change | Notes |
|-------|---------------|---------------|--------|-------|
| frontend-design | 6/10 | 8/10 | +2 | Added font pairings, color palettes, anti-patterns, component templates |
| gh-commit-push-pr | 4/10 | 7/10 | +3 | Added conventions, PR templates, prepare_commit script |
| theme-factory | 7/10 | 7/10 | 0 | Added JSON + scripts (matching previous recommendations) |
| brainstorming | 6/10 | 7.5/10 | +1.5 | Added platform mapping, improved routing |

---

## Implementation History

Summary of post-analysis implementation work. Full details in git history.

| Revision | Scope | Key Outcome |
|----------|-------|-------------|
| v2 | Contract/evals framework | `skill-evals` skill, contract v1, 44/0-fail/42-warn/2-pass |
| v3 | Pilot strict CI | 5 skills strict-enforced via GitHub Actions |
| v4 | Expanded strict set | 13 skills strict-enforced |
| v5 | Trigger-collision baseline | 12 cases, 22/28 passed (78.6%) across 3 clusters |
| v6 | Collision fixes + scorer | 26/28 passed (92.9%), disc_name_tokens, expanded stopwords |
| v7 | Expanded fixtures + full strict | 34 cases across 12 clusters, 44/44 strict, CI full catalog |

### Current Status

- **Strict contract**: 44/44 pass (4 non-blocking context_budget warnings)
- **Trigger evals**: 74/84 assertions pass (88.1%) across 3 fixtures
- **CI**: enforces `--strict` on full catalog (`.github/workflows/skill-contract-pilot.yml`)

### Accepted Lexical Limits (10 failures)

All remaining trigger-eval failures are false positives from genuine vocabulary overlap. The lexical scorer cannot distinguish semantic intent. An LLM-based router handles these correctly. See [`docs/system/SKILL-BEST-PRACTICES.md`](system/SKILL-BEST-PRACTICES.md) for guidance on explicit invocation for these pairs.

| Pair | Shared terms | Failures |
|------|-------------|----------|
| vercel-deploy / vercel-preview-logs | deploy, preview | 2 |
| local-review / gh-review-pr | review, changes | 2 |
| first-principles / brainstorming | approaches, trade-offs | 2 |
| fetchmd / markdown-converter | markdown, convert | 3 |
| skill-creator / template | workflow, steps, trigger | 1 |

### Key Artifacts

| Artifact | Path |
|----------|------|
| Contract spec | `docs/system/skill-contract-v1.md` |
| Best practices | `docs/system/SKILL-BEST-PRACTICES.md` |
| Roadmap | `docs/system/ROADMAP.md` |
| Contract report | `docs/project/skill-contract-application-2026-03-07.md` |
| Collision fixtures | `skills/skill-evals/assets/trigger-collision-cases-*.json` |
| Collision results | `docs/project/skill-trigger-collision-evals-*.json` |

### Next

- Address 4 context_budget warnings (compound-docs, json-canvas, obsidian-bases, obsidian-markdown).
