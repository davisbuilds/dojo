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


def test_modern_plan_frontmatter_requires_resolved_author(tmp_path: Path) -> None:
    module = load_module()
    base = {
        "date": "2026-07-22",
        "topic": "example",
        "stage": "plan",
        "status": "draft",
        "source": "test",
        "risk_profile": "routine",
        "readiness": "draft",
    }

    missing = module.validate_frontmatter(base, "plan", False, tmp_path / "plan.md")
    unresolved = module.validate_frontmatter(
        {**base, "author": "<agent>"}, "plan", False, tmp_path / "plan.md"
    )

    assert "Missing required frontmatter key: author" in missing
    assert "Frontmatter 'author' must name the producing agent" in unresolved


def test_legacy_plan_frontmatter_remains_valid_without_author(tmp_path: Path) -> None:
    module = load_module()
    frontmatter = {
        "date": "2026-07-22",
        "topic": "example",
        "stage": "plan",
        "status": "draft",
        "source": "test",
    }

    assert module.validate_frontmatter(
        frontmatter, "plan", False, tmp_path / "plan.md"
    ) == []


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


def test_degenerate_done_when_language_is_advisory() -> None:
    module = load_module()
    body = plan_body("- Create: `src/example.py`").replace(
        "- The example behaves as agreed.",
        "- The output is not empty and the command completes.",
    )

    advisories = module.collect_advisories(body)

    assert any("pinned magnitude" in advisory for advisory in advisories)


def test_pinned_done_when_threshold_is_not_degenerate() -> None:
    module = load_module()
    body = plan_body("- Create: `src/example.py`").replace(
        "- The example behaves as agreed.",
        "- At least 95 of 100 fixtures produce the expected result.",
    )

    assert module.collect_advisories(body) == []


def test_done_when_advisory_does_not_scan_later_plan_sections() -> None:
    module = load_module()
    body = plan_body("- Create: `src/example.py`").replace(
        "- The example behaves as agreed.",
        "- At least 95 of 100 fixtures produce the expected result.",
    ).replace(
        "- Risk: an external dependency is unavailable.",
        "- Risk: deployment completes before monitoring attaches.",
    )

    assert module.collect_advisories(body) == []


def test_external_tool_step_without_behavior_measured_is_advisory() -> None:
    module = load_module()
    body = plan_body(
        "- Create: `src/example.py`",
        implementation_steps="1. Run `tmux new -d -s work` and confirm the pane.",
    )

    advisories = module.collect_advisories(body)

    assert any(
        "tmux" in advisory and "**Behavior Measured**" in advisory
        for advisory in advisories
    )


def test_behavior_measured_marker_suppresses_external_tool_advisory() -> None:
    module = load_module()
    body = plan_body(
        "- Create: `src/example.py`",
        markers="**Behavior Measured**\n\n- `tmux -V` -> `tmux 3.4`\n\n",
        implementation_steps="1. Run `tmux new -d -s work` and confirm the pane.",
    )

    assert all(
        "**Behavior Measured**" not in advisory
        for advisory in module.collect_advisories(body)
    )


def test_hyphenated_tool_names_are_not_external_tool_invocations() -> None:
    module = load_module()
    # Names and paths that merely start with a tool token — a hyphen is a word
    # boundary but not a command terminator — must not read as invocations.
    body = plan_body(
        "- Create: `src/example.py`",
        implementation_steps=(
            "1. Wire the `gh-commit-push-pr` skill; read `codex-rs/core/lib.rs`,\n"
            "   `codex-primary-runtime`, and `codex-tui-clipped.json`."
        ),
    )

    assert all(
        "**Behavior Measured**" not in advisory
        for advisory in module.collect_advisories(body)
    )


def test_internal_only_task_has_no_external_tool_advisory() -> None:
    module = load_module()
    body = plan_body(
        "- Create: `src/example.py`",
        implementation_steps="1. Call the internal helper `render()` and assert output.",
    )

    assert all(
        "**Behavior Measured**" not in advisory
        for advisory in module.collect_advisories(body)
    )


