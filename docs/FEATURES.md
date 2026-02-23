# Features

Product-surface reference for the Agent Skills Repository.

## Skills Catalog

38 skills organized by category:

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
| `local-review` | Findings-first local reviews on workspace diffs |
| `verify-before-complete` | Require verification evidence before completion claims |

### Content Creation and Design

| Skill | Purpose |
|-------|---------|
| `algorithmic-art` | Generative art with p5.js and controlled randomness |
| `frontend-design` | Distinctive, production-grade frontend interfaces |
| `gemini-imagen` | Image generation/editing via Gemini API |
| `gpt-imagen` | Image generation/editing via OpenAI Image API |
| `theme-factory` | Apply preset or generated theme systems |
| `web-design-guidelines` | Review UI against web interface guidelines |
| `screenshot` | Capture screenshots across platforms |

### Development Workflows

| Skill | Purpose |
|-------|---------|
| `autonomous-engineering` | Full end-to-end feature workflows (`/lfg`, `/slfg`) |
| `brainstorming` | Explore requirements before implementation |
| `first-principles` | Systems reasoning for high-stakes decisions |
| `writing-plans` | Structured implementation plans with explicit verification and handoff gates |
| `create-cli` | CLI parameter and UX design |
| `agent-native-architecture` | Build agent-native apps with tool/action parity |
| `deep-research` | Web-backed research with conditional depth and evidence filtering |

### Platform Integrations

| Skill | Purpose |
|-------|---------|
| `vercel-deploy` | Deploy to Vercel |
| `vercel-preview-logs` | Debug Vercel preview deployments |
| `vercel-react-best-practices` | React/Next.js performance optimization |
| `vercel-react-native-skills` | React Native and Expo best practices |
| `vercel-composition-patterns` | Scalable React composition patterns |
| `playwright` | Browser automation from the terminal |

### Knowledge and Documentation

| Skill | Purpose |
|-------|---------|
| `obsidian-markdown` | Obsidian Flavored Markdown with wikilinks and callouts |
| `obsidian-bases` | Obsidian Bases with views, filters, and formulas |
| `json-canvas` | JSON Canvas files for visual canvases |
| `markdown-converter` | Convert file formats to Markdown |
| `compact-session` | Session summaries for context handoff |
| `compound-docs` | Capture solved problems as documentation |

### Meta / Skill Management

| Skill | Purpose |
|-------|---------|
| `skill-creator` | Initialize, validate, and package new skills |
| `skill-installer` | Install skills from curated lists or GitHub repos |
| `skill-standardizer` | Detect drift and unify skill copies |
| `find-skills` | Discover installable skills |
| `template` | Starter scaffold for new skills |

## Hook-Enforced Quality Gates

- SKILL.md frontmatter validated on every write/edit (pre-tool-use).
- `skills.json` manifest regenerated after every SKILL.md change (post-tool-use).
- `docs/plans/*-implementation.md` validated after every write/edit (post-tool-use).
- Uncommitted changes and unpushed commits blocked at session stop.
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

## Skill Packaging

Skills can be packaged into `.skill` files (zip format) for distribution:

```bash
python skills/skill-creator/scripts/package_skill.py <skill-name> ./dist
```

Pre-packaged skills are available in `docs/downloads/`.
