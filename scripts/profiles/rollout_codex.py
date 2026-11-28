#!/usr/bin/env python3
"""Observe Codex from the record of what it *sent*, not from a re-render.

Task 0 built a probe on ``codex debug prompt-input`` and every later task trusted
it. On 2026-08-04 a live TUI session printed *"Skill descriptions were
shortened"* while that probe reported 76% of budget and zero degradation for the
same directory, model, and minute. Both were internally correct. ``debug
prompt-input`` renders the ``codex exec`` path, which does **not** load
account-synced connector plugins; the interactive TUI does. The gap was 69 of 110
entries.

The probe's parsing was right, its port of Codex's arithmetic was right, and it
agreed with Codex's own charged figure to 0.15%. **It was right about a session
nobody opens.** Precision is not fidelity.

Codex writes each session's rendered prompt to
``~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl``, including the whole
``<skills_instructions>`` block and the session's ``originator``. That is a
record of what was sent rather than a re-render of what might be, and it makes
the surface split observable instead of invisible. This module reads it and
reuses ``probe_codex.parse_block`` unchanged — a second parser would be a second
thing that can disagree.

Two further corrections live here, both found by measuring rather than reasoning:

**The limit is disclosed by saturation, and it is a property of the build.** Codex
spends the listing budget to the last token, so two renders of different inputs
that both saturate must total the same number — and that number is the limit.
Sweeping 89 parseable rollouts across twelve CLI builds:

===========  ===============================================
build        saturated total (= ceiling)
===========  ===============================================
0.139.0      5,358
0.142.3/4    5,534
0.143.0      5,440   = 2% x 272,000, the vendor formula
0.144.1      5,440 **and** 7,440 (a 372,000-window model)
0.144.6      5,440
0.145.0      ~4,000
0.146.0      4,000
===========  ===============================================

So ``2% x context_window`` was **correct through 0.144.x**, including the
372,000-window case — and **0.145.0 changed it**. An earlier revision of this
module claimed the budget "does not move with the model at all"; that was an
overclaim from two models on one build, corrected once the history was swept.
What survives is stronger and is what ``derive_limit`` enforces: a ceiling
belongs to one build, samples from two builds may never be pooled, and a limit
read from the catalog without a saturation check is provisional.

**Demand outside local control must be attributed separately, and compared as a
set.** Account connectors appear, change, and vanish with no local action:
removing two freed 734 tokens on 2026-08-06 while a Codex desktop update added
723 back the same day. Net 11 tokens, entry count unchanged at 56 — so a check
comparing *totals* would have reported that nothing happened.

Contract: docs/specs/2026-07-27-distribution-profiles-spec.md (SC-04).
"""

from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from collections.abc import Collection, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import BinaryIO

from .probe_codex import (
    AVAILABLE_HEADER,
    ROOTS_HEADER,
    Entry,
    INTRO_ABSOLUTE,
    Listing,
    _absolute,
    alias_table_cost_tokens,
    line_cost_tokens,
    parse_block,
    render_available_skills_body,
)

BLOCK_OPEN = "<skills_instructions>"
BLOCK_CLOSE = "</skills_instructions>"

SURFACE_TUI = "codex-tui"
SURFACE_DESKTOP = "Codex Desktop"
# WHY: only the surfaces a person works in render the account-synced
# connectors; `codex exec` does not load them.
INTERACTIVE_SURFACES = frozenset({SURFACE_TUI, SURFACE_DESKTOP})
SURFACE_EXEC = "codex_exec"
#: What ``probe_codex`` observes: an alias of the exec path.
SURFACE_PROBE = "exec"

_ROOT_RE = re.compile(r"^- `(?P<alias>\w+)` = `(?P<path>.+)`$")
_CATALOG_SOURCES = ("Host", "Cloud", "Selected-environment")
_UPDATE_ENTRIES = "### Added or updated skills:"
_UPDATE_ROOTS = "These mappings replace earlier mappings for the same aliases."
_INTRO_WITHOUT_DESCRIPTIONS = INTRO_ABSOLUTE.replace("name, description, and", "name and")
_BLOCK_MARKER = BLOCK_OPEN.encode()
_TURN_CONTEXT_MARKER = b'"turn_context"'
_ROLLBACK = "thread_rolled_back"
_CATALOG_KINDS = {
    "host_skills.instructions": "Host",
    "cloud_skills.instructions": "Cloud",
    "skills.instructions": "Selected-environment",
    "skills.catalog": "Host",
}
_SOURCE_KEYS = {"Host": "host_skills", "Cloud": "cloud_skills", "Selected-environment": "skills"}
_CATALOG_MARKERS = (_BLOCK_MARKER, *(json.dumps(kind).encode() for kind in _CATALOG_KINDS))
_RECORD_MARKERS = (
    *_CATALOG_MARKERS, b'"session_meta"', _TURN_CONTEXT_MARKER, b'"compacted"', b'"world_state"',
    json.dumps(_ROLLBACK).encode(),
)

