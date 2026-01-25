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
python skill-creator/scripts/init_skill.py <skill-name> --path <output-directory>
```

Creates a skill directory with template SKILL.md and example resource directories.

### Validate a skill

```bash
python skill-creator/scripts/quick_validate.py <path/to/skill-folder>
```

Checks frontmatter format, required fields, naming conventions.

### Package a skill for distribution

```bash
python skill-creator/scripts/package_skill.py <path/to/skill-folder> [output-directory]
```

Validates and creates a `.skill` file (zip format) for distribution.

## Key Design Principles

1. **Concise is key**: The context window is shared. Only add information the agent doesn't already have.

2. **Progressive disclosure**: Metadata always loaded (~100 words) → SKILL.md body on trigger (<5k words) → bundled resources as needed.

3. **Degrees of freedom**: Match specificity to task fragility - high freedom for flexible tasks (text instructions), low freedom for fragile operations (specific scripts).

4. **Description is the trigger**: The `description` field determines when the agent uses the skill. Include both what it does AND specific scenarios/triggers.

## Existing Skills

| Skill                 | Purpose                                      |
| --------------------- | -------------------------------------------- |
| `algorithmic-art/`    | Create generative art with p5.js             |
| `skill-creator/`      | Meta-skill for creating new skills           |
| `gh-review-pr/`       | Review GitHub PRs with merge recommendations |
| `gh-fix-issue/`       | Fix GitHub issues end-to-end                 |
| `gh-triage-issues/`   | Triage and label GitHub issues               |
| `compact-session/`    | Create session summaries for context handoff |
| `frontend-design/`    | Create distinctive frontend interfaces       |
| `create-cli/`         | Build command-line tools                     |
| `nano-banana-pro/`    | Image generation with Nano Banana Pro        |
| `theme-factory/`      | Generate color themes                        |
| `markdown-converter/` | Convert markdown documents                   |

## Specification

Full skill specification: https://agentskills.io/specification
