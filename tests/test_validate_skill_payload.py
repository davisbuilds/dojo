"""Tests for the pre-tool-use skill validation hook.

The hook must validate the SKILL.md content a Write/Edit *would produce*, not the
content already on disk. Validating the on-disk file deadlocks: an invalid
SKILL.md blocks the very edit that would fix it.
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
HOOK = REPO_ROOT / "hooks" / "validate_skill_payload.py"


def load_hook_module():
    spec = importlib.util.spec_from_file_location("validate_skill_payload", HOOK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

VALID = """---
name: demo-skill
description: A valid demo skill. Use when the user asks for a demo.
skill-type: workflow
version: 1.0.0
---

# Demo
"""

MISSING_VERSION = """---
name: demo-skill
description: A demo skill with no version. Use when the user asks for a demo.
skill-type: workflow
---

# Demo
"""

# A colon-space inside an unquoted YAML scalar silently turns the description
# into a mapping and blows up the parse. This is a real bug that shipped.
BAD_YAML = """---
name: demo-skill
description: A demo skill. Use when asked. Optional: never scores the user.
skill-type: workflow
version: 1.0.0
---

# Demo
"""


def run_hook(payload: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )


def write_payload(path: Path, content: str) -> dict:
    return {"tool_name": "Write", "tool_input": {"file_path": str(path), "content": content}}


def edit_payload(path: Path, old: str, new: str, replace_all: bool = False) -> dict:
    return {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": str(path),
            "old_string": old,
            "new_string": new,
            "replace_all": replace_all,
        },
    }


@pytest.fixture
def skill_dir(tmp_path: Path) -> Path:
    d = tmp_path / "demo-skill"
    d.mkdir()
    return d


def test_allows_non_skill_files(tmp_path: Path):
    other = tmp_path / "README.md"
    assert run_hook(write_payload(other, "not a skill")).returncode == 0


def test_allows_valid_write_to_new_file(skill_dir: Path):
    assert run_hook(write_payload(skill_dir / "SKILL.md", VALID)).returncode == 0


def test_blocks_write_of_invalid_content(skill_dir: Path):
    result = run_hook(write_payload(skill_dir / "SKILL.md", MISSING_VERSION))
    assert result.returncode == 2
    assert "version" in result.stderr.lower()


def test_blocks_write_of_unparseable_yaml(skill_dir: Path):
    result = run_hook(write_payload(skill_dir / "SKILL.md", BAD_YAML))
    assert result.returncode == 2
    assert "yaml" in result.stderr.lower()


def test_allows_write_that_repairs_an_invalid_file(skill_dir: Path):
    """The deadlock case: an invalid file on disk must not block the fix."""
    target = skill_dir / "SKILL.md"
    target.write_text(MISSING_VERSION)
    assert run_hook(write_payload(target, VALID)).returncode == 0


def test_allows_edit_that_repairs_an_invalid_file(skill_dir: Path):
    """The other deadlock case, hit while fixing frontmatter in place."""
    target = skill_dir / "SKILL.md"
    target.write_text(MISSING_VERSION)
    payload = edit_payload(target, "skill-type: workflow", "skill-type: workflow\nversion: 1.0.0")
    assert run_hook(payload).returncode == 0


def test_blocks_edit_that_introduces_invalid_frontmatter(skill_dir: Path):
    target = skill_dir / "SKILL.md"
    target.write_text(VALID)
    payload = edit_payload(target, "version: 1.0.0", "version: not-semver")
    result = run_hook(payload)
    assert result.returncode == 2
    assert "semver" in result.stderr.lower()


def test_allows_edit_leaving_file_valid(skill_dir: Path):
    target = skill_dir / "SKILL.md"
    target.write_text(VALID)
    payload = edit_payload(target, "# Demo", "# Demo Skill")
    assert run_hook(payload).returncode == 0


def test_allows_edit_whose_old_string_is_absent(skill_dir: Path):
    """Not the hook's job to police that — the Edit tool will error on its own."""
    target = skill_dir / "SKILL.md"
    target.write_text(VALID)
    payload = edit_payload(target, "text that is not present", "whatever")
    assert run_hook(payload).returncode == 0


def test_allows_edit_to_missing_file(skill_dir: Path):
    payload = edit_payload(skill_dir / "SKILL.md", "a", "b")
    assert run_hook(payload).returncode == 0


def test_malformed_hook_input_does_not_block(skill_dir: Path):
    result = subprocess.run(
        [sys.executable, str(HOOK)], input="not json", capture_output=True, text=True
    )
    assert result.returncode == 0


def test_missing_validator_dependency_degrades_to_allow(skill_dir, monkeypatch):
    """A guard hook must not block edits because its own dependency is missing."""
    module = load_hook_module()
    # Simulate PyYAML (or the validator) being unimportable.
    monkeypatch.setattr(module, "_load_validator", lambda: None)
    target = skill_dir / "SKILL.md"
    monkeypatch.setattr("sys.stdin", _StdinStub(json.dumps(write_payload(target, MISSING_VERSION))))
    assert module.main() == 0


def test_load_validator_returns_none_on_import_error(monkeypatch):
    module = load_hook_module()
    import builtins
    real_import = builtins.__import__

    def boom(name, *args, **kwargs):
        if name == "quick_validate":
            raise ImportError("simulated missing dependency")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", boom)
    assert module._load_validator() is None


class _StdinStub:
    def __init__(self, text):
        self._text = text

    def read(self):
        return self._text
