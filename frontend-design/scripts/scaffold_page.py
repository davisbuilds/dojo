#!/usr/bin/env python3
"""Generate a starter HTML page with a specific aesthetic direction.

Produces a single-file HTML page with fonts, colors, and base styles
pre-configured for the chosen aesthetic. The output is a working starting
point, not a finished product.

Usage:
    python scaffold_page.py --aesthetic brutalist --title "My Project"
    python scaffold_page.py --aesthetic luxury --dark
    python scaffold_page.py --list
"""

import argparse
import sys
import os
from datetime import datetime

AESTHETICS = {
    "brutalist": {
        "fonts_import": "https://fonts.googleapis.com/css2?family=Bebas+Neue&family=JetBrains+Mono:wght@400;500;700&display=swap",
        "font_display": "'Bebas Neue', sans-serif",
        "font_body": "'JetBrains Mono', monospace",
        "light": {
            "bg": "#f5f5f5", "surface": "#ffffff", "text": "#111111",
            "muted": "#666666", "accent": "#ff2d2d",
        },
        "dark": {
            "bg": "#111111", "surface": "#1c1c1c", "text": "#eeeeee",
            "muted": "#666666", "accent": "#ff2d2d",
        },
        "radius": "0px",
        "heading_transform": "uppercase",
        "heading_weight": "400",
        "body_size": "0.875rem",
        "letter_spacing": "0.02em",
    },
    "editorial": {
        "fonts_import": "https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,700;9..144,900&family=Source+Serif+4:wght@300;400;500;600&display=swap",
        "font_display": "'Fraunces', serif",
        "font_body": "'Source Serif 4', serif",
        "light": {
            "bg": "#faf9f6", "surface": "#ffffff", "text": "#1a1a1a",
            "muted": "#8b8b8b", "accent": "#c44d2b",
        },
        "dark": {
            "bg": "#1a1410", "surface": "#2a2118", "text": "#e8ddd0",
            "muted": "#8c7a6b", "accent": "#e07a2f",
        },
        "radius": "2px",
        "heading_transform": "none",
        "heading_weight": "900",
        "body_size": "1.05rem",
        "letter_spacing": "normal",
    },
    "luxury": {
        "fonts_import": "https://fonts.googleapis.com/css2?family=Bodoni+Moda:wght@400;700;900&family=Libre+Franklin:wght@300;400;500&display=swap",
        "font_display": "'Bodoni Moda', serif",
        "font_body": "'Libre Franklin', sans-serif",
        "light": {
            "bg": "#f5f0e8", "surface": "#fffdf7", "text": "#2c2c2c",
            "muted": "#8a8578", "accent": "#4a6741",
        },
        "dark": {
            "bg": "#0a0a0b", "surface": "#16161a", "text": "#e2e2e6",
            "muted": "#72727e", "accent": "#c9a84c",
        },
        "radius": "0px",
        "heading_transform": "uppercase",
        "heading_weight": "400",
        "body_size": "0.95rem",
        "letter_spacing": "0.08em",
    },
    "playful": {
        "fonts_import": "https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Nunito:wght@400;500;600;700&display=swap",
        "font_display": "'Fredoka', sans-serif",
        "font_body": "'Nunito', sans-serif",
        "light": {
            "bg": "#fef0f5", "surface": "#ffffff", "text": "#3a2c3e",
            "muted": "#b0a0b8", "accent": "#6eb5ff",
        },
        "dark": {
            "bg": "#12101c", "surface": "#1e1b2e", "text": "#f0e6ff",
            "muted": "#7b6f99", "accent": "#ff6b8a",
        },
        "radius": "16px",
        "heading_transform": "none",
        "heading_weight": "700",
        "body_size": "1rem",
        "letter_spacing": "normal",
    },
    "retro-futuristic": {
        "fonts_import": "https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Exo+2:wght@300;400;500;600&display=swap",
        "font_display": "'Orbitron', sans-serif",
        "font_body": "'Exo 2', sans-serif",
        "light": {
            "bg": "#e8ebe4", "surface": "#f4f6f1", "text": "#2a3028",
            "muted": "#6b7a66", "accent": "#1570ef",
        },
        "dark": {
            "bg": "#020d1a", "surface": "#0a1f33", "text": "#c5dbe6",
            "muted": "#4a6d80", "accent": "#00ffc8",
        },
        "radius": "4px",
        "heading_transform": "uppercase",
        "heading_weight": "700",
        "body_size": "0.9rem",
        "letter_spacing": "0.06em",
    },
    "organic": {
        "fonts_import": "https://fonts.googleapis.com/css2?family=Zilla+Slab:wght@400;500;600;700&family=Karla:wght@400;500;600;700&display=swap",
        "font_display": "'Zilla Slab', serif",
        "font_body": "'Karla', sans-serif",
        "light": {
            "bg": "#f2e8d9", "surface": "#faf4ea", "text": "#3d2e1e",
            "muted": "#9c8772", "accent": "#c45a3c",
        },
        "dark": {
            "bg": "#1a2e1a", "surface": "#243524", "text": "#e8ead5",
            "muted": "#7a8c6e", "accent": "#d4a843",
        },
        "radius": "6px",
        "heading_transform": "none",
        "heading_weight": "600",
        "body_size": "1rem",
        "letter_spacing": "normal",
    },
}

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link href="{fonts_import}" rel="stylesheet">
<style>
  :root {{
    --color-bg: {bg};
    --color-surface: {surface};
    --color-text: {text};
    --color-muted: {muted};
    --color-accent: {accent};
    --font-display: {font_display};
    --font-body: {font_body};
    --radius: {radius};
  }}

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    background: var(--color-bg);
    color: var(--color-text);
    font-family: var(--font-body);
    font-size: {body_size};
    line-height: 1.6;
    letter-spacing: {letter_spacing};
    -webkit-font-smoothing: antialiased;
  }}

  h1, h2, h3, h4 {{
    font-family: var(--font-display);
    font-weight: {heading_weight};
    text-transform: {heading_transform};
    line-height: 1.1;
  }}

  a {{ color: var(--color-accent); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}

  .container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
  }}

  /* -- Header -- */
  .header {{
    padding: 1.5rem 0;
    border-bottom: 1px solid color-mix(in srgb, var(--color-text) 10%, transparent);
  }}

  .header__inner {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
  }}

  .header__logo {{
    font-family: var(--font-display);
    font-size: 1.25rem;
    font-weight: {heading_weight};
    text-transform: {heading_transform};
    color: var(--color-text);
    text-decoration: none;
  }}

  .header__nav {{
    display: flex;
    gap: 2rem;
    list-style: none;
  }}

  .header__nav a {{
    font-size: 0.8rem;
    color: var(--color-muted);
    transition: color 0.2s ease;
  }}

  .header__nav a:hover {{
    color: var(--color-text);
    text-decoration: none;
  }}

  /* -- Hero -- */
  .hero {{
    padding: 8rem 0 6rem;
  }}

  .hero h1 {{
    font-size: clamp(2.5rem, 6vw, 5rem);
    margin-bottom: 1.5rem;
    max-width: 16ch;
  }}

  .hero p {{
    font-size: 1.1rem;
    color: var(--color-muted);
    max-width: 45ch;
    margin-bottom: 2.5rem;
  }}

  .hero__cta {{
    display: inline-block;
    background: var(--color-accent);
    color: var(--color-bg);
    font-family: var(--font-body);
    font-size: 0.85rem;
    font-weight: 500;
    padding: 0.75rem 1.75rem;
    border-radius: var(--radius);
    text-decoration: none;
    transition: opacity 0.2s ease;
  }}

  .hero__cta:hover {{
    opacity: 0.85;
    text-decoration: none;
  }}

  /* -- Section -- */
  .section {{
    padding: 5rem 0;
    border-top: 1px solid color-mix(in srgb, var(--color-text) 8%, transparent);
  }}

  .section__label {{
    font-family: var(--font-body);
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--color-accent);
    margin-bottom: 1.5rem;
  }}

  .section h2 {{
    font-size: clamp(1.5rem, 3vw, 2.5rem);
    margin-bottom: 1rem;
  }}

  .section p {{
    color: var(--color-muted);
    max-width: 60ch;
  }}

  /* -- Cards -- */
  .cards {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin-top: 3rem;
  }}

  .card {{
    background: var(--color-surface);
    border-radius: var(--radius);
    padding: 2rem;
    border: 1px solid color-mix(in srgb, var(--color-text) 6%, transparent);
  }}

  .card h3 {{
    font-size: 1.15rem;
    margin-bottom: 0.75rem;
    text-transform: none;
  }}

  .card p {{
    font-size: 0.875rem;
    color: var(--color-muted);
    line-height: 1.6;
  }}

  /* -- Footer -- */
  .footer {{
    padding: 3rem 0;
    border-top: 1px solid color-mix(in srgb, var(--color-text) 8%, transparent);
    margin-top: 4rem;
  }}

  .footer p {{
    font-size: 0.75rem;
    color: var(--color-muted);
  }}
