#!/usr/bin/env python3
"""Compose profiles deterministically, and give each composition an identity.

Two identities live here and conflating them was the defect spec revision 9
corrected, so the split is the point of this module:

* **Profile identity** is *intent*. It hashes the normalized selection and the
  reviewed definition bodies — nothing else. It is **harness-independent by
  construction**, and resolved membership is deliberately not an input. Feed
  membership in and a member suppressed on one harness would make two machines
  running the same reviewed selection look like they had asked for different
  things.
* **Realization identity** is *what landed*. It binds profile identity to the
  canonical revision, the target, the harness/model version, the budget policy,
  and the equivalence declaration. Suppression belongs here.

The consequence worth stating: two harnesses can share one profile identity and
hold different realizations without either being drift (SC-11).

Suppression is narrow on purpose. A member is removed only when the equivalence
declaration says this harness ships its own equivalent, with evidence. It is
**never** inferred from a name match — an undeclared collision is *reported* for
the caller to surface, because guessing wrong silently removes a skill the
maintainer selected, and a lost skill is far worse than a duplicated one.

Contract: docs/specs/2026-07-27-distribution-profiles-spec.md (SC-01, SC-02,
SC-11, EV-NEG-01, EV-NEG-06, EV-CON-02).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum

from .definitions import (
    BASELINE,
    INSPECTION,
    SUPPORTED_HARNESSES,
    Equivalence,
    Profile,
    resolved_members,
)


class SelectionError(ValueError):
    """An invalid selection request. Carries a distinct `code`.

    The code exists so a caller can distinguish *why* a selection was refused
    without parsing prose. Every rejection path in this module has its own; a
    test asserting only that something raised cannot tell a correct refusal from
    an accidental one.
    """

    def __init__(self, code: SelectionErrorCode, message: str) -> None:
        super().__init__(f"[{code.value}] {message}")
        self.code = code


class SelectionErrorCode(str, Enum):
    UNKNOWN_PROFILE = "unknown-profile"
    MISSING_CORE = "missing-core"
    NO_OVERLAY = "no-overlay"
    REPEATED_TOKEN = "repeated-token"
    FULL_NOT_EXCLUSIVE = "full-not-exclusive"


@dataclass(frozen=True)
class Resolution:
    """A resolved composition, before any harness is considered."""

    selection: tuple[str, ...]
    members: tuple[str, ...]
    identity: str


@dataclass(frozen=True)
class Suppression:
    """One member removed because the harness ships its own equivalent."""

    skill: str
    bundled_entry: str
    evidence: str


@dataclass(frozen=True)
class Collision:
    """A member sharing a name with a bundled entry, with no declaration.

    Reported, never acted on. This is the shape that must not silently become a
    `Suppression`.
    """

    skill: str
    bundled_entry: str


@dataclass(frozen=True)
class HarnessResolution:
    """What a resolved composition becomes at one harness."""

    harness: str
    realized: tuple[str, ...]
    suppressed: tuple[Suppression, ...]
    collisions: tuple[Collision, ...]


def resolve(selection: list[str] | tuple[str, ...], definitions: dict[str, Profile], catalog: dict[str, dict]) -> Resolution:
    """Set union over `core` plus the named overlays, lexically ordered.

    Composition order has no semantic effect: the members are sorted and the
    identity hashes the *normalized* selection, so all 720 orderings of the six
    overlays produce one result (EV-CON-02).
    """
    tokens = tuple(selection)

    seen: set[str] = set()
    for token in tokens:
        if token in seen:
            raise SelectionError(
                SelectionErrorCode.REPEATED_TOKEN,
                f"profile {token!r} named more than once in one selection",
            )
        seen.add(token)

    unknown = sorted(t for t in tokens if t not in definitions)
    if unknown:
        raise SelectionError(
            SelectionErrorCode.UNKNOWN_PROFILE,
            f"unknown profile(s) {', '.join(unknown)}; known: {', '.join(sorted(definitions))}",
        )

    if INSPECTION in seen and len(seen) > 1:
        others = sorted(seen - {INSPECTION})
        raise SelectionError(
            SelectionErrorCode.FULL_NOT_EXCLUSIVE,
            f"{INSPECTION!r} is a fixed inspection profile and cannot combine with {', '.join(others)}",
        )

    if INSPECTION not in seen:
        if BASELINE not in seen:
            raise SelectionError(
                SelectionErrorCode.MISSING_CORE,
                f"every deployable composition includes {BASELINE!r}; selection was {', '.join(sorted(seen)) or 'empty'}",
            )
        if seen == {BASELINE}:
            raise SelectionError(
                SelectionErrorCode.NO_OVERLAY,
                f"a {BASELINE!r}-only selection is not a deployable composition; name at least one capability overlay",
            )

    members: set[str] = set()
    for token in sorted(seen):
        members.update(resolved_members(definitions[token], catalog))

    normalized = tuple(sorted(seen))
    return Resolution(
        selection=normalized,
        members=tuple(sorted(members)),
        identity=profile_identity(normalized, definitions),
    )


def profile_identity(selection: tuple[str, ...] | list[str], definitions: dict[str, Profile]) -> str:
    """SHA-256 over the normalized selection and the reviewed definition bodies.

    **Resolved membership is not an input, and that is load-bearing.** Profile
    identity answers "what did the maintainer ask for", which is the same
    question on every harness. Including membership would make a Codex
    realization and a Claude Code realization of one reviewed selection hash
    differently, and SC-11 would then read every legitimate suppression as drift.

    `full`'s sentinel is hashed as the sentinel rather than expanded, for the
    same reason it is stored that way: authoring a skill changes what `full`
    contains but not what was asked for.
    """
    normalized = sorted(set(selection))
    bodies = [
        {
            "name": definitions[name].name,
            "kind": definitions[name].kind,
            "members": list(definitions[name].members),
        }
        for name in normalized
    ]
    blob = json.dumps(
        {"selection": normalized, "definitions": bodies},
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def resolve_for_harness(
    resolution: Resolution,
    equivalences: dict[str, Equivalence],
    harness: str,
    bundled_entries: tuple[str, ...] | list[str] = (),
) -> HarnessResolution:
    """Apply declared suppressions; report undeclared collisions.

    `equivalences` is `Equivalences.for_harness(harness)`. `bundled_entries` is
    what the harness actually lists — pass the probe's observation, not a guess,
    because a collision can only exist against an entry that is really there.
    Task 0 found `review-agent` present on disk and in no listing; an entry the
    model never sees displaces nothing.
    """
    if harness not in SUPPORTED_HARNESSES:
        raise SelectionError(
            SelectionErrorCode.UNKNOWN_PROFILE,
            f"unknown harness {harness!r}; supported: {', '.join(SUPPORTED_HARNESSES)}",
        )

    realized: list[str] = []
    suppressed: list[Suppression] = []
    collisions: list[Collision] = []
    listed = set(bundled_entries)

    for member in resolution.members:
        declared = equivalences.get(member)
        if declared is not None:
            suppressed.append(
                Suppression(
                    skill=member,
                    bundled_entry=declared.bundled_entry,
                    evidence=declared.evidence,
                )
            )
            continue
        if member in listed:
            # Same name, no declaration. Report it and keep the member: the
            # maintainer selected it, and suppressing on a guess is how a
            # catalog loses a skill nobody notices is gone.
            collisions.append(Collision(skill=member, bundled_entry=member))
        realized.append(member)

    return HarnessResolution(
        harness=harness,
        realized=tuple(realized),
        suppressed=tuple(suppressed),
        collisions=tuple(collisions),
    )


def realization_identity(
    profile_id: str,
    canonical_revision: str,
    target_identity: str,
    harness_model_version: str,
    budget_policy_identity: str,
    equivalence_identity: str,
) -> str:
    """SHA-256 over the six fields that decide what actually landed.

    Any of them changing is a new realization request rather than an idempotent
    replay (spec Authority, "Retry and concurrency"). The equivalence declaration
    is included precisely so that editing it — which changes what lands without
    changing what was asked for — cannot be mistaken for a repeat of the same
    request.
    """
    blob = json.dumps(
        {
            "profile_identity": profile_id,
            "canonical_revision": canonical_revision,
            "target_identity": target_identity,
            "harness_model_version": harness_model_version,
            "budget_policy_identity": budget_policy_identity,
            "equivalence_identity": equivalence_identity,
        },
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()
