#!/usr/bin/env python3
"""Enumerate what a target actually exposes — from the probe, not the filesystem.

One rule governs this module and it has been violated six times in this program
by four different authors: **the filesystem never adds an entry the probe did not
list.** Files on disk, packages installed, entries cached — none of them are what
a harness sends to the model. The probe decides membership; the filesystem only
attaches content identity, topology, and source descriptions to entries the probe
already reported.

Two live cases keep it honest. `microsoft-foundry` is installed and disabled, so
it is on disk and in no listing. `review-agent` ships inside Codex and appears in
no listing either. Both cost nothing and neither can displace a profile member.

Shadowing is **policy data, not a branch on a harness name**, because the two
deployable harnesses behave oppositely: Codex lists both copies of a duplicated
name and charges for both, while Claude Code deduplicates (94 loaded, 75 sent).
Hard-coding either would be right for one harness and silently wrong for the
other.

Contract: docs/specs/2026-07-27-distribution-profiles-spec.md (SC-04, SC-05).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .budget import Policy
from .probe_codex import Listing, _absolute

REPO_ROOT = Path(__file__).resolve().parents[2]
_STANDARDIZER = REPO_ROOT / "skills" / "skill-standardizer" / "scripts"

# Per-harness plugin caches, kept here for assertions and evidence. The
# standardizer's `is_plugin_cache_path` hardcodes the Claude needle
# `/.claude/plugins/cache`, which Codex never reads — reusing it for Codex
# classifies Codex's own listed plugin entries as non-plugin and hides them.
#
# This module does **not** re-classify. `probe_codex.classify` already assigns
# origin from the capture's own inferred home, and a second classifier here was
# dead code: a mutation swapping the Codex needle for the Claude one passed every
# test, because the line only ever re-labelled entries that were already
# correctly labelled. A second implementation is a second thing that can
# disagree, so it was removed rather than kept as belt-and-braces.
PLUGIN_CACHE = {
    "codex": "/.codex/plugins/",
    "claude-code": "/.claude/plugins/",
}


@dataclass
class ObservedEntry:
    """One listed entry, with whatever the filesystem could add about it."""

    name: str
    origin: str
    scope: str
    locator: str
    source_description: str | None = None
    listed_description: str | None = None
    cost: int = 0
    is_symlink: bool | None = None
    link_target: str | None = None
    dir_hash: str | None = None
    duplicate_of: str | None = None
    exempt: bool = False
    # Everything this module builds comes from a probe, so it was rendered. The
    # field exists so a caller constructing a *hypothetical* entry — a
    # composition scored before any target exists — can say so, and Task 3's
    # detector will not read "nobody looked" as "the harness removed it".
    observed: bool = True


@dataclass
class Observation:
    """Everything one target exposes to one harness."""

    harness: str
    entries: list[ObservedEntry] = field(default_factory=list)
    root_lines: list[str] = field(default_factory=list)
    unsupported: list[str] = field(default_factory=list)
    warning: str | None = None

    @property
    def duplicated_names(self) -> tuple[str, ...]:
        seen, dupes = set(), set()
        for entry in self.entries:
            if entry.name in seen:
                dupes.add(entry.name)
            seen.add(entry.name)
        return tuple(sorted(dupes))

    def as_budget_entries(self) -> list[dict]:
        """The shape Task 3's `assess` consumes.

        **Foreign, bundled, and plugin entries have no readable source**, and
        SC-04 requires counting them anyway — they occupy the same budget. For
        those, the listed description is the best available evidence and is used
        as the cost basis, with `cost_basis` recording that it came from
        observation rather than source.

        Costing them at zero understated a live target by 20% (3,307 against a
        probe-charged 4,132) — silently, and in the direction that makes an
        over-budget catalog look safe. Where a source description *is* available
        it always wins, because that is the only input immune to elision.
        """
        entries = []
        for e in self.entries:
            basis = "source" if e.source_description is not None else "observed"
            entries.append(
                {
                    "name": e.name,
                    "source_description": e.source_description
                    if e.source_description is not None
                    else (e.listed_description or ""),
                    "cost_basis": basis,
                    **({"listed_description": e.listed_description} if e.observed else {}),
                    "locator": e.locator,
                    "exempt": e.exempt,
                }
            )
        return entries

    @property
    def cost_basis_counts(self) -> dict[str, int]:
        """How many entries were costed from source versus from observation.

        Evidence must be able to say this: an observation-derived cost is a floor
        rather than a truth, because a degraded entry's rendering is shorter than
        its source.
        """
        counts = {"source": 0, "observed": 0}
        for e in self.entries:
            counts["source" if e.source_description is not None else "observed"] += 1
        return counts



def _standardizer():
    """Import the standardizer library, confining the coupling to one place.

    It uses a bare `from skill_standardizer_lib import ...`, so its directory has
    to be on `sys.path` (see `sync.py:9`).
    """
    if str(_STANDARDIZER) not in sys.path:
        sys.path.insert(0, str(_STANDARDIZER))
    import skill_standardizer_lib  # noqa: PLC0415

    return skill_standardizer_lib


def source_descriptions(skills_root: Path) -> dict[str, str]:
    """Untruncated `description` frontmatter, keyed by skill name.

    This is the only valid cost input: a description read back from a rendered
    listing has already been through whatever elision the harness applied.

    **Parsed as YAML, never by regex.** A `^description:\\s*(.*)$` match captures
    only the first line, so a folded scalar (`description: >-`) yields one or two
    characters instead of four hundred. Five skills in this catalog use folded
    descriptions and four are overlay members, including both `engineering`
    anchors — that overlay's cost was understated by roughly 1,200 characters
    before this was caught by comparing computed demand against the probe's own
    charged figure. Silent, and in the direction that makes an over-budget
    catalog look safe.
    """
    out: dict[str, str] = {}
    for path in sorted(skills_root.iterdir()):
        skill_md = path / "SKILL.md"
        if not path.is_dir() or path.name.startswith(("_", ".")) or not skill_md.exists():
            continue
        parts = skill_md.read_text(encoding="utf-8").split("---")
        if len(parts) < 2:
            continue
        try:
            frontmatter = yaml.safe_load(parts[1]) or {}
        except yaml.YAMLError:
            continue
        description = frontmatter.get("description")
        if isinstance(description, str) and description.strip():
            out[path.name] = description.strip()
    return out


def observe_codex(listing: Listing, policy: Policy, skills_root: Path,
                  cwd: Path | None = None) -> Observation:
    """Build an observation from a classified Codex listing.

    `listing` must already have been through `probe_codex.classify`, which
    resolves the project root non-strictly — Codex reports a symlink's target,
    so an unresolved comparison finds project scope nowhere.
    """
    if policy.harness != "codex":
        raise ValueError(f"expected a codex policy, got {policy.harness!r}")

    descriptions = source_descriptions(skills_root)
    observation = Observation(harness=policy.harness, root_lines=list(listing.root_lines),
                              warning=listing.warning)

    seen: dict[str, str] = {}
    for entry in listing.entries:
        if entry.origin == "unknown":
            raise ValueError(
                f"entry {entry.name!r} is unclassified; classify the listing before observing it, "
                "or every origin silently collapses into one bucket"
            )
        observed = ObservedEntry(
            name=entry.name,
            origin=entry.origin,
            scope=entry.scope,
            locator=_absolute(entry.locator, listing.root_lines),
            listed_description=entry.description,
            source_description=descriptions.get(entry.name),
            cost=entry.cost_tokens,
            exempt=entry.origin == "harness-bundled",
        )
        # Codex does not shadow: a name in two roots is two entries with two
        # costs. Record the relationship rather than collapsing it.
        if entry.name in seen and not policy.shadows_by_name:
            observed.duplicate_of = seen[entry.name]
        seen.setdefault(entry.name, observed.locator)
        observation.entries.append(observed)

    _attach_topology(observation, skills_root)
    return observation


def observe_claude(result, debug, policy: Policy, skills_root: Path) -> Observation:
    """Build an observation from a Claude Code request capture plus its debug run.

    Claude Code's listing carries **no locators**, so origin comes from joining
    listed names against known roots — membership from the listing, labels from
    the filesystem, never the reverse. `debug.sent` is the listing count;
    `debug.loaded` is not, and using it restates the filesystem error.
    """
    if policy.harness != "claude-code":
        raise ValueError(f"expected a claude-code policy, got {policy.harness!r}")

    descriptions = source_descriptions(skills_root)
    observation = Observation(harness=policy.harness)

    for entry in result.entries:
        observation.entries.append(
            ObservedEntry(
                name=entry.name,
                origin=entry.origin,
                scope=entry.scope,
                locator="",
                listed_description=entry.description,
                source_description=descriptions.get(entry.name),
                exempt=entry.origin in ("harness-bundled", "unresolved"),
            )
        )

    if debug is not None and debug.sent is not None and debug.sent != len(observation.entries):
        observation.unsupported.append(
            f"debug reports {debug.sent} sent but {len(observation.entries)} entries parsed"
        )
    if debug is not None:
        observation.warning = "over budget" if debug.over_budget else None
    return observation


def _attach_topology(observation: Observation, skills_root: Path) -> None:
    """Add content identity and symlink topology for dojo-managed entries.

    Reuses the standardizer's `hash_directory` so drift semantics cannot diverge
    between this package and the tool that already owns them (SC-05, SC-09).
    """
    lib = _standardizer()
    for entry in observation.entries:
        if entry.origin != "dojo-managed" or not entry.locator:
            continue
        directory = Path(entry.locator).parent
        if not directory.is_dir():
            continue
        entry.is_symlink = directory.is_symlink()
        if entry.is_symlink:
            entry.link_target = str(Path(directory).readlink())
        try:
            entry.dir_hash = lib.hash_directory(directory)
        except Exception:  # noqa: BLE001 — a hashable tree is a bonus, not a requirement
            entry.dir_hash = None
