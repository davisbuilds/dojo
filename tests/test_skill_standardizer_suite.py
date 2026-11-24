"""Regression tests for skill-standardizer planning and apply behavior."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path

import pytest


SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "skill-standardizer" / "scripts"


def _load_script_main(module_name: str, filename: str):
    spec = importlib.util.spec_from_file_location(module_name, SCRIPTS / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.main


with pytest.MonkeyPatch.context() as imports:
    imports.syspath_prepend(str(SCRIPTS))
    from skill_standardizer_lib import (
        apply_actions,
        build_audit_report,
        resolve_context,
        root_describe,
        summarize_report,
        version_delta,
    )

    audit_main = _load_script_main("skill_standardizer_audit", "audit.py")
    discover_main = _load_script_main("skill_standardizer_discover", "discover.py")
    sync_main = _load_script_main("skill_standardizer_sync", "sync.py")


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


HOME_ENV_NAMES = ("AGENTS_HOME", "CODEX_HOME", "CLAUDE_HOME", "GEMINI_HOME")


@pytest.fixture(autouse=True)
def isolate_harness_homes(tmp_path, monkeypatch):
    """Keep harness discovery and any writes inside the test's temporary directory."""
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    for name in HOME_ENV_NAMES:
        monkeypatch.setenv(name, str(home / name.lower()))
    monkeypatch.chdir(tmp_path)


def test_a_project_root_linking_to_canonical_is_not_a_duplicate(tmp_path, monkeypatch) -> None:
    """A project may link directly to canonical even when a global copy exists."""
    repo = tmp_path / "repo"
    skills = repo / "skills"
    skills.mkdir(parents=True)
    (repo / "AGENTS.md").write_text("x", encoding="utf-8")
    write_skill(skills, "write-plan")

    agents_home = tmp_path / ".agents"
    codex_home = tmp_path / ".codex"
    claude_home = tmp_path / ".claude"
    for home in [agents_home, codex_home, claude_home]:
        (home / "skills").mkdir(parents=True)
    write_skill(agents_home / "skills", "write-plan")

    project = tmp_path / "some-project" / ".agents" / "skills"
    project.mkdir(parents=True)
    os.symlink(str(skills / "write-plan"), project / "write-plan")

    monkeypatch.setenv("AGENTS_HOME", str(agents_home))
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    monkeypatch.setenv("CLAUDE_HOME", str(claude_home))
    monkeypatch.chdir(repo)

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
    assert not offending, f"a link to canonical must not read as a local duplicate: {offending}"


def test_a_project_root_holding_a_copy_is_still_reported(tmp_path, monkeypatch) -> None:
    """The control. Accepting a link must not accept a copy along with it."""
    repo = tmp_path / "repo"
    skills = repo / "skills"
    skills.mkdir(parents=True)
    (repo / "AGENTS.md").write_text("x", encoding="utf-8")
    write_skill(skills, "write-plan")

    agents_home = tmp_path / ".agents"
    codex_home = tmp_path / ".codex"
    claude_home = tmp_path / ".claude"
    for home in [agents_home, codex_home, claude_home]:
        (home / "skills").mkdir(parents=True)
    write_skill(agents_home / "skills", "write-plan")

    project = tmp_path / "some-project" / ".agents" / "skills"
    project.mkdir(parents=True)
    write_skill(project, "write-plan")

    monkeypatch.setenv("AGENTS_HOME", str(agents_home))
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    monkeypatch.setenv("CLAUDE_HOME", str(claude_home))
    monkeypatch.chdir(repo)

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
    assert any(code.startswith("LOCAL_DUPLICATE_GLOBAL") for code in codes), (
        f"a project copy of a global skill must still be reported: {codes}"
    )