# WHY: origin is read from the locator, because a fixture's paths do not exist
# on the machine reading it; the `.codex-remote-plugin-install.json` marker is
# checked when present and never required.
CONNECTOR_SEGMENT = "/plugins/cache/openai-curated-remote/"
PLUGIN_CACHE_SEGMENT = "/plugins/cache/"
BUNDLED_SEGMENTS = ("/.codex/skills/.system/", "codex-primary-runtime")
DOJO_SEGMENT = "/.agents/skills/"
REMOTE_MARKER = ".codex-remote-plugin-install.json"

ORIGIN_DOJO = "dojo-managed"
ORIGIN_BUNDLED = "harness-bundled"
ORIGIN_CONNECTOR = "connector"
ORIGIN_PLUGIN = "plugin"
ORIGIN_FOREIGN = "foreign"

# WHY: `connector` is governed by a ChatGPT account setting, reported
# `not installed` by `codex plugin list` while listing, and its local
# `enabled = false` key is inert (controlled test, 2026-08-04).
UNCONTROLLED_ORIGINS = frozenset({ORIGIN_CONNECTOR, ORIGIN_PLUGIN, ORIGIN_BUNDLED})


@dataclass(frozen=True)
class RolloutMeta:
    """Everything the rollout states about the session that produced a listing."""

    path: Path
    surface: str
    cli_version: str
    cwd: str
    model: str | None
    session_id: str | None = None
    observed_at: str | None = None
    catalog_kind: str = "full"
    is_subagent: bool = False

    @property
    def harness_build(self) -> str:
        """The identity a verdict is bounded by (SC-04, revision 14).

        A desktop update introduced a whole plugin marketplace worth 18% of
        budget with no local action, so a verdict measured against one build says
        nothing about the next.
        """
        return f"{self.cli_version}/{self.model or 'unknown-model'}"


@dataclass
class RolloutObservation:
    """One session's listing, with the surface that produced it."""

    meta: RolloutMeta
    listing: Listing
    descriptions_intentionally_omitted: bool = False

    @property
    def charged_tokens(self) -> int:
        return self.listing.charged_tokens

    @property
    def entry_names(self) -> frozenset[str]:
        return frozenset(e.name for e in self.listing.entries)

    @property
    def classification_alarm(self) -> str | None:
        """Set when an implausible share of entries fell through to `foreign`."""
        return classification_alarm(self)

    def absolute_locator(self, locator: str) -> str:
        """Expand an `rN/...` alias against the roots table.

        **Classification must never run on a raw locator.** In alias render mode
        every locator is `rN/<rest>`, which matches none of the absolute path
        segments, so every entry classifies as `foreign` and the uncontrolled set
        comes back empty — a confident zero. Caught here by a test asserting the
        set was non-empty against a fixture known to contain connectors.
        """
        return _absolute(locator, self.listing.root_lines)

    def origin_of(self, locator: str) -> str:
        return classify_locator(self.absolute_locator(locator))

    @property
    def uncontrolled_entries(self) -> frozenset[str]:
        """Entries the operator does not govern, as `origin:name` identities.

        Returned as a **set**, never a count or a sum. On 2026-08-06 two
        uncontrolled changes cancelled to 11 tokens with the entry count
        unchanged at 56; anything comparing totals would have reported that
        nothing happened.

        **Qualified by origin, because a bare name is ambiguous.** Codex does not
        shadow across roots, so one name can be listed twice from two origins and
        charged twice: `skill-creator` is bundled by Codex *and* shipped by dojo,
        which is exactly the collision the harness-equivalence declaration exists
        to record. Keyed by name alone, that one entry made the whole catalog
        look partly ungovernable. The version segment is deliberately excluded —
        a plugin version bump is a harness-build change, caught by
        `harness_build`, not a change in which entries are present.
        """
        return frozenset(
            f"{origin}:{e.name}"
            for e in self.listing.entries
            for origin in (self.origin_of(e.locator),)
            if origin in UNCONTROLLED_ORIGINS
        )


FOREIGN_SHARE_ALARM = 0.25


def classification_alarm(observation: "RolloutObservation") -> str | None:
    """Whether an implausible share of entries fell through to `foreign`.

    `foreign` is the classifier's else-branch, so a change in how the harness
    renders locators degrades into it **silently and wholesale** rather than
    erroring. That is what 0.147.0 did: every dojo skill became `foreign`, the
    attribution still summed correctly, and only reading the labels caught it.
    A bucket that means "none of the above" must be watched, because a
    classifier cannot tell the difference between a foreign skill and a shape it
    no longer recognises.
    """
    entries = observation.listing.entries
    if not entries:
        return None
    foreign = sum(1 for e in entries if observation.origin_of(e.locator) == ORIGIN_FOREIGN)
    share = foreign / len(entries)
    if share <= FOREIGN_SHARE_ALARM:
        return None
    return (
        f"{foreign} of {len(entries)} entries ({share:.0%}) classified as "
        f"{ORIGIN_FOREIGN!r} — above the {FOREIGN_SHARE_ALARM:.0%} alarm. The "
        "harness may have changed how it renders locators; verify before "
        "trusting any attribution from this observation."
    )


