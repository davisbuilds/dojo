# AGENTS.md

This file provides guidance to AI agents when working with code in this repository.

## Overview

This repository contains Agent Skills - modular packages that extend an agent's capabilities with specialized knowledge, workflows, and tool integrations. Skills transform a general-purpose agent into a specialized agent for specific domains or tasks.

## Skill Structure

Every skill follows this structure:

```
skill-name/
├── SKILL.md           # Required: frontmatter + instructions
├── scripts/           # Optional: executable Python/Bash code
├── references/        # Optional: documentation loaded into context as needed
└── assets/            # Optional: templates, images, fonts for output
```

### SKILL.md Requirements

- **Frontmatter** (YAML): Must include `name` (hyphen-case, max 64 chars) and `description` (max 1024 chars, no angle brackets)
- **Body** (Markdown): Instructions loaded only after the skill triggers
- Allowed frontmatter fields: `name`, `description`, `license`, `allowed-tools`, `metadata`

## Commands

### Create a new skill

```bash
python skills/skill-creator/scripts/init_skill.py <skill-name> --path <output-directory>
```

Creates a skill directory with template SKILL.md and example resource directories.

### Validate a skill

```bash
python skills/skill-creator/scripts/quick_validate.py <path/to/skill-folder>
```

Checks frontmatter format, required fields, naming conventions. The validator uses a polyglot shebang that works with both `python` and `python3`, so it can be invoked directly or with either interpreter.

### Package a skill for distribution

```bash
python skills/skill-creator/scripts/package_skill.py <path/to/skill-folder> [output-directory]
```

Validates and creates a `.skill` file (zip format) for distribution.

## Key Design Principles

1. **Concise is key**: The context window is shared. Only add information the agent doesn't already have.

2. **Progressive disclosure**: Metadata always loaded (~100 words) → SKILL.md body on trigger (<5k words) → bundled resources as needed.

3. **Degrees of freedom**: Match specificity to task fragility - high freedom for flexible tasks (text instructions), low freedom for fragile operations (specific scripts).

4. **Description is the trigger**: The `description` field determines when the agent uses the skill. Include both what it does AND specific scenarios/triggers.

## Hooks

Scripts in `hooks/` enforce quality and inject context automatically. Configured in `.claude/settings.json` (and mirrored in `.agents/settings.json` for other harnesses).

| Hook | Event | What it does |
|------|-------|--------------|
| `session-start-skill-catalog.sh` | SessionStart | Injects skill catalog from `skills.json`, recent git log, and a pointer to AGENTS.md |
| `pre-tool-use-validate-skill.sh` | PreToolUse (Write\|Edit) | Runs `quick_validate.py` when a SKILL.md is written or edited; blocks on invalid frontmatter |
| `post-tool-use-regen-manifest.sh` | PostToolUse (Write\|Edit) | Regenerates `skills.json` after a SKILL.md is modified |
| `stop-hook-git-check.sh` | Stop | Blocks if there are uncommitted changes, untracked files, or unpushed commits |
| `stop-hook-skill-structure.sh` | Stop | Validates that modified skill directories have SKILL.md and matching directory/frontmatter names |

## Existing Skills

| Skill                        | Purpose                                          |
| ---------------------------- | ------------------------------------------------ |
| `skills/agent-native-architecture/` | Build agent-native applications and MCP tool workflows |
| `skills/algorithmic-art/` | Create generative art with p5.js |
| `skills/autonomous-engineering/` | Run end-to-end autonomous feature workflows |
| `skills/brainstorm/` | Explore requirements and design before implementation |
| `skills/code-review-agents/` | Run specialized multi-agent code reviews and audits |
| `skills/compact-session/` | Create session summaries for context handoff |
| `skills/compound-docs/` | Capture solved problems as categorized documentation |
| `skills/create-cli/` | Design and refine command-line interfaces |
| `skills/find-skills/` | Discover and install relevant skills |
| `skills/first-principles/` | Apply first-principles systems reasoning to tough technical problems |
| `skills/frontend-design/` | Create distinctive frontend interfaces |
| `skills/gh-commit-push-pr/` | Commit, push, and open a GitHub PR |
| `skills/gh-fix-issue/` | Fix GitHub issues end-to-end |
| `skills/gh-review-pr/` | Review GitHub PRs with merge recommendations |
| `skills/gh-triage-issues/` | Triage and label GitHub issues |
| `skills/imagegen/` | Generate and edit images via the OpenAI Image API |
| `skills/json-canvas/` | Create and edit JSON Canvas (`.canvas`) files |
| `skills/markdown-converter/` | Convert documents and files to Markdown |
| `skills/nano-banana-pro/` | Generate and edit images with Nano Banana Pro |
| `skills/obsidian-bases/` | Create and edit Obsidian Bases (`.base`) files |
| `skills/obsidian-markdown/` | Create and edit Obsidian Flavored Markdown |
| `skills/playwright/` | Automate real browser workflows from the terminal |
| `skills/skill-creator/` | Meta-skill for creating and updating skills |
| `skills/skill-installer/` | Install skills from curated lists or GitHub repos |
| `skills/template/` | Starter template for new skills |
| `skills/theme-factory/` | Generate and apply visual themes |
| `skills/vercel-composition-patterns/` | Apply scalable React composition patterns |
| `skills/vercel-deploy/` | Deploy applications and sites to Vercel |
| `skills/vercel-react-best-practices/` | Apply React and Next.js performance best practices |
| `skills/vercel-react-native-skills/` | Apply React Native and Expo best practices |
| `skills/verify-before-complete/` | Require verification evidence before completion claims |
| `skills/web-design-guidelines/` | Review UI code against web interface guidelines |

## Provenance

Several skill families in this repository were derived from or inspired by external projects:

- **Compound Engineering skills** (`agent-native-architecture`, `autonomous-engineering`, `code-review-agents`, `compound-docs`): adapted from the [compound-engineering-plugin](https://github.com/everyinc/compound-engineering-plugin).
- **Vercel skills** (`vercel-composition-patterns`, `vercel-deploy`, `vercel-react-best-practices`, `vercel-react-native-skills`): based on Vercel's React and Next.js best-practice rules.
- **Obsidian skills** (`json-canvas`, `obsidian-bases`, `obsidian-markdown`): based on [Kepano's](https://github.com/kepano) Obsidian skill definitions.
- **Skill registry**: browse and discover community skills at [skills.sh](https://skills.sh).

## Specification

Full skill specification: https://agentskills.io/specification
