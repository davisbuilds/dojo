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
├── commands/          # Optional: command-wrapper docs for slash-style entrypoints
├── scripts/           # Optional: Executable scripts (Python/Bash)
├── references/        # Optional: Documentation files
└── assets/            # Optional: Templates, images, or other assets
```

The `SKILL.md` file contains the "brain" of the skill—the prompt instructions that are loaded into the agent's context when the skill is triggered.

## Available Skills

44 skills across categories: GitHub workflows, code review, content creation, dev workflows, platform integrations, knowledge management, and meta/skill tooling. See [docs/system/FEATURES.md](docs/system/FEATURES.md) for the full catalog.

## Hooks

Seven hooks in `hooks/` enforce skill quality, inject session context, and nudge agents to capture learnings (skill catalog, frontmatter validation, manifest regeneration, git checks, structure checks, session retro reminder). Configured in `.claude/settings.json` and `.agents/settings.json`. See [docs/system/ARCHITECTURE.md](docs/system/ARCHITECTURE.md) for details.

## Prerequisites

### System tools

The hooks require `git`, `jq`, `python3`, `sed`, and `grep`. These ship with most systems. Verify with:

```bash
for cmd in git jq python3 sed grep; do command -v "$cmd" >/dev/null && echo "$cmd: ok" || echo "$cmd: MISSING"; done
```

If everything prints `ok`, skip ahead to [Python dependencies](#python-dependencies). Otherwise install the missing tool(s) via your package manager (e.g. `brew install jq`, `apt install jq`).

### Python dependencies

Install the core Python dependencies (currently just **PyYAML**, used by the validation and manifest-generation scripts the hooks invoke):

```bash
pip install -r requirements.txt
```

#### Optional (skill-specific)

Some skills bundle their own dependencies. Uncomment the relevant sections in `requirements.txt` or install manually:

| Skill | Extra packages |
|-------|---------------|
| `skills/gpt-imagen/` | `openai>=1.0.0`, `Pillow>=10.0.0` |
| `skills/gemini-imagen/` | `google-genai>=1.0.0`, `Pillow>=10.0.0` |

These skills also require API keys set as environment variables (`OPENAI_API_KEY`, `GEMINI_API_KEY`).

## Creating a New Skill

You can use the `skill-creator` scripts to scaffold a new skill:

```bash
# Create a new skill directory
python skills/skill-creator/scripts/init_skill.py <skill-name> --path ./ \
  --resources scripts,references --examples

# Validate your skill structure (works with both `python` and `python3`)
python skills/skill-creator/scripts/quick_validate.py <skill-name>

# Package a skill for distribution
python skills/skill-creator/scripts/package_skill.py <skill-name> ./dist

# Optional: generate OpenAI/Codex metadata add-on
python skills/skill-creator/scripts/generate_openai_yaml.py <skill-name> \
  --interface default_prompt="Use $<skill-name> to help with this task."
```

The validator uses a polyglot shebang so it can also be run directly and will work in environments that provide either `python` or `python3`.

## Usage

When working with an agent that supports these skills:
1. **Trigger**: The agent will select a skill based on its `description` in `SKILL.md` when it matches your request.
2. **Follow Instructions**: The agent will then follow the specific protocols defined in the skill's body.
3. **Tools**: Some skills may require specific tools (like `gh` CLI or `python`) to be installed in your environment.

### Skill Installer Targets

`skills/skill-installer` supports both Codex and Claude Code destinations:

```bash
# Install to Claude Code skills (~/.claude/skills by default)
python3 skills/skill-installer/scripts/install-skill-from-github.py \
  --agent claude \
  --repo openai/skills \
  --path skills/.curated/create-cli
```

### Command Wrappers

Some skills include optional `commands/*.md` wrappers for slash-style entrypoints. See [docs/system/FEATURES.md](docs/system/FEATURES.md) for the full list.

## Resources

- **`AGENTS.md`**: Guidance for AI agents on how to use this repository (single source of truth).
- **`CLAUDE.md`**: Symlink to `AGENTS.md` so Claude Code picks up the same instructions.
- **`requirements.txt`**: Python dependencies for hooks and scripts (core + optional per-skill extras).

## Documentation

- Contributor workflow and PR expectations: [CONTRIBUTING.md](CONTRIBUTING.md)
- Agent implementation guidance: [AGENTS.md](AGENTS.md)
- Architecture and skill structure: [docs/system/ARCHITECTURE.md](docs/system/ARCHITECTURE.md)
- Skills catalog and feature reference: [docs/system/FEATURES.md](docs/system/FEATURES.md)
- Setup and operations: [docs/system/OPERATIONS.md](docs/system/OPERATIONS.md)
- Product vision and principles: [docs/project/VISION.md](docs/project/VISION.md)
- Product roadmap snapshot: [docs/project/ROADMAP.md](docs/project/ROADMAP.md)
- Git history and branch policy: [docs/project/GIT_HISTORY_POLICY.md](docs/project/GIT_HISTORY_POLICY.md)

## Acknowledgements

- [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)
- [superpowers](https://github.com/obra/superpowers)
- [agent-scripts](https://github.com/steipete/agent-scripts)
- [anthropics/skills](https://github.com/anthropics/skills)
- [compound-engineering-plugin](https://github.com/everyinc/compound-engineering-plugin) — source of the code-review-agents, autonomous-engineering, agent-native-architecture, and compound-docs skills
- [Vercel skills](https://github.com/vercel/next.js) — React, Next.js, React Native best-practice rules and composition patterns, plus preview deployment debugging workflows
- [Kepano's Obsidian skills](https://github.com/kepano) — Obsidian Markdown, Bases, and JSON Canvas skill references
- [skills.sh](https://skills.sh) — community skill registry and discovery
