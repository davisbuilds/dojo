#!/usr/bin/env python3
"""Regression tests for skill-standardizer planning and apply behavior."""

from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from skill_standardizer_lib import apply_actions, build_audit_report, resolve_context


SKILL_TEMPLATE = """---
name: {name}
description: test skill
---

# {name}
"""


def write_skill(root: Path, name: str) -> Path:
    skill_dir = root / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(SKILL_TEMPLATE.format(name=name), encoding="utf-8")
    return skill_dir


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_invalid_entries_do_not_emit_missing_actions() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        repo = base / "repo"
        skills = repo / "skills"
        skills.mkdir(parents=True)
        (repo / "AGENTS.md").write_text("x", encoding="utf-8")
        write_skill(skills, "brainstorming")

        agents_home = base / ".agents"
        codex_home = base / ".codex"
        claude_home = base / ".claude"
        for home in [agents_home, codex_home, claude_home]:
            (home / "skills").mkdir(parents=True)

        os.symlink(str(agents_home / "skills" / "brainstorming"), agents_home / "skills" / "brainstorming")
        os.symlink(str(agents_home / "skills" / "brainstorming"), codex_home / "skills" / "brainstorming")
        os.symlink(str(agents_home / "skills" / "brainstorming"), claude_home / "skills" / "brainstorming")

        os.environ["AGENTS_HOME"] = str(agents_home)
        os.environ["CODEX_HOME"] = str(codex_home)
        os.environ["CLAUDE_HOME"] = str(claude_home)
        os.chdir(repo)

        report = build_audit_report(
            context=resolve_context(str(skills), [], False),
            local_policy="prefer-global-link",
            global_policy="prefer-primary-link",
            keep_local_skills=set(),
            enforce_mirror=True,
            codex_agents_dedupe=True,
        )

        issues = [issue for issue in report["issues"] if issue.get("skill") == "brainstorming"]
        missing_codes = {issue["code"] for issue in issues if issue["code"].startswith("MISSING_")}
        assert_true(not missing_codes, f"unexpected missing codes for invalid entry: {missing_codes}")

        actions = [action for action in report["actions"] if action["skill"] == "brainstorming"]
        action_types = [action["action"] for action in actions]
        assert_true(
            action_types == ["sync_copy", "relink_to_global", "relink_to_global"],
            f"unexpected action set for invalid brainstorming entries: {actions}",
        )


def test_deprecated_replacement_uses_real_source() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        repo = base / "repo"
        skills = repo / "skills"
        skills.mkdir(parents=True)
        (repo / "AGENTS.md").write_text("x", encoding="utf-8")
        write_skill(skills, "obsidian-canvas")

        agents_home = base / ".agents"
        codex_home = base / ".codex"
        claude_home = base / ".claude"
        for home in [agents_home, codex_home, claude_home]:
            (home / "skills").mkdir(parents=True)

        os.symlink(str(claude_home / "skills" / "json-canvas"), claude_home / "skills" / "json-canvas")

        os.environ["AGENTS_HOME"] = str(agents_home)
        os.environ["CODEX_HOME"] = str(codex_home)
        os.environ["CLAUDE_HOME"] = str(claude_home)
        os.chdir(repo)

        report = build_audit_report(
            context=resolve_context(str(skills), [], False),
            local_policy="prefer-global-link",
            global_policy="prefer-primary-link",
            keep_local_skills=set(),
            enforce_mirror=True,
            codex_agents_dedupe=True,
        )

        replacements = [action for action in report["actions"] if action["action"] == "replace_deprecated_skill"]
        assert_true(len(replacements) == 1, f"expected exactly one deprecated replacement action: {replacements}")
        replacement = replacements[0]
        assert_true(replacement.get("link") is False, f"replacement should copy from canonical source: {replacement}")
        assert_true(
            replacement["source"].endswith("/repo/skills/obsidian-canvas"),
            f"replacement should use canonical source when primary mirror is missing: {replacement}",
        )


def test_apply_orders_copy_before_link() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        source = write_skill(base / "canonical", "brainstorming")
        global_root = base / "globals"
        global_root.mkdir()

        report = {
            "actions": [
                {
                    "action": "relink_to_global",
                    "skill": "brainstorming",
                    "source": str(global_root / "brainstorming"),
                    "dest": str(base / "local" / "brainstorming"),
                    "reason": "link after source exists",
                },
                {
                    "action": "create_copy",
                    "skill": "brainstorming",
                    "source": str(source),
                    "dest": str(global_root / "brainstorming"),
                    "reason": "create copy first",
                },
            ]
        }

        result = apply_actions(report, apply=True, backup_root=str(base / "backups"))
        assert_true(not result["errors"], f"apply_actions should succeed: {result}")

        local = base / "local" / "brainstorming"
        assert_true(local.is_symlink(), f"local skill should be a symlink: {local}")
        assert_true(local.exists(), f"local symlink should resolve successfully: {local}")


def main() -> int:
    tests = [
        test_invalid_entries_do_not_emit_missing_actions,
        test_deprecated_replacement_uses_real_source,
        test_apply_orders_copy_before_link,
    ]

    for test in tests:
        test()
        print(f"PASS {test.__name__}")

    print("All skill-standardizer regression tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