</style>
</head>
<body>
  <header class="header">
    <div class="header__inner">
      <a href="#" class="header__logo">{title}</a>
      <nav>
        <ul class="header__nav">
          <li><a href="#">Features</a></li>
          <li><a href="#">About</a></li>
          <li><a href="#">Contact</a></li>
        </ul>
      </nav>
    </div>
  </header>

  <main class="container">
    <section class="hero">
      <h1>{title}</h1>
      <p>Replace this with a compelling description of your project. This starter page is pre-configured with the {aesthetic} aesthetic.</p>
      <a href="#" class="hero__cta">Get Started</a>
    </section>

    <section class="section">
      <span class="section__label">Features</span>
      <h2>What Makes This Different</h2>
      <p>Replace with your content. The typography, colors, and spacing are set for the {aesthetic} direction.</p>

      <div class="cards">
        <div class="card">
          <h3>First Feature</h3>
          <p>Describe the feature here. Keep it concise and focused on the value it provides.</p>
        </div>
        <div class="card">
          <h3>Second Feature</h3>
          <p>Describe the feature here. Keep it concise and focused on the value it provides.</p>
        </div>
        <div class="card">
          <h3>Third Feature</h3>
          <p>Describe the feature here. Keep it concise and focused on the value it provides.</p>
        </div>
      </div>
    </section>
  </main>

  <footer class="footer">
    <div class="container">
      <p>&copy; {year} {title}. All rights reserved.</p>
    </div>
  </footer>
