# Agent Skills Repository

This repository contains **Agent Skills**—modular packages that extend an AI agent's capabilities with specialized knowledge, workflows, and tool integrations. These skills allow general-purpose agents (like Claude or other AI assistants) to perform specialized tasks in specific domains.

## Overview

A "Skill" is a self-contained directory that provides:
- **Instructions**: Detailed guides on how to perform a specific task (in `SKILL.md`).
- **Context**: Specialized knowledge or best practices.
- **Workflow**: A structured approach to complex problems.

## Skill Structure

Each skill is located in its own directory and follows this structure:

```
skill-name/
├── SKILL.md           # Required: Frontmatter (YAML) + Instructions (Markdown)
├── scripts/           # Optional: Executable scripts (Python/Bash)
├── references/        # Optional: Documentation files
└── assets/            # Optional: Templates, images, or other assets
```

The `SKILL.md` file contains the "brain" of the skill—the prompt instructions that are loaded into the agent's context when the skill is triggered.

## Available Skills

| Skill Directory | Description |
|----------------|-------------|
| **`skills/agent-native-architecture/`** | **Agent-Native Architecture**: Build applications where agents are first-class and operate with tool/action parity. |
| **`skills/algorithmic-art/`** | **Generative Art**: Create algorithmic art with p5.js and controlled randomness. |
| **`skills/autonomous-engineering/`** | **Autonomous Delivery**: Run full end-to-end feature workflows (`/lfg`, `/slfg`). |
| **`skills/brainstorm/`** | **Brainstorming Ideas**: Explore intent and shape solutions before implementation. |
| **`skills/code-review-agents/`** | **Review Swarm**: Use specialized agents for architecture, security, data, performance, and deployment review. |
| **`skills/compact-session/`** | **Context Management**: Create concise session summaries for reliable handoff. |
| **`skills/compound-docs/`** | **Knowledge Capture**: Record solved problems as categorized, searchable documentation. |
| **`skills/create-cli/`** | **CLI Builder**: Design and refine command-line interface UX and behavior. |
| **`skills/find-skills/`** | **Skill Discovery**: Find installable skills for requested capabilities. |
| **`skills/first-principles/`** | **Systems Reasoning**: Apply first-principles analysis for high-stakes technical decisions. |
| **`skills/frontend-design/`** | **UI/UX Design**: Build distinctive, production-grade frontend interfaces. |
| **`skills/gh-commit-push-pr/`** | **GitHub Automation**: Commit, push, and open a Pull Request in one guided flow. |
| **`skills/gh-fix-issue/`** | **Issue Resolution**: Fix GitHub issues end-to-end from analysis through PR. |
| **`skills/gh-review-pr/`** | **Code Review**: Review Pull Requests and provide merge recommendations. |
| **`skills/gh-triage-issues/`** | **Issue Triage**: Label, prioritize, and de-duplicate GitHub issues. |
| **`skills/imagegen/`** | **OpenAI Image API**: Generate and edit images with reproducible CLI workflows. |
| **`skills/json-canvas/`** | **JSON Canvas**: Create and edit Obsidian-compatible `.canvas` files. |
| **`skills/markdown-converter/`** | **Document Conversion**: Convert many file formats into Markdown for analysis. |
| **`skills/nano-banana-pro/`** | **Nano Banana Pro**: Generate or edit images via Gemini 3 Pro Image. |
| **`skills/obsidian-bases/`** | **Obsidian Bases**: Create and edit `.base` files with views, filters, formulas, and summaries. |
| **`skills/obsidian-markdown/`** | **Obsidian Markdown**: Author Obsidian-flavored Markdown with wikilinks, embeds, callouts, and properties. |
| **`skills/playwright/`** | **Browser Automation**: Drive real browser workflows from the terminal. |
| **`skills/skill-creator/`** | **Meta-Skill**: Initialize, validate, and package new skills. |
| **`skills/skill-installer/`** | **Skill Installation**: Install curated or repo-based Codex skills. |
| **`skills/template/`** | **Starter Template**: Scaffold directory for creating new skills from scratch. |
| **`skills/theme-factory/`** | **Theming**: Apply preset or generated theme systems to artifacts. |
| **`skills/vercel-composition-patterns/`** | **React Composition**: Use scalable composition patterns for reusable React APIs. |
| **`skills/vercel-deploy/`** | **Vercel Deploy**: Deploy applications and websites to Vercel. |
| **`skills/vercel-react-best-practices/`** | **React Performance**: Apply Vercel’s React/Next.js optimization guidelines. |
| **`skills/vercel-react-native-skills/`** | **React Native Performance**: Apply Vercel best practices for React Native and Expo. |
| **`skills/verify-before-complete/`** | **Quality Control**: Require verification evidence before completion claims. |
| **`skills/web-design-guidelines/`** | **UI Guidelines Audit**: Review interfaces for web guideline compliance. |

