#!/usr/bin/env python3
"""Read the skills listing Codex actually sends to the model.

``codex debug prompt-input`` renders the model-visible prompt as JSON, including
the whole ``<skills_instructions>`` block. This module parses that block. There
is no LLM in the loop and no cached state: every call re-runs the binary, so
staleness is checked rather than assumed.

Two rules this parser exists to enforce, both learned from getting them wrong:

1. **Anchor entries on the trailing locator, never on the first colon.** Plugin
   skills render as ``namespace:name``, so splitting on the first colon drops
   them silently and returns a confident zero.
2. **Only skill lines are charged against the budget.** The intro prose, the
   ``### Available skills`` header, the how-to-use section, and the closing tag
   are *not* counted by ``render.rs``; the alias roots table *is*, indirectly,
   by shrinking the limit. Measuring the whole block overstates cost — on this
   repository by about 11%.

Vendor reference: ``codex-rs/core-skills/src/render.rs`` at pinned revision
``f57467275c``.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

# From render.rs. Kept here as named constants so a vendor bump is a one-line diff.
APPROX_BYTES_PER_TOKEN = 4
SKILL_METADATA_CONTEXT_WINDOW_PERCENT = 2
DEFAULT_SKILL_METADATA_CHAR_BUDGET = 8_000
MAX_DEFAULT_CONTEXT_SKILL_DESCRIPTION_CHARS = 1_024
TRUNCATED_SKILL_DESCRIPTION_SUFFIX = "..."

BLOCK_OPEN = "<skills_instructions>"
BLOCK_CLOSE = "</skills_instructions>"
AVAILABLE_HEADER = "### Available skills"
ROOTS_HEADER = "### Skill roots"

# render.rs picks one of two intros; which one appears tells us the render mode
# without having to infer it from the entry shape.
INTRO_ABSOLUTE = "Each entry includes a name, description, and source locator."
INTRO_ALIASES = "a short path that can be expanded into an absolute path using the skill roots table"


# ``- <name>: <description> (file: <path>)`` with the description optional and the
# locator label open-ended: render.rs emits ``file``, ``environment resource``,
# ``orchestrator resource``, or ``custom resource`` depending on the source.
ENTRY_RE = re.compile(r"^- (?P<body>.*?) \((?P<kind>[a-z ]+): (?P<locator>.*)\)$")
# A name with no description renders as ``- name: (file: ...)``.
NAME_ONLY_RE = re.compile(r"^(?P<name>\S+):$")
NAME_DESC_RE = re.compile(r"^(?P<name>\S+): (?P<description>.*)$", re.DOTALL)


SKILLS_INTRO_WITH_ABSOLUTE_PATHS = (
    "A skill is a set of instructions provided through a `SKILL.md` source. Below is the list of "
    "skills that can be used. Each entry includes a name, description, and source locator. `file` "
    "locators are on the host filesystem, `environment resource` locators are owned by an execution "
    "environment, `orchestrator resource` locators are opaque non-filesystem resources, and `custom "
    "resource` locators use their provider's access mechanism."
)
SKILLS_INTRO_WITH_ALIASES = (
    "A skill is a set of local instructions to follow that is stored in a `SKILL.md` file. Below is "
    "the list of skills that can be used. Each entry includes a name, description, and a short path "
    "that can be expanded into an absolute path using the skill roots table."
)


def approx_tokens(text: str) -> int:
    """``approx_token_count_from_bytes`` — ceiling division over UTF-8 bytes."""
    return (len(text.encode("utf-8")) + APPROX_BYTES_PER_TOKEN - 1) // APPROX_BYTES_PER_TOKEN


def render_available_skills_body(root_lines: list[str], skill_lines: list[str]) -> str:
    """Port of ``render_available_skills_body``, needed for the alias table cost."""
    lines = ["## Skills"]
    if root_lines:
        lines.append(SKILLS_INTRO_WITH_ALIASES)
        lines.append(ROOTS_HEADER)
        lines.extend(root_lines)
    else:
        lines.append(SKILLS_INTRO_WITH_ABSOLUTE_PATHS)
    lines.append(AVAILABLE_HEADER)
    lines.extend(skill_lines)
    return "\n" + "\n".join(lines) + "\n"


def alias_table_cost_tokens(root_lines: list[str]) -> int:
    """``aliased_metadata_overhead_cost`` — a *difference* of two whole-body costs.

    Not the sum of per-line costs. The two bodies differ by the intro text, the
    roots header, and the root lines, and each side is rounded once, so summing
    root lines individually gives a different number.
    """
    if not root_lines:
        return 0
    return approx_tokens(render_available_skills_body(root_lines, [])) - approx_tokens(
        render_available_skills_body([], [])
    )


def line_cost_tokens(line: str) -> int:
    """Cost of one rendered listing line, exactly as ``render.rs`` computes it.

    ``line_cost`` appends a newline and ``approx_token_count_from_bytes`` is a
    ceiling division over UTF-8 *bytes*, not characters.
    """
    return (len((line + "\n").encode("utf-8")) + APPROX_BYTES_PER_TOKEN - 1) // APPROX_BYTES_PER_TOKEN


def budget_for_window(context_window: int | None) -> tuple[int, str]:
    """Return ``(limit, unit)``. Either/or, never a combination.

    ``default_skill_metadata_budget`` takes the **full** context window
    (``session/mod.rs`` passes ``model_info.context_window``), not the
    95%-effective figure.
    """
    if context_window is not None and context_window > 0:
        return max(1, context_window * SKILL_METADATA_CONTEXT_WINDOW_PERCENT // 100), "tokens"
    return DEFAULT_SKILL_METADATA_CHAR_BUDGET, "characters"


@dataclass
class Entry:
    name: str
    description: str | None
    locator_kind: str
    locator: str
    rendered: str
    cost_tokens: int
    origin: str = "unknown"
    scope: str = "unknown"

    @property
    def is_namespaced(self) -> bool:
        """Plugin entries render as ``namespace:name``."""
        return ":" in self.name


@dataclass
class Listing:
    render_mode: str
    entries: list[Entry]
    root_lines: list[str]
    entry_cost_tokens: int
    root_table_cost_tokens: int
    block_chars: int
    warning: str | None = None
    fingerprint: dict = field(default_factory=dict)

    @property
    def charged_tokens(self) -> int:
        """What actually competes for the budget.

        In alias mode the roots table is subtracted from the limit rather than
        added to the cost; charging it here is equivalent and keeps one number
        comparable across modes.
        """
        return self.entry_cost_tokens + self.root_table_cost_tokens


def _run(args: list[str], cwd: str | Path | None) -> str:
    proc = subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"{' '.join(args)} failed ({proc.returncode}): {proc.stderr[:400]}")
    return proc.stdout


def extract_block(prompt_input: list) -> str:
    """Pull the ``<skills_instructions>`` block out of the prompt dump.

    The dump is a list of messages; the block lives in whichever one contains it,
    so we search rather than indexing a position that could move.
    """
    for message in prompt_input:
        for part in message.get("content", []) or []:
            text = part.get("text", "") if isinstance(part, dict) else ""
            if BLOCK_OPEN in text:
                start = text.index(BLOCK_OPEN)
                end = text.index(BLOCK_CLOSE) + len(BLOCK_CLOSE)
                return text[start:end]
    raise LookupError("no <skills_instructions> block in prompt-input")


def parse_block(block: str) -> Listing:
    """Parse a captured block into entries, render mode, and charged cost."""
    if INTRO_ALIASES in block:
        render_mode = "alias"
    elif INTRO_ABSOLUTE in block:
        render_mode = "absolute"
    else:
        raise ValueError("block matches neither known intro; render.rs may have changed")

    lines = block.splitlines()
    entries: list[Entry] = []
    root_lines: list[str] = []
    section = None

    for line in lines:
        if line.startswith(AVAILABLE_HEADER):
            section = "skills"
            continue
        if line.startswith(ROOTS_HEADER):
            section = "roots"
            continue
        if line.startswith("###") or line.startswith("## "):
            section = None
            continue

        if section == "roots" and line.startswith("- "):
            root_lines.append(line)
            continue
        if section != "skills" or not line.startswith("- "):
            continue

        match = ENTRY_RE.match(line)
        if not match:
            # A ``- `` line inside the skills section that carries no locator is
            # not an entry. Skipping silently is how the roots table once got
            # counted as a fake entry, so this is deliberate and narrow.
            continue

        body = match.group("body")
        name_only = NAME_ONLY_RE.match(body)
        if name_only:
            name, description = name_only.group("name"), None
        else:
            name_desc = NAME_DESC_RE.match(body)
            if not name_desc:
                continue
            name, description = name_desc.group("name"), name_desc.group("description")

        entries.append(
            Entry(
                name=name,
                description=description,
                locator_kind=match.group("kind"),
                locator=match.group("locator"),
                rendered=line,
                cost_tokens=line_cost_tokens(line),
            )
        )

    return Listing(
        render_mode=render_mode,
        entries=entries,
        root_lines=root_lines,
        entry_cost_tokens=sum(e.cost_tokens for e in entries),
        root_table_cost_tokens=alias_table_cost_tokens(root_lines),
        block_chars=len(block),
        warning=_find_warning(block),
    )


def _find_warning(block: str) -> str | None:
    """Codex states omission in the prompt; description truncation it does not."""
    for marker in (
        "Exceeded skills context budget",
        "Skill descriptions were shortened",
    ):
        index = block.find(marker)
        if index != -1:
            return block[index : block.find("\n", index) if block.find("\n", index) != -1 else None]
    return None


def models(cwd: str | Path | None = None) -> list[dict]:
    """``codex debug models`` — the source of the context window the budget uses.

    Already emits JSON; there is no ``--json`` flag. Returns the ``models`` list,
    each carrying ``slug``, ``context_window``, ``max_context_window``, and a
    separate ``effective_context_window_percent``. The budget uses
    ``context_window`` — the full window — so the effective percentage is
    recorded but deliberately not applied.
    """
    return json.loads(_run(["codex", "debug", "models"], cwd)).get("models", [])


def active_model(codex_home: Path | None = None) -> str | None:
    """The model this machine actually runs, from ``config.toml``.

    ``debug models`` lists the catalog without marking which is active, and the
    budget is a function of the active model's window. Read key-scoped: only the
    top-level ``model`` assignment, never the whole file.
    """
    home = codex_home or (Path.home() / ".codex")
    config = home / "config.toml"
    if not config.exists():
        return None
    for line in config.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("["):
            break  # past the top-level table; nested tables have their own `model`
        match = re.match(r'^model\s*=\s*"([^"]+)"', stripped)
        if match:
            return match.group(1)
    return None


def probe(cwd: str | Path | None = None) -> Listing:
    """Run the probe live and parse the result."""
    raw = _run(["codex", "debug", "prompt-input"], cwd)
    listing = parse_block(extract_block(json.loads(raw)))
    listing.fingerprint = fingerprint(cwd)
    return listing


def fingerprint(cwd: str | Path | None = None) -> dict:
    """Identify the harness this evidence came from. A change invalidates it."""
    version = _run(["codex", "--version"], cwd).strip()
    catalog = models(cwd)
    slug = active_model()
    entry = next((m for m in catalog if m.get("slug") == slug), None)
    if entry is None:
        # No configured model means Codex picks its own default. Record the
        # ambiguity rather than silently adopting the first catalog row: the
        # windows happen to agree today, and that is not a guarantee.
        windows = {m.get("context_window") for m in catalog if m.get("context_window")}
        window = windows.pop() if len(windows) == 1 else None
        resolution = "catalog-unanimous" if window else "indeterminate"
    else:
        window = entry.get("context_window")
        resolution = "configured"

    limit, unit = budget_for_window(window)
    return {
        "harness": "codex",
        "version": version,
        "model": slug,
        "model_resolution": resolution,
        "context_window": window,
        "effective_context_window_percent": (entry or {}).get("effective_context_window_percent"),
        "budget_limit": limit,
        "budget_unit": unit,
    }


def is_stale(recorded: dict, current: dict) -> list[str]:
    """Fields that changed between two fingerprints.

    Any non-empty result invalidates evidence derived under ``recorded``
    (EV-LEG-03). Returning the field names rather than a bool keeps the report
    able to say *what* changed.
    """
    keys = set(recorded) | set(current)
    return sorted(k for k in keys if recorded.get(k) != current.get(k))


CODEX_HOME_RE = re.compile(r"^(?P<home>.*/\.codex)/")


def infer_codex_home(listing: Listing) -> str | None:
    """Find the Codex home the *capture* was taken under, from its own locators.

    Classification must never depend on the machine reading the evidence. Using
    ``Path.home()`` here works on the capture machine and silently misclassifies
    everywhere else: plugin detection returns zero and bundled ``.system`` skills
    get filed as dojo-managed, because the needles simply never match. That is
    the filesystem-versus-evidence error one more time, so the home is read from
    the listing instead.

    Every Codex listing carries its bundled ``.system`` skills, so at least one
    ``…/.codex/`` locator is always present.
    """
    for entry in listing.entries:
        locator = _absolute(entry.locator, listing.root_lines)
        if match := CODEX_HOME_RE.match(locator):
            return match.group("home")
    for line in listing.root_lines:
        if match := CODEX_HOME_RE.match(re.sub(r"^- `\w+` = `|`$", "", line) + "/"):
            return match.group("home")
    return None


def classify(
    listing: Listing,
    dojo_skills_root: Path,
    codex_home: Path | str | None = None,
    cwd: Path | None = None,
) -> Listing:
    """Label each entry's origin and scope from its locator.

    Origins are ``dojo-managed`` (canonical catalog, by name), ``harness-bundled``
    (Codex's own ``.system`` and runtime skills), ``plugin`` (a Codex plugin
    cache), and ``foreign`` (installed but not ours). Note the plugin needle is
    Codex's own cache path — reusing the standardizer's Claude-only needle here
    yields zero and hides every plugin entry.
    """
    canonical = {p.name for p in dojo_skills_root.iterdir() if p.is_dir() and not p.name.startswith("_")}
    home = str(codex_home) if codex_home else infer_codex_home(listing)
    if home is None:
        raise ValueError(
            "cannot determine the Codex home for this listing; refusing to classify, "
            "because every origin would silently fall through to dojo-managed or foreign"
        )
    plugin_cache = f"{home}/plugins/"
    system_root = f"{home}/skills/.system/"
    # Codex's project scope is `.agents/skills` under the session cwd — not
    # `.claude/skills` (Claude Code's) and not `.agent/skills` (nobody's).
    #
    # It must be **resolved**: Codex reports the symlink's target, not the link.
    # A project root that is a symlink into the canonical catalog (which is how
    # every dojo checkout exposes itself) appears in the roots table as the
    # canonical path, so an unresolved comparison finds project scope nowhere and
    # reports a confident zero.
    # ``resolve()`` is non-strict, so a link whose target is absent on this
    # machine still resolves. That matters for evidence captured elsewhere: the
    # target need not exist here for the comparison to be meaningful.
    project_root = None
    if cwd:
        candidate = Path(cwd) / ".agents" / "skills"
        if candidate.is_symlink() or candidate.is_dir():
            project_root = f"{candidate.resolve()}/"

    for entry in listing.entries:
        locator = _absolute(entry.locator, listing.root_lines)

        if entry.locator_kind != "file":
            entry.origin = "harness-bundled"
        elif plugin_cache in locator:
            entry.origin = "plugin"
        elif system_root in locator or "codex-primary-runtime" in locator:
            entry.origin = "harness-bundled"
        elif ":" not in entry.name and entry.name in canonical:
            entry.origin = "dojo-managed"
        else:
            entry.origin = "foreign"

        entry.scope = "project" if project_root and locator.startswith(project_root) else "user"
    return listing


def _absolute(locator: str, root_lines: list[str]) -> str:
    """Expand an alias-mode locator (``r2/imagegen/SKILL.md``) to an absolute path.

    Classification must not depend on render mode: the same skill is `plugin` in
    both modes, and in alias mode its locator carries no path to match against.
    """
    if locator.startswith("/"):
        return locator
    for line in root_lines:
        match = re.match(r"^- `(?P<alias>\w+)` = `(?P<path>.*)`$", line)
        if match and locator.startswith(match.group("alias") + "/"):
            return match.group("path") + locator[len(match.group("alias")) :]
    return locator


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cwd", default=".", help="working directory to probe")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    parser.add_argument("--from-fixture", help="parse a captured prompt-input JSON instead of probing")
    args = parser.parse_args(argv)

    if args.from_fixture:
        listing = parse_block(extract_block(json.loads(Path(args.from_fixture).read_text())))
    else:
        listing = probe(args.cwd)

    if args.json:
        payload = asdict(listing)
        payload["charged_tokens"] = listing.charged_tokens
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    else:
        limit = listing.fingerprint.get("budget_limit") or 0
        print(f"render mode      : {listing.render_mode}")
        print(f"entries          : {len(listing.entries)}")
        print(f"namespaced       : {sum(1 for e in listing.entries if e.is_namespaced)}")
        print(f"charged tokens   : {listing.charged_tokens}")
        print(f"block chars      : {listing.block_chars}")
        if limit:
            print(f"budget           : {limit} ({100 * listing.charged_tokens / limit:.1f}%)")
        if listing.warning:
            print(f"warning          : {listing.warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
