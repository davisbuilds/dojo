#!/bin/sh
""":"
if command -v python >/dev/null 2>&1; then
    exec python "$0" "$@"
fi
exec python3 "$0" "$@"
":"""
"""Generate a self-contained, browseable skill catalog from skills.json.

Reads the generated manifest (the runtime source of truth) and writes a single
zero-dependency HTML page with client-side search/filter. The skill data is
embedded inline so the page works over file:// without a server or fetch.

Usage:
    gen_catalog.py            # write docs/catalog/index.html
    gen_catalog.py --check    # exit non-zero if the catalog is stale
"""

import argparse
import html
import json
import sys
from pathlib import Path

PAGE_TEMPLATE = """<!DOCTYPE html>
<!-- AUTO-GENERATED from skills.json by scripts/gen_catalog.py — do not edit -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>dojo skill catalog</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font: 15px/1.5 system-ui, sans-serif; margin: 0; padding: 2rem; max-width: 60rem; margin-inline: auto; }}
  h1 {{ font-size: 1.4rem; margin: 0 0 .25rem; }}
  .meta {{ opacity: .65; margin-bottom: 1.25rem; }}
  #q {{ width: 100%; padding: .6rem .8rem; font-size: 1rem; border: 1px solid #8884; border-radius: 8px; box-sizing: border-box; }}
  .count {{ opacity: .65; margin: .75rem 0; font-size: .85rem; }}
  .skill {{ border: 1px solid #8883; border-radius: 10px; padding: .8rem 1rem; margin: .6rem 0; }}
  .skill h2 {{ font-size: 1rem; margin: 0 0 .3rem; font-family: ui-monospace, monospace; }}
  .skill p {{ margin: .3rem 0; }}
  .triggers {{ margin-top: .4rem; }}
  .tag {{ display: inline-block; font-size: .78rem; padding: .1rem .5rem; border: 1px solid #8884; border-radius: 999px; margin: .15rem .25rem .15rem 0; opacity: .85; }}
  .hidden {{ display: none; }}
</style>
</head>
<body>
<h1>dojo skill catalog</h1>
<div class="meta">{count} skills · generated from <code>skills.json</code></div>
<input id="q" type="search" placeholder="Filter by name, description, or trigger…" autofocus>
<div class="count" id="count"></div>
<div id="list"></div>
<script id="data" type="application/json">{data}</script>
<script>
  const skills = JSON.parse(document.getElementById('data').textContent);
  const list = document.getElementById('list');
  const countEl = document.getElementById('count');
  const esc = s => s.replace(/[&<>"]/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]));
  function render(skillsToShow) {{
    list.innerHTML = skillsToShow.map(s => {{
      const triggers = (s.triggers || []).map(t => `<span class="tag">${{esc(t)}}</span>`).join('');
      return `<div class="skill"><h2>${{esc(s.name)}}</h2><p>${{esc(s.description)}}</p>`
        + (triggers ? `<div class="triggers">${{triggers}}</div>` : '') + `</div>`;
    }}).join('');
    countEl.textContent = `${{skillsToShow.length}} shown`;
  }}
  document.getElementById('q').addEventListener('input', e => {{
    const q = e.target.value.toLowerCase().trim();
    render(!q ? skills : skills.filter(s => {{
      const hay = (s.name + ' ' + s.description + ' ' + (s.triggers || []).join(' ')).toLowerCase();
      return hay.includes(q);
    }}));
  }});
  render(skills);
</script>
</body>
</html>
"""


def build_page(manifest: dict) -> str:
    skills = manifest.get("skills", [])
    catalog = [
        {k: v for k, v in s.items() if k in ("name", "description", "triggers")}
        for s in skills
    ]
    data = html.escape(json.dumps(catalog, ensure_ascii=False), quote=False)
    return PAGE_TEMPLATE.format(count=len(catalog), data=data)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--manifest", default="skills.json", help="Path to skills.json (default: skills.json)")
    parser.add_argument("--out", default="docs/catalog/index.html", help="Output HTML path")
    parser.add_argument("--check", action="store_true", help="Report drift without writing; exit 1 if stale")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = (repo_root / manifest_path).resolve()
    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = (repo_root / out_path).resolve()

    if not manifest_path.exists():
        print(f"Manifest not found: {manifest_path} (run generate_skills_manifest.py)", file=sys.stderr)
        return 1

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    page = build_page(manifest)

    current = out_path.read_text(encoding="utf-8") if out_path.exists() else None
    if current == page:
        if args.check:
            print("Catalog is up to date.")
        else:
            print("No changes.")
        return 0

    if args.check:
        print("Catalog is stale (run scripts/gen_catalog.py).", file=sys.stderr)
        return 1

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(page, encoding="utf-8")
    try:
        shown = out_path.relative_to(repo_root)
    except ValueError:
        shown = out_path
    print(f"Wrote {shown} ({len(manifest.get('skills', []))} skills)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
