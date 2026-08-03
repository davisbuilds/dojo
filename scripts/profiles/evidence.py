#!/usr/bin/env python3
"""Assemble the deterministic conformance report, and detect legacy topologies.

Two properties make this report usable as evidence rather than output:

**Byte-identity over unchanged inputs.** Every date comes from the *policy
record*, never the clock, and every list is lexically ordered. Wall-clock and
hostname live in a separate `envelope` that `--json` does not emit. The existing
standardizer report embeds `utc_now_iso()`, which is why the payload is split
rather than reused.

**A suppressed member is distinguishable from one the profile never selected.**
That distinction is the entire reason suppression is declared rather than
achieved by editing membership: SC-11 requires every cross-harness difference to
be *attributable*, and a report listing only what landed cannot support that.

Phase 1's main operating mode is `unprofiled`. No profile can be applied until
Task 12, so every real target is unprofiled today — a target with full
observation and no declaration to compare against, which is precisely the gap
the contract exists to close. It is never `conformant`, never `unsupported`, and
exits 2.

Contract: docs/specs/2026-07-27-distribution-profiles-spec.md (SC-06, SC-09,
SC-11, EV-NEG-04, EV-CON-02).
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path

from .budget import Assessment, Policy, Verdict
from .observe import Observation
from .resolve import HarnessResolution, Resolution

# SC-06's field set, verbatim. The report asserts against this, so adding or
# dropping a field is a deliberate edit rather than a silent change in shape.
SC06_FIELDS = (
    "assertions",
    "budget",
    "canonical_revision",
    "collisions",
    "drift",
    "foreign_entries",
    "harness",
    "legacy_topologies",
    "plugin_entries",
    "profile",
    "realization_identity",
    "resolved_members",
    "routing_coverage",
    "shadowed_names",
    "state",
    "suppressed",
)


class ExitCode(IntEnum):
    """Caller semantics, fixed by the contract.

    2 is *evaluated and not conformant* — a real answer. 1 is *could not
    finish*. Collapsing them would make an incomplete run indistinguishable from
    a clean failure, which is how a partial report ends up trusted.
    """

    CONFORMANT = 0
    INCOMPLETE = 1
    NONCONFORMANT = 2


# Plain string constants rather than an Enum: these values are serialized into
# evidence and compared byte-for-byte, so their spelling is contractual and
# should be visible at the point of use.
STATE_CONFORMANT = "conformant"
STATE_NONCONFORMANT = "nonconformant"
STATE_UNPROFILED = "unprofiled"
STATE_UNSUPPORTED = "unsupported"


@dataclass
class Evidence:
    """The normative payload. Byte-identical over unchanged inputs."""

    payload: dict
    partial: bool = False
    envelope: dict = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(self.payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))

    @property
    def exit_code(self) -> ExitCode:
        if self.partial:
            return ExitCode.INCOMPLETE
        if self.payload.get("state") == STATE_CONFORMANT:
            return ExitCode.CONFORMANT
        return ExitCode.NONCONFORMANT

    def __post_init__(self) -> None:
        # Asserted in code, not only in a test: a report that could not finish
        # must never be emitted with exit 0.
        if self.partial and self.payload.get("state") == STATE_CONFORMANT:
            raise ValueError("a partial report cannot be conformant")


def detect_legacy_topologies(observation: Observation, catalog_size: int) -> list[dict]:
    """SC-09's four shapes, detected without mutating anything.

    (a) is the one that matters most: a scope root that *is* a symlink to a
    canonical tree exposes the whole catalog. It is reported as **full canonical
    membership at the selected revision**, never as an implicit `full` profile —
    accepting it as `full` would launder an accident into a declaration.
    """
    found: list[dict] = []

    managed = [e for e in observation.entries if e.origin == "dojo-managed"]
    if managed and len(managed) >= catalog_size:
        found.append({
            "kind": "whole-catalog-link",
            "detail": "scope root exposes the full canonical catalog",
            "member_count": len(managed),
        })

    concrete = sorted(e.name for e in managed if e.is_symlink is False)
    if concrete:
        found.append({"kind": "concrete-secondary-copy", "entries": concrete})

    drifted = sorted(
        e.name for e in managed
        if e.source_description is not None
        and e.listed_description is not None
        and e.listed_description != e.source_description
    )
    if drifted:
        found.append({"kind": "version-skewed-content", "entries": drifted})

    return found


def dirty_state(repo_root: Path, selected_members: tuple[str, ...]) -> list[str]:
    """Paths whose uncommitted changes make a target audit-only (EV-NEG-04).

    Narrow by construction: only changes to a *selected* canonical skill or to
    `profiles/` count. An unrelated working-tree edit does not block an otherwise
    valid evaluation, because treating every dirty tree as audit-only would make
    the verifier unusable during ordinary work.
    """
    try:
        out = subprocess.run(
            # `-uall` is required. By default git *collapses* untracked
            # directories to `?? skills/`, so a wholly-new selected skill never
            # matches its own path prefix and a dirty target reports clean — the
            # failure direction that lets unreviewed content look deployable.
            ["git", "-C", str(repo_root), "status", "--porcelain", "-uall"],
            capture_output=True, text=True, check=False, timeout=30,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return ["<git unavailable: source revision unverifiable>"]

    selected_paths = {f"skills/{name}/" for name in selected_members} | {"profiles/"}
    dirty = []
    for line in out.splitlines():
        path = line[3:].strip()
        if any(path.startswith(prefix) for prefix in selected_paths):
            dirty.append(path)
    return sorted(dirty)


def canonical_revision(repo_root: Path) -> str | None:
    """The selected source revision, or None when it cannot be verified.

    A source with no verifiable revision is audit-only even when its content can
    be hashed: content identity says what is there, not which reviewed revision
    it is.
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=False, timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() or None if result.returncode == 0 else None


