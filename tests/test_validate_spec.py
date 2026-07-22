from __future__ import annotations

import importlib.util
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
