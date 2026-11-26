"""Spec and plan validation hooks must fire for the paths harnesses actually send."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
KINDS = {
    "spec": ("docs/specs", "2026-01-01-example-spec.md", "skills/write-spec/scripts"),
    "plan": ("docs/plans", "2026-01-01-example-plan.md", "skills/write-plan/scripts"),
}


@pytest.fixture
def checkout(tmp_path: Path) -> Path:
    repo = tmp_path / "checkout"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    shutil.copytree(ROOT / "hooks", repo / "hooks", ignore=shutil.ignore_patterns("__pycache__"))
    for _, _, scripts in KINDS.values():
        shutil.copytree(ROOT / scripts, repo / scripts, ignore=shutil.ignore_patterns("__pycache__"))
    (repo / ".venv").symlink_to(Path(sys.prefix), target_is_directory=True)
    return repo


def run(kind: str, cwd: Path, file_path: str) -> subprocess.CompletedProcess[str]:
    payload = {"tool_name": "Write", "tool_input": {"file_path": file_path}}
    return subprocess.run(
        ["bash", f"hooks/post-tool-use-validate-{kind}.sh"],
        cwd=cwd, input=json.dumps(payload), capture_output=True, text=True,
    )


def invalid_doc(repo: Path, kind: str) -> Path:
    directory, name, _ = KINDS[kind]
    doc = repo / directory / name
    doc.parent.mkdir(parents=True)
    doc.write_text("# Not a valid document\n")
    return doc


@pytest.mark.parametrize("kind", sorted(KINDS))
@pytest.mark.parametrize("form", ["absolute", "relative", "via_symlink"])
def test_invalid_document_is_rejected_for_every_path_form(
    checkout: Path, tmp_path: Path, kind: str, form: str
) -> None:
    doc = invalid_doc(checkout, kind)
    if form == "absolute":
        file_path = str(doc)
    elif form == "relative":
        file_path = str(doc.relative_to(checkout))
    else:
        alias = tmp_path / "alias"
        alias.symlink_to(checkout, target_is_directory=True)
        file_path = str(alias / doc.relative_to(checkout))
    result = run(kind, checkout, file_path)
    assert result.returncode == 2, result.stderr
    assert "validation failed" in result.stderr


@pytest.mark.parametrize("kind", sorted(KINDS))
def test_documents_outside_the_contract_directory_are_ignored(checkout: Path, kind: str) -> None:
    directory, name, _ = KINDS[kind]
    elsewhere = checkout / "notes" / directory / name
    elsewhere.parent.mkdir(parents=True)
    elsewhere.write_text("# Not a valid document\n")
    assert run(kind, checkout, str(elsewhere)).returncode == 0
    outside = checkout.parent / name
    outside.write_text("# Not a valid document\n")
    assert run(kind, checkout, str(outside)).returncode == 0
    assert run(kind, checkout, str(checkout / directory / f"missing-{name}")).returncode == 0


@pytest.mark.parametrize("kind", sorted(KINDS))
def test_tracked_documents_pass_by_absolute_path(kind: str) -> None:
    directory, _, _ = KINDS[kind]
    documents = sorted((ROOT / directory).glob(f"*-{kind}.md"))
    assert documents, "the pass control needs a tracked document"
    for document in documents:
        result = run(kind, ROOT, str(document))
        assert result.returncode == 0, result.stderr
