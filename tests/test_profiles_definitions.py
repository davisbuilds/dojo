"""Task 1 — the reviewed profile definitions and the harness-equivalence file.

Three disciplines shape almost every assertion here, and each exists because
this program has already lost time to its absence:

* **No hardcoded totals.** `full` is asserted against
  `len(skills.json["skills"])` computed at test time, never against the literal
  48. Authoring a skill must not be able to falsify a test silently — and a test
  that pins the count is the same defect spec revision 7 removed from EV-LEG-01.
* **Every rejection asserts the message, not just the raise.** `pytest.raises`
  alone cannot tell "rejected for the right reason" from "rejected by accident",
  and these fixtures deliberately break one rule at a time inside otherwise
  valid data, where several rules could plausibly fire.
* **Contract constants are restated here from the spec**, not imported from
  `definitions`. Importing them would make a test that "checks SC-02" pass
  against any mutation of SC-02 — it would only be checking the module against
  itself.

Negative fixtures are built by copying the real `profiles/` directory and
breaking exactly one thing, so they cannot drift away from the shape of the real
data the way a hand-written minimal fixture does.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
PROFILES_DIR = REPO_ROOT / "profiles"
CATALOG_PATH = REPO_ROOT / "skills.json"
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from profiles import definitions  # noqa: E402
from profiles.definitions import ProfileDefinitionError  # noqa: E402

# --- Contract constants, quoted from the spec rather than imported. ---------

# SC-02: the public profile vocabulary.
SC02_VOCABULARY = {
    "core",
    "engineering",
    "research",
    "design",
    "knowledge",
    "shipping",
    "skill-authoring",
    "full",
}

# SC-03: `core` contains the general delivery loop.
SC03_CORE = {
    "brainstorming",
    "first-principles",
    "write-spec",
    "write-plan",
    "diagnose",
    "local-review",
    "test-strategy",
    "verify-before-complete",
}

# SC-02: required anchors, per overlay.
SC02_ANCHORS = {
    "engineering": {"create-cli", "secure-code"},
    "research": {"deep-research", "research-architect"},
    "design": {"design-critique", "web-design-guidelines"},
    "knowledge": {"obsidian-markdown", "session-retro"},
    "shipping": {"gh-commit-push-pr", "vercel-deploy"},
    "skill-authoring": {"skill-creator", "skill-standardizer"},
}

SC02_MIN_NON_CORE = 2


@pytest.fixture
def catalog() -> dict:
    return definitions.load_catalog(CATALOG_PATH)


@pytest.fixture
def profiles(catalog) -> dict:
    return definitions.load_definitions(PROFILES_DIR, catalog)


@pytest.fixture
def equivalences(catalog):
    return definitions.load_equivalences(PROFILES_DIR / "harness-equivalences.yaml", catalog)


@pytest.fixture
def workdir(tmp_path) -> Path:
    """A copy of the real profiles directory, for breaking one rule at a time."""
    target = tmp_path / "profiles"
    shutil.copytree(PROFILES_DIR, target)
    return target


def mutate(path: Path, **changes) -> None:
    """Rewrite one profile file with `changes` applied; `None` deletes a key."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    for key, value in changes.items():
        if value is None:
            data.pop(key, None)
        else:
            data[key] = value
    path.write_text(yaml.safe_dump(data, sort_keys=True), encoding="utf-8")


def mutate_equivalences(path: Path, entries: list[dict]) -> None:
    path.write_text(yaml.safe_dump({"version": 1, "equivalences": entries}, sort_keys=True), encoding="utf-8")


def load(workdir: Path, catalog: dict) -> dict:
    return definitions.load_definitions(workdir, catalog)


# ---------------------------------------------------------------------------
# The definitions as authored
# ---------------------------------------------------------------------------


def test_vocabulary_is_exactly_the_sc02_set(profiles):
    """Exhaustive in both directions: no extra profile, none missing.

    An extra file is the interesting half. A per-project fork or a stray copy
    dropped into this directory would otherwise enter the public vocabulary by
    being present, which SC-02 makes a contract revision rather than an edit.
    """
    assert set(profiles) == SC02_VOCABULARY
    assert list(profiles) == sorted(profiles), "definitions must be returned in lexical order"


def test_core_is_exactly_the_sc03_eight(profiles, catalog):
    assert set(definitions.resolved_members(profiles["core"], catalog)) == SC03_CORE