def test_partition_only_done_when_is_advisory() -> None:
    module = load_module()
    body = plan_body("- Create: `src/example.py`").replace(
        "- The example behaves as agreed.",
        "- Only the legacy caller takes the old path.",
    )

    advisories = module.collect_advisories(body)

    assert any("single branch" in advisory for advisory in advisories)


def test_every_declared_done_when_is_advisory() -> None:
    module = load_module()
    body = plan_body("- Create: `src/example.py`").replace(
        "- The example behaves as agreed.",
        "- The manifest carries every declared `--runtime-executable`.",
    )

    advisories = module.collect_advisories(body)

    assert any("vacuously true" in advisory for advisory in advisories)


def test_discover_repo_root_survives_deleted_cwd(tmp_path: Path) -> None:
    module = load_module()
    plan = tmp_path / "docs" / "plans" / "example-plan.md"
    plan.parent.mkdir(parents=True)
    plan.write_text("placeholder", encoding="utf-8")

    deleted = tmp_path / "gone"
    deleted.mkdir()
    original = Path.cwd()
    import os

    os.chdir(deleted)
    deleted.rmdir()
    try:
        root = module.discover_repo_root(plan)
    finally:
        os.chdir(original)

    assert root == plan.parent.resolve()


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


def high_risk_addendum(blocking_findings: str = "none") -> str:
    return f"""## High-Risk Readiness

### Traceability

| Contract ID | Task | Proof |
| --- | --- | --- |
| SC-01 | Task 0 | `pytest -q` |
| EV-NEG-01 | Task 0 | `pytest -q` |
| EV-REC-01 | Task 0 | `pytest -q` |
| EV-CON-01 | Task 0 | `pytest -q` |
| EV-LEG-01 | Task 0 | `pytest -q` |

### Capability And Authority Map

| Actor | Allowed | Forbidden | Effective-runtime proof |
| --- | --- | --- | --- |
| Worker | Assigned workspace | External sentinel | `pytest -q` |

### Side Effects And Failure Windows

| Effect | Before | After | Recovery |
| --- | --- | --- | --- |
| Remote mutation | No remote state | One durable result | Reconcile by identity |

### Evidence Lifecycle

| Evidence | Trusted producer | Created | Claim | Consumers | Freshness |
| --- | --- | --- | --- | --- | --- |
| Runtime probe | Isolated host | Task 0 | Boundary holds | Release gate | Runtime fingerprint |

### Consumer Closure

- Identity, retry, outcome, cadence, supersession, and compatibility consumers
  update atomically in Task 0.

### Lifecycle And Compatibility

- Legacy state follows EV-LEG-01 before new state is accepted.

### Execution Hooks

- Dependency and lifecycle hooks are reviewed before privileged execution.

### Capability Stop Gates

- Task 0 stops unless direct, indirect, credential, and state-class probes pass.

### Readiness Review

- Deterministic validation: passed
- Adversarial critique: complete
- Closure critique: complete
- Blocking findings: {blocking_findings}

"""


def high_risk_plan_body(
    files: str,
    dependencies: str = "None",
    include_legacy_scenario: bool = True,
) -> str:
    body = plan_body(
        files,
        markers=(
            "**Assumptions Verified**\n\n"
            "- `src/example.py:1` is the boundary seam.\n\n"
            "**Test Discovery Verified**\n\n"
            "- `pytest tests/test_example.py -q` runs the boundary test.\n\n"
        ),
    ).replace("### Task 1:", "### Task 0:").replace(
        "**Dependencies**\n\nNone", f"**Dependencies**\n\n{dependencies}"
    )
    addendum = high_risk_addendum()
    if not include_legacy_scenario:
        addendum = addendum.replace("| EV-LEG-01 | Task 0 | `pytest -q` |\n", "").replace(
            "EV-LEG-01", "the legacy scenario"
        )
    return body.replace("## Risks And Mitigations", addendum + "## Risks And Mitigations")


