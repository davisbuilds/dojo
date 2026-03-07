# Skill Best Practices

Research-backed guidance for skill authoring and evaluation. Based on 2025-2026 vendor docs, arXiv literature, and internal experience. Extracted from the [skills analysis](../skills-analysis-2026-3-07.md).

## Key Principles

1. **Progressive disclosure + narrow scope are converging norms**
   OpenAI and Anthropic both formalize metadata-first loading with on-demand resource expansion, and both stress single-purpose, composable skills over broad "do-everything" bundles [1][6][9].

2. **Trigger quality is a first-class quality dimension**
   Routing-style descriptions, explicit "not for" boundaries, and negative trigger examples reduce false activations and skill collision [1][3][6][10].

3. **Eval-driven skill development is the default for mature teams**
   Treat skill behavior as testable: explicit/implicit/contextual trigger tests, negative controls, and regression tracking [4][6].

4. **Deterministic vs opportunistic invocation should be explicit**
   For high-stakes or pipeline-critical work, use explicit skill invocation. For discovery-heavy workflows, implicit routing is fine [1][3].

5. **Long-running workflows need operational scaffolding**
   Container/session reuse, compaction checkpoints, artifact handoff conventions, and network/security constraints matter more than better prompts [3].

6. **Instruction files are governed operational assets**
   Version in-repo, include in onboarding, treat as governed docs -- not ad-hoc local notes [7].

## Design Contract

Every SKILL.md should include (enforced by `skill-contract-v1.md`):

- **Single responsibility** -- one clear purpose
- **Trigger boundary** -- description says when to use AND when not to
- **I/O contract** -- what the skill produces
- **Verification** -- how to check the skill worked correctly

See `docs/system/skill-contract-v1.md` for the full checklist.

## Anti-Patterns

- **Negative trigger clauses in descriptions** increase lexical overlap with competing skills (e.g. "Do NOT use for Gemini" adds "gemini" as a matching token). Use distinct vocabulary instead of cross-references.
- **Instruction-only skills** are not inherently weak -- they become weak when they lack routing cues, I/O contracts, or eval loops.
- **Overly strict language** ("MUST", "NEVER", "STRICT ENFORCEMENT") in advisory skills creates friction. Reserve strong language for safety-critical behaviors.

## Trigger Collision Guidance

When two skills share domain vocabulary, the lexical scorer cannot distinguish them by intent. Known limit pairs and their shared terms:

| Pair | Shared Terms | Resolution |
|------|-------------|------------|
| vercel-deploy / vercel-preview-logs | deploy, preview | Semantic (intent-based) |
| local-review / gh-review-pr | review, changes | Semantic (local vs GitHub) |
| first-principles / brainstorming | approaches, trade-offs | Semantic (depth vs breadth) |
| fetchmd / markdown-converter | markdown, convert | Accepted (different tool domains) |
| skill-creator / template | workflow, steps, trigger | Semantic (guided vs scaffold) |

For these pairs, explicit invocation (`$skill-name`) is recommended in production.

## Sources

[1] OpenAI, "Agent Skills (Codex docs)": https://developers.openai.com/codex/skills
[2] "Organizing, Orchestrating, and Benchmarking Agent Skills at Ecosystem Scale" (arXiv 2603.02176): https://arxiv.org/abs/2603.02176
[3] OpenAI, "Shell + Skills + Compaction" (2026-02-11): https://developers.openai.com/blog/skills-shell-tips
[4] OpenAI, "Testing Agent Skills Systematically with Evals" (2026-01-22): https://developers.openai.com/blog/eval-skills
[5] "Agent Skills for Large Language Models" (arXiv 2602.12430): https://arxiv.org/abs/2602.12430
[6] Anthropic, "Skill authoring best practices": https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
[7] Anthropic, "Scaling agentic coding across your organization": https://resources.anthropic.com/hubfs/Scaling%20agentic%20coding%20across%20your%20organization.pdf
[8] "SkillWeaver" (arXiv 2504.07079): https://arxiv.org/abs/2504.07079
[9] Anthropic, "Skills overview": https://claude.com/docs/skills/overview
[10] Anthropic, "The Complete Guide to Building Skill for Claude" (2026): https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf
[11] "PolySkill" (arXiv 2510.15863): https://arxiv.org/abs/2510.15863
[12] Agent Skills Specification: https://agentskills.io/specification