def test_every_overlay_carries_its_anchors_and_two_non_core_members(profiles, catalog):
    """SC-02's two membership rules, checked against the spec's own anchor table."""
    core = set(definitions.resolved_members(profiles["core"], catalog))
    for name, anchors in SC02_ANCHORS.items():
        members = set(definitions.resolved_members(profiles[name], catalog))
        assert anchors <= members, f"overlay {name} is missing anchor(s) {sorted(anchors - members)}"
        assert len(members - core) >= SC02_MIN_NON_CORE


def test_full_resolves_to_every_canonical_skill(profiles, catalog):
    """The count is computed here, never quoted.

    `full` must track the catalog, so the assertion reads `skills.json` at test
    time. A pinned member list in `full.yaml` would satisfy the count on the day
    it was written and quietly stop tracking; the sentinel assertion below is
    what rules that out.
    """
    expected = {s["name"] for s in json.loads(CATALOG_PATH.read_text())["skills"]}
    resolved = definitions.resolved_members(profiles["full"], catalog)
    assert set(resolved) == expected
    assert len(resolved) == len(json.loads(CATALOG_PATH.read_text())["skills"])
    assert profiles["full"].is_sentinel and profiles["full"].members == ()


def test_every_resolved_member_exists_in_the_catalog(profiles, catalog):
    for name, profile in profiles.items():
        for member in definitions.resolved_members(profile, catalog):
            assert member in catalog, f"{name} names {member}, absent from skills.json"


def test_overlay_coverage_of_the_catalog_is_deliberately_partial(profiles, catalog):
    """Restraint is a property of the data, so it is asserted rather than assumed.

    Overlays exist to fit a listing budget — roughly `core` plus one overlay at a
    200k Claude Code window — so full coverage of the catalog would be a defect,
    not completeness. Stated as a strict-subset relation rather than a size
    constant so that authoring a skill cannot break it.
    """
    covered = {m for name in SC02_ANCHORS for m in profiles[name].members}
    covered |= set(profiles["core"].members)
    assert covered < set(catalog), "every catalog skill is in a profile; overlays have stopped selecting"


def test_no_two_overlays_are_the_same_set(profiles):
    """Two overlays resolving identically would make the vocabulary a fiction."""
    sets = {name: frozenset(profiles[name].members) for name in SC02_ANCHORS}
    assert len(set(sets.values())) == len(sets)


# ---------------------------------------------------------------------------
# Rejection cases — plan step 5. Each asserts the message names the offender.
# ---------------------------------------------------------------------------


def test_rejects_unreadable_yaml(workdir, catalog):
    (workdir / "design.yaml").write_text("name: design\nmembers: [unclosed\n", encoding="utf-8")
    with pytest.raises(ProfileDefinitionError, match=r"design\.yaml.*not readable YAML"):
        load(workdir, catalog)


def test_rejects_duplicate_key_inside_one_file(workdir, catalog):
    """One file per profile makes a duplicate *definition* detectable.

    A repeated key inside a single file is the other half of the same failure and
    PyYAML's default is last-wins: the reviewed list above would be discarded in
    silence, and the file would still read as correct.
    """
    (workdir / "shipping.yaml").write_text(
        "name: shipping\nkind: overlay\ndescription: x\n"
        "members: [gh-commit-push-pr, vercel-deploy]\n"
        "members: [caveman]\n",
        encoding="utf-8",
    )
    with pytest.raises(ProfileDefinitionError, match=r"shipping\.yaml.*duplicate key 'members'"):
        load(workdir, catalog)


def test_rejects_missing_required_key(workdir, catalog):
    mutate(workdir / "research.yaml", members=None)
    with pytest.raises(ProfileDefinitionError, match=r"research\.yaml.*missing required key\(s\) members"):
        load(workdir, catalog)


def test_rejects_an_unrecognised_key(workdir, catalog):
    """A key the loader does not read is a silent no-op, which is the problem.

    `members_extra:` or a misspelled `member:` would sit in a reviewed file
    looking load-bearing while changing nothing — the reader would believe a
    membership rule that the verifier never applies.
    """
    mutate(workdir / "design.yaml", owner="design-team")
    with pytest.raises(ProfileDefinitionError, match=r"design\.yaml.*unknown key\(s\) owner"):
        load(workdir, catalog)


@pytest.mark.parametrize("members", [[], {}, "core"], ids=["empty-list", "mapping", "bare-string"])
def test_rejects_members_that_are_not_a_non_empty_list(workdir, catalog, members):
    """A zero-member profile must not resolve to "nothing selected, all fine".

    The bare-string case is the one that motivates this: `members: core` is
    plausible YAML, is not the sentinel, and would otherwise be iterated
    character by character into four one-letter member names.
    """
    mutate(workdir / "knowledge.yaml", members=members)
    with pytest.raises(ProfileDefinitionError, match=r"knowledge\.yaml.*'knowledge' declares no members"):
        load(workdir, catalog)