def classify_locator(locator: str) -> str:
    """Origin from the locator, with the remote marker as confirmation when present.

    **Resolve before classifying.** Task 0 recorded "Codex reports resolved
    paths" — true of every build through 0.146.0, and false from 0.147.0, which
    reports the symlink path as written. `~/.codex/skills/<name>/SKILL.md` is a
    link into `~/.agents/skills/`, so keying on the target segment alone made
    every dojo skill classify as `foreign` the moment the build changed: 2,547
    tokens of the operator's own catalog, silently relabelled as someone else's.
    A path shape is a constant scoped to a version.

    Resolution is best-effort: a fixture's paths do not exist on the machine
    reading it, so an unresolvable locator is classified as written.
    """
    probe = Path(locator)
    try:
        if probe.exists():
            locator = str(probe.resolve())
    except OSError:
        pass
    if CONNECTOR_SEGMENT in locator:
        return ORIGIN_CONNECTOR
    if DOJO_SEGMENT in locator:
        return ORIGIN_DOJO
    if any(seg in locator for seg in BUNDLED_SEGMENTS):
        return ORIGIN_BUNDLED
    if PLUGIN_CACHE_SEGMENT in locator:
        probe = Path(locator)
        for parent in list(probe.parents)[:6]:
            if (parent / REMOTE_MARKER).exists():
                return ORIGIN_CONNECTOR
        return ORIGIN_PLUGIN
    return ORIGIN_FOREIGN


class RolloutReadError(ValueError):
    """A rollout whose latest catalog evidence cannot be interpreted."""

    def __init__(self, meta: RolloutMeta, reason: str):
        super().__init__(reason)
        self.meta = meta


def _field(payload: dict, name: str) -> str | None:
    value = payload.get(name)
    return value if isinstance(value, str) and value else None


def _timestamp(value: str | None) -> str | None:
    if value is not None:
        try:
            when = datetime.fromisoformat(value)
            if when.tzinfo is not None:
                return when.astimezone(UTC).isoformat(timespec="microseconds")
        except (ValueError, OverflowError):
            pass
    return None


def _session_meta(path: Path, payload: dict) -> RolloutMeta:
    source = payload.get("source")
    return RolloutMeta(
        path=path,
        surface=_field(payload, "originator") or "unknown",
        cli_version=_field(payload, "cli_version") or "unknown",
        cwd=_field(payload, "cwd") or "",
        model=_field(payload, "model"),
        session_id=_field(payload, "id"),
        is_subagent=(payload.get("thread_source") == "subagent"
                     or (isinstance(source, dict) and "subagent" in source)),
    )


