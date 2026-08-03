#!/usr/bin/env python3
"""Load and validate the profile definitions and the harness-equivalence file.

This module answers two questions and deliberately not a third. It answers *what
does the reviewed data say* and *is it internally consistent against the
canonical catalog*. It does **not** compose a selection into a realization — that
is `resolve.py` — so nothing here takes a harness, a target, or a budget.

Everything fails closed. There is no path through this module that turns an
ambiguous definition into a plausible default: the whole point of the contract
is that absence from a profile is intentional exclusion (SC-01), and a loader
that repairs a broken definition destroys exactly that distinction.

Three rules are worth reading before changing anything:

1. **Duplicate YAML keys are an error, not last-wins.** One file per profile
   already makes a duplicate *definition* detectable; a repeated `members:` key
   inside one file would otherwise silently discard the reviewed list above it.
2. **`full` holds a sentinel, never a pinned list.** A pinned list goes stale the
   moment anyone authors a skill, which is the defect spec revision 7 removed
   from EV-LEG-01. `resolved_members` expands it against `skills.json` at call
   time.
3. **The non-`core` count is checked before the anchors.** Both rules come from
   SC-02, but every anchor is itself a non-`core` skill, so an overlay carrying
   its anchors can never fail the count. Checking anchors first would make the
   count rule unreachable and therefore untestable — a validation rule that
   cannot fire is indistinguishable from one that is missing.

Contract: docs/specs/2026-07-27-distribution-profiles-spec.md (SC-01, SC-02,
SC-03, SC-11). Build sequence: docs/plans/2026-07-31-distribution-profiles-plan.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

# SC-02 fixes the public vocabulary. It is a contract term, so an unrecognised
# profile file is rejected rather than loaded: a stray copy, a rename, or a
# per-project fork (excluded by the spec's Assumptions) would otherwise enter the
# vocabulary by being dropped in a directory.
BASELINE = "core"
INSPECTION = "full"
OVERLAYS = ("design", "engineering", "knowledge", "research", "shipping", "skill-authoring")
VOCABULARY = frozenset({BASELINE, INSPECTION, *OVERLAYS})

# name -> kind. A file naming itself `core` with `kind: overlay` is a definition
# error and not a synonym; kind drives resolution rules in Task 2.
KIND_BY_NAME = {BASELINE: "baseline", INSPECTION: "inspection", **{o: "overlay" for o in OVERLAYS}}
KINDS = frozenset(KIND_BY_NAME.values())

# SC-02's required anchors, verbatim. Anchors constrain the *definition*; a
# realization may still suppress one on a harness that ships its own equivalent.
ANCHORS = {
    "design": ("design-critique", "web-design-guidelines"),
    "engineering": ("create-cli", "secure-code"),
    "knowledge": ("obsidian-markdown", "session-retro"),
    "research": ("deep-research", "research-architect"),
    "shipping": ("gh-commit-push-pr", "vercel-deploy"),
    "skill-authoring": ("skill-creator", "skill-standardizer"),
}

MIN_NON_CORE_MEMBERS = 2
SENTINEL = "*"
REQUIRED_PROFILE_KEYS = ("name", "kind", "description", "members")
EQUIVALENCE_FILENAME = "harness-equivalences.yaml"
REQUIRED_EQUIVALENCE_KEYS = ("skill", "harness", "bundled_entry", "evidence")

# The harnesses a realization can be produced for. Used only to reject an unknown
# harness and to catch a member declared equivalent *everywhere*, which resolves
# to an empty realization and is a definition error rather than a resolution
# (spec Evaluation, EV-NEG-06).
SUPPORTED_HARNESSES = ("claude-code", "codex")


class ProfileDefinitionError(ValueError):
    """Raised for any invalid definition. Messages name the offending file and member.

    Callers distinguish causes by reading the message, so every raise below states
    the profile or `(skill, harness)` pair at fault. A bare "invalid profile" is
    useless in a verifier whose entire job is to say *what* is wrong.
    """


class _NoDuplicateKeyLoader(yaml.SafeLoader):
    """SafeLoader that refuses duplicate mapping keys instead of taking the last."""


def _no_duplicate_keys(loader: _NoDuplicateKeyLoader, node: yaml.MappingNode) -> dict:
    seen: set = set()
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=True)
        if key in seen:
            raise ProfileDefinitionError(f"duplicate key {key!r} in mapping at line {key_node.start_mark.line + 1}")
        seen.add(key)
    return yaml.SafeLoader.construct_mapping(loader, node, deep=True)


_NoDuplicateKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _no_duplicate_keys)


def _load_yaml(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ProfileDefinitionError(f"{path.name}: cannot be read ({exc})") from exc
    try:
        data = yaml.load(text, Loader=_NoDuplicateKeyLoader)
    except ProfileDefinitionError as exc:
        raise ProfileDefinitionError(f"{path.name}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ProfileDefinitionError(f"{path.name}: is not readable YAML ({exc})") from exc
    if not isinstance(data, dict):
        raise ProfileDefinitionError(f"{path.name}: must be a YAML mapping, got {type(data).__name__}")
    return data


@dataclass(frozen=True)
class Profile:
    """One reviewed profile definition.

    `members` is empty for the `full` sentinel. Read membership through
    `resolved_members`, which expands the sentinel against the live catalog; a
    caller reading `.members` directly would see `full` as empty and report a
    zero-member profile as conformant.
    """

    name: str
    kind: str
    description: str
    members: tuple[str, ...]
    is_sentinel: bool
    source: Path


def load_catalog(path: Path | str) -> dict[str, dict]:
    """Read `skills.json` into `{name: entry}`.

    The manifest is the runtime inventory source of truth (CLAUDE.md), so
    membership is validated against it rather than against a directory listing:
    the two can disagree, and `skills.json` is what the harnesses' generators and
    hooks read.
    """
    path = Path(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProfileDefinitionError(f"cannot read canonical catalog {path}: {exc}") from exc
    skills = data.get("skills")
    if not isinstance(skills, list) or not skills:
        raise ProfileDefinitionError(f"{path}: holds no skills; refusing to validate membership against an empty catalog")
    catalog = {}
    for entry in skills:
        name = entry.get("name")
        if not name:
            raise ProfileDefinitionError(f"{path}: catalog entry without a name: {entry!r}")
        if name in catalog:
            raise ProfileDefinitionError(f"{path}: duplicate catalog entry {name!r}")
        catalog[name] = entry
    return catalog


def _parse_profile(path: Path) -> Profile:
    """Per-file rules: required keys, known kind, sentinel discipline, duplicates."""
    data = _load_yaml(path)

    missing = [k for k in REQUIRED_PROFILE_KEYS if k not in data]
    if missing:
        raise ProfileDefinitionError(f"{path.name}: missing required key(s) {', '.join(sorted(missing))}")
    unknown = sorted(set(data) - set(REQUIRED_PROFILE_KEYS))
    if unknown:
        raise ProfileDefinitionError(f"{path.name}: unknown key(s) {', '.join(unknown)}")

    name, kind, description, raw_members = (data[k] for k in REQUIRED_PROFILE_KEYS)

    if not isinstance(name, str) or not name.strip():
        raise ProfileDefinitionError(f"{path.name}: `name` must be a non-empty string")
    if kind not in KINDS:
        raise ProfileDefinitionError(
            f"{path.name}: profile {name!r} declares unknown kind {kind!r}; expected one of {', '.join(sorted(KINDS))}"
        )
    if not isinstance(description, str) or not description.strip():
        raise ProfileDefinitionError(
            f"{path.name}: profile {name!r} has an empty `description`; these files are reviewed data "
            "and a definition that does not say why it exists cannot be challenged"
        )

    # The sentinel is the inspection profile's whole point and nothing else's.
    # An overlay carrying `"*"` would resolve to the entire catalog while looking
    # like a small overlay in review — the widening this contract exists to stop.
    if raw_members == SENTINEL:
        if name != INSPECTION:
            raise ProfileDefinitionError(
                f"{path.name}: profile {name!r} uses the whole-catalog sentinel {SENTINEL!r}; "
                f"only {INSPECTION!r} may"
            )
        return Profile(name, kind, description, (), True, path)
    if name == INSPECTION:
        raise ProfileDefinitionError(
            f"{path.name}: profile {INSPECTION!r} must declare members: {SENTINEL!r}, not a pinned list; "
            "a pinned list goes stale the moment a skill is authored"
        )

    if not isinstance(raw_members, list) or not raw_members:
        raise ProfileDefinitionError(
            f"{path.name}: profile {name!r} declares no members; expected a non-empty list of "
            f"canonical skill names, got {type(raw_members).__name__}"
        )
    if not all(isinstance(m, str) and m.strip() for m in raw_members):
        raise ProfileDefinitionError(f"{path.name}: profile {name!r} has a non-string member entry")
    duplicates = sorted({m for m in raw_members if raw_members.count(m) > 1})
    if duplicates:
        raise ProfileDefinitionError(
            f"{path.name}: profile {name!r} lists member(s) {', '.join(duplicates)} more than once"
        )
    return Profile(name, kind, description, tuple(sorted(raw_members)), False, path)


def load_definitions(profiles_dir: Path | str, catalog: dict[str, dict] | None = None) -> dict[str, Profile]:
    """Load every profile definition, validated against the canonical catalog.

    Returns `{name: Profile}` in lexical name order. `catalog` defaults to the
    `skills.json` beside `profiles_dir`, so the documented one-argument call in
    the plan works, but tests pass an explicit catalog to stay hermetic.
    """
    profiles_dir = Path(profiles_dir)
    if catalog is None:
        catalog = load_catalog(profiles_dir.parent / "skills.json")

    paths = sorted(p for p in profiles_dir.glob("*.yaml") if p.name != EQUIVALENCE_FILENAME)
    if not paths:
        raise ProfileDefinitionError(f"{profiles_dir}: holds no profile definitions")

    by_name: dict[str, Profile] = {}
    for path in paths:
        profile = _parse_profile(path)
        if profile.name in by_name:
            raise ProfileDefinitionError(
                f"duplicate profile definition {profile.name!r}: declared in "
                f"{by_name[profile.name].source.name} and {path.name}"
            )
        by_name[profile.name] = profile

    _validate_vocabulary(by_name, profiles_dir)
    for name in sorted(by_name):
        _validate_membership(by_name[name], by_name[BASELINE], catalog)
    return {name: by_name[name] for name in sorted(by_name)}


def _validate_vocabulary(by_name: dict[str, Profile], profiles_dir: Path) -> None:
    """SC-02's vocabulary is exhaustive in both directions."""
    unknown = sorted(set(by_name) - VOCABULARY)
    if unknown:
        raise ProfileDefinitionError(
            f"{profiles_dir}: profile(s) {', '.join(unknown)} are outside the SC-02 vocabulary "
            f"({', '.join(sorted(VOCABULARY))}); adding one is a contract revision"
        )
    absent = sorted(VOCABULARY - set(by_name))
    if absent:
        raise ProfileDefinitionError(
            f"{profiles_dir}: SC-02 profile(s) {', '.join(absent)} have no definition file"
        )
    for name, profile in sorted(by_name.items()):
        if profile.kind != KIND_BY_NAME[name]:
            raise ProfileDefinitionError(
                f"{profile.source.name}: profile {name!r} declares kind {profile.kind!r}, "
                f"but SC-02 makes it {KIND_BY_NAME[name]!r}"
            )