def write_high_risk_spec(root: Path, readiness: str = "ready") -> Path:
    path = root / "docs" / "specs" / "example-spec.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        f"---\nrisk_profile: high\nreadiness: {readiness}\n---\n\n"
        "- SC-01: boundary holds\n"
        "- EV-NEG-01: forbidden path\n"
        "- EV-REC-01: recovery path\n"
        "- EV-CON-01: concurrent path\n"
        "- EV-LEG-01: legacy path\n",
        encoding="utf-8",
    )
    return path


def write_complete_high_risk_plan(root: Path) -> Path:
    target = root / "src" / "example.py"
    target.parent.mkdir(parents=True)
    target.write_text("boundary = True\n", encoding="utf-8")
    plan = root / "docs" / "plans" / "example-plan.md"
    plan.parent.mkdir(parents=True)
    plan.write_text(
        "---\n"
        "date: 2026-07-27\n"
        "author: gpt-5.6-sol\n"
        "topic: example\n"
        "stage: plan\n"
        "status: draft\n"
        "source: test\n"
        "risk_profile: high\n"
        "readiness: ready\n"
        "spec: docs/specs/example-spec.md\n"
        "---\n\n"
        + high_risk_plan_body(
            "- Modify: `src/example.py`\n- Test: `tests/test_example.py`"
        ),
        encoding="utf-8",
    )
    return plan


def test_routine_plan_does_not_require_high_risk_sections(tmp_path: Path) -> None:
    module = load_module()

    assert module.validate_high_risk(
        {}, plan_body("- Create: `src/example.py`"), tmp_path / "plan.md"
    ) == []


def test_high_risk_plan_requires_linked_spec_and_structured_addendum(
    tmp_path: Path,
) -> None:
    module = load_module()

    errors = module.validate_high_risk(
        {"risk_profile": "high", "readiness": "draft"},
        plan_body("- Modify: `src/example.py`"),
        tmp_path / "plan.md",
    )

    assert any("spec" in error.lower() for error in errors)
    assert any("High-Risk Readiness" in error for error in errors)


def test_high_risk_plan_accepts_complete_addendum_and_spec_coverage(
    tmp_path: Path,
) -> None:
    module = load_module()
    write_high_risk_spec(tmp_path)
    target = tmp_path / "src" / "example.py"
    target.parent.mkdir(parents=True)
    target.write_text("boundary = True\n", encoding="utf-8")

    errors = module.validate_high_risk(
        {
            "risk_profile": "high",
            "readiness": "ready",
            "spec": "docs/specs/example-spec.md",
        },
        high_risk_plan_body("- Modify: `src/example.py`\n- Test: `tests/test_example.py`"),
        tmp_path / "docs" / "plans" / "example-plan.md",
        repo_root=tmp_path,
    )

    assert errors == []


def test_cli_discovers_external_repository_root_from_plan_path(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "consumer"
    repo.mkdir()
    subprocess.run(
        ["git", "init", "-q", str(repo)],
        check=True,
        capture_output=True,
        text=True,
    )
    write_high_risk_spec(repo)
    plan = write_complete_high_risk_plan(repo)

    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(plan)],
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert f"PASS: {plan}" in proc.stdout


def test_cli_uses_current_directory_when_plan_is_outside_git(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "consumer"
    repo.mkdir()
    write_high_risk_spec(repo)
    plan = write_complete_high_risk_plan(repo)

    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(plan)],
        cwd=repo,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert f"PASS: {plan}" in proc.stdout


def test_cli_explicit_repo_root_overrides_plan_location(tmp_path: Path) -> None:
    repo = tmp_path / "consumer"
    repo.mkdir()
    write_high_risk_spec(repo)
    plan = write_complete_high_risk_plan(repo)
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    relocated_plan = artifacts / plan.name
    relocated_plan.write_text(plan.read_text(encoding="utf-8"), encoding="utf-8")

    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            str(relocated_plan),
            "--repo-root",
            str(repo),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert f"PASS: {relocated_plan}" in proc.stdout


