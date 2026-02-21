#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
#     "pillow>=10.0.0",
# ]
# ///
"""
Unified image generation, editing, and composition using the Gemini API.

Subcommands:
    generate  Create an image from a text prompt.
    edit      Edit an existing image with a text instruction.
    compose   Combine multiple images with a text instruction.

Usage:
    uv run generate_image.py generate --prompt "a sunset" --filename sunset.png
    uv run generate_image.py edit --prompt "add clouds" --input-image photo.png --filename edited.png
    uv run generate_image.py compose --prompt "merge styles" --input-images a.png b.png --filename merged.png
"""

import argparse
import os
import sys
from pathlib import Path

MODEL = "gemini-3-pro-image-preview"

ASPECT_CHOICES = ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"]
RESOLUTION_CHOICES = ["1K", "2K", "4K"]


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def get_api_key(provided_key: str | None) -> str:
    """Return API key from arg or env. Exit 1 if neither is available."""
    key = provided_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        print("Error: No API key provided.", file=sys.stderr)
        print("Please either:", file=sys.stderr)
        print("  1. Provide --api-key argument", file=sys.stderr)
        print("  2. Set GEMINI_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)
    return key


def save_image(pil_image, output_path: Path) -> None:
    """Save a PIL image, choosing format from the file extension.

    PNG  -> saved as PNG (preserves RGBA).
    Other -> saved as JPEG (RGBA converted to RGB with white background).
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if str(output_path).lower().endswith(".png"):
        pil_image.save(str(output_path), format="PNG")
    else:
        # JPEG cannot handle RGBA
        if pil_image.mode == "RGBA":
            rgb = pil_image.new("RGB", pil_image.size, (255, 255, 255))
            rgb.paste(pil_image, mask=pil_image.split()[3])
            pil_image = rgb
        elif pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")
        pil_image.save(str(output_path), format="JPEG")


def build_config(resolution: str | None, aspect_ratio: str | None):
    """Build a GenerateContentConfig with optional ImageConfig."""
    from google.genai import types

    config_kwargs: dict = {"response_modalities": ["TEXT", "IMAGE"]}

    image_config_kwargs: dict = {}
    if resolution:
        image_config_kwargs["image_size"] = resolution
    if aspect_ratio:
        image_config_kwargs["aspect_ratio"] = aspect_ratio

    if image_config_kwargs:
        config_kwargs["image_config"] = types.ImageConfig(**image_config_kwargs)

    return types.GenerateContentConfig(**config_kwargs)


def process_response(response, output_path: Path) -> None:
    """Iterate response parts, print text, and save the first image."""
    from PIL import Image as PILImage
    from io import BytesIO

    image_saved = False
    for part in response.parts:
        if part.text is not None:
            print(f"Model response: {part.text}")
        elif part.inline_data is not None:
            image_data = part.inline_data.data
            if isinstance(image_data, str):
                import base64
                image_data = base64.b64decode(image_data)
            image = PILImage.open(BytesIO(image_data))
            save_image(image, output_path)
            image_saved = True

    if image_saved:
        print(f"\nImage saved: {output_path.resolve()}")
    else:
        print("Error: No image was generated in the response.", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------

def cmd_generate(args: argparse.Namespace) -> None:
    """Handle the 'generate' subcommand."""
    api_key = get_api_key(args.api_key)

    from google import genai

    client = genai.Client(api_key=api_key)
    output_path = Path(args.filename)
    config = build_config(args.resolution, args.aspect)

    print(f"Generating image with resolution {args.resolution or '1K'}...")

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=args.prompt,
            config=config,
        )
        process_response(response, output_path)
    except Exception as e:
        print(f"Error generating image: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_edit(args: argparse.Namespace) -> None:
    """Handle the 'edit' subcommand."""
    api_key = get_api_key(args.api_key)

    from google import genai
    from PIL import Image as PILImage

    client = genai.Client(api_key=api_key)
    output_path = Path(args.filename)

    # Load input image
    try:
        input_image = PILImage.open(args.input_image)
        print(f"Loaded input image: {args.input_image}")
    except Exception as e:
        print(f"Error loading input image: {e}", file=sys.stderr)
        sys.exit(1)

    # Auto-detect resolution when not explicitly provided
    resolution = args.resolution
    if resolution is None:
        width, height = input_image.size
        max_dim = max(width, height)
        if max_dim >= 3000:
            resolution = "4K"
        elif max_dim >= 1500:
            resolution = "2K"
        else:
            resolution = "1K"
        print(f"Auto-detected resolution: {resolution} (from input {width}x{height})")

    config = build_config(resolution, args.aspect)
    print(f"Editing image with resolution {resolution}...")

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=[input_image, args.prompt],
            config=config,
        )
        process_response(response, output_path)
    except Exception as e:
        print(f"Error editing image: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_compose(args: argparse.Namespace) -> None:
    """Handle the 'compose' subcommand."""
    api_key = get_api_key(args.api_key)

    # Validate image count
    if len(args.input_images) < 1:
        print("Error: At least one input image is required.", file=sys.stderr)
        sys.exit(1)
    if len(args.input_images) > 14:
        print("Error: Maximum 14 input images supported.", file=sys.stderr)
        sys.exit(1)

    # Verify all files exist before calling API
    for path in args.input_images:
        if not os.path.exists(path):
            print(f"Error: Image not found: {path}", file=sys.stderr)
            sys.exit(1)

    from google import genai
    from PIL import Image as PILImage

    client = genai.Client(api_key=api_key)
    output_path = Path(args.filename)

    images = [PILImage.open(p) for p in args.input_images]
    contents = [args.prompt] + images

    config = build_config(args.resolution, args.aspect)
    print(f"Composing {len(images)} image(s) with resolution {args.resolution or '1K'}...")

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=config,
        )
        process_response(response, output_path)
    except Exception as e:
        print(f"Error composing images: {e}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def _add_common_args(parser: argparse.ArgumentParser) -> None:
    """Add arguments shared by all subcommands."""
    parser.add_argument("--prompt", "-p", required=True, help="Text prompt / instruction")
    parser.add_argument("--filename", "-f", required=True, help="Output filename (e.g. result.png)")
    parser.add_argument(
        "--resolution", "-r",
        choices=RESOLUTION_CHOICES,
        default=None,
        help="Output resolution: 1K (default), 2K, or 4K",
    )
    parser.add_argument(
        "--aspect", "-a",
        choices=ASPECT_CHOICES,
        help="Output aspect ratio (e.g. 16:9)",
    )
    parser.add_argument(
        "--api-key", "-k",
        help="Gemini API key (overrides GEMINI_API_KEY env var)",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate, edit, or compose images with the Gemini API",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # generate
    gen_parser = subparsers.add_parser("generate", help="Create an image from a text prompt")
    _add_common_args(gen_parser)

    # edit
    edit_parser = subparsers.add_parser("edit", help="Edit an existing image")
    _add_common_args(edit_parser)
    edit_parser.add_argument(
        "--input-image", "-i", required=True,
        help="Path to the input image to edit",
    )

    # compose
    compose_parser = subparsers.add_parser("compose", help="Combine multiple images")
    _add_common_args(compose_parser)
    compose_parser.add_argument(
        "--input-images", "-I", nargs="+", required=True,
        help="Paths to input images (1-14)",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    dispatch = {
        "generate": cmd_generate,
        "edit": cmd_edit,
        "compose": cmd_compose,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
