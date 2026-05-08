# Features

Product-surface reference for the Agent Skills Repository.

## Skills Catalog

Catalog snapshot by category. For canonical runtime inventory, use `skills.json` (currently 52 skills):

```bash
jq '.skills | length' skills.json
```

### GitHub Workflows

| Skill | Purpose |
|-------|---------|
| `gh-commit-push-pr` | Commit, push, and open a Pull Request |
| `gh-fix-issue` | Fix GitHub issues end-to-end from analysis through PR |
| `gh-review-pr` | Review Pull Requests with merge recommendations |
| `gh-triage-issues` | Label, prioritize, and de-duplicate GitHub issues |

### Code Review and Quality

| Skill | Purpose |
|-------|---------|
| `code-review-agents` | Multi-agent reviews: architecture, security, data, performance, deployment |
| `diagnose` | Disciplined six-phase debugging loop — build a deterministic pass/fail signal, reproduce, hypothesise, instrument, fix, regression-test |
| `local-review` | Findings-first local reviews on workspace diffs |
| `repo-hardening` | Audit repos for supply-chain risk, generate repo-local security artifacts, and drive hardening work |
| `test-strategy` | Testing methodology: TDD, real dependencies over mocks, behavior-based tests |
| `verify-before-complete` | Require verification evidence before completion claims |

### Content Creation and Design

| Skill | Purpose |
|-------|---------|
| `algorithmic-art` | Generative art with p5.js and controlled randomness |
| `design-md` | Read, write, lint, diff, and export DESIGN.md files via the pinned `@google/design.md` CLI |
| `design-critique` | Audit UI against a 37-pattern slop catalog and return ranked, scoped findings |
| `frontend-design` | Distinctive, production-grade frontend interfaces |
| `gemini-imagen` | Image generation/editing via Gemini API |
| `gpt-imagen` | Image generation/editing via OpenAI Image API |
| `theme-factory` | Apply preset or generated theme systems |
| `web-design-guidelines` | Review UI against web interface guidelines |
| `screenshot` | Capture screenshots across platforms |

The four design skills above compose into a pipeline: `design-md` (token spec) → `frontend-design` (build) → `design-critique` (taste / AI-slop review), with `web-design-guidelines` as a parallel rule-compliance pass (Vercel WIG, accessibility, UX). Each skill's body carries a `Sibling skills` footer that names the adjacent stages and hand-off cues.

### Development Workflows

| Skill | Purpose |
|-------|---------|
| `autonomous-engineering` | Full end-to-end feature workflows (`/lfg`, `/slfg`) |
| `brainstorming` | Explore requirements before implementation |
| `caveman` | Sticky ultra-compressed output mode (~75% token cut) until the user says "stop caveman" |
| `first-principles` | Systems reasoning for high-stakes decisions |
| `writing-plans` | Structured implementation plans with explicit verification and handoff gates |
| `create-cli` | CLI parameter and UX design |
| `agent-native-architecture` | Build agent-native apps with tool/action parity |
| `deep-research` | Web-backed research with conditional depth and evidence filtering |
| `self-improve` | Capture learnings, compact them, and promote validated patterns into reusable artifacts |

### Platform Integrations

| Skill | Purpose |
|-------|---------|
| `vercel-deploy` | Deploy to Vercel |
| `vercel-preview-logs` | Debug Vercel preview deployments |
| `vercel-react-best-practices` | React/Next.js performance optimization |
| `nextjs-app-router` | Next.js App Router patterns, data fetching, and debugging |
| `vercel-react-native-skills` | React Native and Expo best practices |
| `vercel-composition-patterns` | Scalable React composition patterns |
| `playwright` | Browser automation from the terminal |

### Knowledge and Documentation

| Skill | Purpose |
|-------|---------|
| `obsidian-markdown` | Obsidian Flavored Markdown with wikilinks and callouts |
| `obsidian-bases` | Obsidian Bases with views, filters, and formulas |
| `obsidian-canvas` | Obsidian Canvas files for visual canvases |
| `markdown-converter` | Convert file formats to Markdown |
| `compact-session` | Session summaries for context handoff |
| `compound-docs` | Capture solved problems as documentation |

### Meta / Skill Management

| Skill | Purpose |
|-------|---------|
| `skill-creator` | Initialize, validate, and package new skills |
| `skill-evals` | Validate SKILL contract compliance and run trigger-eval scaffolds |
| `skill-installer` | Install skills from curated lists or GitHub repos |
| `skill-standardizer` | Detect drift and unify skill copies |
| `find-skills` | Discover installable skills |
| `template` | Starter scaffold for new skills |

## Hook-Enforced Quality Gates

- SKILL.md frontmatter validated on every write/edit (pre-tool-use).
- New or updated skills should declare `skill-type` so contract validation applies the right structure for workflow vs reference skills.
- Pushes to protected branches are blocked unless the command includes an explicit `DOJO_ALLOW_PROTECTED_PUSH=1` override.
- `skills.json` manifest regenerated after every SKILL.md change (post-tool-use).
- `docs/plans/*-implementation.md` validated after every write/edit (post-tool-use).
- Uncommitted changes and untracked files blocked at session stop. Unpushed commits no longer block — push timing is the operator's call.
- Skill directory structure validated at session stop.

## Command Wrappers

Slash-style entrypoints for harnesses that support command files:

- `/review` — local code review
- `/review-pr` — GitHub PR review
- `/fix-issue` — GitHub issue resolution
- `/triage-issue` — GitHub issue triage
- `/commit-push-pr` — commit, push, PR flow
- `/brainstorm` — brainstorming session
- `/plan` — implementation planning workflow
- `/standardize-skills` — skill standardization
- `/deep-research` — route depth and filter evidence in one command
- `/repo-audit` — generate repo-local audit artifacts and summarize hardening gaps
- `/repo-harden` — implement the highest-value hardening fixes and refresh the audit packet
- `/self-improve` — capture, compact, propose, and extract self-improvement artifacts
- `/retro` — capture session learnings into existing project reference docs, including matching root, `docs/system`, or `docs/project` files

## Skill Packaging

Skills can be packaged into `.skill` files (zip format) for distribution:

```bash
python skills/skill-creator/scripts/package_skill.py <skill-name> ./dist
```

Pre-packaged skills are available in `docs/downloads/`.