</body>
</html>"""


def list_aesthetics():
    print("Available aesthetics:\n")
    for name in sorted(AESTHETICS):
        a = AESTHETICS[name]
        display_font = a["font_display"].split(",")[0].strip("'\"")
        body_font = a["font_body"].split(",")[0].strip("'\"")
        print(f"  {name:<20} {display_font} + {body_font}")
    print(f"\n{len(AESTHETICS)} aesthetics available.")


def scaffold(aesthetic_name, title, dark, output):
    if aesthetic_name not in AESTHETICS:
        print(f"Error: unknown aesthetic '{aesthetic_name}'", file=sys.stderr)
        print(f"Available: {', '.join(sorted(AESTHETICS))}", file=sys.stderr)
        sys.exit(1)

    a = AESTHETICS[aesthetic_name]
    palette = a["dark"] if dark else a["light"]

    html = TEMPLATE.format(
        title=title,
        aesthetic=aesthetic_name,
        fonts_import=a["fonts_import"],
        font_display=a["font_display"],
        font_body=a["font_body"],
        bg=palette["bg"],
        surface=palette["surface"],
        text=palette["text"],
        muted=palette["muted"],
        accent=palette["accent"],
        radius=a["radius"],
        heading_weight=a["heading_weight"],
        heading_transform=a["heading_transform"],
        body_size=a["body_size"],
        letter_spacing=a["letter_spacing"],
        year=datetime.now().year,
    )

    output_path = output or f"{aesthetic_name}-page.html"
    with open(output_path, "w") as f:
        f.write(html)

    full_path = os.path.abspath(output_path)
    mode = "dark" if dark else "light"
    print(f"Created {full_path}")
    print(f"Aesthetic: {aesthetic_name} ({mode})")
    print(f"Fonts: {a['font_display'].split(',')[0].strip(chr(39))} + {a['font_body'].split(',')[0].strip(chr(39))}")
    return full_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate a starter HTML page with a specific aesthetic direction."
    )
    parser.add_argument("--list", action="store_true", help="List available aesthetics")
    parser.add_argument("--aesthetic", "-a", type=str, help="Aesthetic direction to use")
    parser.add_argument("--title", "-t", type=str, default="Project", help="Page title (default: Project)")
    parser.add_argument("--dark", action="store_true", help="Use dark color palette")
    parser.add_argument("--output", "-o", type=str, help="Output file path (default: <aesthetic>-page.html)")

    args = parser.parse_args()

    if args.list:
        list_aesthetics()
        sys.exit(0)

    if not args.aesthetic:
        parser.error("--aesthetic is required (or use --list to see options)")

    scaffold(args.aesthetic, args.title, args.dark, args.output)


if __name__ == "__main__":
    main()
