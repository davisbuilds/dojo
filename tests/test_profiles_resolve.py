"""Task 2 — resolution, the two identities, and selection validation.

The tests that matter most here are the ones proving *what is not an input*.
Profile identity must not move when a harness suppresses a member, and
realization identity must move when anything about what-landed changes. Getting
either backwards produces a system that reads every legitimate suppression as
drift, or one that replays a stale request as idempotent.

Discipline, as elsewhere in this package: no hardcoded catalog totals, every
rejection asserts its own error *code* rather than merely that something raised,
and each detector is exercised against a case known to be present.
"""

from __future__ import annotations

import itertools
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
PROFILES_DIR = REPO_ROOT / "profiles"
CATALOG_PATH = REPO_ROOT / "skills.json"
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from profiles import definitions, resolve as resolve_mod  # noqa: E402
from profiles.definitions import ProfileDefinitionError  # noqa: E402
from profiles.resolve import (  # noqa: E402
    SelectionError,
    SelectionErrorCode,
    profile_identity,
    realization_identity,
    resolve,
    resolve_for_harness,
)

OVERLAYS = ("design", "engineering", "knowledge", "research", "shipping", "skill-authoring")


@pytest.fixture
def catalog() -> dict:
    return definitions.load_catalog(CATALOG_PATH)


@pytest.fixture
def defs(catalog) -> dict:
    return definitions.load_definitions(PROFILES_DIR, catalog)


@pytest.fixture
def equivalences(catalog):
    return definitions.load_equivalences(PROFILES_DIR / "harness-equivalences.yaml", catalog)


# --------------------------------------------------------------------------
# Composition
# --------------------------------------------------------------------------


def test_all_720_permutations_resolve_identically(defs, catalog):
    """EV-CON-02, at full strength.

    Six overlays give 720 orderings. A sample would not satisfy this: order
    dependence is exactly the kind of bug that hides in whichever orderings a
    sample happens to miss.
    """
    results = {
        (r.members, r.identity)
        for r in (
            resolve(("core", *perm), defs, catalog) for perm in itertools.permutations(OVERLAYS)
        )
    }
    assert len(results) == 1


def test_composition_is_set_union_and_collapses_overlap(defs, catalog):
    """The explicit non-error case: overlays may share members.

    Asserted with a constructed overlapping pair so the *accept* path is
    exercised. A module that rejected all overlap would pass every rejection
    test in this file.
    """
    shared = "verify-before-complete"
    a = definitions.Profile(
        name="engineering", kind="overlay", description="x",
        members=("create-cli", "secure-code", shared), source=Path("a.yaml"), is_sentinel=False,
    )
    b = definitions.Profile(
        name="research", kind="overlay", description="x",
        members=("deep-research", "research-architect", shared), source=Path("b.yaml"), is_sentinel=False,
    )
    patched = {**defs, "engineering": a, "research": b}
    result = resolve(("core", "engineering", "research"), patched, catalog)
    assert result.members.count(shared) == 1
    assert {"create-cli", "deep-research"} <= set(result.members)


def test_full_tracks_the_catalog_rather_than_a_list(defs, catalog):
    """`full` expands at resolve time, so authoring a skill cannot falsify it."""
    result = resolve(("full",), defs, catalog)
    assert set(result.members) == set(catalog)
    assert len(result.members) == len(catalog)


# --------------------------------------------------------------------------
# Rejections — each with its own code
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "selection, code",
    [
        (("core", "nonexistent"), SelectionErrorCode.UNKNOWN_PROFILE),
        (("engineering",), SelectionErrorCode.MISSING_CORE),
        (("core",), SelectionErrorCode.NO_OVERLAY),
        (("core", "engineering", "engineering"), SelectionErrorCode.REPEATED_TOKEN),
        (("full", "engineering"), SelectionErrorCode.FULL_NOT_EXCLUSIVE),
    ],
)
def test_each_rejection_carries_its_own_code(defs, catalog, selection, code):
    """EV-NEG-01. Distinct codes, asserted individually.

    A shared code would make "refused for the right reason" and "refused by
    accident" indistinguishable to any caller.
    """
    with pytest.raises(SelectionError) as excinfo:
        resolve(selection, defs, catalog)
    assert excinfo.value.code is code
    assert code.value in str(excinfo.value)


def test_the_five_codes_are_actually_distinct():
    """Guards the parametrisation above: five aliases of one value would pass it."""
    codes = [
        SelectionErrorCode.UNKNOWN_PROFILE,
        SelectionErrorCode.MISSING_CORE,
        SelectionErrorCode.NO_OVERLAY,
        SelectionErrorCode.REPEATED_TOKEN,
        SelectionErrorCode.FULL_NOT_EXCLUSIVE,
    ]
    assert len({c.value for c in codes}) == len(codes)


# --------------------------------------------------------------------------
# Identity: what is, and is not, an input
# --------------------------------------------------------------------------


def test_profile_identity_ignores_selection_order(defs):
    assert profile_identity(("core", "research"), defs) == profile_identity(("research", "core"), defs)


def test_profile_identity_moves_when_a_definition_body_changes(defs):
    """Membership of a *definition* is intent, so editing it is a new profile."""
    before = profile_identity(("core", "research"), defs)
    widened = definitions.Profile(
        name="research", kind="overlay", description="x",
        members=(*defs["research"].members, "fetchmd", "caveman"),
        source=Path("r.yaml"), is_sentinel=False,
    )
    after = profile_identity(("core", "research"), {**defs, "research": widened})
    assert before != after


