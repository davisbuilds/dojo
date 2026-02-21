# Gemini Imagen Skill Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Merge `nano-banana-pro` and `gemini-imagegen` into a single agent-agnostic `gemini-imagen` skill.

**Architecture:** Single skill directory with one unified CLI script (`generate_image.py`) supporting three subcommands (generate, edit, compose). SKILL.md provides agent-agnostic operational instructions and API reference.

**Tech Stack:** Python 3.10+, google-genai, Pillow, PEP 723 inline metadata, uv

---

### Task 1: Create skill directory and script

**Files:**
- Create: `skills/gemini-imagen/scripts/generate_image.py`

**Step 1: Create the directory**

```bash
mkdir -p skills/gemini-imagen/scripts
```

**Step 2: Write `generate_image.py`**

Create `skills/gemini-imagen/scripts/generate_image.py` with:

- PEP 723 shebang and inline metadata:
  ```python
  #!/usr/bin/env python3
  # /// script
  # requires-python = ">=3.10"
  # dependencies = [
  #     "google-genai>=1.0.0",
  #     "pillow>=10.0.0",
  # ]
  # ///
  ```

- Three subcommands via `argparse` sub-parsers:
  - `generate`: `--prompt` (required), `--filename` (required), `--resolution` (1K/2K/4K, default 1K), `--aspect` (aspect ratio choices), `--api-key`
  - `edit`: same as generate plus `--input-image` (required)
  - `compose`: same as generate but `--input-images` (nargs="+", required) instead of `--input-image`

- Shared helper functions:
  - `get_api_key(provided_key)` — check arg then `GEMINI_API_KEY` env var
  - `save_image(image_data, output_path)` — format-aware: if path ends `.png`, save with `format="PNG"`; otherwise save as JPEG with `format="JPEG"`. Handle RGBA→RGB conversion for JPEG.
  - `build_config(resolution, aspect_ratio)` — build `GenerateContentConfig` with optional `ImageConfig`

- Model: hardcode `gemini-3-pro-image-preview` as default for all subcommands

- Edit subcommand: auto-detect resolution from input image dimensions when `--resolution` not provided (from nano-banana-pro logic: >=3000px→4K, >=1500px→2K, else 1K)

- Compose subcommand: validate 1-14 images, verify all exist

- Response processing: iterate `response.parts`, print text, save image. Exit 1 if no image generated.

**Step 3: Make script executable**

```bash
chmod +x skills/gemini-imagen/scripts/generate_image.py
```

**Step 4: Test the script parses correctly**

```bash
uv run skills/gemini-imagen/scripts/generate_image.py generate --help
uv run skills/gemini-imagen/scripts/generate_image.py edit --help
uv run skills/gemini-imagen/scripts/generate_image.py compose --help
```

Expected: each prints its help text with the correct arguments.

**Step 5: Commit**

```bash
git add skills/gemini-imagen/scripts/generate_image.py
git commit -m "feat(gemini-imagen): add unified generate_image.py script"
```

---

### Task 2: Write SKILL.md

**Files:**
- Create: `skills/gemini-imagen/SKILL.md`

**Step 1: Write the SKILL.md**

Create `skills/gemini-imagen/SKILL.md` with these sections in order:

1. **Frontmatter**: `name: gemini-imagen`, description covering generate/edit/compose/aspect ratios/resolutions

2. **Title + intro**: one line about GEMINI_API_KEY requirement

3. **Quick Reference table**: model, default resolution, default aspect ratio

4. **Usage**: agent-agnostic invocation examples for all three subcommands. Use relative path pattern: `uv run <skill-dir>/scripts/generate_image.py`. Explain the agent resolves `<skill-dir>` based on its harness.

5. **Default Workflow**: draft (1K) → iterate → final (4K) from nano-banana-pro

6. **Resolution Options**: 1K/2K/4K with natural language mapping (from nano-banana-pro)

7. **Aspect Ratios**: full list with use-case guidance (from gemini-imagegen)

8. **API Key**: check order (--api-key, then env var)

9. **Preflight + Common Failures**: from nano-banana-pro

10. **Filename Convention**: `yyyy-mm-dd-hh-mm-ss-name.jpg` pattern

11. **Prompt Templates**: generation and editing templates from nano-banana-pro

12. **Prompting Best Practices**: photorealistic, stylized, text, mockups from gemini-imagegen

13. **Advanced: Multi-Turn Refinement**: API pattern only (from gemini-imagegen), no script

14. **Advanced: Google Search Grounding**: API pattern (from gemini-imagegen)

15. **Advanced: Multiple Reference Images**: note about compose subcommand + API pattern

16. **File Format Notes**: JPEG default, PNG conversion, format verification

**Step 2: Validate the skill**

```bash
python skills/skill-creator/scripts/quick_validate.py skills/gemini-imagen
```

Expected: validation passes.

**Step 3: Commit**

```bash
git add skills/gemini-imagen/SKILL.md
git commit -m "feat(gemini-imagen): add SKILL.md with operational and reference docs"
```

---

### Task 3: Delete old skills

**Files:**
- Delete: `skills/nano-banana-pro/` (entire directory)
- Delete: `skills/gemini-imagegen/` (entire directory)

**Step 1: Remove nano-banana-pro**

```bash
rm -rf skills/nano-banana-pro
```

**Step 2: Remove gemini-imagegen**

```bash
rm -rf skills/gemini-imagegen
```

**Step 3: Verify skills.json regenerates**

The post-tool hook should regenerate `skills.json` when SKILL.md files change. If not triggered automatically:

```bash
python skills/skill-creator/scripts/quick_validate.py skills/gemini-imagen
```

Verify `skills.json` no longer contains `nano-banana-pro` or `gemini-imagegen` entries and does contain `gemini-imagen`.

**Step 4: Commit**

```bash
git add -u skills/nano-banana-pro skills/gemini-imagegen skills.json
git commit -m "refactor: remove nano-banana-pro and gemini-imagegen (replaced by gemini-imagen)"
```

---

### Task 4: Update CLAUDE.md skills table

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Edit the skills table**

In the `## Existing Skills` table in `CLAUDE.md`:
- Remove the `skills/nano-banana-pro/` row
- Remove the `skills/gemini-imagegen/` row (if present)
- Add: `| skills/gemini-imagen/ | Generate, edit, and compose images via the Gemini API |`
- Keep alphabetical order

**Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update skills table for gemini-imagen"
```

---

### Task 5: Push and verify

**Step 1: Push all commits**

```bash
git push
```

**Step 2: Verify final state**

```bash
ls skills/gemini-imagen/
# Expected: SKILL.md  scripts/

ls skills/gemini-imagen/scripts/
# Expected: generate_image.py

# Verify old skills are gone
ls skills/nano-banana-pro 2>&1
# Expected: No such file or directory

ls skills/gemini-imagegen 2>&1
# Expected: No such file or directory
```
