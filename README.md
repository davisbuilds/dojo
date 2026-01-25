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
| **`algorithmic-art/`** | **Generative Art**: Creating algorithmic art using p5.js with seeded randomness and interactive parameter exploration. |
| **`brainstorm/`** | **Brainstorming Ideas**: Helps turn ideas into fully formed designs and specs through natural collaborative dialogue. |
| **`compact-session/`** | **Context Management**: Creates session summaries to efficiently hand off context between sessions or agents. |
| **`create-cli/`** | **CLI Builder**: Specialized workflows for building command-line tools. |
| **`frontend-design/`** | **UI/UX Design**: Guidelines and workflows for creating distinctive, high-quality frontend interfaces. |
| **`gh-commit-push-pr/`** | **GitHub Automation**: Streamlined workflow to commit changes, push to a branch, and open a Pull Request in a single step. |
| **`gh-fix-issue/`** | **Issue Resolution**: End-to-end workflow for fixing GitHub issues. |
| **`gh-review-pr/`** | **Code Review**: Capabilities for reviewing Pull Requests and providing merge recommendations. |
| **`gh-triage-issues/`** | **Issue Triage**: Tools and instructions for triaging and labeling GitHub issues. |
| **`markdown-converter/`** | **Document Conversion**: Utilities to convert various document formats to and from Markdown. |
| **`nano-banana-pro/`** | **Image Generation**: Interface for generating images using Nano Banana Pro. |
| **`skill-creator/`** | **Meta-Skill**: A set of tools to initialize, validate, and package *new* skills. |
| **`theme-factory/`** | **Theming**: Tools for generating color themes and design tokens. |
| **`verify-before-complete/`** | **Quality Control**: Enforces a "verification before completion" protocol to ensure no work is marked done without evidence. |

## Creating a New Skill

You can use the `skill-creator` scripts to scaffold a new skill:

```bash
# Create a new skill directory
python skill-creator/scripts/init_skill.py <skill-name> --path ./

# Validate your skill structure
python skill-creator/scripts/quick_validate.py <skill-name>
```

## Usage

When working with an agent that supports these skills:
1. **Trigger**: The agent will select a skill based on its `description` in `SKILL.md` when it matches your request.
2. **Follow Instructions**: The agent will then follow the specific protocols defined in the skill's body.
3. **Tools**: Some skills may require specific tools (like `gh` CLI or `python`) to be installed in your environment.

## Resources

- **`AGENTS.md`**: Detailed guidance for AI agents on how to use this repository.
- **`CLAUDE.md`**: Specific guidance for Claude Code.

## Acknowledgements

- [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)
- [superpowers](https://github.com/obra/superpowers)
- [agent-scripts](https://github.com/steipete/agent-scripts)
- [anthropics/skills](https://github.com/anthropics/skills)
