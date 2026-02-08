#!/usr/bin/env python3
"""Generate CSS custom properties from a theme JSON file.

Reads a theme's JSON definition and outputs CSS custom properties that can
be dropped into any stylesheet. Supports multiple output formats.

Usage:
    python generate_css.py ocean-depths               # by theme name
    python generate_css.py ../themes/ocean-depths.json # by file path
    python generate_css.py ocean-depths --format vars  # just the variables
    python generate_css.py ocean-depths --format full  # variables + base styles
    python generate_css.py --all                       # all themes as vars
    python generate_css.py ocean-depths -o theme.css   # write to file
"""

import argparse
import json
import os
import sys
import glob

THEMES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "themes")


def find_theme(name_or_path):
    """Resolve a theme name or file path to a loaded JSON dict."""
    # Direct path
    if os.path.isfile(name_or_path):
        with open(name_or_path) as f:
            return json.load(f)

    # Name lookup in themes directory
    slug = name_or_path.lower().replace(" ", "-")
    json_path = os.path.join(THEMES_DIR, f"{slug}.json")
    if os.path.isfile(json_path):
        with open(json_path) as f:
            return json.load(f)

    print(f"Error: theme '{name_or_path}' not found.", file=sys.stderr)
    print(f"Looked for: {json_path}", file=sys.stderr)
    available = list_themes()
    if available:
        print(f"Available: {', '.join(available)}", file=sys.stderr)
    sys.exit(1)


def list_themes():
    """Return sorted list of available theme slugs."""
    pattern = os.path.join(THEMES_DIR, "*.json")
    return sorted(
        os.path.splitext(os.path.basename(f))[0]
        for f in glob.glob(pattern)
    )


def generate_vars(theme):
    """Generate CSS custom properties block."""
    css_vars = theme.get("css", {})
    if not css_vars:
        print("Warning: theme has no 'css' field.", file=sys.stderr)
        return ""

    lines = [f"  /* Theme: {theme['name']} */"]
    for prop, value in css_vars.items():
        lines.append(f"  {prop}: {value};")

    heading = theme.get("typography", {}).get("heading", {})
    body = theme.get("typography", {}).get("body", {})
    if heading:
        lines.append(f"  --theme-font-heading: {heading.get('family', 'sans-serif')};")
        lines.append(f"  --theme-font-heading-weight: {heading.get('weight', 'bold')};")
    if body:
        lines.append(f"  --theme-font-body: {body.get('family', 'sans-serif')};")
        lines.append(f"  --theme-font-body-weight: {body.get('weight', 'normal')};")

    return ":root {\n" + "\n".join(lines) + "\n}"


def generate_full(theme):
    """Generate CSS variables plus base element styles."""
    vars_block = generate_vars(theme)

    base_styles = """
body {
  background-color: var(--theme-bg);
  color: var(--theme-text);
  font-family: var(--theme-font-body), sans-serif;
  font-weight: var(--theme-font-body-weight);
  line-height: 1.6;
  margin: 0;
}

h1, h2, h3, h4, h5, h6 {
  font-family: var(--theme-font-heading), sans-serif;
  font-weight: var(--theme-font-heading-weight);
  color: var(--theme-text);
  line-height: 1.2;
}

a {
  color: var(--theme-accent);
}

a:hover {
  opacity: 0.8;
}

.surface {
  background-color: var(--theme-surface);
  border-radius: 4px;
}

.text-muted {
  color: var(--theme-muted);
}

.accent {
  color: var(--theme-accent);
}

.btn-primary {
  background-color: var(--theme-accent);
  color: var(--theme-bg);
  border: none;
  padding: 0.6rem 1.4rem;
  font-family: var(--theme-font-body), sans-serif;
  font-size: 0.85rem;
  cursor: pointer;
  border-radius: 4px;
}

.btn-primary:hover {
  opacity: 0.9;
}"""

    return vars_block + "\n" + base_styles


def generate_all_vars():
    """Generate CSS variables for all themes, each scoped by data attribute."""
    themes = list_themes()
    blocks = []
    for slug in themes:
        theme = find_theme(slug)
        css_vars = theme.get("css", {})
        heading = theme.get("typography", {}).get("heading", {})
        body = theme.get("typography", {}).get("body", {})

        lines = [f"  /* {theme['name']} */"]
        for prop, value in css_vars.items():
            lines.append(f"  {prop}: {value};")
        if heading:
            lines.append(f"  --theme-font-heading: {heading.get('family', 'sans-serif')};")
            lines.append(f"  --theme-font-heading-weight: {heading.get('weight', 'bold')};")
        if body:
            lines.append(f"  --theme-font-body: {body.get('family', 'sans-serif')};")
            lines.append(f"  --theme-font-body-weight: {body.get('weight', 'normal')};")

        selector = f'[data-theme="{slug}"]'
        blocks.append(f"{selector} {{\n" + "\n".join(lines) + "\n}")

    return "\n\n".join(blocks)


def main():
    parser = argparse.ArgumentParser(
        description="Generate CSS custom properties from theme JSON."
    )
    parser.add_argument("theme", nargs="?", help="Theme name or path to JSON file")
    parser.add_argument(
        "--format", "-f",
        choices=["vars", "full"],
        default="vars",
        help="Output format: 'vars' (custom properties only) or 'full' (vars + base styles)"
    )
    parser.add_argument("--output", "-o", help="Write to file instead of stdout")
    parser.add_argument("--all", action="store_true", help="Generate variables for all themes")
    parser.add_argument("--list", action="store_true", help="List available themes")

    args = parser.parse_args()

    if args.list:
        for slug in list_themes():
            theme = find_theme(slug)
            mode = theme.get("mode", "?")
            print(f"  {slug:<22} ({mode})")
        return

    if args.all:
        css = generate_all_vars()
    elif args.theme:
        theme = find_theme(args.theme)
        if args.format == "full":
            css = generate_full(theme)
        else:
            css = generate_vars(theme)
    else:
        parser.error("provide a theme name, --all, or --list")
        return

    if args.output:
        with open(args.output, "w") as f:
            f.write(css + "\n")
        print(f"Written to {os.path.abspath(args.output)}", file=sys.stderr)
    else:
        print(css)


if __name__ == "__main__":
    main()