@contextmanager
def _rollout_stream(path: Path) -> Iterator[BinaryIO]:
    if path.suffix != ".zst":
        with path.open("rb") as stream:
            yield stream
        return
    try:
        process = subprocess.Popen(
            ["zstd", "-q", "-dc", "--", str(path.resolve())],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError as exc:
        raise ValueError("zstd is required to read compressed rollouts") from exc
    with process:
        assert process.stdout is not None
        try:
            yield process.stdout
        except BaseException:
            process.kill()
            raise
        if process.wait() != 0:
            raise ValueError("compressed rollout could not be decompressed completely")


def _records(stream: BinaryIO) -> Iterator[dict]:
    for raw in stream:
        if not any(marker in raw for marker in _RECORD_MARKERS):
            continue
        try:
            record = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            if any(marker in raw for marker in _CATALOG_MARKERS):
                raise ValueError("malformed rollout record contains skills instructions") from exc
            if _TURN_CONTEXT_MARKER in raw:
                yield {"type": "turn_context"}
            continue
        if isinstance(record, dict):
            yield record


def _content_item(values: object, index: int) -> object:
    if isinstance(values, list) and index < len(values):
        return values[index]
    return None


@dataclass(frozen=True)
class _CatalogBlock:
    text: str
    source: str
    delta: bool
    typed: bool
    unsupported: str | None = None


def _catalog_blocks(message: dict) -> Iterator[_CatalogBlock]:
    if message.get("type") != "message" or message.get("role") != "developer":
        return
    content = message.get("content")
    if not isinstance(content, list):
        return
    metadata = message.get("internal_chat_message_metadata_passthrough")
    metadata = metadata if isinstance(metadata, dict) else {}
    for index, part in enumerate(content):
        kind = _content_item(metadata.get("content_item_kinds"), index)
        metadata_item = _content_item(metadata.get("content_item_metadata"), index)
        provenance = metadata_item.get("provenance") if isinstance(metadata_item, dict) else None
        provenance_type = _field(provenance, "type") if isinstance(provenance, dict) else None
        if provenance_type not in (None, "skills", "unknown"):
            continue
        typed = provenance_type == "skills"
        typed_source = _CATALOG_KINDS.get(kind) if isinstance(kind, str) else None
        if kind is not None and typed_source is None and not typed:
            continue
        text = ""
        if isinstance(part, dict) and part.get("type") == "input_text":
            text = (_field(part, "text") or "").strip()
        if text.startswith(BLOCK_OPEN):
            yield _catalog_block(text, typed_source, typed)
        elif typed_source is not None and typed:
            yield _CatalogBlock(text, typed_source, False, True, "unsupported catalog wrapper")


def _catalog_block(text: str, typed_source: str | None, typed: bool) -> _CatalogBlock:
    heading = text[len(BLOCK_OPEN):].strip().partition("\n")[0].strip()
    for source in _CATALOG_SOURCES:
        if heading in (f"## {source} skills", f"## {source} skills update"):
            return _CatalogBlock(text, source, heading.endswith(" update"), typed)
    source = typed_source or "Host"
    if heading.startswith("## ") and heading not in ("## Skills", "## Skills update"):
        return _CatalogBlock(text, source, False, typed, "unsupported catalog source heading")
    return _CatalogBlock(text, source, heading == "## Skills update", typed)


def _root_aliases(root_lines: list[str]) -> dict[str, str]:
    roots = {}
    for line in root_lines:
        match = _ROOT_RE.fullmatch(line)
        if not match or match["alias"] in roots:
            raise ValueError("unrecognized or duplicate catalog alias mapping")
        roots[match["alias"]] = line
    return roots


def _is_absolute_path(path: str) -> bool:
    return "\0" not in path and (path.startswith("/") or bool(re.match(r"^[A-Za-z]:[/\\]", path)))


def _entry_key(entry: Entry, roots: list[str]) -> tuple[str, str]:
    locator = _absolute(entry.locator, roots)
    if entry.locator_kind == "file" and not _is_absolute_path(locator):
        raise ValueError("catalog file locator has no resolvable root")
    return entry.locator_kind, locator


def _parse_full(block: str) -> Listing:
    if not block.endswith(BLOCK_CLOSE) or BLOCK_CLOSE in block[:-len(BLOCK_CLOSE)]:
        raise ValueError("malformed skills instruction wrapper")
    listing = parse_block(block.replace(_INTRO_WITHOUT_DESCRIPTIONS, INTRO_ABSOLUTE, 1))
    listing.block_chars = len(block)
    section = False
    seen = False
    skill_lines = []
    for line in block[len(BLOCK_OPEN):-len(BLOCK_CLOSE)].splitlines():
        if line == AVAILABLE_HEADER:
            if seen:
                raise ValueError("catalog repeats the available skills section")
            section = seen = True
        elif line.startswith(("## ", "### ")):
            section = False
        elif section and line.strip() and not line.startswith(
            ("Exceeded skills context budget", "Skill descriptions were shortened"),
        ):
            skill_lines.append(line)
    if not seen or [entry.rendered for entry in listing.entries] != skill_lines:
        raise ValueError("unrecognized available skills section")
    _root_aliases(listing.root_lines)
    for entry in listing.entries:
        _entry_key(entry, listing.root_lines)
    if listing.root_lines:
        listing.render_mode = "alias"
    return listing


def _delta_entries(block: str, previous_roots: list[str]) -> tuple[list[Entry], list[str]]:
    if not block.endswith(BLOCK_CLOSE):
        raise ValueError("malformed skills instruction wrapper")
    lines = block[len(BLOCK_OPEN):-len(BLOCK_CLOSE)].strip().splitlines()[1:]
    try:
        entries_at = lines.index(_UPDATE_ENTRIES)
    except ValueError as exc:
        raise ValueError("catalog update does not identify added or updated skills") from exc
    roots = _root_aliases(previous_roots)
    if entries_at:
        if lines[:2] != [ROOTS_HEADER, _UPDATE_ROOTS] or entries_at == 2:
            raise ValueError("unrecognized catalog update headings")
        roots.update(_root_aliases(lines[2:entries_at]))
    additions = lines[entries_at + 1:]
    if not additions or any(not line.startswith("- ") for line in additions):
        raise ValueError("catalog update contains unsupported entries or notices")
    root_lines = list(roots.values())
    rendered = render_available_skills_body(root_lines, additions)
    parsed = _parse_full(f"{BLOCK_OPEN}{rendered}{BLOCK_CLOSE}")
    return parsed.entries, root_lines


def _preserve_locator(entry: Entry, old_roots: list[str], new_roots: list[str]) -> Entry:
    locator = _absolute(entry.locator, old_roots)
    if locator != _absolute(entry.locator, new_roots):
        rendered = entry.rendered.removesuffix(f"{entry.locator})") + f"{locator})"
        return replace(entry, locator=locator, rendered=rendered, cost_tokens=line_cost_tokens(rendered))
    return entry


def _apply_delta(previous: Listing, block: str) -> Listing:
    additions, roots = _delta_entries(block, previous.root_lines)
    entry_positions: dict[tuple[str, str], list[int]] = {}
    entries = []
    for index, entry in enumerate(previous.entries):
        key = _entry_key(entry, previous.root_lines)
        entry_positions.setdefault(key, []).append(index)
        entries.append(_preserve_locator(entry, previous.root_lines, roots))
    previous_names = {entry.name for entry in previous.entries}
    seen = set()
    for entry in additions:
        key = _entry_key(entry, roots)
        positions = entry_positions.get(key, [])
        if len(positions) > 1 or key in seen:
            raise ValueError("catalog update has an ambiguous skill identity")
        seen.add(key)
        if positions:
            entries[positions[0]] = entry
        elif entry.name in previous_names:
            raise ValueError("catalog update changes the locator of an existing skill name")
        else:
            entries.append(entry)
    return Listing(
        render_mode="alias" if roots else "absolute",
        entries=entries,
        root_lines=roots,
        entry_cost_tokens=sum(entry.cost_tokens for entry in entries),
        root_table_cost_tokens=alias_table_cost_tokens(roots),
        block_chars=previous.block_chars + len(block),
        warning=previous.warning,
    )


def _combine_catalogs(catalogs: list[Listing]) -> Listing:
    if len(catalogs) == 1:
        return catalogs[0]
    roots = list(dict.fromkeys(line for listing in catalogs for line in listing.root_lines))
    entries = [
        _preserve_locator(entry, listing.root_lines, roots)
        for listing in catalogs for entry in listing.entries
    ]
    return Listing(
        render_mode="alias" if roots else "absolute",
        entries=entries,
        root_lines=roots,
        entry_cost_tokens=sum(entry.cost_tokens for entry in entries),
        root_table_cost_tokens=sum(listing.root_table_cost_tokens for listing in catalogs),
        block_chars=sum(listing.block_chars for listing in catalogs),
        warning=next((listing.warning for listing in catalogs if listing.warning), None),
    )


@dataclass
class _CatalogState:
    sources: dict[str, Listing] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)
    deltas: set[str] = field(default_factory=set)
    descriptionless: set[str] = field(default_factory=set)

    def apply(self, block: _CatalogBlock) -> None:
        source = block.source
        try:
            if block.unsupported is not None:
                raise ValueError(block.unsupported)
            if block.delta:
                previous = self.sources.get(source)
                if previous is None or source in self.errors:
                    raise ValueError("catalog update has no verified full listing")
                self.sources[source] = _apply_delta(previous, block.text)
                self.deltas.add(source)
            else:
                self.sources[source] = _parse_full(block.text)
                self.deltas.discard(source)
                self.descriptionless.discard(source)
                if _INTRO_WITHOUT_DESCRIPTIONS in block.text:
                    self.descriptionless.add(source)
        except ValueError as exc:
            self.errors[source] = str(exc)
        else:
            self.errors.pop(source, None)

    def after_compaction(self, payload: dict) -> tuple[_CatalogState, dict[str, str]]:
        history = payload["replacement_history"]
        metadata = payload.get("replacement_history_metadata")
        aligned = isinstance(metadata, list) and len(metadata) == len(history)
        replacement = _CatalogState()
        fresh = aligned
        bodies: dict[str, str] = {}
        for index, message in enumerate(history):
            if not isinstance(message, dict):
                continue
            for block in _catalog_blocks(message):
                item_meta = _content_item(metadata, index) if aligned else None
                fresh = (fresh and block.typed and not block.delta and isinstance(item_meta, dict)
                         and "history_sequence" not in item_meta)
                replacement.apply(block)
                bodies[_SOURCE_KEYS[block.source]] = block.text[len(BLOCK_OPEN):-len(BLOCK_CLOSE)].strip()
        return replacement, bodies if fresh and not replacement.errors else {}

    def invalidate(self, reason: str, *, other: _CatalogState | None = None) -> _CatalogState:
        sources = self.sources.keys() | self.errors.keys()
        if other is not None:
            sources |= other.sources.keys() | other.errors.keys()
        return _CatalogState(errors=dict.fromkeys(sources, reason))


