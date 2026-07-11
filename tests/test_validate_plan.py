from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "skills" / "write-plan" / "scripts" / "validate_plan.py"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_plan", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def plan_body(
    files: str,
    markers: str = "",
    implementation_steps: str = "1. Make the agreed change.",
) -> str:
    return f"""# Grounding Example Plan

## Goal

Deliver the agreed outcome.

## Scope

In scope: the agreed outcome.

## Assumptions And Constraints

- Keep the implementation small.

## Task Breakdown

### Task 1: Update the example

**Objective**

Make the example behave as agreed.

**Files**

{files}

**Dependencies**

None

**Implementation Steps**

{implementation_steps}

**Verification**

- Run: `true`
- Expect: command succeeds.

**Done When**

- The example behaves as agreed.

{markers}
## Risks And Mitigations

- Risk: an external dependency is unavailable.
  Mitigation: report a clear failure.

## Verification Matrix

| Requirement | Proof command | Expected signal |
| --- | --- | --- |
| Example works | `true` | command succeeds |

## Handoff

1. Execute the task.
"""


def write_plan(tmp_path: Path, files: str, markers: str = "") -> Path:
    path = tmp_path / "grounding-example-plan.md"
    path.write_text(
        "---\n"
        "date: 2026-07-11\n"
        "topic: grounding-example\n"
        "stage: plan\n"
        "status: draft\n"
        "source: test\n"
        "---\n\n"
        + plan_body(files, markers),
        encoding="utf-8",
    )
    return path


def test_existing_code_task_without_grounding_marker_is_advisory() -> None:
    module = load_module()

    advisories = module.collect_advisories(
        plan_body("- Modify: `src/example.py`")
    )

    assert advisories == [
        "Task 1: Update the example: modifies existing code but has no "
        "**Assumptions Verified** marker"
    ]


def test_create_only_task_needs_no_grounding_marker() -> None:
    module = load_module()

    assert module.collect_advisories(plan_body("- Create: `src/example.py`")) == []


def test_test_changing_task_without_discovery_marker_is_advisory() -> None:
    module = load_module()

    advisories = module.collect_advisories(
        plan_body(
            "- Test: `tests/test_example.py`",
            "**Assumptions Verified**\n\n- Existing behavior is verified.\n\n",
        )
    )

    assert advisories == [
        "Task 1: Update the example: changes tests but has no "
        "**Test Discovery Verified** marker"
    ]


def test_explicit_grounding_and_discovery_markers_suppress_advisories() -> None:
    module = load_module()

    markers = """**Assumptions Verified**

- `src/example.py:12` is the edited seam.

**Test Discovery Verified**

- `pytest tests/test_example.py -q` runs the literal test file.

"""

    assert module.collect_advisories(
        plan_body(
            "- Modify: `src/example.py`\n- Test: `tests/test_example.py`", markers
        )
    ) == []


def test_marker_mentions_in_task_prose_do_not_suppress_advisories() -> None:
    module = load_module()

    advisories = module.collect_advisories(
        plan_body(
            "- Modify: `src/example.py`\n- Test: `tests/test_example.py`",
            implementation_steps=(
                "1. Add `**Assumptions Verified**` to the plan template.\n"
                "2. Add `**Test Discovery Verified**` to the plan template."
            ),
        )
    )

    assert advisories == [
        "Task 1: Update the example: modifies existing code but has no "
        "**Assumptions Verified** marker",
        "Task 1: Update the example: changes tests but has no "
        "**Test Discovery Verified** marker",
    ]


def test_inline_marker_sections_suppress_advisories() -> None:
    module = load_module()

    markers = """**Assumptions Verified**: `src/example.py:12` is the seam.

**Test Discovery Verified**: `pytest tests/test_example.py -q` runs the test.

"""

    assert module.collect_advisories(
        plan_body(
            "- Modify: `src/example.py`\n- Test: `tests/test_example.py`", markers
        )
    ) == []


def test_advisories_do_not_change_a_valid_plan_exit_status(tmp_path: Path) -> None:
    path = write_plan(tmp_path, "- Modify: `src/example.py`")

    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(path), "--strict-filename"],
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0
    assert f"PASS: {path}" in proc.stdout
    assert "ADVISORY" in proc.stdout
    assert "**Assumptions Verified**" in proc.stdout


def test_missing_plan_still_reports_a_validation_error_without_a_traceback(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing-plan.md"

    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(missing), "--strict-filename"],
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 1
    assert f"File not found: {missing}" in proc.stdout
    assert "Traceback" not in proc.stderr


def test_non_markdown_binary_target_reports_a_validation_error_without_a_traceback(
    tmp_path: Path,
) -> None:
    target = tmp_path / "not-a-plan.bin"
    target.write_bytes(b"\xff\xfe")

    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(target)],
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 1
    assert f"Not a markdown file: {target}" in proc.stdout
    assert "Traceback" not in proc.stderr
