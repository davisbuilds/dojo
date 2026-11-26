from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "skills" / "skill-evals" / "scripts" / "check_skill_versions.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_skill_versions", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def write_skill(repo: Path, name: str, version: str | None, body: str = "Initial body.") -> None:
    skill_dir = repo / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    fm = [f"name: {name}", f"description: Use when testing {name}."]
    if version is not None:
        fm.append(f"version: {version}")
    fm.append("skill-type: reference")
    (skill_dir / "SKILL.md").write_text(
        "---\n" + "\n".join(fm) + "\n---\n\n# Test\n\n" + body + "\n",
        encoding="utf-8",
    )


def init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "Test User")
    return repo


def test_semver_accepts_prerelease_identifiers_starting_with_zero() -> None:
    module = load_module()

    assert module.SemVer.parse("1.0.0-0rc.1") < module.SemVer.parse("1.0.0")


@pytest.mark.parametrize("version", ["1.0.1", "1.0.1-rc.1+build.1"])
def test_changed_skill_requires_version_increase_and_changelog(tmp_path: Path, version: str) -> None:
    module = load_module()
    repo = init_repo(tmp_path)
    skills_root = repo / "skills"
    write_skill(repo, "alpha", "1.0.0")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "baseline")
    base = "HEAD"

    write_skill(repo, "alpha", "1.0.0", body="Changed body.")
    errors = module.check_versions(repo, skills_root, base, include_untracked=True)
    assert any("version did not increase" in error for error in errors)

    write_skill(repo, "alpha", version, body="Changed body.")
    errors = module.check_versions(repo, skills_root, base, include_untracked=True)
    assert errors == [f"alpha: missing CHANGELOG.md entry for {version}"]

    (skills_root / "alpha" / "CHANGELOG.md").write_text(
        f"# Changelog\n\n## {version} - 2026-11-25\n\n- Clarified behavior.\n",
        encoding="utf-8",
    )
    assert module.check_versions(repo, skills_root, base, include_untracked=True) == []



@pytest.mark.parametrize(
    "changelog",
    [
        pytest.param("## 1.0.1\n\n- Changed behavior.\n", id="undated"),
        pytest.param("## 1.0.1 - 2026-1-5\n\n- Changed behavior.\n", id="wrong-date-format"),
        pytest.param("## 1.0.1 - 2026-02-30\n\n- Changed behavior.\n", id="invalid-date"),
        pytest.param("### 1.0.1 - 2026-11-25\n\n- Changed behavior.\n", id="wrong-heading-level"),
        pytest.param("## 1.0.1 - 2026-11-25\n\nChanged behavior.\n", id="no-bullet"),
        pytest.param("## 1.0.1 - 2026-11-25\n\n- \n", id="empty-bullet"),
        pytest.param(
            "## 1.0.1 - 2026-11-25\n\n## 1.0.0 - 2026-11-24\n\n- Earlier change.\n",
            id="bullet-in-another-entry",
        ),
        pytest.param(
            "## 1.0.1 - 2026-11-25\n\n```text\n- Example only.\n```\n",
            id="bullet-in-code-example",
        ),
        pytest.param(
            "## 1.0.1 - 2026-11-25\n\n<!--\n- Hidden text.\n-->\n",
            id="bullet-in-comment",
        ),
    ],
)
def test_changed_skill_requires_dated_changelog_entry_with_bullet(tmp_path: Path, changelog: str) -> None:
    module = load_module()
    repo = init_repo(tmp_path)
    skills_root = repo / "skills"
    write_skill(repo, "alpha", "1.0.0")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "baseline")

    write_skill(repo, "alpha", "1.0.1", body="Changed body.")
    (skills_root / "alpha" / "CHANGELOG.md").write_text(changelog, encoding="utf-8")

    assert module.check_versions(repo, skills_root, "HEAD", include_untracked=True) == [
        "alpha: missing CHANGELOG.md entry for 1.0.1"
    ]


def test_unversioned_base_allows_initial_baseline_without_changelog(tmp_path: Path) -> None:
    module = load_module()
    repo = init_repo(tmp_path)
    skills_root = repo / "skills"
    write_skill(repo, "alpha", None)
    git(repo, "add", ".")
    git(repo, "commit", "-m", "unversioned baseline")

    write_skill(repo, "alpha", "1.0.0", body="Baseline version added.")

    assert module.check_versions(repo, skills_root, "HEAD", include_untracked=True) == []


def test_generated_sidecar_and_changelog_only_changes_are_ignored(tmp_path: Path) -> None:
    module = load_module()
    repo = init_repo(tmp_path)
    skills_root = repo / "skills"
    write_skill(repo, "alpha", "1.0.0")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "baseline")

    sidecar = skills_root / "alpha" / "agents" / "openai.yaml"
    sidecar.parent.mkdir(parents=True)
    sidecar.write_text("# generated\n", encoding="utf-8")
    (skills_root / "alpha" / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")

    assert module.check_versions(repo, skills_root, "HEAD", include_untracked=True) == []


def test_appended_run_memory_does_not_require_a_version_bump(tmp_path: Path) -> None:
    module = load_module()
    repo = init_repo(tmp_path)
    skills_root = repo / "skills"
    write_skill(repo, "alpha", "1.0.0")
    references = skills_root / "alpha" / "references"
    references.mkdir(parents=True)
    (references / "postmortems.md").write_text("# Postmortems\n", encoding="utf-8")
    (references / "executor-profiles.md").write_text("# Profiles\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "baseline")

    (references / "postmortems.md").write_text(
        "# Postmortems\n\n## 2026-07-23 — a run\n\n- A durable lesson.\n", encoding="utf-8"
    )
    (references / "executor-profiles.md").write_text(
        "# Profiles\n\n## Some executor — as of 2026-07-23\n\n- A quirk.\n", encoding="utf-8"
    )

    assert module.check_versions(repo, skills_root, "HEAD", include_untracked=True) == []


def test_other_reference_files_still_require_a_version_bump(tmp_path: Path) -> None:
    module = load_module()
    repo = init_repo(tmp_path)
    skills_root = repo / "skills"
    write_skill(repo, "alpha", "1.0.0")
    references = skills_root / "alpha" / "references"
    references.mkdir(parents=True)
    (references / "skeleton.md").write_text("# Skeleton\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "baseline")

    (references / "skeleton.md").write_text("# Skeleton\n\nA behavior change.\n", encoding="utf-8")

    findings = module.check_versions(repo, skills_root, "HEAD", include_untracked=True)
    assert len(findings) == 1
    assert "version did not increase" in findings[0]


def test_invalid_base_ref_fails_explicitly(tmp_path: Path) -> None:
    module = load_module()
    repo = init_repo(tmp_path)
    skills_root = repo / "skills"
    write_skill(repo, "alpha", "1.0.0")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "baseline")

    assert module.check_versions(repo, skills_root, "missing/base", include_untracked=True) == [
        "git base ref is not resolvable: missing/base"
    ]
