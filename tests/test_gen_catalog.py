from __future__ import annotations

import html
import importlib.util
import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "gen_catalog.py"


def load_module():
    spec = importlib.util.spec_from_file_location("gen_catalog", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def embedded_data(page: str):
    m = re.search(r'<script id="data" type="application/json">(.*?)</script>', page, re.DOTALL)
    assert m
    return json.loads(html.unescape(m.group(1)))


def test_build_page_embeds_name_desc_triggers():
    module = load_module()
    manifest = {
        "version": 1,
        "skills": [
            {
                "name": "diagnose",
                "description": "Debug hard bugs.",
                "version": "1.2.0",
                "triggers": ["debug this"],
                "path": "skills/diagnose",
            },
            {"name": "handoff", "description": "Summarize a session.", "version": "1.0.0", "path": "skills/handoff"},
        ],
    }
    page = module.build_page(manifest)
    data = embedded_data(page)
    assert [s["name"] for s in data] == ["diagnose", "handoff"]
    assert data[0]["version"] == "1.2.0"
    assert data[0]["triggers"] == ["debug this"]
    # path is dropped from the catalog payload; triggers omitted when absent
    assert "path" not in data[0]
    assert "triggers" not in data[1]
    assert "53 skills" not in page  # count reflects this manifest
    assert "2 skills" in page
    assert 'class="version">v${esc(s.version)}' in page


def test_check_detects_drift(tmp_path: Path, monkeypatch):
    module = load_module()
    manifest = tmp_path / "skills.json"
    manifest.write_text(json.dumps({"version": 1, "skills": [{"name": "a", "description": "x", "version": "1.0.0"}]}), encoding="utf-8")
    out = tmp_path / "catalog.html"

    monkeypatch.setattr("sys.argv", ["gen", "--manifest", str(manifest), "--out", str(out), "--check"])
    assert module.main() == 1  # not generated yet

    monkeypatch.setattr("sys.argv", ["gen", "--manifest", str(manifest), "--out", str(out)])
    assert module.main() == 0  # write

    monkeypatch.setattr("sys.argv", ["gen", "--manifest", str(manifest), "--out", str(out), "--check"])
    assert module.main() == 0  # clean


def test_escapes_html_in_descriptions():
    module = load_module()
    manifest = {"version": 1, "skills": [{"name": "x", "description": '<script>alert("xss")</script>', "version": "1.0.0"}]}
    page = module.build_page(manifest)
    # raw closing script tag must not appear unescaped in the embedded JSON payload
    assert "</script>alert" not in page
    data = embedded_data(page)
    assert data[0]["description"] == '<script>alert("xss")</script>'