def build_evidence(
    resolution: Resolution | None,
    harness_resolution: HarnessResolution | None,
    observation: Observation,
    assessment: Assessment,
    policy: Policy,
    *,
    repo_root: Path,
    catalog_size: int,
    realization_id: str | None = None,
    equivalence_id: str | None = None,
    routing_coverage: dict | None = None,
    partial: bool = False,
) -> Evidence:
    """Assemble one target's evidence.

    `resolution is None` means the target carries no declaration — the
    `unprofiled` state, which is phase 1's normal case rather than an edge one.
    """
    revision = canonical_revision(repo_root)
    members = resolution.members if resolution else ()
    dirty = dirty_state(repo_root, members)

    if partial:
        state = STATE_UNSUPPORTED
    elif revision is None:
        state = STATE_UNSUPPORTED
    elif resolution is None:
        state = STATE_UNPROFILED
    elif dirty:
        state = STATE_UNSUPPORTED
    elif assessment.verdict is Verdict.DEPLOYABLE:
        state = STATE_CONFORMANT
    elif assessment.verdict is Verdict.UNSUPPORTED:
        state = STATE_UNSUPPORTED
    else:
        state = STATE_NONCONFORMANT

    payload = {
        "state": state,
        "canonical_revision": revision,
        "profile": {
            "selection": list(resolution.selection) if resolution else [],
            "identity": resolution.identity if resolution else None,
            "dirty_selected_paths": dirty,
        },
        "realization_identity": realization_id,
        "resolved_members": sorted(members),
        # A suppressed member is not a member the profile never selected. Each
        # entry names what displaced it and why, so a cross-harness difference is
        # attributable rather than merely observed (SC-11).
        "suppressed": sorted(
            (
                {"skill": s.skill, "bundled_entry": s.bundled_entry, "evidence": s.evidence}
                for s in (harness_resolution.suppressed if harness_resolution else ())
            ),
            key=lambda d: d["skill"],
        ),
        "collisions": sorted(
            (
                {"skill": c.skill, "bundled_entry": c.bundled_entry}
                for c in (harness_resolution.collisions if harness_resolution else ())
            ),
            key=lambda d: d["skill"],
        ),
        "harness": {
            "name": policy.harness,
            "version": policy.harness_version,
            "model": policy.model,
            "policy_identity": policy.identity,
            "deployable_pair": policy.deployable,
            "shadows_by_name": policy.shadows_by_name,
        },
        "budget": {
            "unit": assessment.unit,
            "limit": assessment.limit,
            "demand": assessment.demand,
            "basis_points": assessment.basis_points,
            "headroom": assessment.limit - assessment.demand,
            "verdict": assessment.verdict.value,
            "gating": assessment.gating,
            "cost_basis": observation.cost_basis_counts,
            "reason": assessment.reason,
        },
        "drift": {
            "degradations": [d.value for d in assessment.degradations],
            "unsupported": sorted(observation.unsupported),
        },
        "foreign_entries": sorted(e.name for e in observation.entries if e.origin == "foreign"),
        "plugin_entries": sorted(e.name for e in observation.entries if e.origin == "plugin"),
        "shadowed_names": list(observation.duplicated_names),
        "legacy_topologies": detect_legacy_topologies(observation, catalog_size),
        "routing_coverage": routing_coverage or {"skills_with_fixtures": [], "reported": False},
        "assertions": {"executed": 0, "outcomes": []},
        "equivalence_identity": equivalence_id,
    }
    # `equivalence_identity` is nested under profile rather than top level to keep
    # the SC-06 field set exact; kept addressable here for readability.
    payload["profile"]["equivalence_identity"] = payload.pop("equivalence_identity")

    return Evidence(payload=payload, partial=partial)


def build_evidence_json(*args, **kwargs) -> str:
    return build_evidence(*args, **kwargs).to_json()
