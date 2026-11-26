from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
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
    return json.loads(m.group(1))


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
    assert "path" not in data[0]
    assert "triggers" not in data[1]
    assert "53 skills" not in page
    assert "2 skills" in page
    assert 'class="version">v${esc(s.version)}' in page


def test_check_detects_drift(tmp_path: Path, monkeypatch):
    module = load_module()
    manifest = tmp_path / "skills.json"
    manifest.write_text(json.dumps({"version": 1, "skills": [{"name": "a", "description": "x", "version": "1.0.0"}]}), encoding="utf-8")
    out = tmp_path / "catalog.html"

    monkeypatch.setattr("sys.argv", ["gen", "--manifest", str(manifest), "--out", str(out), "--check"])
    assert module.main() == 1

    monkeypatch.setattr("sys.argv", ["gen", "--manifest", str(manifest), "--out", str(out)])
    assert module.main() == 0

    monkeypatch.setattr("sys.argv", ["gen", "--manifest", str(manifest), "--out", str(out), "--check"])
    assert module.main() == 0


def test_catalog_merges_independent_version_bumps(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", "/dev/null")
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("GIT_MERGE_AUTOEDIT", "no")
    manifest_path = tmp_path / "skills.json"
    catalog_path = tmp_path / "docs/catalog/index.html"
    manifest = {
        "version": 1,
        "skills": [
            {"name": "alpha", "description": "First skill.", "version": "1.0.0"},
            {"name": "beta", "description": "Second skill.", "version": "1.0.0"},
        ],
    }

    def git(*args: str, check: bool = True):
        return subprocess.run(
            ["git", *args], cwd=tmp_path, check=check, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )

    def generate():
        subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--manifest", str(manifest_path), "--out", str(catalog_path)],
            cwd=tmp_path, check=True,
        )

    def commit_catalog(message: str):
        generate()
        git("add", str(manifest_path), str(catalog_path))
        git("commit", "-m", message)

    git("init", "-b", "main")
    git("config", "user.name", "Catalog test")
    git("config", "user.email", "test@example.invalid")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    commit_catalog("Generate catalog")

    for index, branch in enumerate(("bump-alpha", "bump-beta")):
        git("checkout", "-b", branch, "main")
        branch_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        branch_manifest["skills"][index]["version"] = "1.0.1"
        manifest_path.write_text(json.dumps(branch_manifest, indent=2) + "\n", encoding="utf-8")
        commit_catalog(branch)

    merge = git("merge", "bump-alpha", check=False)
    assert merge.returncode == 0, merge.stdout
    merged_catalog = catalog_path.read_bytes()
    assert [skill["version"] for skill in embedded_data(merged_catalog.decode("utf-8"))] == ["1.0.1", "1.0.1"]
    generate()
    assert catalog_path.read_bytes() == merged_catalog


def test_escapes_html_in_descriptions():
    module = load_module()
    manifest = {"version": 1, "skills": [{"name": "x", "description": '<script>alert("xss")</script>', "version": "1.0.0"}]}
    page = module.build_page(manifest)
    assert "</script>alert" not in page
    data = embedded_data(page)
    assert data[0]["description"] == '<script>alert("xss")</script>'


def test_content_edges_preserve_text_and_script_boundary():
    module = load_module()
    manifest = json.loads((REPO_ROOT / "tests/fixtures/catalog-content-edges.json").read_text())
    page = module.build_page(manifest)
    assert embedded_data(page) == manifest["skills"]
    payload = re.search(r'<script id="data" type="application/json">(.*?)</script>', page, re.DOTALL).group(1)
    assert "<" not in payload