def _validate_membership(profile: Profile, core: Profile, catalog: dict[str, dict]) -> None:
    """Cross-file rules: members exist, overlays are non-trivial and anchored."""
    unknown = [m for m in profile.members if m not in catalog]
    if unknown:
        raise ProfileDefinitionError(
            f"{profile.source.name}: profile {profile.name!r} names member(s) "
            f"{', '.join(sorted(unknown))} absent from the canonical catalog"
        )
    if profile.kind != "overlay":
        return

    # Order matters — see the module docstring. Every anchor is non-`core`, so
    # running the anchor check first would make this one unreachable.
    non_core = sorted(set(profile.members) - set(core.members))
    if len(non_core) < MIN_NON_CORE_MEMBERS:
        raise ProfileDefinitionError(
            f"{profile.source.name}: overlay {profile.name!r} adds {len(non_core)} non-{BASELINE!r} "
            f"member(s) ({', '.join(non_core) or 'none'}); SC-02 requires at least {MIN_NON_CORE_MEMBERS}"
        )
    missing_anchors = [a for a in ANCHORS[profile.name] if a not in profile.members]
    if missing_anchors:
        raise ProfileDefinitionError(
            f"{profile.source.name}: overlay {profile.name!r} is missing required SC-02 anchor(s) "
            f"{', '.join(sorted(missing_anchors))}"
        )


