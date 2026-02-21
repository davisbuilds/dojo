---
name: gemini-imagen
description: "Generate, edit, and compose images via the Gemini API. Use when creating images from text, editing existing images, composing multiple images, or generating images with specific aspect ratios and resolutions."
---

# Gemini Imagen

Generate and edit images using Google's Gemini API. The environment variable `GEMINI_API_KEY` must be set.

## Quick Reference

| Setting      | Default                        | Options                                                    |
| ------------ | ------------------------------ | ---------------------------------------------------------- |
| Model        | `gemini-3-pro-image-preview`   | -                                                          |
| Resolution   | 1K                             | 1K, 2K, 4K                                                 |
| Aspect Ratio | 1:1                            | 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9      |

## Usage

```bash
uv run <skill-dir>/scripts/generate_image.py generate --prompt "a sunset" --filename "2026-02-21-14-30-00-sunset.jpg"
uv run <skill-dir>/scripts/generate_image.py edit --prompt "add clouds" --input-image photo.jpg --filename "2026-02-21-14-35-00-cloudy.jpg"
uv run <skill-dir>/scripts/generate_image.py compose --prompt "merge these scenes" --input-images a.jpg b.jpg --filename "2026-02-21-14-40-00-merged.jpg"
```

Run from the user's working directory so images save where expected, not in the skill directory.

## Default Workflow

Follow a draft-iterate-final pattern:

1. **Draft (1K):** Generate with default resolution for a quick feedback loop.
2. **Iterate:** Adjust the prompt in small diffs. Use a new filename per run. For editing, keep the same `--input-image`.
3. **Final (4K):** Only when the prompt is locked. Add `--resolution 4K`.

## Resolution Options

| Flag           | Approximate Size | When to Use                        |
| -------------- | ---------------- | ---------------------------------- |
| `--resolution 1K` | ~1024px       | Drafts, quick iteration            |
| `--resolution 2K` | ~2048px       | Medium-quality deliverables        |
| `--resolution 4K` | ~4096px       | Final output, print, high-res use  |

Natural language mapping:

- No mention of resolution -> 1K
- "low resolution", "1080p", "1K" -> 1K
- "2K", "2048", "medium" -> 2K
- "high resolution", "hi-res", "4K", "ultra" -> 4K

The `edit` subcommand auto-detects resolution from the input image dimensions when `--resolution` is not provided.

## Aspect Ratios

| Ratio  | Use Case                       |
| ------ | ------------------------------ |
| 1:1    | Square (social media, icons)   |
| 2:3    | Portrait photo standard        |
| 3:2    | Landscape photo standard       |
| 3:4    | Portrait display, presentation |
| 4:3    | Landscape display, presentation|
| 4:5    | Portrait photo (Instagram)     |
| 5:4    | Landscape photo                |
| 9:16   | Vertical video (Stories, Reels)|
| 16:9   | Horizontal video (YouTube)     |
| 21:9   | Ultra-wide, panoramic          |

## API Key

The script checks for an API key in this order:

1. `--api-key` argument
2. `GEMINI_API_KEY` environment variable

## Preflight and Common Failures

### Preflight Checklist

```bash
command -v uv          # must exist
test -n "$GEMINI_API_KEY"  # or pass --api-key
# For edit: verify input image exists
test -f <input-image-path>
```

### Common Failures

| Error Message                        | Cause and Fix                                              |
| ------------------------------------ | ---------------------------------------------------------- |
| "Error: No API key provided."        | Set `GEMINI_API_KEY` or pass `--api-key`                   |
| "Error loading input image:"         | Wrong path; verify the `--input-image` path exists         |
| quota / permission / 403             | Wrong key, no API access, or quota exceeded                |

## Filename Convention

Pattern: `yyyy-mm-dd-hh-mm-ss-name.jpg`

- **Timestamp:** current date and time in 24-hour format
- **Name:** descriptive lowercase with hyphens, 1-5 words
- **Extension:** `.jpg` by default (Gemini returns JPEG)

Examples:

- `2026-02-21-14-30-00-sunset.jpg`
- `2026-02-21-09-15-42-product-hero-shot.jpg`
- `2026-02-21-16-05-11-blue-gradient-bg.jpg`

## Prompt Templates

### Generation

> "Create an image of: \<subject\>. Style: \<style\>. Composition: \<camera/shot\>. Lighting: \<lighting\>. Background: \<background\>. Color palette: \<palette\>. Avoid: \<list\>."

### Editing (preserve everything else)

> "Change ONLY: \<single change\>. Keep identical: subject, composition/crop, pose, lighting, color palette, background, text, and overall style. Do not add new objects. If text exists, keep it unchanged."

## Prompting Best Practices

**Photorealistic:** Include camera details -- lens type, lighting, angle, mood.

> "A plate of sushi on a dark slate counter, shot with a 50mm f/1.4 lens, soft window light from the left, shallow depth of field, warm tones, overhead angle."

**Stylized Art:** Specify style explicitly -- kawaii, cel-shading, bold outlines.

> "A fox sitting in a forest, kawaii style, soft pastels, thick black outlines, big expressive eyes, flat shading, no gradients."

**Text in Images:** Be explicit about font style and placement.

> "A motivational poster with the text 'KEEP GOING' in bold white sans-serif centered on a dark blue gradient background."

**Product Mockups:** Describe lighting setup and surface.

> "A white coffee mug on a marble countertop, studio lighting with a soft key light from the upper right and a fill light from the left, clean white background, slight reflection on the surface."

## Advanced: Multi-Turn Refinement

The script runs single-turn calls. For iterative refinement within a single conversation, use the chat API directly:

```python
from google.genai import types

chat = client.chats.create(
    model="gemini-3-pro-image-preview",
    config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]),
)
response = chat.send_message("Create a logo for 'Acme Corp'")
response = chat.send_message("Make the text bolder and add a blue gradient")
```

## Advanced: Google Search Grounding

Use Google Search grounding to generate images informed by real-world data:

```python
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="Generate an image of the latest Tesla Model Y in a showroom",
    config=types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        tools=[{"google_search": {}}],
    ),
)
```

Note: Google Search grounding does not work with image-only response mode.

## Advanced: Multiple Reference Images

The `compose` subcommand handles multi-image input (up to 14 images). For direct API usage:

```python
from PIL import Image

images = [Image.open(p) for p in ["ref1.jpg", "ref2.jpg", "ref3.jpg"]]
contents = ["Combine these into a single panoramic scene"] + images

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=contents,
    config=config,
)
```

The API supports up to 14 input images per request.

## File Format Notes

- Gemini returns JPEG by default -- always use `.jpg` for output filenames.
- The script handles format automatically: a `.png` extension saves as PNG, anything else saves as JPEG.
- To convert to PNG: use `--filename` with a `.png` extension.
- Verification: run `file image.jpg` to check the actual format on disk.
- All generated images include SynthID watermarks embedded by the Gemini API.
