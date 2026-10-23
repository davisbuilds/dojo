#!/usr/bin/env python3
"""Regression tests for skill-standardizer planning and apply behavior."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
import json
import os
from pathlib import Path
import sys
import tempfile


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from audit import main as audit_main
from skill_standardizer_lib import (
    apply_actions,
    build_audit_report,
    resolve_context,
    summarize_report,
    version_delta,
)


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


def write_versioned_skill(root: Path, name: str, version: str | None, body: str = "") -> Path:
    """A skill whose frontmatter declares `version` verbatim, or omits it when None."""
    skill_dir = root / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    version_line = f"version: {version}\n" if version is not None else ""
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: test skill\n{version_line}---\n\n# {name}\n{body}",
        encoding="utf-8",
    )
    return skill_dir


def write_frontmatter_skill(root: Path, name: str, frontmatter: str) -> Path:
    """A skill whose frontmatter ends with `frontmatter` verbatim, one line or several."""
    skill_dir = root / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: test skill\n{frontmatter}\n---\n\n# {name}\n",
        encoding="utf-8",
    )
    return skill_dir


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


HOME_ENV_NAMES = ("AGENTS_HOME", "CODEX_HOME", "CLAUDE_HOME")


@contextmanager
def isolated_tempdir() -> Iterator[str]:
    """A temporary directory that restores cwd and the harness-home variables.

    Tests point the harness homes at fixtures and chdir into them. Both are
    process-global, so each test restores them on exit, including on failure.
    Restoring inside the directory's context leaves it before removing it, so
    a later test never starts in a deleted cwd.
    """
    original_cwd = os.getcwd()
    original_env = {name: os.environ.get(name) for name in HOME_ENV_NAMES}
    with tempfile.TemporaryDirectory() as td:
        try:
            yield td
        finally:
            for name, value in original_env.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value
            os.chdir(original_cwd)


def test_a_project_root_linking_to_canonical_is_not_a_duplicate() -> None:
    """Project scope links to canonical, and that is the correct state.

    Global roots hold *copies* synced from canonical, so `already_linked` only
    recognised a local entry pointing at the global copy. A project repository
    links straight to canonical instead — deliberately, because project scope
    exists for skills that are *not* global (four design skills were cut from
    the machine-global root in dojo PR #61 precisely so they would be paid for
    only where they are used). Requiring the link to go through a global copy
    would break the case project scope is for, and leave the correct wiring
    reported as a duplicate on every run.
    """
    with isolated_tempdir() as td:
        base = Path(td)
        repo = base / "repo"
        skills = repo / "skills"
        skills.mkdir(parents=True)
        (repo / "AGENTS.md").write_text("x", encoding="utf-8")
        write_skill(skills, "write-plan")

        agents_home = base / ".agents"
        codex_home = base / ".codex"
        claude_home = base / ".claude"
        for home in [agents_home, codex_home, claude_home]:
            (home / "skills").mkdir(parents=True)
        # The global root holds a copy, which is what the sync produces.
        write_skill(agents_home / "skills", "write-plan")

        project = base / "some-project" / ".agents" / "skills"
        project.mkdir(parents=True)
        os.symlink(str(skills / "write-plan"), project / "write-plan")

        os.environ["AGENTS_HOME"] = str(agents_home)
        os.environ["CODEX_HOME"] = str(codex_home)
        os.environ["CLAUDE_HOME"] = str(claude_home)
        os.chdir(repo)

        report = build_audit_report(
            context=resolve_context(str(skills), [str(project)], False),
            local_policy="prefer-global-link",
            global_policy="prefer-primary-link",
            keep_local_skills=set(),
            enforce_mirror=True,
            codex_agents_dedupe=True,
        )

        offending = [
            issue for issue in report["issues"]
            if issue.get("skill") == "write-plan"
            and str(issue.get("code", "")).startswith("LOCAL_DUPLICATE_GLOBAL")
        ]
        assert_true(
            not offending,
            f"a link to canonical must not read as a local duplicate: {offending}")


def test_a_project_root_holding_a_copy_is_still_reported() -> None:
    """The control. Accepting a link must not accept a copy along with it."""
    with isolated_tempdir() as td:
        base = Path(td)
        repo = base / "repo"
        skills = repo / "skills"
        skills.mkdir(parents=True)
        (repo / "AGENTS.md").write_text("x", encoding="utf-8")
        write_skill(skills, "write-plan")

        agents_home = base / ".agents"
        codex_home = base / ".codex"
        claude_home = base / ".claude"
        for home in [agents_home, codex_home, claude_home]:
            (home / "skills").mkdir(parents=True)
        write_skill(agents_home / "skills", "write-plan")

        project = base / "some-project" / ".agents" / "skills"
        project.mkdir(parents=True)
        write_skill(project, "write-plan")           # a copy, not a link

        os.environ["AGENTS_HOME"] = str(agents_home)
        os.environ["CODEX_HOME"] = str(codex_home)
        os.environ["CLAUDE_HOME"] = str(claude_home)
        os.chdir(repo)

        report = build_audit_report(
            context=resolve_context(str(skills), [str(project)], False),
            local_policy="prefer-global-link",
            global_policy="prefer-primary-link",
            keep_local_skills=set(),
            enforce_mirror=True,
            codex_agents_dedupe=True,
        )

        codes = {
            issue["code"] for issue in report["issues"]
            if issue.get("skill") == "write-plan"
        }
        assert_true(
            any(code.startswith("LOCAL_DUPLICATE_GLOBAL") for code in codes),
            f"a project copy of a global skill must still be reported: {codes}")


def test_invalid_entries_do_not_emit_missing_actions() -> None:
    with isolated_tempdir() as td:
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


def test_review_lenses_consolidate_into_existing_local_review() -> None:
    check_review_lens_consolidation("all")


def test_review_lenses_consolidate_without_local_review() -> None:
    check_review_lens_consolidation("none")


def test_review_lenses_consolidate_with_only_primary_local_review() -> None:
    check_review_lens_consolidation("primary")


def check_review_lens_consolidation(existing_roots: str) -> None:
    with isolated_tempdir() as td:
        base = Path(td)
        repo = base / "repo"
        canonical = repo / "skills"
        source = write_skill(canonical, "local-review")
        roots = [base / name / "skills" for name in [".agents", ".codex", ".claude"]]
        for env_name, root in zip(HOME_ENV_NAMES, roots):
            os.environ[env_name] = str(root.parent)
            if existing_roots == "all" or (existing_roots == "primary" and root == roots[0]):
                existing = write_skill(root, "local-review")
                (existing / "SKILL.md").write_text((existing / "SKILL.md").read_text().replace("1.0.0", "0.9.0"))
            for old_name in ["error-handling-review", "type-design-review"]:
                old = write_skill(root, old_name)
                (old / "local-note.md").write_text(old_name)
        os.chdir(repo)

        def audit():
            return build_audit_report(
                context=resolve_context(str(canonical), [], False),
                local_policy="prefer-global-link", global_policy="prefer-primary-link",
                keep_local_skills=set(), enforce_mirror=False,
                codex_agents_dedupe=True, only_existing=True,
                selected_skills={"local-review"},
            )

        report = audit()
        replacements = [a for a in report["actions"] if a["action"] in {"replace_deprecated_skill", "remove_deprecated_skill"}]
        assert_true(len(replacements) == 6, "both old lenses must migrate in all three roots")
        backup_root = base / "backups"
        for _ in range(2):
            result = apply_actions(audit(), apply=True, backup_root=str(backup_root))
            assert_true(not result["errors"], f"migration failed: {result}")
            for root in roots:
                assert_true((root / "local-review" / "SKILL.md").read_bytes() == (source / "SKILL.md").read_bytes(), "replacement missing or stale after apply")
                for old_name in ["error-handling-review", "type-design-review"]:
                    assert_true(not (root / old_name).exists(), "old lens survived a successful apply")
        for root in roots:
            assert_true((root / "local-review" / "SKILL.md").read_bytes() == (source / "SKILL.md").read_bytes(), "replacement differs from canonical")
            for old_name in ["error-handling-review", "type-design-review"]:
                assert_true(not (root / old_name).exists(), "old lens survived")
        assert_true(len(list(backup_root.rglob("local-note.md"))) == 6, "old lenses not preserved")
        assert_true(not audit()["actions"], "consolidation did not converge")


def test_obsidian_format_skills_consolidate_into_obsidian() -> None:
    # Selecting the replacement or any one deprecated alias must keep every
    # alias that resolves to the same replacement in scope.
    for selection in [{"obsidian"}, {"obsidian-canvas"}, {"json-canvas"}]:
        check_obsidian_consolidation(selection)
        check_obsidian_consolidation(selection, linked_secondaries=True)


def check_obsidian_consolidation(selection: set[str], linked_secondaries: bool = False) -> None:
    old_names = ["obsidian-markdown", "obsidian-bases", "obsidian-canvas", "json-canvas"]
    with isolated_tempdir() as td:
        base = Path(td)
        repo = base / "repo"
        canonical = repo / "skills"
        source = write_skill(canonical, "obsidian")
        roots = [base / name / "skills" for name in [".agents", ".codex", ".claude"]]
        for env_name, root in zip(HOME_ENV_NAMES, roots):
            os.environ[env_name] = str(root.parent)
            for old_name in old_names:
                if linked_secondaries and root != roots[0]:
                    root.mkdir(parents=True, exist_ok=True)
                    (root / old_name).symlink_to(roots[0] / old_name, target_is_directory=True)
                else:
                    old = write_skill(root, old_name)
                    (old / "local-note.md").write_text(old_name)
        os.chdir(repo)

        def audit():
            return build_audit_report(
                context=resolve_context(str(canonical), [], False),
                local_policy="prefer-global-link", global_policy="prefer-primary-link",
                keep_local_skills=set(), enforce_mirror=False,
                codex_agents_dedupe=True, only_existing=True,
                selected_skills=selection,
            )

        report = audit()
        migrations = [a for a in report["actions"] if a["action"] in {"replace_deprecated_skill", "remove_deprecated_skill"}]
        assert_true(len(migrations) == len(old_names) * len(roots), f"every old Obsidian skill must migrate in every root for selection {selection}: {migrations}")
        backup_root = base / "backups"
        for _ in range(2):
            result = apply_actions(audit(), apply=True, backup_root=str(backup_root))
            assert_true(not result["errors"], f"migration failed: {result}")
        for root in roots:
            assert_true((root / "obsidian" / "SKILL.md").read_bytes() == (source / "SKILL.md").read_bytes(), "consolidated skill missing or differs from canonical")
            for old_name in old_names:
                assert_true(not os.path.lexists(root / old_name), f"{old_name} survived consolidation for selection {selection}")
        assert_true(len(list(backup_root.rglob("local-note.md"))) == len(old_names) * (1 if linked_secondaries else len(roots)), "old installations were not backed up")
        assert_true(not audit()["actions"], "consolidation did not converge")


def test_agent_native_rename_migrates_existing_installations() -> None:
    for selection in [set(), {"agent-native-architecture"}, {"agent-native-design"}]:
        with isolated_tempdir() as td:
            base = Path(td)
            repo = base / "repo"
            canonical = repo / "skills"
            source = write_skill(canonical, "agent-native-design")
            write_skill(canonical, "unrelated")
            roots = [base / name / "skills" for name in [".agents", ".codex", ".claude"]]
            for env_name, root in zip(HOME_ENV_NAMES, roots):
                os.environ[env_name] = str(root.parent)
                old = write_skill(root, "agent-native-architecture")
                (old / "local-note.md").write_text("preserve this old installation")
            os.chdir(repo)

            def audit():
                return build_audit_report(
                    context=resolve_context(str(canonical), [], False),
                    local_policy="prefer-global-link",
                    global_policy="prefer-primary-link",
                    keep_local_skills=set(), enforce_mirror=False,
                    codex_agents_dedupe=True, only_existing=True,
                    selected_skills=selection,
                )

            report = audit()
            replacements = [a for a in report["actions"] if a["action"] == "replace_deprecated_skill"]
            assert_true(len(replacements) == 3, f"old installs must migrate for selection {selection}: {report}")
            backup_root = base / "backups"
            result = apply_actions(report, apply=True, backup_root=str(backup_root))
            assert_true(not result["errors"], f"migration failed: {result}")
            for root in roots:
                assert_true(not (root / "agent-native-architecture").exists(), "old name survived migration")
                assert_true((root / "agent-native-design" / "SKILL.md").read_bytes() == (source / "SKILL.md").read_bytes(), "replacement differs from canonical")
                assert_true(not (root / "unrelated").exists(), "migration installed an unrelated skill")
            saved_notes = list(backup_root.rglob("local-note.md"))
            assert_true(len(saved_notes) == 3, "old installations were not backed up")
            assert_true(all(p.read_text() == "preserve this old installation" for p in saved_notes), "backup content changed")
            # Existing-name migration may first create independent copies;
            # the ordinary follow-up sync must normalize them and converge.
            followup = apply_actions(audit(), apply=True, backup_root=str(backup_root))
            assert_true(not followup["errors"], f"normalization failed: {followup}")
            assert_true(not audit()["actions"], "migration did not converge")


def test_deprecated_replacement_uses_real_source() -> None:
    with isolated_tempdir() as td:
        base = Path(td)
        repo = base / "repo"
        skills = repo / "skills"
        skills.mkdir(parents=True)
        (repo / "AGENTS.md").write_text("x", encoding="utf-8")
        write_skill(skills, "obsidian")

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
            replacement["source"].endswith("/repo/skills/obsidian"),
            f"replacement should use canonical source when primary mirror is missing: {replacement}",
        )


def test_apply_orders_copy_before_link() -> None:
    with isolated_tempdir() as td:
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
    with isolated_tempdir() as td:
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
    with isolated_tempdir() as td:
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
    with isolated_tempdir() as td:
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
    with isolated_tempdir() as td:
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
    with isolated_tempdir() as td:
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
    with isolated_tempdir() as td:
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
    with isolated_tempdir() as td:
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
    with isolated_tempdir() as td:
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
    with isolated_tempdir() as td:
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


def test_claude_synced_skills_dir_ignored_in_claude_root() -> None:
    with isolated_tempdir() as td:
        base = Path(td)
        skills = _audit_fixture(base)
        # Claude Code keeps account-synced skills one level down, in bucket dirs.
        synced = base / ".claude" / "skills" / "synced"
        write_skill(synced / "bucket-id", "morning")

        report = build_audit_report(
            context=resolve_context(str(skills), [], False),
            local_policy="prefer-global-link",
            global_policy="prefer-primary-link",
            keep_local_skills=set(),
            enforce_mirror=True,
            codex_agents_dedupe=True,
        )

        assert_true(
            "synced" not in _invalid_for(report, (base / ".claude" / "skills").resolve()),
            f"synced should be ignored in the claude root: {report['roots']}",
        )
        assert_true(
            all(issue.get("skill") != "synced" for issue in report["issues"]),
            f"synced should raise no issue: {report['issues']}",
        )


def test_claude_synced_dir_still_reported_in_the_primary_root() -> None:
    with isolated_tempdir() as td:
        base = Path(td)
        skills = _audit_fixture(base)
        (base / ".agents" / "skills" / "synced").mkdir()

        report = build_audit_report(
            context=resolve_context(str(skills), [], False),
            local_policy="prefer-global-link",
            global_policy="prefer-primary-link",
            keep_local_skills=set(),
            enforce_mirror=True,
            codex_agents_dedupe=True,
        )

        assert_true(
            "synced" in _invalid_for(report, (base / ".agents" / "skills").resolve()),
            f"the claude exemption must not leak into the primary root: {report['roots']}",
        )


def test_mirror_never_targets_a_tool_owned_dir() -> None:
    with isolated_tempdir() as td:
        base = Path(td)
        skills = _audit_fixture(base)
        # A canonical skill whose name collides with Claude Code's synced cache.
        write_skill(skills, "synced")
        cache = base / ".claude" / "skills" / "synced"
        write_skill(cache / "bucket-id", "morning")

        report = build_audit_report(
            context=resolve_context(str(skills), [], False),
            local_policy="prefer-global-link",
            global_policy="prefer-primary-link",
            keep_local_skills=set(),
            enforce_mirror=True,
            codex_agents_dedupe=True,
        )

        claude_root = (base / ".claude" / "skills").resolve()
        assert_true(
            all(Path(a["dest"]).resolve() != claude_root / "synced"
                for a in report["actions"] if a.get("dest")),
            f"no action may replace the tool-owned cache: {report['actions']}",
        )
        assert_true(
            any(i["code"] == "RESERVED_NAME_COLLISION" and i["skill"] == "synced"
                for i in report["issues"]),
            f"the collision must be reported: {report['issues']}",
        )


def test_ignore_dir_flag_suppresses_custom_dir() -> None:
    with isolated_tempdir() as td:
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


def test_stale_secondary_link_is_removed_not_relinked() -> None:
    """A secondary global entry naming a skill the operator removed from primary.

    Found live on 2026-08-12: cutting six skills from ~/.agents/skills left
    dangling ~/.claude/skills symlinks behind. The planner proposed
    relink_to_global with a source that no longer existed, and the applier
    creates symlinks without checking, so `sync.py --apply` recreated the broken
    link and reported success. The one repair path for a broken install was a
    silent no-op.

    Removal rather than restore-from-canonical is the point: absence from the
    primary global root is the operator's expressed intent, and reinstalling from
    canonical would quietly undo a deliberate cut.
    """
    with isolated_tempdir() as td:
        base = Path(td)
        repo = base / "repo"
        skills = repo / "skills"
        skills.mkdir(parents=True)
        (repo / "AGENTS.md").write_text("x", encoding="utf-8")
        # Still canonical -- only the *global install* was removed.
        write_skill(skills, "audit-skill")

        agents_home = base / ".agents"
        codex_home = base / ".codex"
        claude_home = base / ".claude"
        for home in [agents_home, codex_home, claude_home]:
            (home / "skills").mkdir(parents=True)

        # Deliberately absent from the primary global root; stale link left behind.
        stale = claude_home / "skills" / "audit-skill"
        os.symlink(str(agents_home / "skills" / "audit-skill"), stale)
        assert_true(stale.is_symlink() and not stale.exists(),
                    "fixture must start dangling or it proves nothing")

        os.environ["AGENTS_HOME"] = str(agents_home)
        os.environ["CODEX_HOME"] = str(codex_home)
        os.environ["CLAUDE_HOME"] = str(claude_home)
        os.chdir(repo)

        report = build_audit_report(
            context=resolve_context(str(skills), [], False),
            local_policy="prefer-global-link",
            global_policy="prefer-primary-link",
            keep_local_skills=set(),
            enforce_mirror=False,
            codex_agents_dedupe=True,
        )

        actions = [a for a in report["actions"] if a["skill"] == "audit-skill"]
        types = [a["action"] for a in actions]
        assert_true(
            "relink_to_global" not in types,
            f"must not relink to a source that does not exist: {actions}",
        )
        assert_true(
            "sync_copy" not in types,
            f"must not reinstall a deliberately removed skill: {actions}",
        )
        assert_true(
            types == ["remove_stale_entry"],
            f"expected a removal, got: {actions}",
        )

        result = apply_actions(report, apply=True, backup_root=str(base / "backups"))
        assert_true(
            not stale.is_symlink() and not stale.exists(),
            "the stale link must be gone after apply",
        )
        assert_true(bool(result["record_path"]), "link removal needs a recovery record")
        saved = json.loads(Path(result["record_path"]).read_text())
        assert_true(saved["backups"][0]["recovery"]["kind"] == "symlink", "record exact link target")


def test_a_broken_primary_entry_is_still_restored_from_canonical() -> None:
    """The case removal must not swallow.

    A broken directory in the *primary* global root is a damaged install of a
    skill that is meant to be there, so canonical restores it. Only a *secondary*
    root naming a skill absent from primary is stale.
    """
    with isolated_tempdir() as td:
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

        # Present but damaged: a directory with no SKILL.md.
        (agents_home / "skills" / "brainstorming").mkdir()

        os.environ["AGENTS_HOME"] = str(agents_home)
        os.environ["CODEX_HOME"] = str(codex_home)
        os.environ["CLAUDE_HOME"] = str(claude_home)
        os.chdir(repo)

        report = build_audit_report(
            context=resolve_context(str(skills), [], False),
            local_policy="prefer-global-link",
            global_policy="prefer-primary-link",
            keep_local_skills=set(),
            enforce_mirror=False,
            codex_agents_dedupe=True,
        )
        types = [a["action"] for a in report["actions"] if a["skill"] == "brainstorming"]
        assert_true("sync_copy" in types,
                    f"a damaged primary entry must be restored from canonical: {types}")
        assert_true("remove_stale_entry" not in types,
                    f"a damaged primary entry is not stale: {types}")


def test_sync_preserves_unknown_backup_history() -> None:
    """Sync never ages out backups whose recovery has not been established."""
    with isolated_tempdir() as td:
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
        # A drifted install, so the apply has something to back up.
        write_skill(agents_home / "skills", "brainstorming")
        (agents_home / "skills" / "brainstorming" / "SKILL.md").write_text(
            "---\nname: brainstorming\ndescription: drifted\nversion: 1.0.0\n---\n",
            encoding="utf-8")

        backup_root = base / "backups"
        for old in ["20260101-000000", "20260102-000000", "20260103-000000"]:
            (backup_root / old).mkdir(parents=True)

        os.environ["AGENTS_HOME"] = str(agents_home)
        os.environ["CODEX_HOME"] = str(codex_home)
        os.environ["CLAUDE_HOME"] = str(claude_home)
        os.chdir(repo)

        report = build_audit_report(
            context=resolve_context(str(skills), [], False),
            local_policy="prefer-global-link",
            global_policy="prefer-primary-link",
            keep_local_skills=set(),
            enforce_mirror=False,
            codex_agents_dedupe=True,
        )
        result = apply_actions(report, apply=True, backup_root=str(backup_root))

        assert_true(bool(result["backups"]), "this fixture must produce a backup")
        # Resolve both sides: on macOS /var is a symlink to /private/var, and the
        # library resolves while the fixture path does not, so raw Path equality
        # compares two spellings of the same directory and never matches.
        written = {Path(b["backup"]).parent.resolve() for b in result["backups"]}
        surviving = {p.resolve() for p in backup_root.iterdir() if p.is_dir()}
        for run in written:
            assert_true(run in surviving, f"pruned the run it just wrote: {run}")
        assert_true(len(surviving) == 5, f"unknown runs, current run, and records must survive: {surviving}")


def test_mirror_copy_repairs_a_secondary_entry_instead_of_removing_it() -> None:
    """Stale-entry removal is a claim about *link* topology.

    Under the default prefer-primary-link policy the secondary roots are
    symlinks to the primary copy, so a name the primary root does not have is an
    orphan and removal is right. Under `--global-policy mirror-copy` the roots
    hold deliberately independent copies -- absence from the primary carries no
    intent at all -- so a damaged secondary entry is repaired from canonical, as
    it always was.
    """
    with isolated_tempdir() as td:
        base = Path(td)
        repo = base / "repo"
        skills = repo / "skills"
        skills.mkdir(parents=True)
        (repo / "AGENTS.md").write_text("x", encoding="utf-8")
        write_skill(skills, "audit-skill")

        agents_home = base / ".agents"
        codex_home = base / ".codex"
        claude_home = base / ".claude"
        for home in [agents_home, codex_home, claude_home]:
            (home / "skills").mkdir(parents=True)

        stale = claude_home / "skills" / "audit-skill"
        os.symlink(str(agents_home / "skills" / "audit-skill"), stale)

        os.environ["AGENTS_HOME"] = str(agents_home)
        os.environ["CODEX_HOME"] = str(codex_home)
        os.environ["CLAUDE_HOME"] = str(claude_home)
        os.chdir(repo)

        report = build_audit_report(
            context=resolve_context(str(skills), [], False),
            local_policy="prefer-global-link",
            global_policy="mirror-copy",
            keep_local_skills=set(),
            enforce_mirror=False,
            codex_agents_dedupe=False,
        )
        claude_actions = [
            a for a in report["actions"]
            if a["skill"] == "audit-skill" and str(claude_home) in str(a["dest"])
        ]
        types = [a["action"] for a in claude_actions]
        assert_true(
            "remove_stale_entry" not in types,
            f"mirror-copy keeps independent copies; it must not delete one: {claude_actions}",
        )
        assert_true(
            "sync_copy" in types,
            f"a damaged mirror-copy entry is repaired from canonical: {claude_actions}",
        )


def test_a_failed_apply_does_not_prune_backup_history() -> None:
    """Failed sync preserves all earlier recovery points."""
    with isolated_tempdir() as td:
        base = Path(td)
        backup_root = base / "backups"
        for old in ["20260101-000000", "20260102-000000", "20260103-000000"]:
            (backup_root / old).mkdir(parents=True)

        broken = {
            "actions": [
                {
                    "action": "sync_copy",
                    "skill": "gone",
                    "source": str(base / "does-not-exist"),
                    "dest": str(base / "dest"),
                }
            ]
        }
        result = apply_actions(broken, apply=True, backup_root=str(backup_root))

        assert_true(bool(result["errors"]), "this fixture must produce an error")
        assert_true(result["discarded_backups"] == [], "failed apply must preserve rollback")
        surviving = sorted(p.name for p in backup_root.iterdir() if p.name != "records")
        assert_true(len(surviving) == 3, f"all runs must survive a failure: {surviving}")


def _version_fixture(base: Path, with_canonical: bool = True) -> tuple[Path, Path, Path, Path]:
    repo = base / "repo"
    skills = repo / "skills"
    if with_canonical:
        skills.mkdir(parents=True)
        (repo / "AGENTS.md").write_text("x", encoding="utf-8")
    homes = [base / ".agents", base / ".codex", base / ".claude"]
    for home in homes:
        (home / "skills").mkdir(parents=True)
    os.environ["AGENTS_HOME"] = str(homes[0])
    os.environ["CODEX_HOME"] = str(homes[1])
    os.environ["CLAUDE_HOME"] = str(homes[2])
    os.chdir(repo if with_canonical else base)
    return skills, homes[0] / "skills", homes[1] / "skills", homes[2] / "skills"


def _version_audit(skills: Path | None, selected: set[str] | None = None) -> dict:
    return build_audit_report(
        context=resolve_context(str(skills) if skills else None, None, False),
        local_policy="prefer-global-link",
        global_policy="prefer-primary-link",
        keep_local_skills=set(),
        enforce_mirror=False,
        selected_skills=selected,
    )


def _version_rows(report: dict) -> dict[tuple[str, str], dict]:
    return {(row["skill"], row["root"]): row for row in report.get("versions", [])}


def test_version_deltas_report_behind_ahead_equal_and_divergent() -> None:
    """Versions say which way a copy moved; content says whether it moved at all.

    Release-relevant changes must bump the version, so an equal version over
    different content is divergence, not equality, and the content drift it
    already raises must survive alongside it.
    """
    with isolated_tempdir() as td:
        skills, agents, codex, _ = _version_fixture(Path(td))
        write_versioned_skill(skills, "alpha", "1.2.0")
        write_versioned_skill(skills, "beta", "1.0.0")
        write_versioned_skill(skills, "gamma", "1.0.0")
        write_versioned_skill(skills, "delta", "1.0.0")
        write_versioned_skill(skills, "rc", "1.2.0")
        write_versioned_skill(agents, "alpha", "1.0.0")
        write_versioned_skill(agents, "beta", "2.0.0")
        write_versioned_skill(agents, "gamma", "1.0.0", body="local edit\n")
        write_versioned_skill(agents, "delta", "1.0.0")
        write_versioned_skill(agents, "rc", "1.2.0-rc.1")
        # A secondary global that already links to the primary copy: no planned
        # action, but its version is still read through the link.
        os.symlink(str(agents / "alpha"), codex / "alpha")

        report = _version_audit(skills)
        rows = _version_rows(report)
        canonical = str(skills.resolve())
        agents_root = str(agents.resolve())
        codex_root = str(codex.resolve())

        expected = {
            ("alpha", agents_root): ("1.2.0", "1.0.0", "behind", True),
            ("alpha", codex_root): ("1.2.0", "1.0.0", "behind", True),
            ("beta", agents_root): ("1.0.0", "2.0.0", "ahead", True),
            ("gamma", agents_root): ("1.0.0", "1.0.0", "divergent", True),
            ("delta", agents_root): ("1.0.0", "1.0.0", "equal", False),
            ("rc", agents_root): ("1.2.0", "1.2.0-rc.1", "behind", True),
        }
        for key, (source_version, current_version, delta, drift) in expected.items():
            row = rows.get(key)
            assert_true(row is not None, f"missing version row {key}: {sorted(rows)}")
            actual = (row["source_version"], row["current_version"], row["version_delta"], row["content_drift"])
            assert_true(
                actual == (source_version, current_version, delta, drift),
                f"{key}: expected {(source_version, current_version, delta, drift)}, got {actual}",
            )
            assert_true(row["source_root"] == canonical, f"{key}: source must be canonical: {row}")
        assert_true(rows[("alpha", codex_root)]["is_symlink"], "linked entry must be marked as a symlink")
        assert_true(
            all(row["root"] != canonical for row in report["versions"]),
            "the source copy is not compared with itself",
        )
        assert_true(
            any(
                issue["code"] == "CONTENT_DRIFT" and issue["skill"] == "gamma"
                for issue in report["issues"]
            ),
            f"an equal version must not hide content drift: {report['issues']}",
        )

        summary = summarize_report(report)
        assert_true("Version deltas:" in summary, f"text summary lacks version deltas:\n{summary}")
        assert_true(
            any("alpha" in line and "behind" in line and "1.0.0" in line and "1.2.0" in line
                for line in summary.splitlines()),
            f"text summary lacks alpha's delta:\n{summary}",
        )
        assert_true(
            any("gamma" in line and "divergent" in line for line in summary.splitlines()),
            f"text summary lacks gamma's divergence:\n{summary}",
        )
        assert_true(
            not any(line.startswith("- delta ") for line in summary.splitlines()),
            f"equal, identical copies need no version line:\n{summary}",
        )


def test_missing_and_malformed_versions_are_unknown_not_zero() -> None:
    with isolated_tempdir() as td:
        skills, agents, _, _ = _version_fixture(Path(td))
        write_versioned_skill(skills, "alpha", "1.0.0")
        write_versioned_skill(skills, "beta", "v2.0.0")
        write_versioned_skill(skills, "gamma", None)
        write_versioned_skill(skills, "delta", '"1.0.0"')
        write_versioned_skill(skills, "epsilon", "1.0.0")
        for name in ("zeta", "eta", "theta"):
            write_versioned_skill(skills, name, "1.2.4")
        write_versioned_skill(agents, "alpha", None)
        write_versioned_skill(agents, "beta", "0.0.0")
        # Were a missing source read as 0.0.0, this would report "ahead".
        write_versioned_skill(agents, "gamma", "0.1.0")
        write_versioned_skill(agents, "delta", "'1.1.0'  # pinned")
        write_versioned_skill(agents, "epsilon", "1.0")
        # Text after a closing quote is a YAML error, not a comment; read as the
        # quoted value, each of these would report "behind".
        write_versioned_skill(agents, "zeta", '"1.2.3" trailing-junk')
        write_versioned_skill(agents, "eta", "'1.2.3' x")
        write_versioned_skill(agents, "theta", '"1.2.3"\t# tab')

        report = _version_audit(skills)
        rows = _version_rows(report)
        agents_root = str(agents.resolve())

        expected = {
            "alpha": ("1.0.0", None, "unknown", "missing"),
            "beta": ("v2.0.0", "0.0.0", "unknown", "SemVer"),
            "gamma": (None, "0.1.0", "unknown", "missing"),
            "epsilon": ("1.0.0", "1.0", "unknown", "SemVer"),
            "zeta": ("1.2.4", '"1.2.3" trailing-junk', "unknown", "SemVer"),
            "eta": ("1.2.4", "'1.2.3' x", "unknown", "SemVer"),
            "theta": ("1.2.4", '"1.2.3"\t# tab', "unknown", "SemVer"),
        }
        for skill, (source_version, current_version, delta, reason) in expected.items():
            row = rows.get((skill, agents_root))
            assert_true(row is not None, f"missing version row for {skill}: {sorted(rows)}")
            actual = (row["source_version"], row["current_version"], row["version_delta"])
            assert_true(
                actual == (source_version, current_version, delta),
                f"{skill}: expected {(source_version, current_version, delta)}, got {actual}",
            )
            assert_true(
                reason in row.get("version_note", ""),
                f"{skill}: unknown delta must say why: {row}",
            )
        # YAML quoting is not part of the version.
        quoted = rows.get(("delta", agents_root))
        assert_true(
            quoted is not None
            and (quoted["source_version"], quoted["current_version"], quoted["version_delta"])
            == ("1.0.0", "1.1.0", "ahead"),
            f"quoted versions must parse like YAML strings: {quoted}",
        )

        summary = summarize_report(report)
        assert_true(
            any("alpha" in line and "unknown" in line and "missing" in line
                for line in summary.splitlines()),
            f"text summary must show the unknown delta:\n{summary}",
        )


def test_version_key_spellings_follow_yaml() -> None:
    """Any spelling YAML reads as the top-level `version` key is the version.

    A nested `version` belongs to its parent mapping, and a near-miss key is
    another key, so neither stands in for a missing top-level version.
    """
    with isolated_tempdir() as td:
        skills, agents, _, _ = _version_fixture(Path(td))
        copies = {
            "plain": "version: 1.2.3",
            "spaced": 'version : "1.2.3"',
            "double-quoted-key": '"version": "1.2.3"',
            "single-quoted-key": "'version': 1.2.3",
            "spaced-quoted-key": "\"version\" : '1.2.3'  # pinned",
            "after-nested": "metadata:\n  version: 9.9.9\nversion: 1.2.3",
            "nested": "metadata:\n  version: 9.9.9",
            "nested-quoted": 'metadata:\n  "version": 9.9.9',
            "near-miss": "versions: 9.9.9\nVersion: 9.9.9\n\"version': 9.9.9",
            "tab-before-colon": "version\t: 9.9.9",
            "quoted-key-junk-value": '"version": "1.2.3" trailing-junk',
        }
        for name, frontmatter in copies.items():
            write_versioned_skill(skills, name, "1.0.0")
            write_frontmatter_skill(agents, name, frontmatter)

        rows = _version_rows(_version_audit(skills))
        agents_root = str(agents.resolve())
        expected = {
            "plain": ("1.2.3", "ahead", None),
            "spaced": ("1.2.3", "ahead", None),
            "double-quoted-key": ("1.2.3", "ahead", None),
            "single-quoted-key": ("1.2.3", "ahead", None),
            "spaced-quoted-key": ("1.2.3", "ahead", None),
            "after-nested": ("1.2.3", "ahead", None),
            "nested": (None, "unknown", "missing"),
            "nested-quoted": (None, "unknown", "missing"),
            "near-miss": (None, "unknown", "missing"),
            # PyYAML rejects a tab between key and colon.
            "tab-before-colon": (None, "unknown", "missing"),
            "quoted-key-junk-value": ('"1.2.3" trailing-junk', "unknown", "SemVer"),
        }
        for name, (current_version, delta, reason) in expected.items():
            row = rows.get((name, agents_root))
            assert_true(row is not None, f"missing version row for {name}: {sorted(rows)}")
            actual = (row["current_version"], row["version_delta"])
            assert_true(
                actual == (current_version, delta),
                f"{name}: expected {(current_version, delta)}, got {actual}: {copies[name]!r}",
            )
            assert_true(
                reason is None or reason in (row["version_note"] or ""),
                f"{name}: unknown delta must say why: {row}",
            )


def test_quoted_versions_read_as_yaml_scalars() -> None:
    """A quoted version or key means what YAML reads it as, escapes included.

    Double quotes decode `x`, `u`, and `U` hex escapes, so they can spell a
    version; backslashes elsewhere are literal. A malformed escape, or one naming
    a surrogate or a code point past U+10FFFF, is reported as written: a lone
    surrogate would break printing the summary.
    """
    bs = "\\"
    with isolated_tempdir() as td:
        skills, agents, _, _ = _version_fixture(Path(td))
        # name: (frontmatter, current_version, delta, note reason)
        cases = {
            "x-escape": (f'version: "{bs}x31.2.3"', "1.2.3", "ahead", None),
            "u-escape": (f'version: "{bs}u0031.2.3"', "1.2.3", "ahead", None),
            "big-u-escape": (f'version: "{bs}U00000031.2.3"', "1.2.3", "ahead", None),
            "uppercase-hex": (f'version: "1{bs}u002E2.3"', "1.2.3", "ahead", None),
            "mixed": (f'version: "1.{bs}x32.3-rc.{bs}u0031"', "1.2.3-rc.1", "ahead", None),
            # The checker strips a decoded version as it strips any other.
            "escaped-space": (f'version: "{bs}x201.2.3"', "1.2.3", "ahead", None),
            "escaped-quote-in-comment": (f'version: "{bs}x31.2.3" # {bs}"', "1.2.3", "ahead", None),
            "escaped-key": (f'"{bs}x76ersion": 1.2.3', "1.2.3", "ahead", None),
            "escaped-key-and-value": (f'"{bs}u0076ersion": "{bs}u0031.2.3"', "1.2.3", "ahead", None),
            "escaped-backslash": (f'version: "{bs}{bs}u0031.2.3"', f"{bs}u0031.2.3", "unknown", "SemVer"),
            "escaped-trailing-backslash": (f'version: "1.2.3{bs}{bs}" # c', f"1.2.3{bs}", "unknown", "SemVer"),
            "single-quoted": (f"version: '{bs}u0031.2.3'", f"{bs}u0031.2.3", "unknown", "SemVer"),
            "single-quoted-quote": ("version: '1.2''3'", "1.2'3", "unknown", "SemVer"),
            "plain": (f"version: {bs}u0031.2.3", f"{bs}u0031.2.3", "unknown", "SemVer"),
            "decoded-then-junk": (f'version: "{bs}u0031.2.3" junk', f'"{bs}u0031.2.3" junk', "unknown", "SemVer"),
            "truncated-u": (f'version: "{bs}u003"', f'"{bs}u003"', "unknown", "SemVer"),
            "truncated-x": (f'version: "1.2.3{bs}x3"', f'"1.2.3{bs}x3"', "unknown", "SemVer"),
            "non-hex": (f'version: "{bs}u00zz.2.3"', f'"{bs}u00zz.2.3"', "unknown", "SemVer"),
            # int(..., 16) would accept the underscore and read 1.2.3.
            "underscore-hex": (f'version: "{bs}u0_31.2.3"', f'"{bs}u0_31.2.3"', "unknown", "SemVer"),
            "unknown-escape": (f'version: "{bs}q1.2.3"', f'"{bs}q1.2.3"', "unknown", "SemVer"),
            "unterminated": (f'version: "1.2.3{bs}"', f'"1.2.3{bs}"', "unknown", "SemVer"),
            "surrogate": (f'version: "{bs}uD800"', f'"{bs}uD800"', "unknown", "SemVer"),
            "big-u-surrogate": (f'version: "{bs}U0000DFFF1.2.3"', f'"{bs}U0000DFFF1.2.3"', "unknown", "SemVer"),
            "past-unicode": (f'version: "{bs}U00110000"', f'"{bs}U00110000"', "unknown", "SemVer"),
            "single-quoted-escaped-key": (f"'{bs}x76ersion': 9.9.9", None, "unknown", "missing"),
            "malformed-key": (f'"{bs}x7version": 9.9.9', None, "unknown", "missing"),
            "surrogate-key": (f'"{bs}uD800ersion": 9.9.9', None, "unknown", "missing"),
            "nested-escaped-key": (f'metadata:\n  "{bs}x76ersion": 9.9.9', None, "unknown", "missing"),
        }
        for name, (frontmatter, _, _, _) in cases.items():
            write_versioned_skill(skills, name, "1.0.0")
            write_frontmatter_skill(agents, name, frontmatter)

        report = _version_audit(skills)
        rows = _version_rows(report)
        agents_root = str(agents.resolve())
        for name, (frontmatter, current_version, delta, reason) in cases.items():
            row = rows.get((name, agents_root))
            assert_true(row is not None, f"missing version row for {name}: {sorted(rows)}")
            actual = (row["current_version"], row["version_delta"])
            assert_true(
                actual == (current_version, delta),
                f"{name}: expected {(current_version, delta)}, got {actual}: {frontmatter!r}",
            )
            assert_true(
                reason is None or reason in (row["version_note"] or ""),
                f"{name}: unknown delta must say why: {row}",
            )
        # Both report formats must still encode.
        summarize_report(report).encode("utf-8")
        json.dumps(report, ensure_ascii=False).encode("utf-8")


def test_version_precedence_follows_semver_ordering() -> None:
    """Numeric parts compare as numbers, prereleases rank below their release."""
    # The precedence example from the SemVer 2.0.0 specification, plus core
    # components whose string order differs from their numeric order.
    ascending = (
        "1.0.0-alpha",
        "1.0.0-alpha.1",
        "1.0.0-alpha.beta",
        "1.0.0-beta",
        "1.0.0-beta.2",
        "1.0.0-beta.11",
        "1.0.0-rc.1",
        "1.0.0",
        "1.9.0",
        "1.10.0",
        "2.0.0",
        "10.0.0",
    )
    for lower, higher in zip(ascending, ascending[1:]):
        assert_true(
            version_delta(higher, lower, False) == ("behind", None),
            f"{lower} must be behind {higher}",
        )
        assert_true(
            version_delta(lower, higher, False) == ("ahead", None),
            f"{higher} must be ahead of {lower}",
        )
    assert_true(
        version_delta("1.0.0+build.1", "1.0.0+build.2", True) == ("equal", None),
        "build metadata has no precedence",
    )
    # The grammar's `\d` admits non-ASCII decimal digits; they compare by value
    # (20 < 21), not by code point (U+0660 sorts after "1").
    assert_true(
        version_delta("1.21.0", "1.2٠.0", False) == ("behind", None),
        "non-ASCII digits must compare by value",
    )
    # Distinct spellings of one value are equal precedence, so comparison moves
    # on to the next identifier, then to identifier count.
    for left, right in (("1.0.0-11", "1.0.0-1١"), ("1.0.0-1١", "1.0.0-11")):
        assert_true(
            version_delta(left, right, True) == ("equal", None),
            f"{right} must equal {left} in precedence",
        )
        assert_true(
            version_delta(left, right, False)[0] == "divergent",
            f"{right} over different content must be divergent from {left}",
        )
    for lower, higher in (
        ("1.0.0-1١.alpha", "1.0.0-11.beta"),
        ("1.0.0-11.alpha", "1.0.0-1١.beta"),
        ("1.0.0-1١", "1.0.0-11.1"),
        ("1.0.0-11", "1.0.0-1١.1"),
    ):
        assert_true(
            version_delta(higher, lower, False) == ("behind", None),
            f"{lower} must be behind {higher}",
        )
        assert_true(
            version_delta(lower, higher, False) == ("ahead", None),
            f"{higher} must be ahead of {lower}",
        )


def test_huge_numeric_versions_compare_without_crashing_the_audit() -> None:
    """SemVer sets no digit limit, so neither may the comparison.

    Python's int() refuses strings past its digit limit (4300 by default). A
    copy declaring a longer numeric part is still valid SemVer: it must compare
    by value, and every other skill must still be reported.
    """
    huge = "1" + "0" * 5000
    huge_plus_one = "1" + "0" * 4999 + "1"
    with isolated_tempdir() as td:
        skills, agents, _, _ = _version_fixture(Path(td))
        pairs = {
            "huge-major": ("1.0.0", f"{huge}.0.0", "ahead"),
            "huge-minor": (f"1.{huge_plus_one}.0", f"1.{huge}.0", "behind"),
            "huge-patch-shorter": (f"1.0.{huge}", f"1.0.9{'9' * 4000}", "behind"),
            "huge-equal": (f"{huge}.0.0", f"{huge}.0.0", "equal"),
            "huge-prerelease": (f"1.0.0-rc.{huge}", f"1.0.0-rc.{huge_plus_one}", "ahead"),
            "huge-prerelease-vs-alpha": (f"1.0.0-rc.{huge}", "1.0.0-rc.a", "ahead"),
            "huge-prerelease-vs-release": ("1.0.0", f"1.0.0-{huge}", "behind"),
            # The same value spelled with a non-ASCII digit: equal precedence
            # over different content.
            "huge-prerelease-respelled": (f"1.0.0-rc.{huge}", f"1.0.0-rc.{huge[:-1]}٠", "divergent"),
            "prerelease-respelled": ("1.0.0-11", "1.0.0-1١", "divergent"),
            "ordinary": ("1.2.0", "1.10.0", "ahead"),
        }
        for name, (source_version, current_version, _) in pairs.items():
            write_versioned_skill(skills, name, source_version)
            write_versioned_skill(agents, name, current_version)

        rows = _version_rows(_version_audit(skills))
        agents_root = str(agents.resolve())
        for name, (_, _, delta) in pairs.items():
            row = rows.get((name, agents_root))
            assert_true(row is not None, f"missing version row for {name}: {sorted(rows)}")
            assert_true(
                row["version_delta"] == delta,
                f"{name}: expected {delta}, got {row['version_delta']}: {row['version_note']}",
            )


def test_version_rows_follow_skill_selection() -> None:
    with isolated_tempdir() as td:
        skills, agents, _, _ = _version_fixture(Path(td))
        for name in ("alpha", "beta"):
            write_versioned_skill(skills, name, "1.1.0")
            write_versioned_skill(agents, name, "1.0.0")

        report = _version_audit(skills, selected={"alpha"})
        skills_reported = {row["skill"] for row in report.get("versions", [])}
        assert_true(skills_reported == {"alpha"}, f"selection must scope version rows: {skills_reported}")


def test_version_source_is_the_preferred_global_without_canonical() -> None:
    with isolated_tempdir() as td:
        _, agents, _, claude = _version_fixture(Path(td), with_canonical=False)
        write_versioned_skill(agents, "alpha", "2.0.0")
        write_versioned_skill(claude, "alpha", "1.0.0")

        report = _version_audit(None)
        assert_true(report["canonical_root"] is None, f"fixture must have no canonical: {report['canonical_root']}")
        row = _version_rows(report).get(("alpha", str(claude.resolve())))
        assert_true(row is not None, f"missing global-only version row: {report.get('versions')}")
        assert_true(
            (row["source_root"], row["version_delta"]) == (str(agents.resolve()), "behind"),
            f"preferred global is the source without canonical: {row}",
        )


# The direct runner's order; tests/test_skill_standardizer_suite.py also runs
# each entry under pytest and checks that it restores process state.
TESTS = (
    test_review_lenses_consolidate_without_local_review,
    test_review_lenses_consolidate_with_only_primary_local_review,
    test_review_lenses_consolidate_into_existing_local_review,
    test_obsidian_format_skills_consolidate_into_obsidian,
    test_agent_native_rename_migrates_existing_installations,
    test_invalid_entries_do_not_emit_missing_actions,
    test_underscore_dirs_are_not_invalid_in_full_scan,
    test_known_non_skill_dir_ignored_in_owning_root,
    test_known_non_skill_dir_still_reported_in_other_roots,
    test_claude_synced_skills_dir_ignored_in_claude_root,
    test_claude_synced_dir_still_reported_in_the_primary_root,
    test_mirror_never_targets_a_tool_owned_dir,
    test_ignore_dir_flag_suppresses_custom_dir,
    test_audit_exit_code_tracks_drift_not_warnings,
    test_audit_exit_code_reports_real_drift,
    test_deprecated_replacement_uses_real_source,
    test_apply_orders_copy_before_link,
    test_apply_copy_ignores_generated_files,
    test_selected_skill_limits_mirror_scope_and_invalid_reports,
    test_selected_skill_apply_creates_only_requested_global_mirror,
    test_selected_missing_skill_reports_typo,
    test_a_project_root_linking_to_canonical_is_not_a_duplicate,
    test_a_project_root_holding_a_copy_is_still_reported,
    test_stale_secondary_link_is_removed_not_relinked,
    test_a_broken_primary_entry_is_still_restored_from_canonical,
    test_sync_preserves_unknown_backup_history,
    test_mirror_copy_repairs_a_secondary_entry_instead_of_removing_it,
    test_a_failed_apply_does_not_prune_backup_history,
    test_version_deltas_report_behind_ahead_equal_and_divergent,
    test_missing_and_malformed_versions_are_unknown_not_zero,
    test_version_key_spellings_follow_yaml,
    test_quoted_versions_read_as_yaml_scalars,
    test_version_precedence_follows_semver_ordering,
    test_huge_numeric_versions_compare_without_crashing_the_audit,
    test_version_rows_follow_skill_selection,
    test_version_source_is_the_preferred_global_without_canonical,
)


def main() -> int:
    for test in TESTS:
        test()
        print(f"PASS {test.__name__}")

    print("All skill-standardizer regression tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
