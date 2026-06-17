from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "gen_skill_docs.py"


def load_module():
    spec = importlib.util.spec_from_file_location("gen_skill_docs", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def setup(tmp_path: Path):
    skills_root = tmp_path / "skills"
    fragments = skills_root / "_fragments"
    fragments.mkdir(parents=True)
    (fragments / "footer.md").write_text("Shared footer line.", encoding="utf-8")

    def make_skill(name: str, body: str) -> Path:
        d = skills_root / name
        d.mkdir()
        md = d / "SKILL.md"
        md.write_text(f"---\nname: {name}\ndescription: x\n---\n\n{body}", encoding="utf-8")
        return md

    return skills_root, fragments, make_skill


def test_expands_directive(setup):
    module = load_module()
    skills_root, fragments, make_skill = setup
    md = make_skill("opted", "Intro\n\n<!-- INCLUDE: footer -->\n")

    text = md.read_text()
    out = module.expand(text, skills_root, skills_root.parent)

    assert "<!-- AUTO-GENERATED from skills/_fragments/footer.md" in out
    assert "Shared footer line." in out
    assert "<!-- /INCLUDE: footer -->" in out


def test_idempotent(setup):
    module = load_module()
    skills_root, fragments, make_skill = setup
    md = make_skill("opted", "Intro\n\n<!-- INCLUDE: footer -->\n")

    once = module.expand(md.read_text(), skills_root, skills_root.parent)
    twice = module.expand(once, skills_root, skills_root.parent)
    assert once == twice


def test_picks_up_fragment_edits(setup):
    module = load_module()
    skills_root, fragments, make_skill = setup
    md = make_skill("opted", "<!-- INCLUDE: footer -->\n")

    first = module.expand(md.read_text(), skills_root, skills_root.parent)
    (fragments / "footer.md").write_text("Updated footer.", encoding="utf-8")
    second = module.expand(first, skills_root, skills_root.parent)

    assert "Updated footer." in second
    assert "Shared footer line." not in second


def test_resolves_namespaced_rules_include(setup):
    module = load_module()
    skills_root, fragments, make_skill = setup
    repo_root = skills_root.parent
    rules = repo_root / "rules"
    rules.mkdir()
    (rules / "skill-authoring.md").write_text("Authoring rule body.", encoding="utf-8")
    md = make_skill("opted", "<!-- INCLUDE: rules/skill-authoring -->\n")

    out = module.expand(md.read_text(), skills_root, repo_root)
    assert "<!-- AUTO-GENERATED from rules/skill-authoring.md" in out
    assert "Authoring rule body." in out
    assert "<!-- /INCLUDE: rules/skill-authoring -->" in out


def test_non_opted_in_skill_untouched(setup, monkeypatch):
    module = load_module()
    skills_root, fragments, make_skill = setup
    plain = make_skill("plain", "No directives here.\n")
    before = plain.read_bytes()

    monkeypatch.setattr("sys.argv", ["gen", "--skills-root", str(skills_root)])
    assert module.main() == 0
    assert plain.read_bytes() == before


def test_check_detects_drift(setup, monkeypatch):
    module = load_module()
    skills_root, fragments, make_skill = setup
    make_skill("opted", "<!-- INCLUDE: footer -->\n")

    monkeypatch.setattr("sys.argv", ["gen", "--skills-root", str(skills_root), "--check"])
    assert module.main() == 1  # never generated -> stale

    monkeypatch.setattr("sys.argv", ["gen", "--skills-root", str(skills_root)])
    assert module.main() == 0  # write

    monkeypatch.setattr("sys.argv", ["gen", "--skills-root", str(skills_root), "--check"])
    assert module.main() == 0  # now clean


def test_missing_fragment_errors(setup, monkeypatch):
    module = load_module()
    skills_root, fragments, make_skill = setup
    make_skill("opted", "<!-- INCLUDE: nope -->\n")

    monkeypatch.setattr("sys.argv", ["gen", "--skills-root", str(skills_root)])
    assert module.main() == 1