def test_repository_path_resolution_rejects_escape(tmp_path: Path) -> None:
    module = load_module()

    assert module.resolve_repo_path("../outside.py", tmp_path) is None


def test_high_risk_plan_reports_missing_spec_coverage_and_unknown_dependency(
    tmp_path: Path,
) -> None:
    module = load_module()
    write_high_risk_spec(tmp_path)
    target = tmp_path / "src" / "example.py"
    target.parent.mkdir(parents=True)
    target.write_text("boundary = True\n", encoding="utf-8")

    errors = module.validate_high_risk(
        {
            "risk_profile": "high",
            "readiness": "draft",
            "spec": "docs/specs/example-spec.md",
        },
        high_risk_plan_body(
            "- Modify: `src/example.py`", dependencies="Task 9", include_legacy_scenario=False
        ),
        tmp_path / "docs" / "plans" / "example-plan.md",
        repo_root=tmp_path,
    )

    assert any("EV-LEG-01" in error for error in errors)
    assert any("unknown dependency Task 9" in error for error in errors)


def test_high_risk_plan_requires_structured_readiness_tables(tmp_path: Path) -> None:
    module = load_module()
    write_high_risk_spec(tmp_path)
    target = tmp_path / "src" / "example.py"
    target.parent.mkdir(parents=True)
    target.write_text("boundary = True\n", encoding="utf-8")
    body = high_risk_plan_body("- Modify: `src/example.py`").replace(
        "| Evidence | Trusted producer | Created | Claim | Consumers | Freshness |",
        "Evidence lifecycle narrative",
    )

    errors = module.validate_high_risk(
        {
            "risk_profile": "high",
            "readiness": "draft",
            "spec": "docs/specs/example-spec.md",
        },
        body,
        tmp_path / "docs" / "plans" / "example-plan.md",
        repo_root=tmp_path,
    )

    assert any("Evidence Lifecycle table" in error for error in errors)


def test_high_risk_plan_rejects_missing_modified_file(tmp_path: Path) -> None:
    module = load_module()
    write_high_risk_spec(tmp_path)

    errors = module.validate_high_risk(
        {
            "risk_profile": "high",
            "readiness": "draft",
            "spec": "docs/specs/example-spec.md",
        },
        high_risk_plan_body("- Modify: `src/missing.py`"),
        tmp_path / "docs" / "plans" / "example-plan.md",
        repo_root=tmp_path,
    )

    assert any("missing modified file: src/missing.py" in error for error in errors)


def test_high_risk_plan_requires_ready_linked_spec(tmp_path: Path) -> None:
    module = load_module()
    write_high_risk_spec(tmp_path, readiness="draft")
    target = tmp_path / "src" / "example.py"
    target.parent.mkdir(parents=True)
    target.write_text("boundary = True\n", encoding="utf-8")

    errors = module.validate_high_risk(
        {
            "risk_profile": "high",
            "readiness": "draft",
            "spec": "docs/specs/example-spec.md",
        },
        high_risk_plan_body("- Modify: `src/example.py`"),
        tmp_path / "docs" / "plans" / "example-plan.md",
        repo_root=tmp_path,
    )

    assert any("linked spec with readiness: ready" in error for error in errors)


def write_legacy_high_risk_spec(root: Path, readiness: str = "ready") -> Path:
    path = root / "docs" / "specs" / "legacy-spec.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\nrisk_profile: high\nreadiness: {readiness}\n---\n\n"
        "- Allowed work succeeds.\n"
        "- Forbidden work leaves no side effect.\n",
        encoding="utf-8",
    )
    return path


def legacy_high_risk_plan_body(files: str, dependencies: str = "None") -> str:
    body = high_risk_plan_body(files, dependencies=dependencies)
    # Replace stable IDs with named contract surfaces (the legacy adoption path).
    for old, new in {
        "SC-01": "session-authority",
        "EV-NEG-01": "forbidden-path",
        "EV-REC-01": "recovery-path",
        "EV-CON-01": "concurrent-path",
        "EV-LEG-01": "legacy-path",
    }.items():
        body = body.replace(old, new)
    return body


