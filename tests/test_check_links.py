from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_links.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_links", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


def make_skill(root: Path, name: str, body: str) -> Path:
    d = root / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: x\nskill-type: workflow\nversion: 1.0.0\n---\n\n{body}",
        encoding="utf-8",
    )
    return d


def test_clean_catalog_has_no_problems(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    a = make_skill(root, "alpha", "See [detail](./references/detail.md).\n\n## Sibling skills\n\n- `beta` — the other one.\n")
    (a / "references").mkdir()
    (a / "references" / "detail.md").write_text("x", encoding="utf-8")
    make_skill(root, "beta", "Nothing to see.\n")
    assert MODULE.check(root, []) == []


def test_broken_relative_link_is_reported(tmp_path: Path) -> None:
    """The reference-cut failure: an index still lists a deleted file."""
    root = tmp_path / "skills"
    make_skill(root, "alpha", "See [gone](./references/deleted.md).\n")
    problems = MODULE.check(root, [])
    assert len(problems) == 1
    assert "broken link" in problems[0] and "deleted.md" in problems[0]


def test_sibling_pointing_at_retired_skill_is_reported(tmp_path: Path) -> None:
    """The retirement failure: a sibling section names a deleted skill."""
    root = tmp_path / "skills"
    make_skill(root, "alpha", "## Sibling skills\n\n- `gh-review-pr` — retired.\n")
    problems = MODULE.check(root, [])
    assert len(problems) == 1
    assert "gh-review-pr" in problems[0]


def test_skills_path_reference_to_missing_skill_is_reported(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    make_skill(root, "alpha", "Run `python3 skills/removed-thing/scripts/go.py`.\n")
    problems = MODULE.check(root, [])
    assert len(problems) == 1
    assert "removed-thing" in problems[0]


def test_sibling_section_ignores_non_skill_words(tmp_path: Path) -> None:
    """Conservative by design: a sibling section mentioning ordinary terms is fine."""
    root = tmp_path / "skills"
    make_skill(root, "alpha", "## Sibling skills\n\n- Use `git` and `main`; see `pull-request` flow.\n")
    problems = MODULE.check(root, [])
    # `git` and `main` have no hyphen so are skipped; `pull-request` does and is flagged.
    assert all("`git`" not in p and "`main`" not in p for p in problems)


def test_external_and_anchor_links_are_skipped(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    make_skill(root, "alpha", "[docs](https://example.com/x.md) and [top](#heading).\n")
    assert MODULE.check(root, []) == []


def test_real_repo_passes() -> None:
    """The live catalog must stay clean; this is the gate CI enforces."""
    assert MODULE.check() == []


def test_fenced_code_blocks_are_ignored(tmp_path: Path) -> None:
    """skill-creator illustrates a hypothetical PDF skill linking to files that
    were never meant to exist. Checking inside fences is pure noise."""
    root = tmp_path / "skills"
    make_skill(root, "alpha", "Example:\n\n```markdown\nSee [FORMS.md](FORMS.md)\n```\n")
    assert MODULE.check(root, []) == []


def test_urls_containing_skills_path_are_ignored(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    make_skill(root, "alpha", "Fetched from https://github.com/openai/skills/tree/main/skills/.curated here.\n")
    assert MODULE.check(root, []) == []


def test_documentation_placeholders_are_ignored(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    make_skill(root, "alpha", "Run `python3 skills/my-skill/scripts/run.py` on your own skill.\n")
    assert MODULE.check(root, []) == []


def test_asset_templates_are_skipped(tmp_path: Path) -> None:
    """Templates carry placeholder paths by design."""
    root = tmp_path / "skills"
    d = make_skill(root, "alpha", "Nothing.\n")
    (d / "assets").mkdir()
    (d / "assets" / "template.md").write_text("See [related](../category/related-problem.md).\n", encoding="utf-8")
    assert MODULE.check(root, []) == []


def test_inline_sibling_mention_is_not_flagged(tmp_path: Path) -> None:
    """Only list heads are sibling entries; a model name mid-sentence is not."""
    root = tmp_path / "skills"
    make_skill(root, "alpha", "## Sibling skills\n\n- `beta` — use when the user asks for `gpt-image-2`.\n")
    make_skill(root, "beta", "x\n")
    assert MODULE.check(root, []) == []


def test_links_into_local_only_archive_are_skipped(tmp_path: Path, monkeypatch) -> None:
    """docs/archive/ is gitignored, so its contents exist locally and never in CI.

    Regression guard for the failure this gate shipped with: it passed on the
    author's machine and failed on a clean checkout, because two living docs
    cite an archived analysis that is deliberately unpublished.
    """
    repo = tmp_path
    (repo / "docs" / "project").mkdir(parents=True)
    (repo / "docs" / "project" / "ROADMAP.md").write_text(
        "Based on the [analysis](../archive/skill-analysis/old.md).\n", encoding="utf-8"
    )
    root = repo / "skills"
    make_skill(root, "alpha", "Nothing.\n")
    monkeypatch.setattr(MODULE, "REPO_ROOT", repo)
    assert MODULE.check(root, [repo / "docs" / "project"]) == []


def test_clean_checkout_matches_working_tree() -> None:
    """The gate must not depend on untracked files being present.

    Anything the checker resolves through a gitignored path is a false pass that
    turns into a CI failure, which is exactly how this shipped broken once.
    """
    import subprocess

    tracked = subprocess.run(
        ["git", "ls-files", "docs", "skills", "README.md"],
        cwd=MODULE.REPO_ROOT, capture_output=True, text=True, check=True,
    ).stdout.split()
    for problem in MODULE.check():
        assert False, f"working tree is not clean for the gate: {problem}"
    # Every living doc the checker scans must itself be tracked.
    for path in MODULE.markdown_files(MODULE.SKILLS_ROOT, MODULE.LIVING_DOCS):
        rel = path.relative_to(MODULE.REPO_ROOT).as_posix()
        assert rel in tracked, f"{rel} is scanned by the gate but not tracked in git"