def _matches_compaction_checkpoint(payload: dict, bodies: dict[str, str]) -> bool:
    snapshot = payload.get("state")
    if payload.get("full") is not True or not isinstance(snapshot, dict):
        return False
    # WHY: the replacement history also carries old developer messages. A
    # body-matching complete checkpoint corroborates the new catalog emission.
    for source, body in bodies.items():
        persisted = snapshot.get(source)
        if not isinstance(persisted, dict) or persisted.get("includeInstructions") is not True:
            return False
        persisted_body = _field(persisted, "body")
        if persisted_body is None or persisted_body.strip() != body:
            return False
    return True


def read_rollout(path: Path | str) -> RolloutObservation | None:
    """Read the latest reconstructable catalog emitted by a Codex rollout."""
    path = Path(path)
    session = _session_meta(path, {})
    meta = session
    state = _CatalogState()
    pending_context = False
    current_context_required = False
    catalog_in_session = False
    turn_in_session = False
    compacted_catalog: _CatalogState | None = None
    compacted_bodies: dict[str, str] = {}
    full_checkpoint = False
    try:
        with _rollout_stream(path) as stream:
            for record in _records(stream):
                kind = record.get("type")
                payload = record.get("payload")
                if kind == "turn_context":
                    if compacted_catalog is not None and full_checkpoint:
                        state = compacted_catalog
                    compacted_catalog = None
                    if pending_context and isinstance(payload, dict):
                        cwd = _field(payload, "cwd")
                        model = _field(payload, "model")
                        if not current_context_required or (cwd and _is_absolute_path(cwd) and model):
                            meta = replace(meta, cwd=cwd or meta.cwd, model=model or meta.model)
                    pending_context = False
                    turn_in_session = True
                elif not isinstance(payload, dict):
                    continue
                elif kind == "session_meta":
                    session = _session_meta(path, payload)
                    catalog_in_session = turn_in_session = pending_context = False
                    compacted_catalog = None
                elif kind == "world_state" and compacted_catalog is not None:
                    full_checkpoint = _matches_compaction_checkpoint(payload, compacted_bodies)
                elif kind == "response_item":
                    blocks = list(_catalog_blocks(payload))
                    if not blocks:
                        continue
                    compacted_catalog = None
                    for block in blocks:
                        state.apply(block)
                    # WHY: resuming an existing rollout appends records without a new
                    # session_meta. Its original build is only attributable to startup.
                    current_context_required = (catalog_in_session or turn_in_session
                                                or any(block.typed or block.delta for block in blocks))
                    meta = replace(
                        session,
                        observed_at=_timestamp(_field(record, "timestamp")),
                        cli_version="unknown" if catalog_in_session or turn_in_session else session.cli_version,
                        cwd="" if current_context_required else session.cwd,
                        model=None if current_context_required else session.model,
                    )
                    catalog_in_session = pending_context = True
                elif kind == "compacted" and isinstance(payload.get("replacement_history"), list):
                    replacement, compacted_bodies = state.after_compaction(payload)
                    if replacement.sources == state.sources and replacement.errors == state.errors:
                        continue
                    state = state.invalidate(
                        "compaction catalog does not match timestamped catalog evidence", other=replacement,
                    )
                    compacted_catalog = replacement if compacted_bodies else None
                    full_checkpoint = False
                    meta = replace(session, observed_at=_timestamp(_field(record, "timestamp")),
                                   cli_version="unknown", cwd="", model=None)
                    pending_context = current_context_required = True
                elif kind == "event_msg" and payload.get("type") == _ROLLBACK:
                    state = state.invalidate("rollback invalidated the verified full listing")
                    compacted_catalog = None
                    pending_context = False
                    turn_in_session = True
                    meta = replace(session, observed_at=_timestamp(_field(record, "timestamp")),
                                   cli_version="unknown", cwd="", model=None)
    except OSError as exc:
        raise RolloutReadError(replace(session, cwd=""), "could not read rollout") from exc
    except ValueError as exc:
        raise RolloutReadError(replace(session, cwd=""), str(exc)) from exc
    if state.errors:
        raise RolloutReadError(meta, next(iter(state.errors.values())))
    if not state.sources:
        return None
    if current_context_required and meta.observed_at is None:
        raise RolloutReadError(meta, "catalog record timestamp is unavailable or invalid")
    if current_context_required and (not meta.cwd or not meta.model):
        raise RolloutReadError(meta, "catalog turn context is unavailable or invalid")
    catalog_kind = "composed" if len(state.sources) > 1 else ("delta" if state.deltas else "full")
    return RolloutObservation(
        meta=replace(meta, catalog_kind=catalog_kind),
        listing=_combine_catalogs(list(state.sources.values())),
        descriptions_intentionally_omitted=bool(state.descriptionless),
    )


