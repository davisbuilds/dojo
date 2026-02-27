# AGENTS.md

This file provides guidance to AI agents when working with code in this repository.

## Overview

This repository contains Agent Skills - modular packages that extend an agent's capabilities with specialized knowledge, workflows, and tool integrations. Skills transform a general-purpose agent into a specialized agent for specific domains or tasks.

## Skill Structure

Every skill follows this structure:

```
skill-name/
├── SKILL.md           # Required: frontmatter + instructions
├── commands/          # Optional: command-wrapper docs for slash-style entrypoints
├── scripts/           # Optional: executable Python/Bash code
├── references/        # Optional: documentation loaded into context as needed
└── assets/            # Optional: templates, images, fonts for output
```

### SKILL.md Requirements

- **Frontmatter** (YAML): Must include `name` (hyphen-case, max 64 chars) and `description` (max 1024 chars, no angle brackets)
- **Body** (Markdown): Instructions loaded only after the skill triggers
- Allowed frontmatter fields: `name`, `description`, `license`, `allowed-tools`, `metadata`, `compatibility`

## Commands

### Create a new skill

```bash
python skills/skill-creator/scripts/init_skill.py <skill-name> --path <output-directory> [--resources scripts,references,assets] [--examples] [--with-openai-agent]
```

Creates a skill directory with a template SKILL.md and optional resource/platform add-ons.

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

### Generate OpenAI metadata (optional add-on)

```bash
python skills/skill-creator/scripts/generate_openai_yaml.py <path/to/skill-folder> [--interface key=value]
```

Creates or updates `agents/openai.yaml` as optional platform-specific metadata.

## Dependencies

Install the core Python dependencies before running hooks or skill-management scripts:

```bash
pip install -r requirements.txt
```

The hooks also require these system tools: `git`, `jq`, `python3`, `sed`, and `grep`.

Some skills have additional optional dependencies (e.g. `openai`, `google-genai`, `Pillow`). See `requirements.txt` for details.

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
| `post-tool-use-validate-implementation-plan.sh` | PostToolUse (Write\|Edit) | Validates `docs/plans/*-implementation.md` against `writing-plans` schema after write/edit |
| `stop-hook-git-check.sh` | Stop | Blocks if there are uncommitted changes, untracked files, or unpushed commits |
| `stop-hook-skill-structure.sh` | Stop | Validates that modified skill directories have SKILL.md and matching directory/frontmatter names |
| `stop-hook-session-learnings.sh` | Stop | Reminds agent to run `/learnings` to capture non-obvious session learnings before ending |

## Existing Skills

42 skills in `skills/`. The full catalog with descriptions is in `docs/system/FEATURES.md`. The auto-generated `skills.json` manifest is the runtime source of truth.

## Specification

Full skill specification: `spec/agent-skills-spec.md`

## Command Wrappers

Some skills include `commands/*.md` wrappers for slash-style entrypoints. See `docs/system/FEATURES.md` for the current list. In harnesses that do not expose command files, these wrappers remain canonical runbooks.
