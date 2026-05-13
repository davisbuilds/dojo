from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "generate_skills_manifest.py"


def load_manifest_module():
    spec = importlib.util.spec_from_file_location("generate_skills_manifest", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_skill(skills_root: Path, dirname: str, frontmatter: str, body: str = "# Skill\n") -> Path:
    skill_dir = skills_root / dirname
    skill_dir.mkdir(parents=True)
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(f"---\n{frontmatter}\n---\n\n{body}", encoding="utf-8")
    return skill_md


def test_extract_frontmatter_returns_yaml_mapping(tmp_path: Path) -> None:
    module = load_manifest_module()
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text(
        "---\n"
        "name: manifest-test\n"
        "description: Builds a test manifest\n"
        "allowed-tools:\n"
        "  - Bash\n"
        "---\n"
        "# Manifest test\n",
        encoding="utf-8",
    )

    assert module.extract_frontmatter(skill_md) == {
        "name": "manifest-test",
        "description": "Builds a test manifest",
        "allowed-tools": ["Bash"],
    }


@pytest.mark.parametrize(
    "content",
    [
        "# Missing frontmatter\n",
        "---\n- not\n- a\n- mapping\n---\n",
        "---\nname: [unterminated\n---\n",
        "---\nname: missing closing delimiter\n",
    ],
)
def test_extract_frontmatter_rejects_invalid_documents(tmp_path: Path, content: str) -> None:
    module = load_manifest_module()
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text(content, encoding="utf-8")

    assert module.extract_frontmatter(skill_md) is None


def test_generate_manifest_writes_valid_skills_and_optional_metadata(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    module = load_manifest_module()
    skills_root = tmp_path / "skills"
    skills_root.mkdir()
    output_path = tmp_path / "skills.json"

    write_skill(
        skills_root,
        "beta",
        "name: beta\n"
        "description: Second skill\n"
        "license: MIT\n"
        "allowed-tools:\n"
        "  - Bash\n"
        "  - Read\n",
    )
    write_skill(skills_root, "alpha", "name: alpha\ndescription: First skill\n")
    write_skill(skills_root, "missing-description", "name: skip-me\n")
    (skills_root / "bad-frontmatter").mkdir()
    (skills_root / "bad-frontmatter" / "SKILL.md").write_text("# No frontmatter\n", encoding="utf-8")

    module.generate_manifest(skills_root, output_path)

    manifest = json.loads(output_path.read_text(encoding="utf-8"))
    assert manifest == {
        "version": 1,
        "skills": [
            {
                "name": "alpha",
                "description": "First skill",
                "path": "skills/alpha",
            },
            {
                "name": "beta",
                "description": "Second skill",
                "path": "skills/beta",
                "license": "MIT",
                "allowed-tools": ["Bash", "Read"],
            },
        ],
    }

    captured = capsys.readouterr()
    assert f"Generated {output_path} with 2 skills" in captured.out
    assert "Warning: skipping" in captured.err
    assert "invalid frontmatter" in captured.err
    assert "missing name or description" in captured.err


def test_generate_manifest_exits_when_skills_directory_is_missing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    module = load_manifest_module()
    missing_dir = tmp_path / "missing"

    with pytest.raises(SystemExit) as exc_info:
        module.generate_manifest(missing_dir, tmp_path / "skills.json")

    assert exc_info.value.code == 1
    assert f"Error: {missing_dir} is not a directory" in capsys.readouterr().err
