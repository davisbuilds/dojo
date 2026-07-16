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

from audit import main as audit_main
from skill_standardizer_lib import apply_actions, build_audit_report, resolve_context


SKILL_TEMPLATE = """---
name: {name}
description: test skill
version: 1.0.0
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


def test_apply_copy_ignores_generated_files() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        source = write_skill(base / "canonical", "brainstorming")
        (source / ".DS_Store").write_text("mac metadata", encoding="utf-8")
        (source / ".pytest_cache").mkdir()
        (source / ".pytest_cache" / "README.md").write_text("cache", encoding="utf-8")
        (source / "scripts" / "__pycache__").mkdir(parents=True)
        (source / "scripts" / "__pycache__" / "helper.cpython-314.pyc").write_bytes(b"cache")
        dest = base / "globals" / "brainstorming"

        report = {
            "actions": [
                {
                    "action": "create_copy",
                    "skill": "brainstorming",
                    "source": str(source),
                    "dest": str(dest),
                    "reason": "copy without generated files",
                },
            ]
        }

        result = apply_actions(report, apply=True, backup_root=str(base / "backups"))
        assert_true(not result["errors"], f"apply_actions should succeed: {result}")
        assert_true((dest / "SKILL.md").exists(), "skill content should be copied")
        assert_true(not (dest / ".DS_Store").exists(), ".DS_Store should not be copied")
        assert_true(not (dest / ".pytest_cache").exists(), ".pytest_cache should not be copied")
        assert_true(not (dest / "scripts" / "__pycache__").exists(), "__pycache__ should not be copied")


def test_selected_skill_limits_mirror_scope_and_invalid_reports() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        repo = base / "repo"
        skills = repo / "skills"
        skills.mkdir(parents=True)
        (repo / "AGENTS.md").write_text("x", encoding="utf-8")
        write_skill(skills, "alpha")
        write_skill(skills, "beta")
        (skills / "_fragments").mkdir()

        agents_home = base / ".agents"
        codex_home = base / ".codex"
        claude_home = base / ".claude"
        for home in [agents_home, codex_home, claude_home]:
            (home / "skills").mkdir(parents=True)

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
            selected_skills={"alpha"},
        )

        assert_true(report["selected_skills"] == ["alpha"], f"selected scope missing: {report}")
        assert_true(
            {action["skill"] for action in report["actions"]} == {"alpha"},
            f"targeted audit should only plan alpha actions: {report['actions']}",
        )
        assert_true(
            all(issue.get("skill") == "alpha" for issue in report["issues"]),
            f"targeted audit should only report alpha issues: {report['issues']}",
        )
        assert_true(
            all("_fragments" not in root["invalid_entries"] for root in report["roots"]),
            f"targeted audit should hide unrelated invalid dirs: {report['roots']}",
        )


def test_selected_skill_apply_creates_only_requested_global_mirror() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        repo = base / "repo"
        skills = repo / "skills"
        skills.mkdir(parents=True)
        (repo / "AGENTS.md").write_text("x", encoding="utf-8")
        write_skill(skills, "alpha")
        write_skill(skills, "beta")

        agents_home = base / ".agents"
        codex_home = base / ".codex"
        claude_home = base / ".claude"
        for home in [agents_home, codex_home, claude_home]:
            (home / "skills").mkdir(parents=True)

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
            selected_skills={"alpha"},
        )
        result = apply_actions(report, apply=True, backup_root=str(base / "backups"))

        assert_true(not result["errors"], f"selected apply should succeed: {result}")
        primary_alpha = agents_home / "skills" / "alpha"
        assert_true(primary_alpha.is_dir(), "selected skill should be copied to primary global")
        assert_true(
            (codex_home / "skills" / "alpha").is_symlink(),
            "selected skill should be linked into Codex global",
        )
        assert_true(
            (claude_home / "skills" / "alpha").is_symlink(),
            "selected skill should be linked into Claude global",
        )
        for home in [agents_home, codex_home, claude_home]:
            assert_true(
                not (home / "skills" / "beta").exists(),
                f"unselected skill should not be installed into {home}",
            )


def test_selected_missing_skill_reports_typo() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        repo = base / "repo"
        skills = repo / "skills"
        skills.mkdir(parents=True)
        (repo / "AGENTS.md").write_text("x", encoding="utf-8")
        write_skill(skills, "alpha")

        agents_home = base / ".agents"
        codex_home = base / ".codex"
        claude_home = base / ".claude"
        for home in [agents_home, codex_home, claude_home]:
            (home / "skills").mkdir(parents=True)

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
            selected_skills={"typo"},
        )

        assert_true(
            [issue["code"] for issue in report["issues"]] == ["SELECTED_SKILL_NOT_FOUND"],
            f"missing selected skill should be reported clearly: {report['issues']}",
        )
        assert_true(not report["actions"], f"missing selected skill should not plan actions: {report['actions']}")


def test_underscore_dirs_are_not_invalid_in_full_scan() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        repo = base / "repo"
        skills = repo / "skills"
        skills.mkdir(parents=True)
        (repo / "AGENTS.md").write_text("x", encoding="utf-8")
        write_skill(skills, "alpha")
        (skills / "_fragments").mkdir()
        (skills / "_fragments" / "shared.md").write_text("fragment", encoding="utf-8")

        agents_home = base / ".agents"
        codex_home = base / ".codex"
        claude_home = base / ".claude"
        for home in [agents_home, codex_home, claude_home]:
            (home / "skills").mkdir(parents=True)

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

        assert_true(
            all("_fragments" not in root["invalid_entries"] for root in report["roots"]),
            f"full-scan audit should not treat _fragments as invalid: {report['roots']}",
        )
        assert_true(
            all(issue.get("skill") != "_fragments" for issue in report["issues"]),
            f"full-scan audit should not raise issues for _fragments: {report['issues']}",
        )


def test_audit_exit_code_tracks_drift_not_warnings() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        repo = base / "repo"
        skills = repo / "skills"
        skills.mkdir(parents=True)
        (repo / "AGENTS.md").write_text("x", encoding="utf-8")
        write_skill(skills, "alpha")

        agents_home = base / ".agents"
        codex_home = base / ".codex"
        claude_home = base / ".claude"
        for home in [agents_home, codex_home, claude_home]:
            (home / "skills").mkdir(parents=True)

        # An intentional non-skill directory in a global root: warning-level,
        # not drift. Mirrors codex-primary-runtime in the real ~/.codex/skills.
        (codex_home / "skills" / "codex-primary-runtime").mkdir()

        os.environ["AGENTS_HOME"] = str(agents_home)
        os.environ["CODEX_HOME"] = str(codex_home)
        os.environ["CLAUDE_HOME"] = str(claude_home)
        os.chdir(repo)

        exit_code = audit_main(
            [
                "--canonical-root",
                str(skills),
                "--global-policy",
                "prefer-primary-link",
                "--only-existing",
                "--format",
                "text",
            ]
        )

        assert_true(
            exit_code == 0,
            f"audit with warnings but no planned actions should exit 0, got {exit_code}",
        )


def test_audit_exit_code_reports_real_drift() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        repo = base / "repo"
        skills = repo / "skills"
        skills.mkdir(parents=True)
        (repo / "AGENTS.md").write_text("x", encoding="utf-8")
        write_skill(skills, "alpha")

        agents_home = base / ".agents"
        codex_home = base / ".codex"
        claude_home = base / ".claude"
        for home in [agents_home, codex_home, claude_home]:
            (home / "skills").mkdir(parents=True)

        # Installed globally but with drifted content: must still exit 2.
        drifted = agents_home / "skills" / "alpha"
        drifted.mkdir(parents=True)
        (drifted / "SKILL.md").write_text("---\nname: alpha\n---\n\n# drifted\n", encoding="utf-8")

        os.environ["AGENTS_HOME"] = str(agents_home)
        os.environ["CODEX_HOME"] = str(codex_home)
        os.environ["CLAUDE_HOME"] = str(claude_home)
        os.chdir(repo)

        exit_code = audit_main(
            [
                "--canonical-root",
                str(skills),
                "--global-policy",
                "prefer-primary-link",
                "--only-existing",
                "--format",
                "text",
            ]
        )

        assert_true(exit_code == 2, f"audit with real drift should exit 2, got {exit_code}")


def _audit_fixture(base: Path) -> Path:
    repo = base / "repo"
    skills = repo / "skills"
    skills.mkdir(parents=True)
    (repo / "AGENTS.md").write_text("x", encoding="utf-8")
    write_skill(skills, "alpha")

    for home in [base / ".agents", base / ".codex", base / ".claude"]:
        (home / "skills").mkdir(parents=True)

    os.environ["AGENTS_HOME"] = str(base / ".agents")
    os.environ["CODEX_HOME"] = str(base / ".codex")
    os.environ["CLAUDE_HOME"] = str(base / ".claude")
    os.chdir(repo)
    return skills


def _invalid_for(report: dict, path: Path) -> list[str]:
    for root in report["roots"]:
        if root["path"] == str(path):
            return root["invalid_entries"]
    raise AssertionError(f"root not found in report: {path}")


def test_known_non_skill_dir_ignored_in_owning_root() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        skills = _audit_fixture(base)
        (base / ".codex" / "skills" / "codex-primary-runtime").mkdir()

        report = build_audit_report(
            context=resolve_context(str(skills), [], False),
            local_policy="prefer-global-link",
            global_policy="prefer-primary-link",
            keep_local_skills=set(),
            enforce_mirror=True,
            codex_agents_dedupe=True,
        )

        assert_true(
            "codex-primary-runtime" not in _invalid_for(report, (base / ".codex" / "skills").resolve()),
            f"codex-primary-runtime should be ignored in the codex root: {report['roots']}",
        )
        assert_true(
            all(issue.get("skill") != "codex-primary-runtime" for issue in report["issues"]),
            f"codex-primary-runtime should raise no issue: {report['issues']}",
        )


def test_known_non_skill_dir_still_reported_in_other_roots() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        skills = _audit_fixture(base)
        # Same name, wrong root: the allowlist is scoped, so this is still odd.
        (skills / "codex-primary-runtime").mkdir()

        report = build_audit_report(
            context=resolve_context(str(skills), [], False),
            local_policy="prefer-global-link",
            global_policy="prefer-primary-link",
            keep_local_skills=set(),
            enforce_mirror=True,
            codex_agents_dedupe=True,
        )

        assert_true(
            "codex-primary-runtime" in _invalid_for(report, skills.resolve()),
            f"allowlist must not leak into the canonical root: {report['roots']}",
        )


def test_ignore_dir_flag_suppresses_custom_dir() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        skills = _audit_fixture(base)
        (base / ".agents" / "skills" / "vendor-runtime").mkdir()

        exit_code = audit_main(
            [
                "--canonical-root",
                str(skills),
                "--global-policy",
                "prefer-primary-link",
                "--only-existing",
                "--ignore-dir",
                "vendor-runtime",
                "--format",
                "text",
            ]
        )

        assert_true(exit_code == 0, f"--ignore-dir should suppress the warning, got exit {exit_code}")


def main() -> int:
    tests = [
        test_invalid_entries_do_not_emit_missing_actions,
        test_underscore_dirs_are_not_invalid_in_full_scan,
        test_known_non_skill_dir_ignored_in_owning_root,
        test_known_non_skill_dir_still_reported_in_other_roots,
        test_ignore_dir_flag_suppresses_custom_dir,
        test_audit_exit_code_tracks_drift_not_warnings,
        test_audit_exit_code_reports_real_drift,
        test_deprecated_replacement_uses_real_source,
        test_apply_orders_copy_before_link,
        test_apply_copy_ignores_generated_files,
        test_selected_skill_limits_mirror_scope_and_invalid_reports,
        test_selected_skill_apply_creates_only_requested_global_mirror,
        test_selected_missing_skill_reports_typo,
    ]

    for test in tests:
        test()
        print(f"PASS {test.__name__}")

    print("All skill-standardizer regression tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