def test_rejects_unknown_kind(workdir, catalog):
    mutate(workdir / "knowledge.yaml", kind="capability")
    with pytest.raises(ProfileDefinitionError, match=r"knowledge\.yaml.*'knowledge'.*unknown kind 'capability'"):
        load(workdir, catalog)


def test_rejects_kind_that_contradicts_the_sc02_role(workdir, catalog):
    mutate(workdir / "core.yaml", kind="overlay")
    with pytest.raises(ProfileDefinitionError, match=r"core\.yaml.*'core'.*kind 'overlay'.*'baseline'"):
        load(workdir, catalog)


def test_rejects_two_files_declaring_the_same_name(workdir, catalog):
    """The plan's documented negative check: copy `core.yaml` and reload."""
    shutil.copy(workdir / "core.yaml", workdir / "core-copy.yaml")
    with pytest.raises(ProfileDefinitionError) as excinfo:
        load(workdir, catalog)
    message = str(excinfo.value)
    assert "duplicate profile definition 'core'" in message
    assert "core.yaml" in message and "core-copy.yaml" in message


def test_rejects_a_profile_outside_the_sc02_vocabulary(workdir, catalog):
    (workdir / "ops.yaml").write_text(
        "name: ops\nkind: overlay\ndescription: x\nmembers: [caveman, handoff]\n", encoding="utf-8"
    )
    with pytest.raises(ProfileDefinitionError, match=r"profile\(s\) ops are outside the SC-02 vocabulary"):
        load(workdir, catalog)


def test_rejects_a_missing_sc02_profile(workdir, catalog):
    (workdir / "design.yaml").unlink()
    with pytest.raises(ProfileDefinitionError, match=r"SC-02 profile\(s\) design have no definition file"):
        load(workdir, catalog)


def test_rejects_a_member_absent_from_the_catalog(workdir, catalog):
    mutate(workdir / "engineering.yaml", members=["create-cli", "secure-code", "no-such-skill"])
    with pytest.raises(ProfileDefinitionError, match=r"engineering\.yaml.*'engineering'.*no-such-skill"):
        load(workdir, catalog)


def test_rejects_an_overlay_with_fewer_than_two_non_core_members(workdir, catalog):
    """Reachable only because the count is checked before the anchors.

    Every anchor is itself a non-`core` skill, so an overlay holding both anchors
    can never fail this count. Were the anchor rule to run first, this rule could
    never fire on any input — a validation rule that cannot fire is
    indistinguishable from one that was never written.
    """
    mutate(workdir / "engineering.yaml", members=["create-cli"])
    with pytest.raises(ProfileDefinitionError, match=r"engineering\.yaml.*'engineering'.*at least 2"):
        load(workdir, catalog)


def test_rejects_an_overlay_missing_an_anchor(workdir, catalog):
    mutate(workdir / "engineering.yaml", members=["api-design", "repo-hardening", "secure-code"])
    with pytest.raises(ProfileDefinitionError, match=r"engineering\.yaml.*'engineering'.*anchor\(s\) create-cli"):
        load(workdir, catalog)


def test_rejects_full_declaring_a_pinned_list(workdir, catalog):
    mutate(workdir / "full.yaml", members=["brainstorming", "diagnose"])
    with pytest.raises(ProfileDefinitionError, match=r"full\.yaml.*'full' must declare members: '\*'"):
        load(workdir, catalog)


def test_rejects_the_sentinel_in_an_overlay(workdir, catalog):
    """The sentinel in an overlay is a whole-catalog widener wearing a small name."""
    mutate(workdir / "design.yaml", members="*")
    with pytest.raises(ProfileDefinitionError, match=r"design\.yaml.*'design' uses the whole-catalog sentinel"):
        load(workdir, catalog)


def test_rejects_a_duplicated_member_within_one_profile(workdir, catalog):
    mutate(workdir / "shipping.yaml", members=["gh-commit-push-pr", "vercel-deploy", "vercel-deploy"])
    with pytest.raises(ProfileDefinitionError, match=r"shipping\.yaml.*'shipping'.*vercel-deploy more than once"):
        load(workdir, catalog)


def test_rejects_an_empty_description(workdir, catalog):
    mutate(workdir / "research.yaml", description="   ")
    with pytest.raises(ProfileDefinitionError, match=r"research\.yaml.*'research'.*empty `description`"):
        load(workdir, catalog)


