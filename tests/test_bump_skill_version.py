from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "skills" / "skill-evals" / "scripts" / "bump_skill_version.py"


def load_module():
    spec = importlib.util.spec_from_file_location("bump_skill_version", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def make_skill(tmp_path: Path, version: str = "1.2.3", changelog: str | None = None) -> Path:
    d = tmp_path / "my-skill"
    d.mkdir()
    (d / "SKILL.md").write_text(
        f"---\nname: my-skill\ndescription: Does a thing.\nversion: {version}\n---\n\n# my-skill\n\nBody stays put.\n",
        encoding="utf-8",
    )
    if changelog is not None:
        (d / "CHANGELOG.md").write_text(changelog, encoding="utf-8")
    return d


# --- pure bump arithmetic --------------------------------------------------


def test_bump_patch():
    m = load_module()
    assert m.bump_version("1.2.3", "patch") == "1.2.4"


def test_bump_minor_resets_patch():
    m = load_module()
    assert m.bump_version("1.2.3", "minor") == "1.3.0"


def test_bump_major_resets_minor_and_patch():
    m = load_module()
    assert m.bump_version("1.2.3", "major") == "2.0.0"


def test_bump_drops_prerelease():
    m = load_module()
    assert m.bump_version("1.2.0-rc.1", "patch") == "1.2.1"


def test_bump_rejects_bad_version():
    m = load_module()
    with pytest.raises(ValueError):
        m.bump_version("v1.2.3", "patch")


# --- end-to-end file effects ----------------------------------------------


def test_end_to_end_updates_skill_and_changelog(tmp_path: Path):
    m = load_module()
    d = make_skill(tmp_path, "1.2.3")
    old, new = m.apply_bump(d, part="minor", date="2026-07-15")
    assert (old, new) == ("1.2.3", "1.3.0")
    skill_text = (d / "SKILL.md").read_text()
    assert "version: 1.3.0" in skill_text
    assert "Body stays put." in skill_text  # body preserved
    assert "description: Does a thing." in skill_text  # other frontmatter preserved
    changelog = (d / "CHANGELOG.md").read_text()
    assert changelog.startswith("## 1.3.0 - 2026-07-15")


def test_creates_changelog_when_missing(tmp_path: Path):
    m = load_module()
    d = make_skill(tmp_path, "1.0.0")
    m.apply_bump(d, part="patch", date="2026-07-15")
    assert (d / "CHANGELOG.md").exists()
    assert (d / "CHANGELOG.md").read_text().startswith("## 1.0.1 - 2026-07-15")


def test_prepends_above_existing_entries(tmp_path: Path):
    m = load_module()
    existing = "## 1.2.3 - 2026-01-01\n\n- First release.\n"
    d = make_skill(tmp_path, "1.2.3", changelog=existing)
    m.apply_bump(d, part="patch", date="2026-07-15")
    text = (d / "CHANGELOG.md").read_text()
    assert text.index("## 1.2.4") < text.index("## 1.2.3")
    assert "First release." in text  # old entry retained


def test_refuses_duplicate_changelog_heading(tmp_path: Path):
    m = load_module()
    existing = "## 1.2.4 - 2026-06-01\n\n- Already here.\n"
    d = make_skill(tmp_path, "1.2.3", changelog=existing)
    with pytest.raises(m.BumpError):
        m.apply_bump(d, part="patch", date="2026-07-15")


def test_dry_run_writes_nothing(tmp_path: Path):
    m = load_module()
    d = make_skill(tmp_path, "1.2.3")
    before = (d / "SKILL.md").read_text()
    old, new = m.apply_bump(d, part="patch", date="2026-07-15", dry_run=True)
    assert (old, new) == ("1.2.3", "1.2.4")
    assert (d / "SKILL.md").read_text() == before
    assert not (d / "CHANGELOG.md").exists()


def test_explicit_set_version(tmp_path: Path):
    m = load_module()
    d = make_skill(tmp_path, "1.2.3")
    old, new = m.apply_bump(d, set_version="2.0.0", date="2026-07-15")
    assert new == "2.0.0"
    assert "version: 2.0.0" in (d / "SKILL.md").read_text()


def test_explicit_set_must_increase(tmp_path: Path):
    m = load_module()
    d = make_skill(tmp_path, "1.2.3")
    with pytest.raises(m.BumpError):
        m.apply_bump(d, set_version="1.2.3", date="2026-07-15")
    with pytest.raises(m.BumpError):
        m.apply_bump(d, set_version="1.0.0", date="2026-07-15")


def test_requires_exactly_one_of_part_or_set(tmp_path: Path):
    m = load_module()
    d = make_skill(tmp_path, "1.2.3")
    with pytest.raises(ValueError):
        m.apply_bump(d, date="2026-07-15")
    with pytest.raises(ValueError):
        m.apply_bump(d, part="patch", set_version="2.0.0", date="2026-07-15")


def test_missing_skill_md_errors(tmp_path: Path):
    m = load_module()
    with pytest.raises(m.BumpError):
        m.apply_bump(tmp_path / "nope", part="patch", date="2026-07-15")


def _write_skill_md(tmp_path: Path, version_line: str) -> Path:
    d = tmp_path / "my-skill"
    d.mkdir()
    (d / "SKILL.md").write_text(
        f"---\nname: my-skill\ndescription: Does a thing.\n{version_line}\n---\n\n# my-skill\n",
        encoding="utf-8",
    )
    return d


def test_reads_and_rewrites_quoted_version(tmp_path: Path):
    m = load_module()
    d = _write_skill_md(tmp_path, 'version: "1.2.3"')
    old, new = m.apply_bump(d, part="patch", date="2026-07-15")
    assert (old, new) == ("1.2.3", "1.2.4")
    assert 'version: "1.2.4"' in (d / "SKILL.md").read_text()


def test_preserves_inline_comment(tmp_path: Path):
    m = load_module()
    d = _write_skill_md(tmp_path, "version: 1.2.3  # pinned")
    m.apply_bump(d, part="patch", date="2026-07-15")
    assert "version: 1.2.4  # pinned" in (d / "SKILL.md").read_text()


def test_entry_text_becomes_bullet(tmp_path: Path):
    m = load_module()
    d = make_skill(tmp_path, "1.2.3")
    m.apply_bump(d, part="patch", date="2026-07-15", entry="Fixed the thing.")
    assert "- Fixed the thing." in (d / "CHANGELOG.md").read_text()