def default_sessions_root() -> Path:
    return Path.home() / ".codex" / "sessions"


def find_rollouts(sessions_root: Path | str | None = None) -> list[Path]:
    """Discover plain and compressed rollouts in session-start order."""
    root = Path(sessions_root) if sessions_root else default_sessions_root()
    plain = set(root.rglob("rollout-*.jsonl"))
    compressed = [
        path for path in root.rglob("rollout-*.jsonl.zst") if path.with_suffix("") not in plain
    ]
    return sorted((*plain, *compressed), key=lambda path: (path.name[8:24], str(path)), reverse=True)


def _observation_order(meta: RolloutMeta) -> float:
    if meta.observed_at is not None:
        return datetime.fromisoformat(meta.observed_at).timestamp()
    # WHY: old captures can lack a record timestamp. Use the local filename
    # only for ordering these historical observations.
    try:
        return datetime.strptime(meta.path.name[8:24], "%Y-%m-%dT%H-%M").timestamp()
    except (ValueError, OSError, OverflowError):
        return float("-inf")


def _matches_scope(
    meta: RolloutMeta, cwd: str | None, surfaces: Collection[str] | None,
    *, include_unknown: bool = False,
) -> bool:
    if surfaces is not None and meta.is_subagent and meta.surface in INTERACTIVE_SURFACES:
        return False
    if surfaces is not None and meta.surface not in surfaces:
        if not (include_unknown and meta.surface == "unknown"):
            return False
    if cwd is None:
        return True
    if not meta.cwd:
        return include_unknown
    try:
        return str(Path(meta.cwd).resolve()) == cwd
    except (OSError, RuntimeError, ValueError):
        return include_unknown


