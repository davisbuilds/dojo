#!/usr/bin/env python3
"""Generate an HTML preview page for a theme.

Reads a theme JSON and populates the preview template with color swatches,
typography specimens, component examples, and a CSS variable reference.

Usage:
    python preview_theme.py ocean-depths                 # creates ocean-depths-preview.html
    python preview_theme.py ocean-depths -o preview.html # custom output path
    python preview_theme.py --all                        # generate previews for all themes
    python preview_theme.py --list                       # list available themes
"""

import argparse
import json
import os
import sys
import glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
THEMES_DIR = os.path.join(SCRIPT_DIR, "..", "themes")
TEMPLATE_PATH = os.path.join(SCRIPT_DIR, "..", "assets", "theme-template.html")


def find_theme(name_or_path):
    """Resolve a theme name or file path to a loaded JSON dict."""
    if os.path.isfile(name_or_path):
        with open(name_or_path) as f:
            return json.load(f)

    slug = name_or_path.lower().replace(" ", "-")
    json_path = os.path.join(THEMES_DIR, f"{slug}.json")
    if os.path.isfile(json_path):
        with open(json_path) as f:
            return json.load(f)

    print(f"Error: theme '{name_or_path}' not found.", file=sys.stderr)
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


def load_template():
    """Load the HTML preview template."""
    if not os.path.isfile(TEMPLATE_PATH):
        print(f"Error: template not found at {TEMPLATE_PATH}", file=sys.stderr)
        sys.exit(1)
    with open(TEMPLATE_PATH) as f:
        return f.read()


def render_css_vars(theme):
    """Render CSS variable declarations for the :root block."""
    css = theme.get("css", {})
    heading = theme.get("typography", {}).get("heading", {})
    body = theme.get("typography", {}).get("body", {})

    lines = []
    for prop, value in css.items():
        lines.append(f"    {prop}: {value};")
    if heading:
        lines.append(f"    --theme-font-heading: {heading.get('family', 'sans-serif')};")
        lines.append(f"    --theme-font-heading-weight: {heading.get('weight', 'bold')};")
    if body:
        lines.append(f"    --theme-font-body: {body.get('family', 'sans-serif')};")
        lines.append(f"    --theme-font-body-weight: {body.get('weight', 'normal')};")

    return "\n".join(lines)


def render_swatches(theme):
    """Render color swatch HTML blocks."""
    colors = theme.get("colors", [])
    swatches = []
    for c in colors:
        swatch = f"""      <div class="swatch">
        <div class="swatch__color" style="background: {c['hex']};"></div>
        <div class="swatch__name">{c['name']}</div>
        <div class="swatch__hex">{c['hex']}</div>
        <div class="swatch__role">{c.get('role', '')}</div>
      </div>"""
        swatches.append(swatch)
    return "\n".join(swatches)


def render_vars_ref(theme):
    """Render the CSS variables reference section."""
    css = theme.get("css", {})
    heading = theme.get("typography", {}).get("heading", {})
    body = theme.get("typography", {}).get("body", {})

    lines = []
    for prop, value in css.items():
        lines.append(
            f'        <span class="vars-ref__prop">{prop}</span>: '
            f'<span class="vars-ref__val">{value}</span>;'
        )
    if heading:
        lines.append(
            f'        <span class="vars-ref__prop">--theme-font-heading</span>: '
            f'<span class="vars-ref__val">{heading.get("family", "sans-serif")}</span>;'
        )
    if body:
        lines.append(
            f'        <span class="vars-ref__prop">--theme-font-body</span>: '
            f'<span class="vars-ref__val">{body.get("family", "sans-serif")}</span>;'
        )

    return "<br>\n".join(lines)


def generate_preview(theme, output_path):
    """Generate a preview HTML file for a theme."""
    template = load_template()

    html = template.replace("{{THEME_NAME}}", theme["name"])
    html = html.replace("{{THEME_DESC}}", theme.get("description", ""))
    html = html.replace("{{THEME_MODE}}", theme.get("mode", "light"))
    html = html.replace("{{CSS_VARS}}", render_css_vars(theme))
    html = html.replace("{{SWATCHES}}", render_swatches(theme))
    html = html.replace("{{VARS_REF}}", render_vars_ref(theme))
    html = html.replace("{{USE_CASES}}", ", ".join(theme.get("use_cases", [])))

    with open(output_path, "w") as f:
        f.write(html)

    return os.path.abspath(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Generate an HTML preview page for a theme."
    )
    parser.add_argument("theme", nargs="?", help="Theme name or path to JSON file")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--all", action="store_true", help="Generate previews for all themes")
    parser.add_argument("--list", action="store_true", help="List available themes")
    parser.add_argument(
        "--output-dir", "-d",
        default=".",
        help="Output directory for --all mode (default: current directory)"
    )

    args = parser.parse_args()

    if args.list:
        for slug in list_themes():
            theme = find_theme(slug)
            mode = theme.get("mode", "?")
            print(f"  {slug:<22} ({mode})  {theme.get('description', '')[:60]}")
        return

    if args.all:
        os.makedirs(args.output_dir, exist_ok=True)
        for slug in list_themes():
            theme = find_theme(slug)
            out = os.path.join(args.output_dir, f"{slug}-preview.html")
            path = generate_preview(theme, out)
            print(f"  {slug:<22} -> {path}")
        print(f"\nGenerated {len(list_themes())} previews.")
        return

    if not args.theme:
        parser.error("provide a theme name, --all, or --list")

    theme = find_theme(args.theme)
    slug = theme.get("slug", args.theme.lower().replace(" ", "-"))
    output = args.output or f"{slug}-preview.html"
    path = generate_preview(theme, output)
    print(f"Preview: {path}")


if __name__ == "__main__":
    main()
