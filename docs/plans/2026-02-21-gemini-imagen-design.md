# Gemini Imagen Skill Design

Merge `nano-banana-pro` and `gemini-imagegen` into a single agent-agnostic image generation skill.

## Problem

Two overlapping skills exist for Gemini image generation:
- `nano-banana-pro` — strong operationally (workflow, preflight, error handling) but hardcodes `~/.codex/` paths and lacks aspect ratio/compose support
- `gemini-imagegen` — strong as reference (aspect ratios, multi-turn, composition) but has stale defaults (flash model), no invocation instructions, and missing PEP 723 metadata

Neither works across all agent harnesses (Claude Code, Codex, Gemini).

## Solution

One unified skill: `gemini-imagen`.

### Structure

```
skills/gemini-imagen/
├── SKILL.md
└── scripts/
    └── generate_image.py
```

No `requirements.txt` — use PEP 723 inline script metadata so `uv run` auto-resolves deps. No library module. No interactive scripts.

### SKILL.md

Agent-agnostic invocation using relative paths from the skill directory. Combines:

- **Operational sections** (from nano-banana-pro): draft/iterate/final workflow, filename conventions (`yyyy-mm-dd-hh-mm-ss-name.jpg`), preflight checks, common failure fixes, resolution mapping from natural language, prompt templates
- **Reference sections** (from gemini-imagegen): aspect ratio list, multi-turn refinement (API pattern only), Google Search grounding, JPEG format gotcha, prompting best practices

Defaults: model `gemini-3-pro-image-preview`, resolution `1K`, aspect ratio `1:1`, extension `.jpg`.

### Script

Single `generate_image.py` with three subcommands:

```
generate_image.py generate --prompt "..." --filename "out.jpg" [--resolution] [--aspect] [--api-key]
generate_image.py edit    --prompt "..." --filename "out.jpg" --input-image "in.jpg" [--resolution] [--aspect] [--api-key]
generate_image.py compose --prompt "..." --filename "out.jpg" --input-images "a.jpg" "b.jpg" [--resolution] [--aspect] [--api-key]
```

Key behaviors:
- PEP 723 inline metadata: `google-genai>=1.0.0`, `pillow>=10.0.0`
- Default model: `gemini-3-pro-image-preview`
- Auto-detect resolution on edit from input image dimensions
- Format-aware saving: `.jpg` saves JPEG, `.png` saves PNG explicitly
- Shared argument parsing with subcommand-specific additions
- Compose defaults to Pro model

### Cleanup

After the new skill is in place:
- Delete `skills/nano-banana-pro/`
- Delete `skills/gemini-imagegen/`
- Update skills table in `CLAUDE.md`
- `skills.json` regenerated automatically by post-tool hook
