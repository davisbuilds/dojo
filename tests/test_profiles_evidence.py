"""Task 5 — deterministic conformance evidence and legacy-topology detection.

The determinism tests come in pairs on purpose. Asserting that two runs produce
identical bytes is satisfied by a function that emits a constant; each is
therefore paired with a perturbation asserting the bytes *change*. Byte-identity
without that pair is not evidence of determinism, only of stability.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "profiles"
POLICIES = REPO_ROOT / "profiles" / "policies"
SKILLS = REPO_ROOT / "skills"
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from profiles import evidence as ev_mod, probe_codex  # noqa: E402
from profiles.budget import assess, load_policy  # noqa: E402
from profiles.definitions import load_catalog, load_definitions, load_equivalences  # noqa: E402
from profiles.evidence import (  # noqa: E402
    SC06_FIELDS,
    STATE_CONFORMANT,
    STATE_UNPROFILED,
    STATE_UNSUPPORTED,
    Evidence,
    ExitCode,
    build_evidence,
    detect_legacy_topologies,
    dirty_state,
)
from profiles.observe import observe_codex  # noqa: E402
from profiles.resolve import resolve, resolve_for_harness  # noqa: E402


@pytest.fixture
def catalog():
    return load_catalog(REPO_ROOT / "skills.json")


@pytest.fixture
def policy():
    return load_policy(POLICIES / "codex.yaml")


@pytest.fixture
def pieces(catalog, policy):
    """A full evaluation over the dojo fixture."""
    payload = json.loads((FIXTURES / "codex-prompt-input-dojo-2026-08-02.json").read_text())
    listing = probe_codex.classify(
        probe_codex.parse_block(probe_codex.extract_block(payload)), SKILLS, None, REPO_ROOT
    )
    observation = observe_codex(listing, policy, SKILLS)
    assessment = assess(observation.as_budget_entries(), policy, root_lines=observation.root_lines)
    defs = load_definitions(REPO_ROOT / "profiles", catalog)
    equivalences = load_equivalences(REPO_ROOT / "profiles" / "harness-equivalences.yaml", catalog)
    resolution = resolve(("core", "skill-authoring"), defs, catalog)
    harness = resolve_for_harness(resolution, equivalences.for_harness("codex"), "codex")
    return resolution, harness, observation, assessment, policy, equivalences


def evidence_for(pieces, catalog, **kwargs):
    resolution, harness, observation, assessment, policy, equivalences = pieces
    return build_evidence(
        resolution, harness, observation, assessment, policy,
        repo_root=REPO_ROOT, catalog_size=len(catalog),
        equivalence_id=equivalences.identity, **kwargs,
    )


# --------------------------------------------------------------------------
# Determinism — each assertion paired with a perturbation
# --------------------------------------------------------------------------


def test_two_runs_over_unchanged_inputs_are_byte_identical(pieces, catalog):
    first = evidence_for(pieces, catalog).to_json()
    second = evidence_for(pieces, catalog).to_json()
    assert hashlib.sha256(first.encode()).hexdigest() == hashlib.sha256(second.encode()).hexdigest()


def test_a_perturbed_input_changes_the_bytes(pieces, catalog):
    """The pair to the test above: byte-identity must not come from a constant."""
    baseline = evidence_for(pieces, catalog).to_json()
    resolution, harness, observation, assessment, policy, equivalences = pieces
    perturbed = build_evidence(
        resolution, harness, observation, assessment, replace(policy, model="different-model"),
        repo_root=REPO_ROOT, catalog_size=len(catalog), equivalence_id=equivalences.identity,
    ).to_json()
    assert perturbed != baseline


def test_no_wall_clock_reaches_the_normative_payload(pieces, catalog):
    """Dates come from the policy record; a timestamp would break byte-identity.

    The existing standardizer report embeds `utc_now_iso()`, which is why the
    payload is split rather than reused. The envelope is where wall-clock and
    hostname belong, and `to_json` never emits it.
    """
    report = evidence_for(pieces, catalog)
    assert "envelope" not in report.payload
    blob = report.to_json()
    for marker in ("utc_now", "hostname", "timestamp", "generated_at"):
        assert marker not in blob


def test_lists_are_lexically_ordered(pieces, catalog):
    payload = evidence_for(pieces, catalog).payload
    for key in ("resolved_members", "foreign_entries", "plugin_entries"):
        assert payload[key] == sorted(payload[key])
    assert [s["skill"] for s in payload["suppressed"]] == sorted(s["skill"] for s in payload["suppressed"])


# --------------------------------------------------------------------------
# Shape
# --------------------------------------------------------------------------


def test_the_report_carries_exactly_the_sc06_field_set(pieces, catalog):
    """Adding or dropping a field must fail, not pass quietly."""
    payload = evidence_for(pieces, catalog).payload
    assert tuple(sorted(payload)) == SC06_FIELDS
    assert len(SC06_FIELDS) == 16


def test_a_suppressed_member_is_distinguishable_from_one_never_selected(pieces, catalog):
    """SC-11's attributability requirement, which is why suppression is declared.

    `skill-creator` is selected and suppressed on Codex. `caveman` was never
    selected. A report that only listed what landed would render the two
    identically, and no cross-harness difference could be attributed.
    """
    payload = evidence_for(pieces, catalog).payload
    suppressed = {s["skill"] for s in payload["suppressed"]}
    assert "skill-creator" in suppressed
    assert "skill-creator" in payload["resolved_members"]
    assert "caveman" not in suppressed
    assert "caveman" not in payload["resolved_members"]
    entry = next(s for s in payload["suppressed"] if s["skill"] == "skill-creator")
    assert entry["bundled_entry"] and entry["evidence"].strip()


# --------------------------------------------------------------------------
# States and exit codes
# --------------------------------------------------------------------------


def test_unprofiled_is_first_class_with_full_observation(pieces, catalog):
    """Phase 1's normal operating mode, not an edge case.

    No profile can be applied until Task 12, so every real target is unprofiled.
    It must carry the full measurement and exit 2 — never conformant, never
    unsupported.
    """
    _, _, observation, assessment, policy, equivalences = pieces
    report = build_evidence(
        None, None, observation, assessment, policy,
        repo_root=REPO_ROOT, catalog_size=len(catalog), equivalence_id=equivalences.identity,
    )
    assert report.payload["state"] == STATE_UNPROFILED
    assert report.exit_code is ExitCode.NONCONFORMANT
    assert report.payload["budget"]["demand"] > 0
    assert report.payload["budget"]["limit"] > 0
    assert report.payload["resolved_members"] == []


def test_a_partial_report_can_never_be_conformant():
    """Enforced in code, not only in a test (spec Contract)."""
    with pytest.raises(ValueError, match="partial report cannot be conformant"):
        Evidence(payload={"state": STATE_CONFORMANT}, partial=True)


def test_partial_reports_exit_one_not_two():
    """1 is "could not finish"; 2 is "finished and not conformant"."""
    report = Evidence(payload={"state": STATE_UNSUPPORTED}, partial=True)
    assert report.exit_code is ExitCode.INCOMPLETE
    assert Evidence(payload={"state": STATE_CONFORMANT}).exit_code is ExitCode.CONFORMANT
    assert Evidence(payload={"state": "nonconformant"}).exit_code is ExitCode.NONCONFORMANT


def test_an_unverifiable_revision_is_unsupported(pieces, catalog, monkeypatch):
    """Content identity says what is there, not which reviewed revision it is."""
    monkeypatch.setattr(ev_mod, "canonical_revision", lambda root: None)
    report = evidence_for(pieces, catalog)
    assert report.payload["state"] == STATE_UNSUPPORTED


# --------------------------------------------------------------------------
# Dirty state, narrowly (EV-NEG-04)
# --------------------------------------------------------------------------


def test_only_changes_to_selected_paths_make_a_target_audit_only(tmp_path):
    """An unrelated working-tree edit must not block an otherwise valid run.

    Treating every dirty tree as audit-only would make the verifier unusable
    during ordinary work, which is how a gate ends up disabled.
    """
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "skills").mkdir()
    (tmp_path / "skills" / "diagnose").mkdir()
    (tmp_path / "skills" / "diagnose" / "SKILL.md").write_text("x")
    (tmp_path / "unrelated.md").write_text("y")

    # `git status --porcelain` alone collapses untracked directories to
    # `?? skills/`, so a wholly-new selected skill would never match its own
    # prefix and a dirty target would report clean. `-uall` is required.
    assert dirty_state(tmp_path, ("diagnose",)) == ["skills/diagnose/SKILL.md"]
    assert dirty_state(tmp_path, ("write-spec",)) == []


def test_git_being_unavailable_is_reported_rather_than_assumed_clean(tmp_path, monkeypatch):
    """Fail closed: an unverifiable source is audit-only, not silently fine."""
    def boom(*args, **kwargs):
        raise OSError("no git")
    monkeypatch.setattr(subprocess, "run", boom)
    assert dirty_state(tmp_path, ()) == ["<git unavailable: source revision unverifiable>"]


# --------------------------------------------------------------------------
# Legacy topologies (SC-09)
# --------------------------------------------------------------------------


def test_a_whole_catalog_link_is_reported_as_full_membership_not_an_implicit_full(pieces, catalog):
    """EV-LEG-01. Accepting it as `full` would launder an accident into a declaration.

    The count tracks the catalog rather than a literal, so authoring a skill
    cannot silently falsify the fixture — the defect spec revision 7 removed.
    """
    _, _, observation, _, _, _ = pieces
    managed = [e for e in observation.entries if e.origin == "dojo-managed"]
    found = detect_legacy_topologies(observation, catalog_size=len(managed))
    kinds = {f["kind"] for f in found}
    assert "whole-catalog-link" in kinds
    entry = next(f for f in found if f["kind"] == "whole-catalog-link")
    assert entry["member_count"] == len(managed)
    assert "full" not in kinds


def test_a_partial_installation_is_not_reported_as_a_whole_catalog_link(pieces, catalog):
    """The negative control for the detector above."""
    _, _, observation, _, _, _ = pieces
    found = detect_legacy_topologies(observation, catalog_size=len(catalog) * 10)
    assert "whole-catalog-link" not in {f["kind"] for f in found}


def test_serialization_is_key_order_independent():
    """Pins `sort_keys`, which two runs of one code path cannot exercise.

    A mutation setting `sort_keys=False` passed every other test in this file:
    the payload is built in a fixed order, so both runs agree regardless. The
    guarantee only matters if the payload is ever assembled in a data-dependent
    order — iterating a set, merging dicts from a scan — at which point unsorted
    keys make the bytes vary without any input changing. Constructing the same
    content in two orders is the only way to see it.
    """
    forward = Evidence(payload={"alpha": 1, "beta": [2, 3], "gamma": {"x": 1, "y": 2}})
    reverse = Evidence(payload={"gamma": {"y": 2, "x": 1}, "beta": [2, 3], "alpha": 1})
    assert forward.to_json() == reverse.to_json()