def test_one_profile_identity_two_harnesses_different_realizations(defs, catalog, equivalences):
    """EV-NEG-06 and SC-11, the central case of spec revision 9.

    Codex bundles `skill-creator`; Claude Code does not. The reviewed selection
    is the same on both, so profile identity must be byte-identical — otherwise
    a cross-machine comparison reads a correct suppression as drift. What landed
    differs, so realization identity must not be.
    """
    result = resolve(("core", "skill-authoring"), defs, catalog)

    codex = resolve_for_harness(result, equivalences.for_harness("codex"), "codex")
    claude = resolve_for_harness(result, equivalences.for_harness("claude-code"), "claude-code")

    assert "skill-creator" not in codex.realized
    assert "skill-creator" in claude.realized

    suppressed = {s.skill: s for s in codex.suppressed}
    assert "skill-creator" in suppressed
    assert suppressed["skill-creator"].bundled_entry
    assert suppressed["skill-creator"].evidence.strip()

    common = dict(
        canonical_revision="rev1", target_identity="t", budget_policy_identity="p",
        equivalence_identity=equivalences.identity,
    )
    codex_id = realization_identity(result.identity, harness_model_version="codex@1", **common)
    claude_id = realization_identity(result.identity, harness_model_version="claude@1", **common)
    assert codex_id != claude_id


def test_suppression_does_not_reach_profile_identity(defs, catalog, equivalences):
    """The property the previous test depends on, isolated.

    If resolved membership ever became an input to profile identity, the two
    harnesses above would hash differently and SC-11 would report drift for a
    correct resolution.
    """
    result = resolve(("core", "skill-authoring"), defs, catalog)
    codex = resolve_for_harness(result, equivalences.for_harness("codex"), "codex")
    assert codex.realized != result.members, "fixture no longer exercises suppression"
    assert profile_identity(result.selection, defs) == result.identity


@pytest.mark.parametrize(
    "field",
    ["canonical_revision", "target_identity", "harness_model_version",
     "budget_policy_identity", "equivalence_identity"],
)
def test_every_realization_field_changes_realization_identity(field):
    """A stale request must never replay as idempotent (spec Authority)."""
    base = dict(
        profile_id="p", canonical_revision="rev1", target_identity="t",
        harness_model_version="h", budget_policy_identity="b", equivalence_identity="e",
    )
    assert realization_identity(**base) != realization_identity(**{**base, field: "changed"})


def test_canonical_revision_moves_realization_but_not_profile_identity(defs, catalog):
    result = resolve(("core", "research"), defs, catalog)
    common = dict(
        profile_id=result.identity, target_identity="t", harness_model_version="h",
        budget_policy_identity="b", equivalence_identity="e",
    )
    assert realization_identity(canonical_revision="a", **common) != realization_identity(
        canonical_revision="b", **common
    )
    assert resolve(("core", "research"), defs, catalog).identity == result.identity


# --------------------------------------------------------------------------
# Suppression is declared, never inferred
# --------------------------------------------------------------------------


def test_an_undeclared_collision_is_reported_and_the_member_survives(defs, catalog, equivalences):
    """The failure this design exists to prevent.

    A name match with no declaration must be *reported*, not acted on. Silently
    suppressing would remove a skill the maintainer selected, and nothing would
    say so — the asymmetry the spec calls out: a duplicate is visible, a missing
    skill is not.
    """
    result = resolve(("core", "research"), defs, catalog)
    collided = "deep-research"
    assert collided in result.members

    hr = resolve_for_harness(
        result, equivalences.for_harness("codex"), "codex", bundled_entries=[collided]
    )
    assert collided in hr.realized
    assert [c.skill for c in hr.collisions] == [collided]
    assert collided not in {s.skill for s in hr.suppressed}


def test_a_declared_equivalence_suppresses_without_needing_a_name_match(defs, catalog):
    """Suppression follows the declaration, not the listing.

    Task 0 found `review-agent` present on disk and in no listing; the converse
    holds too — a declaration is what removes a member, and the bundled entry's
    name need not equal the member's.
    """
    result = resolve(("core", "research"), defs, catalog)
    declared = {
        "deep-research": definitions.Equivalence(
            skill="deep-research", harness="codex",
            bundled_entry="totally-different-name", evidence="constructed",
        )
    }
    hr = resolve_for_harness(result, declared, "codex")
    assert "deep-research" not in hr.realized
    assert hr.suppressed[0].bundled_entry == "totally-different-name"
    assert hr.collisions == ()


def test_an_unknown_harness_is_refused_rather_than_resolved(defs, catalog):
    result = resolve(("core", "research"), defs, catalog)
    with pytest.raises(SelectionError) as excinfo:
        resolve_for_harness(result, {}, "emacs")
    assert excinfo.value.code is SelectionErrorCode.UNKNOWN_PROFILE


def test_a_member_equivalent_on_every_harness_is_rejected_at_load(tmp_path, catalog):
    """EV-NEG-06's definition-error case, enforced before resolution.

    Resolution never sees this: a member suppressed everywhere resolves to a
    realization that can never contain it, which is a broken declaration rather
    than a valid outcome. Asserted here so the guarantee is pinned from the
    consumer's side too — Task 2 relies on it and would otherwise silently
    produce the empty case.
    """
    src = PROFILES_DIR / "harness-equivalences.yaml"
    data = yaml.safe_load(src.read_text())
    everywhere = [
        {"skill": "skill-standardizer", "harness": h, "bundled_entry": "x", "evidence": "constructed"}
        for h in definitions.SUPPORTED_HARNESSES
    ]
    path = tmp_path / "harness-equivalences.yaml"
    path.write_text(yaml.safe_dump({**data, "equivalences": everywhere}))

    with pytest.raises(ProfileDefinitionError) as excinfo:
        definitions.load_equivalences(path, catalog)
    assert "skill-standardizer" in str(excinfo.value)