## Hooks

This repo uses hooks (in `hooks/`) to enforce skill quality and provide session context. Hooks are configured in `.claude/settings.json` and `.agents/settings.json`.

| Hook | When it runs | Purpose |
|------|-------------|---------|
| **Session Start — Skill Catalog** | Session begins | Injects skill catalog from `skills.json`, recent git activity, and a pointer to AGENTS.md so any agent harness knows what's available |
| **PreToolUse — Validate SKILL.md** | Before writing/editing a SKILL.md | Runs frontmatter validation and blocks the write if it fails |
| **PostToolUse — Regenerate Manifest** | After writing/editing a SKILL.md | Regenerates `skills.json` to keep the manifest in sync |
| **Stop — Git Check** | Session ends | Ensures all changes are committed and pushed |
| **Stop — Skill Structure** | Session ends | Checks that modified skill directories have valid SKILL.md with matching names |

## Prerequisites

### System tools

The hook scripts rely on standard CLI tools that should be available on most development machines:

- **Python 3** (>= 3.8)
- **git**
- **jq**
- **sed**, **grep** (used by some stop-hooks)

### Python dependencies

Core Python dependencies are listed in `requirements.txt`. Install them with:

```bash
pip install -r requirements.txt
```

This installs **PyYAML**, which is required by the validation and manifest-generation scripts that the hooks invoke.

#### Optional (skill-specific)

Some skills bundle their own dependencies. Uncomment the relevant sections in `requirements.txt` or install manually:

| Skill | Extra packages |
|-------|---------------|
| `skills/imagegen/` | `openai>=1.0.0`, `Pillow>=10.0.0` |
| `skills/nano-banana-pro/` | `google-genai>=1.0.0`, `Pillow>=10.0.0` |

These skills also require API keys set as environment variables (`OPENAI_API_KEY`, `GEMINI_API_KEY`).

## Creating a New Skill

You can use the `skill-creator` scripts to scaffold a new skill:

```bash
# Create a new skill directory
python skills/skill-creator/scripts/init_skill.py <skill-name> --path ./

# Validate your skill structure (works with both `python` and `python3`)
python skills/skill-creator/scripts/quick_validate.py <skill-name>
```

The validator uses a polyglot shebang so it can also be run directly and will work in environments that provide either `python` or `python3`.

## Usage

When working with an agent that supports these skills:
1. **Trigger**: The agent will select a skill based on its `description` in `SKILL.md` when it matches your request.
2. **Follow Instructions**: The agent will then follow the specific protocols defined in the skill's body.
3. **Tools**: Some skills may require specific tools (like `gh` CLI or `python`) to be installed in your environment.

## Resources

- **`AGENTS.md`**: Guidance for AI agents on how to use this repository (single source of truth).
- **`CLAUDE.md`**: Symlink to `AGENTS.md` so Claude Code picks up the same instructions.
- **`requirements.txt`**: Python dependencies for hooks and scripts (core + optional per-skill extras).

## Acknowledgements

- [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)
- [superpowers](https://github.com/obra/superpowers)
- [agent-scripts](https://github.com/steipete/agent-scripts)
- [anthropics/skills](https://github.com/anthropics/skills)
- [compound-engineering-plugin](https://github.com/everyinc/compound-engineering-plugin) — source of the code-review-agents, autonomous-engineering, agent-native-architecture, and compound-docs skills
- [Vercel skills](https://github.com/vercel/next.js) — React, Next.js, and React Native best-practice rules and composition patterns
- [Kepano's Obsidian skills](https://github.com/kepano) — Obsidian Markdown, Bases, and JSON Canvas skill references
- [skills.sh](https://skills.sh) — community skill registry and discovery