def test_rejects_an_empty_profiles_directory(tmp_path, catalog):
    empty = tmp_path / "profiles"
    empty.mkdir()
    with pytest.raises(ProfileDefinitionError, match="holds no profile definitions"):
        load(empty, catalog)


def test_rejects_an_empty_catalog(tmp_path):
    """Fail closed: an empty catalog would make every membership check vacuous."""
    path = tmp_path / "skills.json"
    path.write_text(json.dumps({"version": 1, "skills": []}), encoding="utf-8")
    with pytest.raises(ProfileDefinitionError, match="holds no skills"):
        definitions.load_catalog(path)


# ---------------------------------------------------------------------------
# Harness equivalences
# ---------------------------------------------------------------------------


def test_the_declaration_is_non_empty_and_names_real_skills(equivalences, catalog):
    """The zero rule. Every validation rule below passes trivially on an empty file.

    So the live declaration is pinned as non-degenerate first: it must actually
    declare pairs, and each must name a skill dojo ships, before any later
    conclusion drawn from "no equivalence declared" means anything.
    """
    assert equivalences.entries
    assert all(e.skill in catalog for e in equivalences.entries)
    assert all(e.bundled_entry and e.evidence for e in equivalences.entries)


def test_codex_bundles_skill_creator(equivalences):
    """The live case spec revision 9 was written from.

    dojo's `skill-creator` is charged to the Codex budget twice in every session
    today. If this declaration disappears, the duplication stops being visible.
    """
    codex = equivalences.for_harness("codex")
    assert "skill-creator" in codex
    assert codex["skill-creator"].bundled_entry
    assert "codex" in codex["skill-creator"].evidence.lower()


def test_a_suppressed_anchor_still_satisfies_sc02(profiles, equivalences):
    """SC-02: anchors constrain the definition, not the realization.

    `skill-creator` is both a required `skill-authoring` anchor and declared
    equivalent on Codex. The definition must still carry it; suppression happens
    at realization time and is not subtraction from the contract.
    """
    assert "skill-creator" in profiles["skill-authoring"].members
    assert "skill-creator" in equivalences.for_harness("codex")


def test_identity_is_computed_over_a_sorted_serialization(equivalences):
    """Probed directly, because `load_equivalences` sorts before hashing.

    Going only through the loader hides whether `equivalence_identity` normalizes
    at all — the mutation that removed its sort passed every end-to-end test.
    Two independent sorts is deliberate: the loader's fixes report order, this
    one fixes identity, and neither should depend on the other staying.
    """
    entries = equivalences.entries
    assert len(entries) > 1, "a single-entry declaration cannot exercise ordering"
    permuted = (entries[-1],) + entries[1:-1] + (entries[0],)
    assert permuted != entries
    assert definitions.equivalence_identity(permuted) == definitions.equivalence_identity(entries)


def test_identity_ignores_order_but_not_content(workdir, catalog, equivalences):
    """Identity feeds realization identity, so both halves matter.

    Reordering the file is a review-time accident with no semantic content and
    must not read as a new realization request; changing a declared pair or its
    evidence must.
    """
    path = workdir / "harness-equivalences.yaml"
    entries = [
        {"skill": e.skill, "harness": e.harness, "bundled_entry": e.bundled_entry, "evidence": e.evidence}
        for e in equivalences.entries
    ]
    mutate_equivalences(path, list(reversed(entries)))
    assert definitions.load_equivalences(path, catalog).identity == equivalences.identity

    entries[0] = {**entries[0], "evidence": entries[0]["evidence"] + " (re-observed)"}
    mutate_equivalences(path, entries)
    assert definitions.load_equivalences(path, catalog).identity != equivalences.identity


def test_rejects_an_unknown_harness(workdir, catalog):
    mutate_equivalences(
        workdir / "harness-equivalences.yaml",
        [{"skill": "skill-creator", "harness": "cursor", "bundled_entry": "x", "evidence": "y"}],
    )
    with pytest.raises(ProfileDefinitionError, match=r"'skill-creator'.*unknown harness 'cursor'"):
        definitions.load_equivalences(workdir / "harness-equivalences.yaml", catalog)


