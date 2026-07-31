from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
HOOK = REPO_ROOT / "hooks" / "pre-tool-use-shell-safety.sh"


def run(command: str | None, tool_name: str = "Bash", raw: str | None = None):
    payload = raw if raw is not None else json.dumps(
        {"tool_name": tool_name, "tool_input": {"command": command}}
    )
    proc = subprocess.run(
        ["bash", str(HOOK)], input=payload, capture_output=True, text=True
    )
    return proc


def warnings_of(proc) -> str:
    """Return the additionalContext text, or '' when the hook stayed silent."""
    if not proc.stdout.strip():
        return ""
    return json.loads(proc.stdout)["hookSpecificOutput"]["additionalContext"]


# --- never blocks -------------------------------------------------------------


@pytest.mark.parametrize(
    "command",
    [
        "for f in $FILES; do echo $f; done",
        "rg -rn pattern",
        "path=/tmp/x",
        "echo hello",
    ],
)
def test_always_exits_zero(command: str) -> None:
    """Warn-only by contract: a false positive must never stop work."""
    assert run(command).returncode == 0


# --- the zsh word-splitting trap ----------------------------------------------


def test_warns_on_unquoted_variable_for_loop() -> None:
    w = warnings_of(run("for s in $RETIRE; do check $s; done"))
    assert "word-split" in w


def test_warns_on_braced_form() -> None:
    assert "word-split" in warnings_of(run("for x in ${LIST}; do echo $x; done"))


@pytest.mark.parametrize(
    "command",
    [
        'for x in "${arr[@]}"; do echo "$x"; done',   # correct array form
        "for f in *.md; do echo $f; done",            # glob, splits fine
        "for f in $(ls); do echo $f; done",           # command substitution splits
        "for i in 1 2 3; do echo $i; done",           # literal list
    ],
)
def test_does_not_warn_on_correct_loops(command: str) -> None:
    assert warnings_of(run(command)) == ""


# --- the ripgrep --replace trap -----------------------------------------------


@pytest.mark.parametrize("command", ["rg -rn foo", "rg -r x pattern", "rg -rln thing"])
def test_warns_on_rg_replace_cluster(command: str) -> None:
    assert "--replace" in warnings_of(run(command))


@pytest.mark.parametrize(
    "command",
    [
        "rg -n pattern",                    # correct line-number flag
        "rg -l pattern",
        "rg --replace X pattern",           # spelled out, presumably deliberate
        "rg pattern",
        "grep -rn pattern .",               # grep -r really is recursive
    ],
)
def test_does_not_warn_on_correct_rg(command: str) -> None:
    assert warnings_of(run(command)) == ""


# --- zsh reserved names -------------------------------------------------------


def test_warns_on_reserved_path_variable() -> None:
    assert "masks command lookup" in warnings_of(run("path=/usr/local/bin; ls"))


def test_does_not_warn_on_ordinary_variable() -> None:
    assert warnings_of(run("mypath=/usr/local/bin; ls")) == ""


# --- fails open ---------------------------------------------------------------


@pytest.mark.parametrize(
    "raw",
    ["", "not json at all", "{}", '{"tool_name": "Read"}'],
)
def test_degrades_silently_on_bad_input(raw: str) -> None:
    """This runs ahead of every Bash call; unexpected input must be a no-op."""
    proc = run(None, raw=raw)
    assert proc.returncode == 0
    assert proc.stdout.strip() == ""


def test_ignores_non_bash_tools() -> None:
    proc = run("for x in $V; do :; done", tool_name="Write")
    assert proc.returncode == 0 and proc.stdout.strip() == ""


def test_multiple_traps_reported_together() -> None:
    w = warnings_of(run("for s in $LIST; do rg -rn $s; done"))
    assert "word-split" in w and "--replace" in w


# --- multi-word literal passed as one argv element ----------------------------


def test_warns_when_multiword_loop_item_is_used_unquoted() -> None:
    """The exact shape that reported four passing CI checks as stale."""
    w = warnings_of(run('for c in "scripts/gen.py --check"; do python3 $c; done'))
    assert "ONE argument" in w


@pytest.mark.parametrize(
    "command",
    [
        'for c in "one.py" "two.py"; do python3 $c; done',   # single-word items
        'for c in "a.py --check"; do python3 "$c"; done',    # quoted use is fine
        'for c in "a.py --check"; do echo done; done',       # var never used
    ],
)
def test_does_not_warn_on_safe_multiword_forms(command: str) -> None:
    assert warnings_of(run(command)) == ""