def resolved_members(profile: Profile, catalog: dict[str, dict]) -> tuple[str, ...]:
    """Membership after sentinel expansion, lexically ordered.

    `full` tracks the catalog rather than a list, so this is the only correct way
    to ask what a profile contains.
    """
    if profile.is_sentinel:
        return tuple(sorted(catalog))
    return profile.members


@dataclass(frozen=True)
class Equivalence:
    """One declared `(skill, harness)` equivalence, with its evidence."""

    skill: str
    harness: str
    bundled_entry: str
    evidence: str


@dataclass(frozen=True)
class Equivalences:
    """The whole declaration plus its identity.

    `identity` is a SHA-256 over the canonical serialization. It feeds
    *realization* identity, never profile identity: a change here changes what
    lands on a harness, not what the maintainer asked for (spec revision 9).
    """

    entries: tuple[Equivalence, ...]
    identity: str
    source: Path

    def for_harness(self, harness: str) -> dict[str, Equivalence]:
        """`{skill: Equivalence}` for one harness — what Task 2 suppresses."""
        if harness not in SUPPORTED_HARNESSES:
            raise ProfileDefinitionError(
                f"unknown harness {harness!r}; supported: {', '.join(SUPPORTED_HARNESSES)}"
            )
        return {e.skill: e for e in self.entries if e.harness == harness}