def test_rejects_an_equivalence_for_a_skill_dojo_does_not_ship(workdir, catalog):
    """Not a harmless no-op: it hides the collision it pretends to resolve."""
    mutate_equivalences(
        workdir / "harness-equivalences.yaml",
        [{"skill": "plugin-creator", "harness": "codex", "bundled_entry": "plugin-creator", "evidence": "y"}],
    )
    with pytest.raises(ProfileDefinitionError, match=r"'codex'.*'plugin-creator'.*absent from the canonical catalog"):
        definitions.load_equivalences(workdir / "harness-equivalences.yaml", catalog)


@pytest.mark.parametrize("field", ["bundled_entry", "evidence"])
def test_rejects_a_declaration_missing_its_evidence_or_entry(workdir, catalog, field):
    """A claim nobody can re-check is not evidence, and this file is a claim."""
    entry = {"skill": "skill-creator", "harness": "codex", "bundled_entry": "skill-creator", "evidence": "seen"}
    entry[field] = "  "
    mutate_equivalences(workdir / "harness-equivalences.yaml", [entry])
    with pytest.raises(ProfileDefinitionError, match=rf"'skill-creator'.*'codex'.*missing {field}"):
        definitions.load_equivalences(workdir / "harness-equivalences.yaml", catalog)


def test_rejects_a_duplicate_skill_harness_pair(workdir, catalog):
    entry = {"skill": "skill-creator", "harness": "codex", "bundled_entry": "skill-creator", "evidence": "seen"}
    mutate_equivalences(workdir / "harness-equivalences.yaml", [entry, {**entry, "evidence": "seen again"}])
    with pytest.raises(ProfileDefinitionError, match=r"duplicate equivalence for \('skill-creator', 'codex'\)"):
        definitions.load_equivalences(workdir / "harness-equivalences.yaml", catalog)


def test_rejects_a_skill_declared_equivalent_on_every_harness(workdir, catalog):
    """EV-NEG-06: that resolves to an empty realization, which is a definition error."""
    entry = {"skill": "skill-creator", "harness": "codex", "bundled_entry": "skill-creator", "evidence": "seen"}
    mutate_equivalences(
        workdir / "harness-equivalences.yaml",
        [entry, {**entry, "harness": "claude-code", "evidence": "also seen"}],
    )
    with pytest.raises(ProfileDefinitionError, match=r"'skill-creator' is declared equivalent on every supported"):
        definitions.load_equivalences(workdir / "harness-equivalences.yaml", catalog)


def test_for_harness_rejects_an_unknown_harness(equivalences):
    with pytest.raises(ProfileDefinitionError, match="unknown harness 'cursor'"):
        equivalences.for_harness("cursor")


def test_for_harness_is_empty_for_claude_code_today(equivalences):
    """Claude Code bundles `doctor`, `artifact-design`, `artifact-capabilities`.

    None exists in skills.json, so an empty result is the correct answer rather
    than a gap — and the non-degeneracy test above is what makes this empty read
    trustworthy instead of a silent instrument failure.
    """
    assert equivalences.for_harness("claude-code") == {}


def test_rejects_a_core_that_is_not_exactly_the_sc03_set(workdir, catalog):
    """PR #58 review, P2. The library accepted a two-member `core`.

    A repo test already asserted `core.yaml`'s contents, but that protects this
    checkout only — `load_definitions` is what a runtime consumer calls against
    whatever is on disk, and it would have proceeded with a baseline missing the
    delivery safeguards every deployable composition is promised. SC-02's
    anchors were enforced in code from the start; SC-03's `core` is the same
    kind of contract constant and is more load-bearing, so the asymmetry was the
    defect.

    Both directions are checked, and the message must name what moved: a
    narrowed baseline and a widened one fail differently and a reader needs to
    know which.
    """
    core_path = workdir / "core.yaml"
    original = yaml.safe_load(core_path.read_text())

    for members, needle in (
        (["brainstorming", "write-spec"], "missing diagnose"),
        (sorted(SC03_CORE) + ["caveman"], "unexpected caveman"),
    ):
        core_path.write_text(yaml.safe_dump({**original, "members": members}))
        with pytest.raises(ProfileDefinitionError) as excinfo:
            definitions.load_definitions(workdir, catalog)
        assert "must be exactly the SC-03 set" in str(excinfo.value)
        assert needle in str(excinfo.value)


def test_the_enforced_core_matches_the_contract_restated_here(profiles):
    """Positive control, and a cross-check of the constant against the spec.

    Without this the rule above could pass by rejecting every input rather than
    by discriminating. `SC03_CORE` is restated independently at the top of this
    file, so editing the constant in `definitions.py` alone fails here.
    """
    assert set(definitions.CORE_MEMBERS) == SC03_CORE
    assert set(profiles["core"].members) == SC03_CORE
