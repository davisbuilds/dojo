from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "skills" / "skill-creator" / "scripts" / "quick_validate.py"


def load_module():
    spec = importlib.util.spec_from_file_location("quick_validate", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_skill(tmp_path: Path, frontmatter: str) -> Path:
    skill_dir = tmp_path / "sample-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\n" + frontmatter + "\n---\n\n# Sample Skill\n",
        encoding="utf-8",
    )
    return skill_dir


def base_frontmatter(version_line: str | None = "version: 1.0.0") -> str:
    lines = [
        "name: sample-skill",
        "description: Use when validating sample skills.",
    ]
    if version_line is not None:
        lines.append(version_line)
    lines.append("skill-type: reference")
    return "\n".join(lines)


def test_accepts_valid_semver_with_prerelease_and_build_metadata(tmp_path: Path) -> None:
    module = load_module()
    skill_dir = write_skill(tmp_path, base_frontmatter("version: 1.2.3-0rc.1+build.7"))

    assert module.validate_skill(skill_dir) == (True, "Skill is valid!")


def test_rejects_missing_version(tmp_path: Path) -> None:
    module = load_module()
    skill_dir = write_skill(tmp_path, base_frontmatter(None))

    assert module.validate_skill(skill_dir) == (False, "Missing 'version' in frontmatter")


def test_rejects_leading_v_version(tmp_path: Path) -> None:
    module = load_module()
    skill_dir = write_skill(tmp_path, base_frontmatter("version: v1.0.0"))

    assert module.validate_skill(skill_dir) == (False, "Version must not use a leading 'v'")


def test_rejects_non_semver_version(tmp_path: Path) -> None:
    module = load_module()
    skill_dir = write_skill(tmp_path, base_frontmatter('version: "1.0"'))

    assert module.validate_skill(skill_dir) == (
        False,
        "Version '1.0' must be valid SemVer, for example 1.0.0",
    )


def test_rejects_numeric_prerelease_with_leading_zero(tmp_path: Path) -> None:
    module = load_module()
    skill_dir = write_skill(tmp_path, base_frontmatter("version: 1.0.0-01"))

    assert module.validate_skill(skill_dir) == (
        False,
        "Version '1.0.0-01' must be valid SemVer, for example 1.0.0",
    )