def equivalence_identity(entries: tuple[Equivalence, ...]) -> str:
    """SHA-256 over a canonical, order-independent serialization.

    Sorted and separator-pinned so that reordering the file — a review-time
    accident with no semantic content — does not read as a new realization
    request, while any change to a declared pair or its evidence does.
    """
    payload = sorted(
        [e.harness, e.skill, e.bundled_entry, " ".join(e.evidence.split())] for e in entries
    )
    blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def load_equivalences(path: Path | str, catalog: dict[str, dict]) -> Equivalences:
    """Load and validate `harness-equivalences.yaml`.

    Every rule here protects the same failure: an equivalence silently removes a
    skill the maintainer selected, so a declaration that cannot be checked, or
    that would empty a member from every harness, is rejected rather than applied.
    """
    path = Path(path)
    data = _load_yaml(path)

    raw = data.get("equivalences")
    if raw is None or not isinstance(raw, list):
        raise ProfileDefinitionError(f"{path.name}: must declare a list under `equivalences`")

    entries: list[Equivalence] = []
    seen: set[tuple[str, str]] = set()
    for item in raw:
        if not isinstance(item, dict):
            raise ProfileDefinitionError(f"{path.name}: equivalence entries must be mappings, got {item!r}")
        missing = [k for k in REQUIRED_EQUIVALENCE_KEYS if not str(item.get(k, "")).strip()]
        if missing:
            raise ProfileDefinitionError(
                f"{path.name}: equivalence for skill {item.get('skill', '<unnamed>')!r} on harness "
                f"{item.get('harness', '<unnamed>')!r} is missing {', '.join(sorted(missing))}"
            )
        skill, harness = item["skill"], item["harness"]
        if harness not in SUPPORTED_HARNESSES:
            raise ProfileDefinitionError(
                f"{path.name}: equivalence for skill {skill!r} names unknown harness {harness!r}; "
                f"supported: {', '.join(SUPPORTED_HARNESSES)}"
            )
        if skill not in catalog:
            raise ProfileDefinitionError(
                f"{path.name}: equivalence on harness {harness!r} names skill {skill!r}, which is absent "
                "from the canonical catalog; declaring one for a skill dojo does not ship hides a future "
                "collision rather than resolving one"
            )
        if (skill, harness) in seen:
            raise ProfileDefinitionError(
                f"{path.name}: duplicate equivalence for ({skill!r}, {harness!r})"
            )
        seen.add((skill, harness))
        entries.append(Equivalence(skill, harness, item["bundled_entry"], item["evidence"]))

    for skill in sorted({e.skill for e in entries}):
        declared = {e.harness for e in entries if e.skill == skill}
        if declared >= set(SUPPORTED_HARNESSES):
            raise ProfileDefinitionError(
                f"{path.name}: skill {skill!r} is declared equivalent on every supported harness "
                f"({', '.join(sorted(declared))}), which resolves to an empty realization everywhere; "
                "that is a profile-definition error, not a resolution"
            )

    ordered = tuple(sorted(entries, key=lambda e: (e.harness, e.skill)))
    return Equivalences(ordered, equivalence_identity(ordered), path)


def main(argv: list[str] | None = None) -> int:
    repo_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Validate and print the profile definitions.")
    parser.add_argument("--profiles-dir", default=str(repo_root / "profiles"))
    parser.add_argument("--catalog", default=str(repo_root / "skills.json"))
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args(argv)

    catalog = load_catalog(args.catalog)
    profiles = load_definitions(args.profiles_dir, catalog)
    equivalences = load_equivalences(Path(args.profiles_dir) / EQUIVALENCE_FILENAME, catalog)

    if args.json:
        json.dump(
            {
                "profiles": {
                    name: {
                        "kind": p.kind,
                        "members": list(resolved_members(p, catalog)),
                        "sentinel": p.is_sentinel,
                    }
                    for name, p in profiles.items()
                },
                "equivalence_identity": equivalences.identity,
                "equivalences": [
                    {"skill": e.skill, "harness": e.harness, "bundled_entry": e.bundled_entry}
                    for e in equivalences.entries
                ],
            },
            sys.stdout,
            indent=2,
            sort_keys=True,
        )
        sys.stdout.write("\n")
    else:
        for name, profile in profiles.items():
            members = resolved_members(profile, catalog)
            print(f"{name:16s} {profile.kind:11s} {len(members):3d} members")
            print(f"                 {', '.join(members)}")
        print(f"\nequivalence identity: {equivalences.identity}")
        for entry in equivalences.entries:
            print(f"  {entry.harness}: {entry.skill} -> {entry.bundled_entry}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
