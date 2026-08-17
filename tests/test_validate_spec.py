from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "skills" / "write-spec" / "scripts" / "validate_spec.py"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_spec", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_modern_contract_frontmatter_requires_resolved_author(tmp_path: Path) -> None:
    module = load_module()
    base = {
        "date": "2026-07-22",
        "topic": "example",
        "stage": "spec",
        "status": "draft",
        "source": "test",
        "risk_profile": "routine",
        "readiness": "draft",
    }

    missing = module.validate_frontmatter(base, "spec", False, tmp_path / "spec.md")
    unresolved = module.validate_frontmatter(
        {**base, "author": "<agent>"}, "spec", False, tmp_path / "spec.md"
    )

    assert "Missing required frontmatter key: author" in missing
    assert "Frontmatter 'author' must name the producing agent" in unresolved


def test_legacy_contract_frontmatter_remains_valid_without_author(tmp_path: Path) -> None:
    module = load_module()
    frontmatter = {
        "date": "2026-07-22",
        "topic": "example",
        "stage": "spec",
        "status": "draft",
        "source": "test",
    }

    assert module.validate_frontmatter(
        frontmatter, "spec", False, tmp_path / "spec.md"
    ) == []


def test_degenerate_acceptance_language_is_advisory() -> None:
    module = load_module()
    body = contract_body().replace(
        "The boundary holds, verified by `pytest -q`.",
        "The pipeline completes and reports `accepted_rows > 0`.",
    )

    advisories = module.collect_advisories(body)

    assert any("pinned magnitude" in advisory for advisory in advisories)


def test_pinned_acceptance_threshold_is_not_degenerate() -> None:
    module = load_module()
    body = contract_body().replace(
        "The boundary holds, verified by `pytest -q`.",
        "At least 95% of 1,000 fixtures pass, verified by `pytest -q`.",
    )

    assert module.collect_advisories(body) == []


def test_advisory_does_not_change_a_valid_contract_exit_status(
    tmp_path: Path,
) -> None:
    path = tmp_path / "example-spec.md"
    path.write_text(
        "---\n"
        "date: 2026-07-27\n"
        "author: gpt-5.6-sol\n"
        "topic: example\n"
        "stage: spec\n"
        "status: draft\n"
        "source: test\n"
        "risk_profile: routine\n"
        "readiness: draft\n"
        "---\n\n"
        + contract_body().replace(
            "The boundary holds, verified by `pytest -q`.",
            "The pipeline completes and reports `accepted_rows > 0`.",
        ),
        encoding="utf-8",
    )

    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(path)],
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0
    assert f"PASS: {path}" in proc.stdout
    assert "ADVISORY" in proc.stdout
    assert "pinned magnitude" in proc.stdout


def contract_body(high_risk_sections: str = "") -> str:
    return f"""# Example Spec

## Problem

An observable workflow can violate its intended authority boundary.

## Contract

The boundary holds, verified by `pytest -q`.

## Success Criteria

- SC-01: Allowed work succeeds.
- SC-02: Forbidden work leaves no side effect.

## Evaluation

Exercise the fixed scenarios below.

## Scope

In scope: observable boundary behavior.

## Assumptions And Constraints

- The runtime can be isolated.

## Open Questions

None.

{high_risk_sections}
## Handoff

1. Hand off to write-plan.
"""


def complete_high_risk_sections(blocking_findings: str = "none") -> str:
    return f"""## Authority And Safety

- The worker may mutate only its assigned workspace.
- External state remains unchanged when authorization is absent or stale.

## Evaluation Scenarios

- EV-NEG-01: A forbidden mutation fails without a side effect.
- EV-REC-01: An interrupted mutation reconciles safely.
- EV-CON-01: Concurrent attempts preserve one observable outcome.
- EV-LEG-01: Legacy state is rejected or migrated without widening authority.

## Readiness Review

- Deterministic validation: passed
- Adversarial critique: complete
- Closure critique: complete
- Blocking findings: {blocking_findings}

"""


def test_routine_contract_does_not_require_high_risk_sections() -> None:
    module = load_module()

    assert module.validate_high_risk({}, contract_body()) == []


def test_high_risk_contract_requires_structured_addendum() -> None:
    module = load_module()

    errors = module.validate_high_risk(
        {"risk_profile": "high", "readiness": "draft"}, contract_body()
    )

    assert any("Authority And Safety" in error for error in errors)
    assert any("Evaluation Scenarios" in error for error in errors)
    assert any("Readiness Review" in error for error in errors)


def test_high_risk_contract_accepts_complete_ready_addendum() -> None:
    module = load_module()

    errors = module.validate_high_risk(
        {"risk_profile": "high", "readiness": "ready"},
        contract_body(complete_high_risk_sections()),
    )

    assert errors == []


def test_high_risk_contract_requires_unique_criteria_and_scenario_classes() -> None:
    module = load_module()
    body = contract_body(complete_high_risk_sections()).replace(
        "SC-02: Forbidden work leaves no side effect.",
        "SC-01: Forbidden work leaves no side effect.",
    ).replace("EV-LEG-01", "EV-NEG-02")

    errors = module.validate_high_risk(
        {"risk_profile": "high", "readiness": "draft"}, body
    )

    assert any("duplicate success criterion ID SC-01" in error for error in errors)
    assert any("legacy" in error.lower() for error in errors)


def test_ready_high_risk_contract_rejects_open_blocking_findings() -> None:
    module = load_module()

    errors = module.validate_high_risk(
        {"risk_profile": "high", "readiness": "ready"},
        contract_body(complete_high_risk_sections("HR-03")),
    )

    assert any("blocking findings" in error.lower() for error in errors)


def legacy_high_risk_sections() -> str:
    return """## Authority And Safety

- The worker may mutate only its assigned workspace.
- External state remains unchanged when authorization is absent or stale.

## Evaluation Scenarios

- A forbidden mutation fails without a side effect.
- An interrupted mutation reconciles safely.
- Concurrent attempts preserve one observable outcome.
- Legacy state is rejected or migrated without widening authority.

## Readiness Review

- Deterministic validation: passed
- Adversarial critique: complete
- Closure critique: complete
- Blocking findings: none

"""


def legacy_contract_body() -> str:
    return contract_body(legacy_high_risk_sections()).replace(
        "- SC-01: Allowed work succeeds.\n"
        "- SC-02: Forbidden work leaves no side effect.",
        "- Allowed work succeeds.\n- Forbidden work leaves no side effect.",
    )


def test_legacy_high_risk_contract_without_ids_is_accepted() -> None:
    module = load_module()

    errors = module.validate_high_risk(
        {"risk_profile": "high", "readiness": "draft"}, legacy_contract_body()
    )

    assert errors == []


def test_partial_id_high_risk_contract_fails_rather_than_downgrading() -> None:
    module = load_module()
    # SC IDs present but scenarios use named surfaces (no EV IDs): partial
    # adoption must fail, not silently downgrade to the legacy path.
    body = contract_body(legacy_high_risk_sections())

    errors = module.validate_high_risk(
        {"risk_profile": "high", "readiness": "draft"}, body
    )

    assert any("evaluation scenario" in error.lower() for error in errors)


def test_legacy_high_risk_contract_still_requires_structural_headings() -> None:
    module = load_module()
    # An id-less high-risk contract is accepted on IDs but not on structure:
    # dropping a required heading still fails.
    body = legacy_contract_body().replace("## Authority And Safety", "## Authority")

    errors = module.validate_high_risk(
        {"risk_profile": "high", "readiness": "draft"}, body
    )

    assert any("Authority And Safety" in error for error in errors)