def test_invalid_entries_do_not_emit_missing_actions(tmp_path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    skills = repo / "skills"
    skills.mkdir(parents=True)
    (repo / "AGENTS.md").write_text("x", encoding="utf-8")
    write_skill(skills, "brainstorming")

    agents_home = tmp_path / ".agents"
    codex_home = tmp_path / ".codex"
    claude_home = tmp_path / ".claude"
    for home in [agents_home, codex_home, claude_home]:
        (home / "skills").mkdir(parents=True)

    os.symlink(str(agents_home / "skills" / "brainstorming"), agents_home / "skills" / "brainstorming")
    os.symlink(str(agents_home / "skills" / "brainstorming"), codex_home / "skills" / "brainstorming")
    os.symlink(str(agents_home / "skills" / "brainstorming"), claude_home / "skills" / "brainstorming")

    monkeypatch.setenv("AGENTS_HOME", str(agents_home))
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    monkeypatch.setenv("CLAUDE_HOME", str(claude_home))
    monkeypatch.chdir(repo)

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
    assert not missing_codes, f"unexpected missing codes for invalid entry: {missing_codes}"

    actions = [action for action in report["actions"] if action["skill"] == "brainstorming"]
    action_types = [action["action"] for action in actions]
    assert action_types == ["sync_copy", "relink_to_global", "relink_to_global"], (
        f"unexpected action set for invalid brainstorming entries: {actions}"
    )


def test_review_lenses_consolidate_into_existing_local_review(tmp_path, monkeypatch) -> None:
    check_review_lens_consolidation(tmp_path, monkeypatch, "all")


def test_review_lenses_consolidate_without_local_review(tmp_path, monkeypatch) -> None:
    check_review_lens_consolidation(tmp_path, monkeypatch, "none")


def test_review_lenses_consolidate_with_only_primary_local_review(tmp_path, monkeypatch) -> None:
    check_review_lens_consolidation(tmp_path, monkeypatch, "primary")


def check_review_lens_consolidation(tmp_path, monkeypatch, existing_roots: str) -> None:
    repo = tmp_path / "repo"
    canonical = repo / "skills"
    source = write_skill(canonical, "local-review")
    roots = [tmp_path / name / "skills" for name in [".agents", ".codex", ".claude"]]
    for env_name, root in zip(("AGENTS_HOME", "CODEX_HOME", "CLAUDE_HOME"), roots):
        monkeypatch.setenv(env_name, str(root.parent))
        if existing_roots == "all" or (existing_roots == "primary" and root == roots[0]):
            existing = write_skill(root, "local-review")
            (existing / "SKILL.md").write_text((existing / "SKILL.md").read_text().replace("1.0.0", "0.9.0"))
        for old_name in ["error-handling-review", "type-design-review"]:
            old = write_skill(root, old_name)
            (old / "local-note.md").write_text(old_name)
    monkeypatch.chdir(repo)

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
    assert len(replacements) == 6, "both old lenses must migrate in all three roots"
    backup_root = tmp_path / "backups"
    for _ in range(2):
        result = apply_actions(audit(), apply=True, backup_root=str(backup_root))
        assert not result["errors"], f"migration failed: {result}"
        for root in roots:
            assert (root / "local-review" / "SKILL.md").read_bytes() == (source / "SKILL.md").read_bytes(), (
                "replacement missing or stale after apply"
            )
            for old_name in ["error-handling-review", "type-design-review"]:
                assert not (root / old_name).exists(), "old lens survived a successful apply"
    for root in roots:
        assert (root / "local-review" / "SKILL.md").read_bytes() == (source / "SKILL.md").read_bytes(), (
            "replacement differs from canonical"
        )
        for old_name in ["error-handling-review", "type-design-review"]:
            assert not (root / old_name).exists(), "old lens survived"
    assert len(list(backup_root.rglob("local-note.md"))) == 6, "old lenses not preserved"
    assert not audit()["actions"], "consolidation did not converge"


@pytest.mark.parametrize("selected_skill", ["obsidian", "obsidian-canvas", "json-canvas"])
@pytest.mark.parametrize("linked_secondaries", [False, True], ids=["copies", "links"])
def test_obsidian_format_skills_consolidate_into_obsidian(
    tmp_path, monkeypatch, selected_skill, linked_secondaries,
) -> None:
    """Selecting a replacement or alias migrates all aliases for that skill."""
    selection = {selected_skill}
    old_names = ["obsidian-markdown", "obsidian-bases", "obsidian-canvas", "json-canvas"]
    repo = tmp_path / "repo"
    canonical = repo / "skills"
    source = write_skill(canonical, "obsidian")
    roots = [tmp_path / name / "skills" for name in [".agents", ".codex", ".claude"]]
    for env_name, root in zip(("AGENTS_HOME", "CODEX_HOME", "CLAUDE_HOME"), roots):
        monkeypatch.setenv(env_name, str(root.parent))
        for old_name in old_names:
            if linked_secondaries and root != roots[0]:
                root.mkdir(parents=True, exist_ok=True)
                (root / old_name).symlink_to(roots[0] / old_name, target_is_directory=True)
            else:
                old = write_skill(root, old_name)
                (old / "local-note.md").write_text(old_name)
    monkeypatch.chdir(repo)

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
    assert len(migrations) == len(old_names) * len(roots), (
        f"every old Obsidian skill must migrate in every root for selection {selection}: {migrations}"
    )
    backup_root = tmp_path / "backups"
    for _ in range(2):
        result = apply_actions(audit(), apply=True, backup_root=str(backup_root))
        assert not result["errors"], f"migration failed: {result}"
    for root in roots:
        assert (root / "obsidian" / "SKILL.md").read_bytes() == (source / "SKILL.md").read_bytes(), (
            "consolidated skill missing or differs from canonical"
        )
        for old_name in old_names:
            assert not os.path.lexists(root / old_name), (
                f"{old_name} survived consolidation for selection {selection}"
            )
    assert (
        len(list(backup_root.rglob("local-note.md"))) == len(old_names) * (1 if linked_secondaries else len(roots))
    ), (
        "old installations were not backed up"
    )
    assert not audit()["actions"], "consolidation did not converge"


def test_agent_native_rename_migrates_existing_installations(tmp_path, monkeypatch) -> None:
    check_skill_rename(tmp_path, monkeypatch, "agent-native-architecture", "agent-native-design", linked_secondaries=False)


def test_cli_design_rename_migrates_existing_installations(tmp_path, monkeypatch) -> None:
    check_skill_rename(tmp_path, monkeypatch, "create-cli", "cli-design", linked_secondaries=True)


def check_skill_rename(tmp_path, monkeypatch, old_name: str, new_name: str, *, linked_secondaries: bool) -> None:
    for case, selection in enumerate([set(), {old_name}, {new_name}]):
        base = tmp_path / str(case)
        repo = base / "repo"
        canonical = repo / "skills"
        source = write_skill(canonical, new_name)
        write_skill(canonical, "unrelated")
        roots = [base / name / "skills" for name in [".agents", ".codex", ".claude"]]
        for env_name, root in zip(("AGENTS_HOME", "CODEX_HOME", "CLAUDE_HOME"), roots):
            monkeypatch.setenv(env_name, str(root.parent))
            if linked_secondaries and root != roots[0]:
                root.mkdir(parents=True)
                (root / old_name).symlink_to(roots[0] / old_name, target_is_directory=True)
            else:
                old = write_skill(root, old_name)
                (old / "local-note.md").write_text("preserve this old installation")
        monkeypatch.chdir(repo)

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
        assert len(replacements) == 3, f"old installs must migrate for selection {selection}: {report}"
        deprecated_issues = [issue for issue in report["issues"] if issue["code"] == "DEPRECATED_SKILL_NAME"]
        assert len(deprecated_issues) == 3, f"audit must report each deprecated install: {report}"
        backup_root = base / "backups"
        result = apply_actions(report, apply=True, backup_root=str(backup_root))
        assert not result["errors"], f"migration failed: {result}"
        for root in roots:
            assert not os.path.lexists(root / old_name), "old name survived migration"
            assert (root / new_name / "SKILL.md").read_bytes() == (source / "SKILL.md").read_bytes(), (
                "replacement differs from canonical"
            )
            assert not (root / "unrelated").exists(), "migration installed an unrelated skill"
        saved_notes = list(backup_root.rglob("local-note.md"))
        expected_saved_notes = 1 if linked_secondaries else len(roots)
        assert len(saved_notes) == expected_saved_notes, "old installations were not backed up"
        assert all(p.read_text() == "preserve this old installation" for p in saved_notes), (
            "backup content changed"
        )
        followup = apply_actions(audit(), apply=True, backup_root=str(backup_root))
        assert not followup["errors"], f"normalization failed: {followup}"
        assert not audit()["actions"], "migration did not converge"
        primary = roots[0] / new_name
        assert not primary.is_symlink(), "primary installation should be a concrete copy"
        for root in roots[1:]:
            installed = root / new_name
            assert installed.is_symlink() and installed.resolve() == primary.resolve(), (
                f"secondary installation must link to primary: {installed}"
            )


def test_deprecated_replacement_uses_real_source(tmp_path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    skills = repo / "skills"
    skills.mkdir(parents=True)
    (repo / "AGENTS.md").write_text("x", encoding="utf-8")
    write_skill(skills, "obsidian")

    agents_home = tmp_path / ".agents"
    codex_home = tmp_path / ".codex"
    claude_home = tmp_path / ".claude"
    for home in [agents_home, codex_home, claude_home]:
        (home / "skills").mkdir(parents=True)

    os.symlink(str(claude_home / "skills" / "json-canvas"), claude_home / "skills" / "json-canvas")

    monkeypatch.setenv("AGENTS_HOME", str(agents_home))
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    monkeypatch.setenv("CLAUDE_HOME", str(claude_home))
    monkeypatch.chdir(repo)

    report = build_audit_report(
        context=resolve_context(str(skills), [], False),
        local_policy="prefer-global-link",
        global_policy="prefer-primary-link",
        keep_local_skills=set(),
        enforce_mirror=True,
        codex_agents_dedupe=True,
    )

    replacements = [action for action in report["actions"] if action["action"] == "replace_deprecated_skill"]
    assert len(replacements) == 1, f"expected exactly one deprecated replacement action: {replacements}"
    replacement = replacements[0]
    assert replacement.get("link") is False, f"replacement should copy from canonical source: {replacement}"
    assert replacement["source"].endswith("/repo/skills/obsidian"), (
        f"replacement should use canonical source when primary mirror is missing: {replacement}"
    )


def test_apply_orders_copy_before_link(tmp_path) -> None:
    source = write_skill(tmp_path / "canonical", "brainstorming")
    global_root = tmp_path / "globals"
    global_root.mkdir()

    report = {
        "actions": [
            {
                "action": "relink_to_global",
                "skill": "brainstorming",
                "source": str(global_root / "brainstorming"),
                "dest": str(tmp_path / "local" / "brainstorming"),
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

    result = apply_actions(report, apply=True, backup_root=str(tmp_path / "backups"))
    assert not result["errors"], f"apply_actions should succeed: {result}"

    local = tmp_path / "local" / "brainstorming"
    assert local.is_symlink(), f"local skill should be a symlink: {local}"
    assert local.exists(), f"local symlink should resolve successfully: {local}"


def test_apply_copy_ignores_generated_files(tmp_path) -> None:
    source = write_skill(tmp_path / "canonical", "brainstorming")
    (source / ".DS_Store").write_text("mac metadata", encoding="utf-8")
    (source / ".pytest_cache").mkdir()
    (source / ".pytest_cache" / "README.md").write_text("cache", encoding="utf-8")
    (source / "scripts" / "__pycache__").mkdir(parents=True)
    (source / "scripts" / "__pycache__" / "helper.cpython-314.pyc").write_bytes(b"cache")
    dest = tmp_path / "globals" / "brainstorming"

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

    result = apply_actions(report, apply=True, backup_root=str(tmp_path / "backups"))
    assert not result["errors"], f"apply_actions should succeed: {result}"
    assert (dest / "SKILL.md").exists(), "skill content should be copied"
    assert not (dest / ".DS_Store").exists(), ".DS_Store should not be copied"
    assert not (dest / ".pytest_cache").exists(), ".pytest_cache should not be copied"
    assert not (dest / "scripts" / "__pycache__").exists(), "__pycache__ should not be copied"


def test_selected_skill_limits_mirror_scope_and_invalid_reports(tmp_path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    skills = repo / "skills"
    skills.mkdir(parents=True)
    (repo / "AGENTS.md").write_text("x", encoding="utf-8")
    write_skill(skills, "alpha")
    write_skill(skills, "beta")
    (skills / "_fragments").mkdir()

    agents_home = tmp_path / ".agents"
    codex_home = tmp_path / ".codex"
    claude_home = tmp_path / ".claude"
    for home in [agents_home, codex_home, claude_home]:
        (home / "skills").mkdir(parents=True)

    monkeypatch.setenv("AGENTS_HOME", str(agents_home))
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    monkeypatch.setenv("CLAUDE_HOME", str(claude_home))
    monkeypatch.chdir(repo)

    report = build_audit_report(
        context=resolve_context(str(skills), [], False),
        local_policy="prefer-global-link",
        global_policy="prefer-primary-link",
        keep_local_skills=set(),
        enforce_mirror=True,
        codex_agents_dedupe=True,
        selected_skills={"alpha"},
    )

    assert report["selected_skills"] == ["alpha"], f"selected scope missing: {report}"
    assert {action["skill"] for action in report["actions"]} == {"alpha"}, (
        f"targeted audit should only plan alpha actions: {report['actions']}"
    )
    assert all(issue.get("skill") == "alpha" for issue in report["issues"]), (
        f"targeted audit should only report alpha issues: {report['issues']}"
    )
    assert all("_fragments" not in root["invalid_entries"] for root in report["roots"]), (
        f"targeted audit should hide unrelated invalid dirs: {report['roots']}"
    )


def test_selected_skill_apply_creates_only_requested_global_mirror(tmp_path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    skills = repo / "skills"
    skills.mkdir(parents=True)
    (repo / "AGENTS.md").write_text("x", encoding="utf-8")
    write_skill(skills, "alpha")
    write_skill(skills, "beta")

    agents_home = tmp_path / ".agents"
    codex_home = tmp_path / ".codex"
    claude_home = tmp_path / ".claude"
    for home in [agents_home, codex_home, claude_home]:
        (home / "skills").mkdir(parents=True)

    monkeypatch.setenv("AGENTS_HOME", str(agents_home))
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    monkeypatch.setenv("CLAUDE_HOME", str(claude_home))
    monkeypatch.chdir(repo)

    report = build_audit_report(
        context=resolve_context(str(skills), [], False),
        local_policy="prefer-global-link",
        global_policy="prefer-primary-link",
        keep_local_skills=set(),
        enforce_mirror=True,
        codex_agents_dedupe=True,
        selected_skills={"alpha"},
    )
    result = apply_actions(report, apply=True, backup_root=str(tmp_path / "backups"))

    assert not result["errors"], f"selected apply should succeed: {result}"
    primary_alpha = agents_home / "skills" / "alpha"
    assert primary_alpha.is_dir(), "selected skill should be copied to primary global"
    assert (codex_home / "skills" / "alpha").is_symlink(), "selected skill should be linked into Codex global"
    assert (claude_home / "skills" / "alpha").is_symlink(), "selected skill should be linked into Claude global"
    for home in [agents_home, codex_home, claude_home]:
        assert not (home / "skills" / "beta").exists(), f"unselected skill should not be installed into {home}"


def test_selected_missing_skill_reports_typo(tmp_path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    skills = repo / "skills"
    skills.mkdir(parents=True)
    (repo / "AGENTS.md").write_text("x", encoding="utf-8")
    write_skill(skills, "alpha")

    agents_home = tmp_path / ".agents"
    codex_home = tmp_path / ".codex"
    claude_home = tmp_path / ".claude"
    for home in [agents_home, codex_home, claude_home]:
        (home / "skills").mkdir(parents=True)

    monkeypatch.setenv("AGENTS_HOME", str(agents_home))
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    monkeypatch.setenv("CLAUDE_HOME", str(claude_home))
    monkeypatch.chdir(repo)

    report = build_audit_report(
        context=resolve_context(str(skills), [], False),
        local_policy="prefer-global-link",
        global_policy="prefer-primary-link",
        keep_local_skills=set(),
        enforce_mirror=True,
        codex_agents_dedupe=True,
        selected_skills={"typo"},
    )

    assert [issue["code"] for issue in report["issues"]] == ["SELECTED_SKILL_NOT_FOUND"], (
        f"missing selected skill should be reported clearly: {report['issues']}"
    )
    assert not report["actions"], f"missing selected skill should not plan actions: {report['actions']}"


def test_underscore_dirs_are_not_invalid_in_full_scan(tmp_path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    skills = repo / "skills"
    skills.mkdir(parents=True)
    (repo / "AGENTS.md").write_text("x", encoding="utf-8")
    write_skill(skills, "alpha")
    (skills / "_fragments").mkdir()
    (skills / "_fragments" / "shared.md").write_text("fragment", encoding="utf-8")

    agents_home = tmp_path / ".agents"
    codex_home = tmp_path / ".codex"
    claude_home = tmp_path / ".claude"
    for home in [agents_home, codex_home, claude_home]:
        (home / "skills").mkdir(parents=True)

    monkeypatch.setenv("AGENTS_HOME", str(agents_home))
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    monkeypatch.setenv("CLAUDE_HOME", str(claude_home))
    monkeypatch.chdir(repo)

    report = build_audit_report(
        context=resolve_context(str(skills), [], False),
        local_policy="prefer-global-link",
        global_policy="prefer-primary-link",
        keep_local_skills=set(),
        enforce_mirror=True,
        codex_agents_dedupe=True,
    )

    assert all("_fragments" not in root["invalid_entries"] for root in report["roots"]), (
        f"full-scan audit should not treat _fragments as invalid: {report['roots']}"
    )
    assert all(issue.get("skill") != "_fragments" for issue in report["issues"]), (
        f"full-scan audit should not raise issues for _fragments: {report['issues']}"
    )


def test_audit_exit_code_tracks_drift_not_warnings(tmp_path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    skills = repo / "skills"
    skills.mkdir(parents=True)
    (repo / "AGENTS.md").write_text("x", encoding="utf-8")
    write_skill(skills, "alpha")

    agents_home = tmp_path / ".agents"
    codex_home = tmp_path / ".codex"
    claude_home = tmp_path / ".claude"
    for home in [agents_home, codex_home, claude_home]:
        (home / "skills").mkdir(parents=True)

    (codex_home / "skills" / "codex-primary-runtime").mkdir()

    monkeypatch.setenv("AGENTS_HOME", str(agents_home))
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    monkeypatch.setenv("CLAUDE_HOME", str(claude_home))
    monkeypatch.chdir(repo)

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

    assert exit_code == 0, f"audit with warnings but no planned actions should exit 0, got {exit_code}"


def test_audit_exit_code_reports_real_drift(tmp_path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    skills = repo / "skills"
    skills.mkdir(parents=True)
    (repo / "AGENTS.md").write_text("x", encoding="utf-8")
    write_skill(skills, "alpha")

    agents_home = tmp_path / ".agents"
    codex_home = tmp_path / ".codex"
    claude_home = tmp_path / ".claude"
    for home in [agents_home, codex_home, claude_home]:
        (home / "skills").mkdir(parents=True)

    drifted = agents_home / "skills" / "alpha"
    drifted.mkdir(parents=True)
    (drifted / "SKILL.md").write_text("---\nname: alpha\n---\n\n# drifted\n", encoding="utf-8")

    monkeypatch.setenv("AGENTS_HOME", str(agents_home))
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    monkeypatch.setenv("CLAUDE_HOME", str(claude_home))
    monkeypatch.chdir(repo)

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

    assert exit_code == 2, f"audit with real drift should exit 2, got {exit_code}"


def _audit_fixture(base: Path, monkeypatch) -> Path:
    repo = base / "repo"
    skills = repo / "skills"
    skills.mkdir(parents=True)
    (repo / "AGENTS.md").write_text("x", encoding="utf-8")
    write_skill(skills, "alpha")

    for home in [base / ".agents", base / ".codex", base / ".claude"]:
        (home / "skills").mkdir(parents=True)

    monkeypatch.setenv("AGENTS_HOME", str(base / ".agents"))
    monkeypatch.setenv("CODEX_HOME", str(base / ".codex"))
    monkeypatch.setenv("CLAUDE_HOME", str(base / ".claude"))
    monkeypatch.chdir(repo)
    return skills


def _invalid_for(report: dict, path: Path) -> list[str]:
    for root in report["roots"]:
        if root["path"] == str(path):
            return root["invalid_entries"]
    raise AssertionError(f"root not found in report: {path}")


def test_known_non_skill_dir_ignored_in_owning_root(tmp_path, monkeypatch) -> None:
    skills = _audit_fixture(tmp_path, monkeypatch)
    (tmp_path / ".codex" / "skills" / "codex-primary-runtime").mkdir()

    report = build_audit_report(
        context=resolve_context(str(skills), [], False),
        local_policy="prefer-global-link",
        global_policy="prefer-primary-link",
        keep_local_skills=set(),
        enforce_mirror=True,
        codex_agents_dedupe=True,
    )

    assert "codex-primary-runtime" not in _invalid_for(report, (tmp_path / ".codex" / "skills").resolve()), (
        f"codex-primary-runtime should be ignored in the codex root: {report['roots']}"
    )
    assert all(issue.get("skill") != "codex-primary-runtime" for issue in report["issues"]), (
        f"codex-primary-runtime should raise no issue: {report['issues']}"
    )


def test_known_non_skill_dir_still_reported_in_other_roots(tmp_path, monkeypatch) -> None:
    skills = _audit_fixture(tmp_path, monkeypatch)
    (skills / "codex-primary-runtime").mkdir()

    report = build_audit_report(
        context=resolve_context(str(skills), [], False),
        local_policy="prefer-global-link",
        global_policy="prefer-primary-link",
        keep_local_skills=set(),
        enforce_mirror=True,
        codex_agents_dedupe=True,
    )

    assert "codex-primary-runtime" in _invalid_for(report, skills.resolve()), (
        f"allowlist must not leak into the canonical root: {report['roots']}"
    )


def test_claude_synced_skills_dir_ignored_in_claude_root(tmp_path, monkeypatch) -> None:
    skills = _audit_fixture(tmp_path, monkeypatch)
    synced = tmp_path / ".claude" / "skills" / "synced"
    write_skill(synced / "bucket-id", "morning")

    report = build_audit_report(
        context=resolve_context(str(skills), [], False),
        local_policy="prefer-global-link",
        global_policy="prefer-primary-link",
        keep_local_skills=set(),
        enforce_mirror=True,
        codex_agents_dedupe=True,
    )

    assert "synced" not in _invalid_for(report, (tmp_path / ".claude" / "skills").resolve()), (
        f"synced should be ignored in the claude root: {report['roots']}"
    )
    assert all(issue.get("skill") != "synced" for issue in report["issues"]), (
        f"synced should raise no issue: {report['issues']}"
    )


def test_claude_synced_dir_still_reported_in_the_primary_root(tmp_path, monkeypatch) -> None:
    skills = _audit_fixture(tmp_path, monkeypatch)
    (tmp_path / ".agents" / "skills" / "synced").mkdir()

    report = build_audit_report(
        context=resolve_context(str(skills), [], False),
        local_policy="prefer-global-link",
        global_policy="prefer-primary-link",
        keep_local_skills=set(),
        enforce_mirror=True,
        codex_agents_dedupe=True,
    )

    assert "synced" in _invalid_for(report, (tmp_path / ".agents" / "skills").resolve()), (
        f"the claude exemption must not leak into the primary root: {report['roots']}"
    )


def test_mirror_never_targets_a_tool_owned_dir(tmp_path, monkeypatch) -> None:
    skills = _audit_fixture(tmp_path, monkeypatch)
    write_skill(skills, "synced")
    cache = tmp_path / ".claude" / "skills" / "synced"
    write_skill(cache / "bucket-id", "morning")

    report = build_audit_report(
        context=resolve_context(str(skills), [], False),
        local_policy="prefer-global-link",
        global_policy="prefer-primary-link",
        keep_local_skills=set(),
        enforce_mirror=True,
        codex_agents_dedupe=True,
    )

    claude_root = (tmp_path / ".claude" / "skills").resolve()
    assert (
        all(Path(a["dest"]).resolve() != claude_root / "synced"
            for a in report["actions"] if a.get("dest"))
    ), (
        f"no action may replace the tool-owned cache: {report['actions']}"
    )
    assert (
        any(i["code"] == "RESERVED_NAME_COLLISION" and i["skill"] == "synced"
            for i in report["issues"])
    ), (
        f"the collision must be reported: {report['issues']}"
    )


def test_ignore_dir_flag_suppresses_custom_dir(tmp_path, monkeypatch) -> None:
    skills = _audit_fixture(tmp_path, monkeypatch)
    (tmp_path / ".agents" / "skills" / "vendor-runtime").mkdir()

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

    assert exit_code == 0, f"--ignore-dir should suppress the warning, got exit {exit_code}"


def test_stale_secondary_link_is_removed_not_relinked(tmp_path, monkeypatch) -> None:
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
    repo = tmp_path / "repo"
    skills = repo / "skills"
    skills.mkdir(parents=True)
    (repo / "AGENTS.md").write_text("x", encoding="utf-8")
    write_skill(skills, "audit-skill")

    agents_home = tmp_path / ".agents"
    codex_home = tmp_path / ".codex"
    claude_home = tmp_path / ".claude"
    for home in [agents_home, codex_home, claude_home]:
        (home / "skills").mkdir(parents=True)

    stale = claude_home / "skills" / "audit-skill"
    os.symlink(str(agents_home / "skills" / "audit-skill"), stale)
    assert stale.is_symlink() and not stale.exists(), "fixture must start dangling or it proves nothing"

    monkeypatch.setenv("AGENTS_HOME", str(agents_home))
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    monkeypatch.setenv("CLAUDE_HOME", str(claude_home))
    monkeypatch.chdir(repo)

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
    assert "relink_to_global" not in types, f"must not relink to a source that does not exist: {actions}"
    assert "sync_copy" not in types, f"must not reinstall a deliberately removed skill: {actions}"
    assert types == ["remove_stale_entry"], f"expected a removal, got: {actions}"

    result = apply_actions(report, apply=True, backup_root=str(tmp_path / "backups"))
    assert not stale.is_symlink() and not stale.exists(), "the stale link must be gone after apply"
    assert bool(result["record_path"]), "link removal needs a recovery record"
    saved = json.loads(Path(result["record_path"]).read_text())
    assert saved["backups"][0]["recovery"]["kind"] == "symlink", "record exact link target"


def test_a_broken_primary_entry_is_still_restored_from_canonical(tmp_path, monkeypatch) -> None:
    """The case removal must not swallow.

    A broken directory in the *primary* global root is a damaged install of a
    skill that is meant to be there, so canonical restores it. Only a *secondary*
    root naming a skill absent from primary is stale.
    """
    repo = tmp_path / "repo"
    skills = repo / "skills"
    skills.mkdir(parents=True)
    (repo / "AGENTS.md").write_text("x", encoding="utf-8")
    write_skill(skills, "brainstorming")

    agents_home = tmp_path / ".agents"
    codex_home = tmp_path / ".codex"
    claude_home = tmp_path / ".claude"
    for home in [agents_home, codex_home, claude_home]:
        (home / "skills").mkdir(parents=True)

    (agents_home / "skills" / "brainstorming").mkdir()

    monkeypatch.setenv("AGENTS_HOME", str(agents_home))
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    monkeypatch.setenv("CLAUDE_HOME", str(claude_home))
    monkeypatch.chdir(repo)

    report = build_audit_report(
        context=resolve_context(str(skills), [], False),
        local_policy="prefer-global-link",
        global_policy="prefer-primary-link",
        keep_local_skills=set(),
        enforce_mirror=False,
        codex_agents_dedupe=True,
    )
    types = [a["action"] for a in report["actions"] if a["skill"] == "brainstorming"]
    assert "sync_copy" in types, f"a damaged primary entry must be restored from canonical: {types}"
    assert "remove_stale_entry" not in types, f"a damaged primary entry is not stale: {types}"


def test_sync_preserves_unknown_backup_history(tmp_path, monkeypatch) -> None:
    """Sync never ages out backups whose recovery has not been established."""
    repo = tmp_path / "repo"
    skills = repo / "skills"
    skills.mkdir(parents=True)
    (repo / "AGENTS.md").write_text("x", encoding="utf-8")
    write_skill(skills, "brainstorming")

    agents_home = tmp_path / ".agents"
    codex_home = tmp_path / ".codex"
    claude_home = tmp_path / ".claude"
    for home in [agents_home, codex_home, claude_home]:
        (home / "skills").mkdir(parents=True)
    write_skill(agents_home / "skills", "brainstorming")
    (agents_home / "skills" / "brainstorming" / "SKILL.md").write_text(
        "---\nname: brainstorming\ndescription: drifted\nversion: 1.0.0\n---\n",
        encoding="utf-8")

    backup_root = tmp_path / "backups"
    for old in ["20260101-000000", "20260102-000000", "20260103-000000"]:
        (backup_root / old).mkdir(parents=True)

    monkeypatch.setenv("AGENTS_HOME", str(agents_home))
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    monkeypatch.setenv("CLAUDE_HOME", str(claude_home))
    monkeypatch.chdir(repo)

    report = build_audit_report(
        context=resolve_context(str(skills), [], False),
        local_policy="prefer-global-link",
        global_policy="prefer-primary-link",
        keep_local_skills=set(),
        enforce_mirror=False,
        codex_agents_dedupe=True,
    )
    result = apply_actions(report, apply=True, backup_root=str(backup_root))

    assert bool(result["backups"]), "this fixture must produce a backup"
    written = {Path(b["backup"]).parent.resolve() for b in result["backups"]}
    surviving = {p.resolve() for p in backup_root.iterdir() if p.is_dir()}
    for run in written:
        assert run in surviving, f"pruned the run it just wrote: {run}"
    assert len(surviving) == 5, f"unknown runs, current run, and records must survive: {surviving}"


def test_mirror_copy_repairs_a_secondary_entry_instead_of_removing_it(tmp_path, monkeypatch) -> None:
    """Stale-entry removal is a claim about *link* topology.

    Under the default prefer-primary-link policy the secondary roots are
    symlinks to the primary copy, so a name the primary root does not have is an
    orphan and removal is right. Under `--global-policy mirror-copy` the roots
    hold deliberately independent copies -- absence from the primary carries no
    intent at all -- so a damaged secondary entry is repaired from canonical, as
    it always was.
    """
    repo = tmp_path / "repo"
    skills = repo / "skills"
    skills.mkdir(parents=True)
    (repo / "AGENTS.md").write_text("x", encoding="utf-8")
    write_skill(skills, "audit-skill")

    agents_home = tmp_path / ".agents"
    codex_home = tmp_path / ".codex"
    claude_home = tmp_path / ".claude"
    for home in [agents_home, codex_home, claude_home]:
        (home / "skills").mkdir(parents=True)

    stale = claude_home / "skills" / "audit-skill"
    os.symlink(str(agents_home / "skills" / "audit-skill"), stale)

    monkeypatch.setenv("AGENTS_HOME", str(agents_home))
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    monkeypatch.setenv("CLAUDE_HOME", str(claude_home))
    monkeypatch.chdir(repo)

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
    assert "remove_stale_entry" not in types, (
        f"mirror-copy keeps independent copies; it must not delete one: {claude_actions}"
    )
    assert "sync_copy" in types, f"a damaged mirror-copy entry is repaired from canonical: {claude_actions}"


def test_a_failed_apply_does_not_prune_backup_history(tmp_path) -> None:
    """Failed sync preserves all earlier recovery points."""
    backup_root = tmp_path / "backups"
    for old in ["20260101-000000", "20260102-000000", "20260103-000000"]:
        (backup_root / old).mkdir(parents=True)

    broken = {
        "actions": [
            {
                "action": "sync_copy",
                "skill": "gone",
                "source": str(tmp_path / "does-not-exist"),
                "dest": str(tmp_path / "dest"),
            }
        ]
    }
    result = apply_actions(broken, apply=True, backup_root=str(backup_root))

    assert bool(result["errors"]), "this fixture must produce an error"
    assert result["discarded_backups"] == [], "failed apply must preserve rollback"
    surviving = sorted(p.name for p in backup_root.iterdir() if p.name != "records")
    assert len(surviving) == 3, f"all runs must survive a failure: {surviving}"


def _version_fixture(base: Path, monkeypatch, with_canonical: bool = True) -> tuple[Path, Path, Path, Path]:
    repo = base / "repo"
    skills = repo / "skills"
    if with_canonical:
        skills.mkdir(parents=True)
        (repo / "AGENTS.md").write_text("x", encoding="utf-8")
    homes = [base / ".agents", base / ".codex", base / ".claude"]
    for home in homes:
        (home / "skills").mkdir(parents=True)
    monkeypatch.setenv("AGENTS_HOME", str(homes[0]))
    monkeypatch.setenv("CODEX_HOME", str(homes[1]))
    monkeypatch.setenv("CLAUDE_HOME", str(homes[2]))
    monkeypatch.chdir(repo if with_canonical else base)
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


def test_version_deltas_report_behind_ahead_equal_and_divergent(tmp_path, monkeypatch) -> None:
    """Versions say which way a copy moved; content says whether it moved at all.

    Release-relevant changes must bump the version, so an equal version over
    different content is divergence, not equality, and the content drift it
    already raises must survive alongside it.
    """
    skills, agents, codex, _ = _version_fixture(tmp_path, monkeypatch)
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
        assert row is not None, f"missing version row {key}: {sorted(rows)}"
        actual = (row["source_version"], row["current_version"], row["version_delta"], row["content_drift"])
        assert actual == (source_version, current_version, delta, drift), (
            f"{key}: expected {(source_version, current_version, delta, drift)}, got {actual}"
        )
        assert row["source_root"] == canonical, f"{key}: source must be canonical: {row}"
    assert rows[("alpha", codex_root)]["is_symlink"], "linked entry must be marked as a symlink"
    assert all(row["root"] != canonical for row in report["versions"]), (
        "the source copy is not compared with itself"
    )
    assert (
        any(
            issue["code"] == "CONTENT_DRIFT" and issue["skill"] == "gamma"
            for issue in report["issues"]
        )
    ), (
        f"an equal version must not hide content drift: {report['issues']}"
    )

    summary = summarize_report(report)
    assert "Version deltas:" in summary, f"text summary lacks version deltas:\n{summary}"
    assert (
        any("alpha" in line and "behind" in line and "1.0.0" in line and "1.2.0" in line
            for line in summary.splitlines())
    ), (
        f"text summary lacks alpha's delta:\n{summary}"
    )
    assert any("gamma" in line and "divergent" in line for line in summary.splitlines()), (
        f"text summary lacks gamma's divergence:\n{summary}"
    )
    assert not any(line.startswith("- delta ") for line in summary.splitlines()), (
        f"equal, identical copies need no version line:\n{summary}"
    )


def test_missing_and_malformed_versions_are_unknown_not_zero(tmp_path, monkeypatch) -> None:
    skills, agents, _, _ = _version_fixture(tmp_path, monkeypatch)
    write_versioned_skill(skills, "alpha", "1.0.0")
    write_versioned_skill(skills, "beta", "v2.0.0")
    write_versioned_skill(skills, "gamma", None)
    write_versioned_skill(skills, "delta", '"1.0.0"')
    write_versioned_skill(skills, "epsilon", "1.0.0")
    for name in ("zeta", "eta", "theta"):
        write_versioned_skill(skills, name, "1.2.4")
    write_versioned_skill(agents, "alpha", None)
    write_versioned_skill(agents, "beta", "0.0.0")
    write_versioned_skill(agents, "gamma", "0.1.0")
    write_versioned_skill(agents, "delta", "'1.1.0'  # pinned")
    write_versioned_skill(agents, "epsilon", "1.0")
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
        assert row is not None, f"missing version row for {skill}: {sorted(rows)}"
        actual = (row["source_version"], row["current_version"], row["version_delta"])
        assert actual == (source_version, current_version, delta), (
            f"{skill}: expected {(source_version, current_version, delta)}, got {actual}"
        )
        assert reason in row.get("version_note", ""), f"{skill}: unknown delta must say why: {row}"
    quoted = rows.get(("delta", agents_root))
    assert (
        quoted is not None
        and (quoted["source_version"], quoted["current_version"], quoted["version_delta"])
        == ("1.0.0", "1.1.0", "ahead")
    ), (
        f"quoted versions must parse like YAML strings: {quoted}"
    )

    summary = summarize_report(report)
    assert (
        any("alpha" in line and "unknown" in line and "missing" in line
            for line in summary.splitlines())
    ), (
        f"text summary must show the unknown delta:\n{summary}"
    )


def test_version_key_spellings_follow_yaml(tmp_path, monkeypatch) -> None:
    """Any spelling YAML reads as the top-level `version` key is the version.

    A nested `version` belongs to its parent mapping, and a near-miss key is
    another key, so neither stands in for a missing top-level version.
    """
    skills, agents, _, _ = _version_fixture(tmp_path, monkeypatch)
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
        "tab-before-colon": (None, "unknown", "missing"),
        "quoted-key-junk-value": ('"1.2.3" trailing-junk', "unknown", "SemVer"),
    }
    for name, (current_version, delta, reason) in expected.items():
        row = rows.get((name, agents_root))
        assert row is not None, f"missing version row for {name}: {sorted(rows)}"
        actual = (row["current_version"], row["version_delta"])
        assert actual == (current_version, delta), (
            f"{name}: expected {(current_version, delta)}, got {actual}: {copies[name]!r}"
        )
        assert reason is None or reason in (row["version_note"] or ""), (
            f"{name}: unknown delta must say why: {row}"
        )


def test_quoted_versions_read_as_yaml_scalars(tmp_path, monkeypatch) -> None:
    """A quoted version or key means what YAML reads it as, escapes included.

    Double quotes decode `x`, `u`, and `U` hex escapes, so they can spell a
    version; backslashes elsewhere are literal. A malformed escape, or one naming
    a surrogate or a code point past U+10FFFF, is reported as written: a lone
    surrogate would break printing the summary.
    """
    bs = "\\"
    skills, agents, _, _ = _version_fixture(tmp_path, monkeypatch)
    cases = {
        "x-escape": (f'version: "{bs}x31.2.3"', "1.2.3", "ahead", None),
        "u-escape": (f'version: "{bs}u0031.2.3"', "1.2.3", "ahead", None),
        "big-u-escape": (f'version: "{bs}U00000031.2.3"', "1.2.3", "ahead", None),
        "uppercase-hex": (f'version: "1{bs}u002E2.3"', "1.2.3", "ahead", None),
        "mixed": (f'version: "1.{bs}x32.3-rc.{bs}u0031"', "1.2.3-rc.1", "ahead", None),
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
        assert row is not None, f"missing version row for {name}: {sorted(rows)}"
        actual = (row["current_version"], row["version_delta"])
        assert actual == (current_version, delta), (
            f"{name}: expected {(current_version, delta)}, got {actual}: {frontmatter!r}"
        )
        assert reason is None or reason in (row["version_note"] or ""), (
            f"{name}: unknown delta must say why: {row}"
        )
    summarize_report(report).encode("utf-8")
    json.dumps(report, ensure_ascii=False).encode("utf-8")


def test_version_precedence_follows_semver_ordering() -> None:
    """Numeric parts compare as numbers, prereleases rank below their release."""
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
        assert version_delta(higher, lower, False) == ("behind", None), f"{lower} must be behind {higher}"
        assert version_delta(lower, higher, False) == ("ahead", None), f"{higher} must be ahead of {lower}"
    assert version_delta("1.0.0+build.1", "1.0.0+build.2", True) == ("equal", None), "build metadata has no precedence"
    assert version_delta("1.21.0", "1.2٠.0", False) == ("behind", None), "non-ASCII digits must compare by value"
    for left, right in (("1.0.0-11", "1.0.0-1١"), ("1.0.0-1١", "1.0.0-11")):
        assert version_delta(left, right, True) == ("equal", None), f"{right} must equal {left} in precedence"
        assert version_delta(left, right, False)[0] == "divergent", (
            f"{right} over different content must be divergent from {left}"
        )
    for lower, higher in (
        ("1.0.0-1١.alpha", "1.0.0-11.beta"),
        ("1.0.0-11.alpha", "1.0.0-1١.beta"),
        ("1.0.0-1١", "1.0.0-11.1"),
        ("1.0.0-11", "1.0.0-1١.1"),
    ):
        assert version_delta(higher, lower, False) == ("behind", None), f"{lower} must be behind {higher}"
        assert version_delta(lower, higher, False) == ("ahead", None), f"{higher} must be ahead of {lower}"


def test_huge_numeric_versions_compare_without_crashing_the_audit(tmp_path, monkeypatch) -> None:
    """SemVer sets no digit limit, so neither may the comparison.

    Python's int() refuses strings past its digit limit (4300 by default). A
    copy declaring a longer numeric part is still valid SemVer: it must compare
    by value, and every other skill must still be reported.
    """
    huge = "1" + "0" * 5000
    huge_plus_one = "1" + "0" * 4999 + "1"
    skills, agents, _, _ = _version_fixture(tmp_path, monkeypatch)
    pairs = {
        "huge-major": ("1.0.0", f"{huge}.0.0", "ahead"),
        "huge-minor": (f"1.{huge_plus_one}.0", f"1.{huge}.0", "behind"),
        "huge-patch-shorter": (f"1.0.{huge}", f"1.0.9{'9' * 4000}", "behind"),
        "huge-equal": (f"{huge}.0.0", f"{huge}.0.0", "equal"),
        "huge-prerelease": (f"1.0.0-rc.{huge}", f"1.0.0-rc.{huge_plus_one}", "ahead"),
        "huge-prerelease-vs-alpha": (f"1.0.0-rc.{huge}", "1.0.0-rc.a", "ahead"),
        "huge-prerelease-vs-release": ("1.0.0", f"1.0.0-{huge}", "behind"),
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
        assert row is not None, f"missing version row for {name}: {sorted(rows)}"
        assert row["version_delta"] == delta, (
            f"{name}: expected {delta}, got {row['version_delta']}: {row['version_note']}"
        )


def test_version_rows_follow_skill_selection(tmp_path, monkeypatch) -> None:
    skills, agents, _, _ = _version_fixture(tmp_path, monkeypatch)
    for name in ("alpha", "beta"):
        write_versioned_skill(skills, name, "1.1.0")
        write_versioned_skill(agents, name, "1.0.0")

    report = _version_audit(skills, selected={"alpha"})
    skills_reported = {row["skill"] for row in report.get("versions", [])}
    assert skills_reported == {"alpha"}, f"selection must scope version rows: {skills_reported}"


def test_version_source_is_the_preferred_global_without_canonical(tmp_path, monkeypatch) -> None:
    _, agents, _, claude = _version_fixture(tmp_path, monkeypatch, with_canonical=False)
    write_versioned_skill(agents, "alpha", "2.0.0")
    write_versioned_skill(claude, "alpha", "1.0.0")

    report = _version_audit(None)
    assert report["canonical_root"] is None, f"fixture must have no canonical: {report['canonical_root']}"
    row = _version_rows(report).get(("alpha", str(claude.resolve())))
    assert row is not None, f"missing global-only version row: {report.get('versions')}"
    assert (row["source_root"], row["version_delta"]) == (str(agents.resolve()), "behind"), (
        f"preferred global is the source without canonical: {row}"
    )


def test_global_gemini_discovery_and_env_override(tmp_path, monkeypatch) -> None:
    """global-gemini defaults to ~/.gemini/config/skills and honors GEMINI_HOME."""
    home = tmp_path / "user-home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("GEMINI_HOME", raising=False)
    for env_name, folder in (
        ("AGENTS_HOME", ".agents"),
        ("CODEX_HOME", ".codex"),
        ("CLAUDE_HOME", ".claude"),
    ):
        target = home / folder / "skills"
        target.mkdir(parents=True)
        monkeypatch.setenv(env_name, str(home / folder))
    monkeypatch.chdir(tmp_path)

    absent = root_describe(resolve_context(None, None, False))
    absent_gemini = next(
        (r for r in absent["roots"] if r["kind"] == "global-gemini"),
        None,
    )
    expected_default = (home / ".gemini" / "config" / "skills").resolve()
    assert (
        absent_gemini is not None
        and absent_gemini["path"] == str(expected_default)
        and absent_gemini["exists"] is False
    ), f"default global-gemini root must resolve even when absent: {absent['roots']}"

    expected_default.mkdir(parents=True)
    write_skill(expected_default, "alpha")
    present = root_describe(resolve_context(None, None, False))
    present_gemini = next(
        (r for r in present["roots"] if r["kind"] == "global-gemini"),
        None,
    )
    assert (
        present_gemini is not None
        and present_gemini["exists"] is True
        and present_gemini["skills"] == ["alpha"]
    ), f"present default global-gemini root must be discovered: {present['roots']}"

    real_gemini = tmp_path / "gemini-real"
    (real_gemini / "config" / "skills").mkdir(parents=True)
    write_skill(real_gemini / "config" / "skills", "beta")
    gemini_link = tmp_path / "gemini-link"
    gemini_link.symlink_to(real_gemini, target_is_directory=True)
    monkeypatch.setenv("GEMINI_HOME", str(gemini_link))

    overridden = root_describe(resolve_context(None, None, False))
    overridden_gemini = next(
        (r for r in overridden["roots"] if r["kind"] == "global-gemini"),
        None,
    )
    assert (
        overridden_gemini is not None
        and overridden_gemini["path"] == str((real_gemini / "config" / "skills").resolve())
        and overridden_gemini["skills"] == ["beta"]
    ), f"GEMINI_HOME must resolve symlinked home to config/skills: {overridden['roots']}"
    assert discover_main(["--format", "text"]) == 0


def test_global_gemini_audit_and_sync_link_to_primary(tmp_path, monkeypatch) -> None:
    """global-gemini copies and canonical links normalize to ~/.agents/skills/<name>."""
    repo = tmp_path / "repo"
    skills = repo / "skills"
    skills.mkdir(parents=True)
    (repo / "AGENTS.md").write_text("x", encoding="utf-8")
    write_skill(skills, "alpha")
    write_skill(skills, "beta")
    write_skill(skills, "gamma")

    agents_home = tmp_path / ".agents"
    codex_home = tmp_path / ".codex"
    claude_home = tmp_path / ".claude"
    gemini_home = tmp_path / ".gemini"
    for home in [agents_home, codex_home, claude_home]:
        (home / "skills").mkdir(parents=True)
    (gemini_home / "config" / "skills").mkdir(parents=True)

    for name in ("alpha", "beta", "gamma"):
        write_skill(agents_home / "skills", name)
        (codex_home / "skills" / name).symlink_to(
            (agents_home / "skills" / name).resolve(), target_is_directory=True
        )
        (claude_home / "skills" / name).symlink_to(
            (agents_home / "skills" / name).resolve(), target_is_directory=True
        )

    write_skill(gemini_home / "config" / "skills", "alpha")
    (gemini_home / "config" / "skills" / "beta").symlink_to(
        (skills / "beta").resolve(), target_is_directory=True
    )
    os.symlink(
        "../../../.agents/skills/gamma",
        gemini_home / "config" / "skills" / "gamma",
    )

    monkeypatch.setenv("AGENTS_HOME", str(agents_home))
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    monkeypatch.setenv("CLAUDE_HOME", str(claude_home))
    monkeypatch.setenv("GEMINI_HOME", str(gemini_home))
    monkeypatch.chdir(repo)

    report = build_audit_report(
        context=resolve_context(str(skills), [], False),
        local_policy="prefer-global-link",
        global_policy="prefer-primary-link",
        keep_local_skills=set(),
        enforce_mirror=False,
        codex_agents_dedupe=True,
    )
    gemini_actions = [
        a for a in report["actions"]
        if str((gemini_home / "config" / "skills").resolve()) in str(a.get("dest", ""))
    ]
    assert (
        {a["skill"] for a in gemini_actions} == {"alpha", "beta"}
        and all(a["action"] == "relink_to_global" for a in gemini_actions)
    ), f"gamma relative symlink must pass and alpha/beta must relink: {report}"

    exit_before = audit_main(["--canonical-root", str(skills), "--format", "text"])
    assert exit_before == 2, f"expected drift exit 2 before sync, got {exit_before}"

    sync_code = sync_main([
        "--canonical-root", str(skills),
        "--global-policy", "prefer-primary-link",
        "--apply",
        "--backup-root", str(tmp_path / "backups"),
    ])
    assert sync_code == 0, f"sync_main failed with exit {sync_code}"

    for name in ("alpha", "beta", "gamma"):
        entry = gemini_home / "config" / "skills" / name
        assert entry.is_symlink() and entry.resolve() == (agents_home / "skills" / name).resolve(), (
            f"{name} in global-gemini must resolve to primary global: {entry}"
        )

    exit_after = audit_main(["--canonical-root", str(skills), "--format", "text"])
    assert exit_after == 0, f"expected clean exit 0 after sync, got {exit_after}"


def test_global_gemini_absent_root_handling(tmp_path, monkeypatch) -> None:
    """Absent secondary global roots are neither reported as drift nor created on mirror."""
    repo = tmp_path / "repo"
    skills = repo / "skills"
    skills.mkdir(parents=True)
    (repo / "AGENTS.md").write_text("x", encoding="utf-8")
    write_skill(skills, "alpha")

    agents_home = tmp_path / ".agents"
    codex_home = tmp_path / ".codex"
    claude_home = tmp_path / ".claude"
    gemini_home = tmp_path / ".gemini"
    (agents_home / "skills").mkdir(parents=True)
    (codex_home / "skills").mkdir(parents=True)
    write_skill(agents_home / "skills", "alpha")
    (codex_home / "skills" / "alpha").symlink_to(
        (agents_home / "skills" / "alpha").resolve(), target_is_directory=True
    )

    monkeypatch.setenv("AGENTS_HOME", str(agents_home))
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    monkeypatch.setenv("CLAUDE_HOME", str(claude_home))
    monkeypatch.setenv("GEMINI_HOME", str(gemini_home))
    monkeypatch.chdir(repo)

    default_code = audit_main(["--canonical-root", str(skills), "--format", "text"])
    assert default_code == 0, f"absent roots must not fail default audit: {default_code}"

    mirror_report = build_audit_report(
        context=resolve_context(str(skills), [], False),
        local_policy="prefer-global-link",
        global_policy="prefer-primary-link",
        keep_local_skills=set(),
        enforce_mirror=True,
        codex_agents_dedupe=True,
    )
    assert not mirror_report["actions"] and not mirror_report["issues"], (
        f"enforce_mirror must not target absent secondary roots: {mirror_report}"
    )
    sync_code = sync_main([
        "--canonical-root", str(skills),
        "--enforce-mirror",
        "--apply",
        "--backup-root", str(tmp_path / "backups"),
    ])
    assert sync_code == 0, f"sync with absent roots failed: {sync_code}"
    assert not (gemini_home / "config" / "skills").exists(), "must not create absent global-gemini"
    assert not (claude_home / "skills").exists(), "must not create absent global-claude"

    (gemini_home / "config" / "skills").mkdir(parents=True)
    present_report = build_audit_report(
        context=resolve_context(str(skills), [], False),
        local_policy="prefer-global-link",
        global_policy="prefer-primary-link",
        keep_local_skills=set(),
        enforce_mirror=True,
        codex_agents_dedupe=True,
    )
    assert [a["dest"] for a in present_report["actions"]] == [
        str((gemini_home / "config" / "skills" / "alpha").resolve())
    ], f"existing global-gemini must receive mirror link: {present_report}"


def test_global_gemini_precedence_mirror_copy_and_versions(tmp_path, monkeypatch) -> None:
    """global-gemini ranks after global-claude and reports mirror-copy drift and versions."""
    agents_home = tmp_path / ".agents"
    codex_home = tmp_path / ".codex"
    claude_home = tmp_path / ".claude"
    gemini_home = tmp_path / ".gemini"
    for home in [agents_home, codex_home, claude_home]:
        (home / "skills").mkdir(parents=True)
    (gemini_home / "config" / "skills").mkdir(parents=True)

    write_versioned_skill(claude_home / "skills", "shared", "2.0.0")
    write_versioned_skill(gemini_home / "config" / "skills", "shared", "1.0.0")

    monkeypatch.setenv("AGENTS_HOME", str(agents_home))
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    monkeypatch.setenv("CLAUDE_HOME", str(claude_home))
    monkeypatch.setenv("GEMINI_HOME", str(gemini_home))
    monkeypatch.chdir(tmp_path)

    link_report = build_audit_report(
        context=resolve_context(None, None, False),
        local_policy="prefer-global-link",
        global_policy="prefer-primary-link",
        keep_local_skills=set(),
        enforce_mirror=False,
        codex_agents_dedupe=True,
    )
    assert (
        len(link_report["actions"]) == 1
        and link_report["actions"][0]["action"] == "relink_to_global"
        and Path(link_report["actions"][0]["source"]).resolve()
        == (claude_home / "skills" / "shared").resolve()
        and Path(link_report["actions"][0]["dest"]).resolve()
        == (gemini_home / "config" / "skills" / "shared").resolve()
    ), f"global-gemini must link to global-claude when primary lacks skill: {link_report}"

    mirror_report = build_audit_report(
        context=resolve_context(None, None, False),
        local_policy="prefer-global-link",
        global_policy="mirror-copy",
        keep_local_skills=set(),
        enforce_mirror=False,
        codex_agents_dedupe=False,
    )
    assert (
        any(i["code"] == "GLOBAL_DRIFT" for i in mirror_report["issues"])
        and len(mirror_report["actions"]) == 1
        and mirror_report["actions"][0]["action"] == "sync_copy"
        and Path(mirror_report["actions"][0]["dest"]).resolve()
        == (gemini_home / "config" / "skills" / "shared").resolve()
    ), f"mirror-copy must sync drifted global-gemini from global-claude: {mirror_report}"
    version_row = next(
        (r for r in link_report["versions"] if r["skill"] == "shared"),
        None,
    )
    assert (
        version_row is not None
        and version_row["root_kind"] == "global-gemini"
        and version_row["version_delta"] == "behind"
    ), f"version delta must report global-gemini behind global-claude: {link_report['versions']}"


def test_global_gemini_normalize_primary_stale_and_deprecated(tmp_path, monkeypatch) -> None:
    """global-gemini supports promotion, stale link cleanup, and deprecated renames."""
    repo = tmp_path / "repo"
    skills = repo / "skills"
    skills.mkdir(parents=True)
    (repo / "AGENTS.md").write_text("x", encoding="utf-8")
    write_skill(skills, "cli-design")
    write_skill(skills, "removed-skill")

    agents_home = tmp_path / ".agents"
    codex_home = tmp_path / ".codex"
    claude_home = tmp_path / ".claude"
    gemini_home = tmp_path / ".gemini"
    for home in [agents_home, codex_home, claude_home]:
        (home / "skills").mkdir(parents=True)
    gemini_skills = gemini_home / "config" / "skills"
    gemini_skills.mkdir(parents=True)

    write_skill(agents_home / "skills", "cli-design")
    write_skill(gemini_skills, "solo")
    write_skill(gemini_skills, "create-cli")
    os.symlink(str(agents_home / "skills" / "removed-skill"), gemini_skills / "removed-skill")

    monkeypatch.setenv("AGENTS_HOME", str(agents_home))
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    monkeypatch.setenv("CLAUDE_HOME", str(claude_home))
    monkeypatch.setenv("GEMINI_HOME", str(gemini_home))
    monkeypatch.chdir(repo)

    report = build_audit_report(
        context=resolve_context(str(skills), [], False),
        local_policy="prefer-global-link",
        global_policy="prefer-primary-link",
        keep_local_skills=set(),
        enforce_mirror=False,
        codex_agents_dedupe=True,
        normalize_primary=True,
    )
    codes = {(i["code"], i.get("skill")) for i in report["issues"]}
    assert (
        ("PROMOTE_TO_PRIMARY", "solo") in codes
        and ("STALE_SECONDARY_GLOBAL", "removed-skill") in codes
        and ("DEPRECATED_SKILL_NAME", "create-cli") in codes
    ), f"expected promotion, stale, and deprecated issues in global-gemini: {report['issues']}"

    result = apply_actions(report, apply=True, backup_root=str(tmp_path / "backups"))
    assert not result["errors"], f"apply failed: {result}"
    assert (agents_home / "skills" / "solo").is_dir() and not (agents_home / "skills" / "solo").is_symlink(), (
        "solo must be promoted as concrete dir in primary global"
    )
    assert (
        (gemini_skills / "solo").is_symlink()
        and (gemini_skills / "solo").resolve() == (agents_home / "skills" / "solo").resolve()
    ), "solo in global-gemini must link to primary after promotion"
    assert not os.path.lexists(gemini_skills / "removed-skill"), (
        "stale dangling symlink in global-gemini must be removed"
    )
    assert (
        not os.path.lexists(gemini_skills / "create-cli")
        and (gemini_skills / "cli-design").is_symlink()
        and (gemini_skills / "cli-design").resolve() == (agents_home / "skills" / "cli-design").resolve()
    ), "deprecated create-cli in global-gemini must migrate to cli-design symlink"