def observations(sessions_root: Path | str | None = None, *, cwd: str | Path | None = None,
                 surface: str | Collection[str] | None = None, limit: int | None = None,
                 errors: list | None = None,
                 evidence_errors: list[RolloutReadError] | None = None) -> list[RolloutObservation]:
    """Find observations in catalog-record order, reporting unreadable evidence."""
    wanted_cwd = str(Path(cwd).resolve()) if cwd else None
    surfaces = {surface} if isinstance(surface, str) else surface
    found: list[RolloutObservation] = []
    for path in find_rollouts(sessions_root):
        try:
            observation = read_rollout(path)
        except RolloutReadError as exc:
            if errors is not None:
                errors.append((path, str(exc)))
            if evidence_errors is not None and _matches_scope(
                exc.meta, wanted_cwd, surfaces, include_unknown=True,
            ):
                evidence_errors.append(exc)
            continue
        if observation is not None and _matches_scope(observation.meta, wanted_cwd, surfaces):
            found.append(observation)
    found.sort(key=lambda observation: _observation_order(observation.meta), reverse=True)
    return found[:limit]


@dataclass
class LimitEvidence:
    """A budget limit and the basis it rests on.

    ``provisional`` is the load-bearing field. A limit taken from a vendor
    catalog and never checked against behaviour is provisional, and a provisional
    limit may not make a pair deployable — because that is exactly the mistake
    that made a 100%-of-budget target read as 74% for four days.
    """

    limit: int | None
    #: ``"observed"``, ``"vendor"``, or ``"indeterminate"``.
    basis: str
    provisional: bool
    reason: str = ""
    #: ``(entry_count, charged_tokens)`` pairs.
    samples: tuple[tuple[int, int], ...] = ()


def derive_limit(obs: list[RolloutObservation], *, clipped_only: bool = True) -> LimitEvidence:
    """Establish the limit by saturation, from renders that were actually clipped.

    Requires **two renders with different entry counts** whose charged totals
    agree exactly. Different counts matter: two renders of the same catalog agree
    trivially and disclose nothing. Only a clipped render saturates — an
    under-budget listing totals whatever it happens to cost, which is not a
    limit.
    """
    # WHY: never mix harness builds. The limit is a property of the build (0.144.1
    # charged 6,188 tokens unclipped where 0.146.0 saturates at 4,000), so pooling
    # fabricates a disagreement or averages two real ceilings into neither.
    eligible = [
        observation for observation in obs
        if observation.meta.catalog_kind == "full" and observation.meta.cli_version != "unknown"
    ]
    builds = {observation.meta.harness_build for observation in eligible}
    if len(builds) > 1:
        return LimitEvidence(
            None, "indeterminate", True,
            f"samples span {len(builds)} harness builds ({', '.join(sorted(builds))}); "
            "a limit is a property of one build",
            (),
        )

    samples: list[tuple[int, int]] = []
    for observation in eligible:
        if clipped_only and not is_saturated(observation):
            continue
        samples.append((len(observation.listing.entries), observation.charged_tokens))

    if len(samples) < 2:
        return LimitEvidence(None, "indeterminate", True,
                             f"need 2 saturating renders, have {len(samples)}",
                             tuple(samples))

    counts = {n for n, _ in samples}
    totals = {t for _, t in samples}
    if len(counts) < 2:
        return LimitEvidence(None, "indeterminate", True,
                             "all saturating renders have the same entry count, "
                             "so their agreement is trivial",
                             tuple(samples))
    if len(totals) != 1:
        return LimitEvidence(None, "indeterminate", True,
                             f"saturating renders disagree: {sorted(totals)}",
                             tuple(samples))
    return LimitEvidence(totals.pop(), "observed", False,
                         f"{len(samples)} saturating renders across "
                         f"{len(counts)} entry counts agree exactly",
                         tuple(samples))


