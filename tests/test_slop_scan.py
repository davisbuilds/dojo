from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "slop_scan.py"


def load_module():
    spec = importlib.util.spec_from_file_location("slop_scan", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_flags_known_slop_phrases():
    module = load_module()
    text = (
        "# Title\n"
        "It's important to note that this delves into a rich tapestry of ideas.\n"
        "In today's fast-paced world we unlock the power of synergy.\n"
    )
    findings = module.scan_text(text)
    labels = {f[1] for f in findings}
    assert "filler-opener" in labels
    assert "hype-verb" in labels  # "delve into" + "unlock the power of"
    assert "cliche-metaphor" in labels  # "rich tapestry"
    assert "hype-temporal" in labels  # "in today's fast-paced world"


def test_clean_technical_prose_has_no_hits():
    module = load_module()
    text = (
        "Run the validator against the skills root. It returns a non-zero exit "
        "code when a required check fails. Use --strict in CI.\n"
    )
    assert module.scan_text(text) == []


def test_cli_exit_codes(tmp_path: Path, monkeypatch):
    module = load_module()
    dirty = tmp_path / "dirty.md"
    dirty.write_text("We delve into the realm of possibility.\n", encoding="utf-8")
    clean = tmp_path / "clean.md"
    clean.write_text("A deterministic linter with clear exit codes.\n", encoding="utf-8")

    monkeypatch.setattr("sys.argv", ["slop", str(dirty)])
    assert module.main() == 1

    monkeypatch.setattr("sys.argv", ["slop", str(clean)])
    assert module.main() == 0

    monkeypatch.setattr("sys.argv", ["slop", "--warn-only", str(dirty)])
    assert module.main() == 0


def test_repo_default_set_is_clean(monkeypatch):
    module = load_module()
    monkeypatch.setattr("sys.argv", ["slop"])
    assert module.main() == 0
