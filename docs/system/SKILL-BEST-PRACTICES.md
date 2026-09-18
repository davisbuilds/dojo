# Skill Best Practices

Authoring and maintenance guidance for Dojo. The design stance below expresses
project policy from [VISION.md](../project/VISION.md) and observed workflow
friction; it is not a claim that model training has eliminated particular
failure modes. The research notes and source list retain the background from the
[earlier skills analysis](../archive/skill-analysis/skills-analysis-2026-3-07.md).

## Design for Capable Agents

Start with the agent's actual baseline: model, tools, harness instructions,
repository guidance, and accepted task context. A skill should supply a missing
capability or improve a consequential decision. It should not require the agent
to demonstrate generic competence through a prescribed ritual.

Distinguish the content you are adding:

| Content | Authoring default |
| --- | --- |
| Specialized knowledge, tool usage, schemas, local conventions | Keep what the agent needs; locate details near the capability and disclose them on demand. |
| User preferences and authority boundaries | State them explicitly, scoped to where they apply. Greater intelligence does not supply missing preferences or permission. |
| Safeguards for consequential failures | Preserve the protected outcome and appropriate evidence; use a fixed sequence only when order matters. |
| Generic reasoning or methodology | Remove, compress, or make advisory unless a specific failure or behavioral evidence justifies it. |
| Presentation and artifacts | Require a format only for a real consumer or explicit request; otherwise offer an adaptable example. |

An instruction should justify the freedom it removes. Prefer an observable
outcome and evidence requirement over a mandated reasoning sequence, option
count, hypothesis quota, exact closing phrase, or repeated acceptance template.
Changing MUST to should is insufficient if the surrounding workflow still
requires the same unnecessary work.

## Scope, Composition, and Artifacts

Use the smallest process sufficient to resolve the actual uncertainty and
substantiate the result. Match depth to dependencies, reversibility, blast radius,
and the consequence of error. File count or a familiar domain keyword is not
an escalation criterion by itself.

Keep the user's task primary. Consulting a sibling supplies relevant guidance
without recursively activating its deliverables and handoffs. Preserve existing
authorization and higher-priority harness loading rules. A skill body cannot
waive those rules; it can avoid expanding the work after consultation.

Reuse accepted tickets, conversations, contracts, and fresh proof. Publish a
separate artifact when requested, required by the project, or useful for a
specific consumer such as a later executor or reviewer. Formal spec/plan schemas
still apply when those artifacts are produced, including their high-risk gates.

For example, a settled CLI addition can consult output-contract guidance while
being implemented. An investigation-only request can finish with a supported
cause and proposed remedy. Neither requires a new document pipeline or an
unauthorized fix. A migration with unresolved recovery behavior still requires
that decision and its proof before the dependent action.

## Review and Retirement

During authoring or substantive revision, identify what the guidance adds and
which failure, preference, or consumer justifies its constraints. This is a
review lens, not a new mandatory report or metadata schema.

Revisit guidance after recurring friction, relevant model/tool changes, or new
behavioral evidence. Options include deleting generic coaching, turning process
into a reference, narrowing the trigger or distribution scope, consolidating
redundant guidance, and retiring the skill. Moving the same mandatory reading
into references does not remove its cost.

Use proportional evidence. Clear scope conflicts and duplicate requirements can
be repaired from source and concrete incidents. Larger claims about improved
outcomes need comparisons with a baseline that keeps the same harness/repo
controls. Include routine work, consequential failure cases, and requests where
the skill should add no process. Observe correctness, missed boundaries,
unnecessary artifacts/stops, cost, and time; separate script/schema tests,
lexical routing checks, and live behavioral results. Consultation counts and
shorter prompts are not proof of marginal value.

Update all surfaces that encode a changed requirement: description, body,
wrapper, references/templates, validators/tests, and generated metadata as
applicable. Update release metadata and standing docs. Avoid solving every
incident by adding another universal rule. Aim for useful behavior as capability
changes, not permanent adherence to today's workflow.

## Research Background

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

Every SKILL.md needs these design elements. The validator checks structural
anchors; it cannot establish the quality of the decisions or behavior:

- **Single responsibility** -- one clear purpose
- **Trigger boundary** -- a precise description and explicit scope/non-goals
- **I/O contract** -- what the task receives; consultation may simply improve the existing output
- **Verification** -- how to check the skill worked correctly

See `docs/system/skill-contract-v1.md` for the full checklist.

## Anti-Patterns

- **Negative trigger clauses in descriptions** increase lexical overlap with competing skills (e.g. "Do NOT use for Gemini" adds "gemini" as a matching token). Use distinct vocabulary instead of cross-references.
- **Instruction-only skills** are not inherently weak -- they become weak when they lack routing cues, I/O contracts, or eval loops.
- **Overly strict language** in advisory guidance creates friction. Reserve mandates for actual authority, safety, compatibility, or consumer requirements; explain the condition that makes them necessary.
- **Repository-relative paths in runnable commands.** A command a skill tells the agent to run — `bash skills/<name>/scripts/x.sh`, `python3 skills/<name>/scripts/x.py`, or an operand like `--config skills/<name>/rules/` — resolves against the **user's** working directory, not dojo. Skills are installed globally and load from whatever repository the session is in, so a `skills/<name>/...` path is simply not there and the command fails everywhere except a dojo checkout (where it works, which is what hides the bug). Anchor every runnable path to **`<skill-dir>/...`** — the agent substitutes the directory it loaded the skill from — and anchor *operands* too, not just the executable: `bash <skill-dir>/scripts/scan.sh --config <skill-dir>/rules/`. This is distinct from a **file reference** in prose (`see references/REFERENCE.md`), which is correctly relative to the skill root because a reader already knows where the skill is. `tests/test_skill_script_paths.py` enforces this across the catalog; `skill-evals`/`skill-creator` are exempt because they are dojo's own gates, meant to run from a dojo checkout.

## Trigger Collision Guidance

When two skills share domain vocabulary, the lexical scorer cannot distinguish them by intent. Known limit pairs and their shared terms:

| Pair | Shared Terms | Resolution |
|------|-------------|------------|
| vercel-deploy / vercel-preview-logs | deploy, preview | Semantic (intent-based) |
| first-principles / brainstorming | approaches, trade-offs | Semantic (depth vs breadth) |
| fetchmd / markdown-converter | markdown, convert | Accepted (different tool domains) |
| skill-creator / template | workflow, steps, trigger | Semantic (guided vs scaffold) |
| design-critique / web-design-guidelines | review, audit, UI | Reciprocal description hand-off + sibling-skills footer; semantic (taste/AI-slop vs rule-compliance/a11y). Note: reciprocal pointers add the other skill's name as a matching token, slightly worsening cross-routing risk in exchange for clearer intent on a smarter scorer. |

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