def clipped_entry_names(observation: RolloutObservation) -> list[str]:
    """Names whose descriptions were cut by the budget, in listed order.

    The shape rule `is_saturated` reduces to a boolean, kept in one place so the
    two can never disagree about which entries are affected. Empty whenever the
    listing is not saturated, so its emptiness is the predicate.

    Two independent signals must agree, because the shape rule alone cannot tell
    "clipped to a common length" from "written to a common length". A catalog of
    templated descriptions — generated metadata, a vendor bundle sharing a
    boilerplate summary — can put a fifth of its entries within three characters
    of the longest without anything having been cut, and this feeds a persistent
    outcome that speaks every session, so a false positive here is not a stray
    line in a report but a warning the operator learns to scroll past.

    The corroborating signal is that budget clipping cuts *mid-sentence*: it
    appends nothing and respects no boundary, so a clipped description does not
    end in terminal punctuation. Measured across every sample on hand, the two
    agree almost exactly on real clipping (42 of 42, 76 of 79, 32 of 33) and not
    at all on listings that fit (0 of 2, 0 of 1) -- so requiring both costs
    nothing that was ever detected and refuses the case the shape alone invents.
    """
    listing = observation.listing
    warning = listing.warning or ""
    if "All skill descriptions were removed" in warning:
        return [entry.name for entry in listing.entries if entry.description is None]
    entries = [entry for entry in listing.entries if entry.description]
    if not entries and not observation.descriptions_intentionally_omitted and len(listing.entries) >= 3:
        return [entry.name for entry in listing.entries]
    lengths = [len(entry.description or "") for entry in entries]
    if len(lengths) < 3:
        return []
    longest = max(lengths)
    if longest >= 1_000:
        return []
    at_longest = [
        entry for entry, length in zip(entries, lengths)
        if abs(length - longest) <= 3
    ]
    if len(at_longest) < max(3, len(lengths) // 5):
        return []
    cut_midsentence = sum(
        1 for entry in at_longest
        if not (entry.description or "").rstrip().endswith((".", "!", "?"))
    )
    if cut_midsentence * 2 <= len(at_longest):
        return []
    return [entry.name for entry in at_longest]


def is_saturated(observation: RolloutObservation, source_descriptions: dict | None = None) -> bool:
    """Whether this render was clipped, i.e. spent its whole budget.

    Detected from the render itself: Codex's budget-driven clipping is uniform,
    so a saturated listing has many descriptions at an identical length that is
    shorter than the 1,024-character pre-cap. That pre-cap appends ``"..."``;
    budget clipping appends nothing, which is why the shape rather than a marker
    has to carry the signal.
    """
    if source_descriptions:
        if len(observation.listing.entries) < 3:
            return False
        return any(
            (e.description is not None or not observation.descriptions_intentionally_omitted)
            and len(e.description or "") < len(source_descriptions.get(e.name, ""))
            for e in observation.listing.entries
        )
    return bool(clipped_entry_names(observation))


def qualified_identities(listing: Listing) -> Counter:
    """`origin:name` per listed entry, with multiplicity preserved.

    A `Counter` rather than a set because Codex charges each copy of a
    duplicated name separately, so losing one copy is a real change.
    """
    return Counter(
        f"{classify_locator(_absolute(e.locator, listing.root_lines))}:{e.name}"
        for e in listing.entries
    )


def surface_mismatch(live: Listing, recorded: RolloutObservation) -> dict | None:
    """Report a live probe disagreeing with the recorded session.

    Returned rather than reconciled: this disagreement *is* the defect this
    module exists to catch, so it must be visible in evidence. Reconciling it
    silently would restore exactly the failure of the last four days.
    """
    # WHY: a multiset of qualified identities, not a set of bare names. Codex lists
    # and charges every copy of a duplicated name, so a set misses one copy going.
    live_ids = qualified_identities(live)
    recorded_ids = qualified_identities(recorded.listing)
    if live_ids == recorded_ids:
        return None
    only_recorded = recorded_ids - live_ids
    only_live = live_ids - recorded_ids
    return {
        "kind": "surface-mismatch",
        "live_surface": SURFACE_PROBE,
        "recorded_surface": recorded.meta.surface,
        "live_entries": sum(live_ids.values()),
        "recorded_entries": sum(recorded_ids.values()),
        "only_in_recorded": sorted(only_recorded.elements()),
        "only_in_live": sorted(only_live.elements()),
        "detail": (
            "the live probe renders a different code path than the recorded "
            "session; the recorded session is authoritative"
        ),
    }


def staleness(previous: RolloutObservation, current: RolloutObservation) -> list[str]:
    """Why a prior verdict no longer holds (SC-04, revision 14).

    Compares the uncontrolled entry **set**, not its size or cost. Both were
    unchanged on 2026-08-06 while six entries left and nine arrived.
    """
    reasons = []
    for label, obs in (("previous", previous), ("current", current)):
        alarm = obs.classification_alarm
        if alarm:
            reasons.append(f"{label} observation has degraded classification: {alarm}")
    if previous.meta.harness_build != current.meta.harness_build:
        reasons.append(
            f"harness build changed: {previous.meta.harness_build} -> "
            f"{current.meta.harness_build}"
        )
    before, after = previous.uncontrolled_entries, current.uncontrolled_entries
    if before != after:
        gone, arrived = sorted(before - after), sorted(after - before)
        reasons.append(
            "uncontrolled entry set changed: "
            f"-{len(gone)} +{len(arrived)} ({', '.join(gone[:3] + arrived[:3])}…)"
        )
    return reasons


class ClassificationError(RuntimeError):
    """Raised when origin classification is too degraded to attribute demand."""


def attribute_demand(observation: RolloutObservation,
                     source_descriptions: dict[str, str] | None = None,
                     *, allow_degraded: bool = False) -> dict[str, int]:
    """True demand per origin, from untruncated source where it is available.

    Where a source description is unavailable — a connector's payload, a bundled
    skill — the rendered text is a floor rather than a truth, and the caller is
    told so by `cost_basis` elsewhere. Costing those at zero understated a live
    target by 20%.
    """
    # WHY: fail closed (SC-04). An attribution over wholesale-misclassified entries
    # sums correctly and means nothing.
    alarm = classification_alarm(observation)
    if alarm and not allow_degraded:
        raise ClassificationError(alarm)

    totals: dict[str, int] = {}
    descriptions = source_descriptions or {}
    for entry in observation.listing.entries:
        # WHY: classify on the absolute locator, cost on the rendered one: Codex
        # charges the alias form, so costing the expansion would overstate.
        origin = observation.origin_of(entry.locator)
        text = descriptions.get(entry.name, entry.description or "")
        line = f"- {entry.name}: {text} ({entry.locator_kind}: {entry.locator})"
        totals[origin] = totals.get(origin, 0) + line_cost_tokens(line)
    if observation.listing.root_lines:
        totals["alias-table"] = observation.listing.root_table_cost_tokens
    return totals