def test_legacy_high_risk_plan_with_idless_spec_is_accepted(tmp_path: Path) -> None:
    module = load_module()
    write_legacy_high_risk_spec(tmp_path)
    target = tmp_path / "src" / "example.py"
    target.parent.mkdir(parents=True)
    target.write_text("boundary = True\n", encoding="utf-8")

    errors = module.validate_high_risk(
        {
            "risk_profile": "high",
            "readiness": "ready",
            "spec": "docs/specs/legacy-spec.md",
        },
        legacy_high_risk_plan_body(
            "- Modify: `src/example.py`\n- Test: `tests/test_example.py`"
        ),
        tmp_path / "docs" / "plans" / "legacy-plan.md",
        repo_root=tmp_path,
    )

    assert errors == []


def test_legacy_high_risk_plan_requires_named_traceability_rows(tmp_path: Path) -> None:
    module = load_module()
    write_legacy_high_risk_spec(tmp_path)
    target = tmp_path / "src" / "example.py"
    target.parent.mkdir(parents=True)
    target.write_text("boundary = True\n", encoding="utf-8")

    body = legacy_high_risk_plan_body(
        "- Modify: `src/example.py`\n- Test: `tests/test_example.py`"
    )
    # Strip every named-surface row, leaving only the Traceability header: an
    # id-less plan must still trace obligations, not skip coverage entirely.
    for surface in (
        "session-authority",
        "forbidden-path",
        "recovery-path",
        "concurrent-path",
        "legacy-path",
    ):
        body = body.replace(f"| {surface} | Task 0 | `pytest -q` |\n", "")

    errors = module.validate_high_risk(
        {
            "risk_profile": "high",
            "readiness": "ready",
            "spec": "docs/specs/legacy-spec.md",
        },
        body,
        tmp_path / "docs" / "plans" / "legacy-plan.md",
        repo_root=tmp_path,
    )

    assert any("trace named contract surfaces" in error for error in errors)


def test_high_risk_plan_inventing_ids_against_idless_spec_fails(tmp_path: Path) -> None:
    module = load_module()
    write_legacy_high_risk_spec(tmp_path)
    target = tmp_path / "src" / "example.py"
    target.parent.mkdir(parents=True)
    target.write_text("boundary = True\n", encoding="utf-8")

    # The plan carries IDs the id-less spec never declared: partial adoption
    # must fail, not silently downgrade to the legacy path.
    errors = module.validate_high_risk(
        {
            "risk_profile": "high",
            "readiness": "ready",
            "spec": "docs/specs/legacy-spec.md",
        },
        high_risk_plan_body(
            "- Modify: `src/example.py`\n- Test: `tests/test_example.py`"
        ),
        tmp_path / "docs" / "plans" / "legacy-plan.md",
        repo_root=tmp_path,
    )

    assert any("references unknown linked spec ID" in error for error in errors)
    assert not any("must define SC-NN" in error for error in errors)


def test_high_risk_plan_rejects_unknown_traceability_task(tmp_path: Path) -> None:
    module = load_module()
    write_high_risk_spec(tmp_path)
    target = tmp_path / "src" / "example.py"
    target.parent.mkdir(parents=True)
    target.write_text("boundary = True\n", encoding="utf-8")
    body = high_risk_plan_body("- Modify: `src/example.py`").replace(
        "| SC-01 | Task 0 |", "| SC-01 | Task 9 |"
    )

    errors = module.validate_high_risk(
        {
            "risk_profile": "high",
            "readiness": "draft",
            "spec": "docs/specs/example-spec.md",
        },
        body,
        tmp_path / "docs" / "plans" / "example-plan.md",
        repo_root=tmp_path,
    )

    assert any("traceability references unknown Task 9" in error for error in errors)
