from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "skills" / "research-architect" / "scripts" / "lint_prompt.py"


def load_module():
    spec = importlib.util.spec_from_file_location("lint_prompt", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


lint_prompt = load_module()


def make_prompt(*, slots: bool = False, comments: bool = False, extra: str = "") -> str:
    parts = [
        "Compare backup methods for a local SQLite desktop app. Explain the tradeoffs "
        "for an offline user, citing the official documentation.",
    ]
    if slots:
        parts.append("Background: {{SEED_SOURCES}}")
    if comments:
        parts.append("<!-- drafting note: resolve scope -->")
    parts.append(extra)
    return "\n".join(parts)


def check(result: dict, name: str) -> dict:
    return next(c for c in result["checks"] if c["name"] == name)


# The linter checks shippable text, not a prescribed research methodology.
@pytest.mark.parametrize("executor", ["web", "terminal"])
def test_focused_prompt_needs_no_workflow_sections(executor):
    prompt = (
        "Compare SQLite backup options for a local desktop app. Explain which "
        "option fits an offline user and cite the official documentation."
    )
    assert lint_prompt.evaluate(prompt, executor)["status"] == "pass"


@pytest.mark.parametrize("executor", ["web", "terminal"])
def test_instruction_count_does_not_gate_prompt(executor):
    prompt = make_prompt(extra="You must preserve the supplied constraint.\n" * 65)
    assert lint_prompt.evaluate(prompt, executor)["status"] == "pass"


@pytest.mark.parametrize("prompt", ["", " \n\t"])
def test_empty_prompt_fails(prompt):
    result = lint_prompt.evaluate(prompt, "terminal")
    assert check(result, "nonempty_prompt")["status"] == "fail"
    assert result["status"] == "fail"


# --- individual checks ----------------------------------------------------


def test_clean_prompt_passes_everything():
    result = lint_prompt.evaluate(make_prompt(), executor="terminal")
    assert result["status"] == "pass"
    assert all(c["status"] == "pass" for c in result["checks"])


def test_unfilled_slots_fail_and_are_named():
    result = lint_prompt.evaluate(make_prompt(slots=True), executor="terminal")
    c = check(result, "unfilled_slots")
    assert c["status"] == "fail"
    assert "SEED_SOURCES" in c["detail"]
    assert result["status"] == "fail"


def test_leftover_drafting_comments_fail():
    result = lint_prompt.evaluate(make_prompt(comments=True), executor="terminal")
    assert check(result, "drafting_comments")["status"] == "fail"


@pytest.mark.parametrize("trailer", ["</content>", "</tool_result>", "</write>"])
def test_trailing_harness_debris_fails(trailer):
    result = lint_prompt.evaluate(make_prompt(extra=f"\n{trailer}\n"), executor="terminal")
    c = check(result, "harness_debris")
    assert c["status"] == "fail"
    assert trailer in c["detail"]


def test_xml_like_text_inside_prompt_is_not_treated_as_trailing_debris():
    text = make_prompt(extra="Use <content>example</content> as the fixture.\nThen summarize it.\n")
    result = lint_prompt.evaluate(text, executor="terminal")
    assert check(result, "harness_debris")["status"] == "pass"


# --- CLI ------------------------------------------------------------------


def run_cli(tmp_path: Path, text: str, *args: str) -> subprocess.CompletedProcess:
    prompt = tmp_path / "prompt.md"
    prompt.write_text(text)
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(prompt), *args],
        capture_output=True,
        text=True,
    )


def test_cli_pass_exits_zero_with_json(tmp_path):
    proc = run_cli(tmp_path, make_prompt(), "--executor", "terminal", "--json")
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload["status"] == "pass"
    assert payload["executor"] == "terminal"


def test_cli_fail_exits_one(tmp_path):
    proc = run_cli(tmp_path, make_prompt(slots=True), "--executor", "terminal")
    assert proc.returncode == 1
    assert "unfilled_slots" in proc.stdout


def test_cli_warn_exits_zero_unless_strict(tmp_path):
    text = make_prompt(extra=SEEDED_FLOATING)
    assert run_cli(tmp_path, text, "--executor", "web").returncode == 0
    assert run_cli(tmp_path, text, "--executor", "web", "--strict").returncode == 1


def test_cli_missing_file_exits_two(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(tmp_path / "nope.md")],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2


# --- seeded statistics ----------------------------------------------------


SEEDED_FLOATING = (
    "**Seed sources (vetted; start here):**\n"
    "- A large-N study reportedly finds 1.2B trades show no longshot bias.\n"
)

SEEDED_IDENTIFIED = (
    "**Seed sources (vetted; start here):**\n"
    "- Underconfidence in prediction markets, arXiv 2602.19520 — reports 292M\n"
    "  trades; verify the headline finding before relying on it.\n"
)


def test_floating_statistic_in_seed_block_warns():
    result = lint_prompt.evaluate(make_prompt(extra=SEEDED_FLOATING), "terminal")
    entry = check(result, "seeded_statistics")
    assert entry["status"] == "warn"
    assert "1.2B" in entry["detail"]


def test_identified_statistic_in_seed_block_passes():
    result = lint_prompt.evaluate(make_prompt(extra=SEEDED_IDENTIFIED), "terminal")
    assert check(result, "seeded_statistics")["status"] == "pass"


def test_magnitudes_outside_the_seed_block_are_ignored():
    # The seed block ends at the next bold label, so the 1.5M below is body
    # prose the executor is asked to produce -- not seeded background.
    extra = SEEDED_IDENTIFIED + "\n**Source floor:** report the 1.5M-case base rate.\n"
    result = lint_prompt.evaluate(make_prompt(extra=extra), "terminal")
    assert check(result, "seeded_statistics")["status"] == "pass"


def test_small_counts_inside_the_seed_block_are_not_statistics():
    extra = (
        "**Seed sources (vetted; start here):**\n"
        "- All seed sources plus >=10 adjacent primary sources spanning X, Y, Z.\n"
    )
    result = lint_prompt.evaluate(make_prompt(extra=extra), "terminal")
    assert check(result, "seeded_statistics")["status"] == "pass"


def test_seeded_statistics_warning_does_not_fail_the_run(tmp_path):
    assert run_cli(tmp_path, make_prompt(extra=SEEDED_FLOATING),
                   "--executor", "terminal").returncode == 0
    assert run_cli(tmp_path, make_prompt(extra=SEEDED_FLOATING),
                   "--executor", "terminal", "--strict").returncode == 1
