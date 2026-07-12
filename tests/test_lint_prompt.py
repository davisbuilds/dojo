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


def make_prompt(
    *,
    slots: bool = False,
    comments: bool = False,
    rubric: bool = True,
    degradation: bool = True,
    do_not: bool = True,
    summary: bool = True,
    self_report: bool = True,
    extra: str = "",
) -> str:
    parts = [
        "# Research Prompt\n",
        "You are a skeptical research analyst. Your job: map the territory.\n",
    ]
    if slots:
        parts.append("**Seed sources:** {{SEED_SOURCES}}\n")
    if comments:
        parts.append("<!-- drafting guidance that should have been deleted -->\n")
    if do_not:
        parts.append(
            "**Do NOT (known failure modes for this topic):**\n"
            "- treat k-anonymity as equivalent to formal DP\n"
        )
    if degradation:
        parts.append(
            "**Degradation order:** if depth becomes constrained, deliver "
            "sections 3 and 6 at full depth and stub the rest.\n"
        )
    if rubric:
        parts.append(
            "This report will be scored against the following acceptance "
            "criteria by a separate verification pass.\n"
        )
    if summary:
        parts.append(
            "End the report with a machine-parseable summary block: "
            "`key_findings` / `citations` / `confidence_gaps` / `next_queries`.\n"
        )
    if self_report:
        parts.append(
            "Close with a short **self-report**: confidence, gaps, and which "
            "instructions you could not fully follow.\n"
        )
    parts.append(extra)
    return "\n".join(parts)


def check(result: dict, name: str) -> dict:
    return next(c for c in result["checks"] if c["name"] == name)


# --- instruction counting -------------------------------------------------


def test_count_instructions_counts_imperative_markers():
    text = "You must cite. Never guess. Always date claims. Do not pad."
    assert lint_prompt.count_instructions(text) == 4


def test_count_instructions_case_insensitive():
    assert lint_prompt.count_instructions("Do NOT invent. you MUST verify.") == 2


def test_count_instructions_zero_on_plain_prose():
    assert lint_prompt.count_instructions("A useful null result is a success.") == 0


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


@pytest.mark.parametrize(
    ("kwargs", "name"),
    [
        ({"rubric": False}, "rubric_present"),
        ({"degradation": False}, "degradation_order"),
        ({"do_not": False}, "do_not_list"),
        ({"summary": False}, "summary_block"),
        ({"self_report": False}, "self_report"),
    ],
)
def test_missing_required_block_fails(kwargs, name):
    result = lint_prompt.evaluate(make_prompt(**kwargs), executor="terminal")
    assert check(result, name)["status"] == "fail"
    assert result["status"] == "fail"


def test_partial_summary_block_fails():
    text = make_prompt(summary=False, extra="Include `key_findings` and `citations`.\n")
    result = lint_prompt.evaluate(text, executor="terminal")
    c = check(result, "summary_block")
    assert c["status"] == "fail"
    assert "confidence_gaps" in c["detail"]


# --- instruction budget ---------------------------------------------------


def base_count() -> int:
    return lint_prompt.count_instructions(make_prompt())


def imperatives(n: int) -> str:
    return "".join(f"You must check item {i}.\n" for i in range(n))


def test_budget_over_fails_for_web():
    over = lint_prompt.BUDGETS["web"] - base_count() + 1
    result = lint_prompt.evaluate(make_prompt(extra=imperatives(over)), executor="web")
    assert check(result, "instruction_budget")["status"] == "fail"


def test_budget_same_count_passes_for_terminal():
    over = lint_prompt.BUDGETS["web"] - base_count() + 1
    result = lint_prompt.evaluate(
        make_prompt(extra=imperatives(over)), executor="terminal"
    )
    assert check(result, "instruction_budget")["status"] == "pass"


def test_budget_within_ten_percent_warns():
    target = int(lint_prompt.BUDGETS["web"] * 0.9) - base_count() + 1
    result = lint_prompt.evaluate(
        make_prompt(extra=imperatives(target)), executor="web"
    )
    assert check(result, "instruction_budget")["status"] == "warn"
    assert result["status"] == "warn"


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
    target = int(lint_prompt.BUDGETS["web"] * 0.9) - base_count() + 1
    text = make_prompt(extra=imperatives(target))
    assert run_cli(tmp_path, text, "--executor", "web").returncode == 0
    assert run_cli(tmp_path, text, "--executor", "web", "--strict").returncode == 1


def test_cli_missing_file_exits_two(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(tmp_path / "nope.md")],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2
