#!/bin/sh
""":"
if command -v python >/dev/null 2>&1; then
    exec python "$0" "$@"
fi
exec python3 "$0" "$@"
":"""
"""PreToolUse hook: validate the SKILL.md a Write/Edit *would produce*.

Reads the tool-input JSON on stdin, projects the resulting SKILL.md content, and
validates that. It deliberately does not validate the file already on disk: doing
so deadlocks, because an invalid SKILL.md then blocks the very edit that would
repair it.

Exit codes:
    0 = allow (not a SKILL.md, unknown tool, or the projected content is valid)
    2 = block (the projected content would be an invalid SKILL.md)

Anything it cannot reason about (malformed input, a missing file, an Edit whose
old_string is absent) is allowed through. The tool itself, the post-write hooks,
and CI remain the backstops.
"""

import json
import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_validator():
    """Import the skill validator lazily, returning None if it is unavailable.

    A guard hook must never block an edit because of its own missing dependency
    (e.g. PyYAML absent in a fresh checkout). Callers treat None as "skip".
    """
    sys.path.insert(0, str(REPO_ROOT / "skills" / "skill-creator" / "scripts"))
    try:
        from quick_validate import validate_skill
    except Exception:  # missing dependency, broken import — degrade to allow
        return None
    return validate_skill


def project_content(tool_input: dict, target: Path) -> str | None:
    """Return the SKILL.md content this tool call would leave on disk.

    None means "cannot project" — allow the call through.
    """
    if "content" in tool_input:  # Write
        content = tool_input.get("content")
        return content if isinstance(content, str) else None

    if "old_string" in tool_input:  # Edit
        old = tool_input.get("old_string")
        new = tool_input.get("new_string")
        if not isinstance(old, str) or not isinstance(new, str) or not target.is_file():
            return None
        current = target.read_text(encoding="utf-8")
        if old not in current:
            return None
        count = -1 if tool_input.get("replace_all") else 1
        return current.replace(old, new, count)

    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        tool_input = payload["tool_input"]
        file_path = Path(tool_input["file_path"])
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return 0

    if file_path.name != "SKILL.md":
        return 0

    projected = project_content(tool_input, file_path)
    if projected is None:
        return 0

    validate_skill = _load_validator()
    if validate_skill is None:
        # Dependency unavailable — allow the edit rather than block it. The Stop
        # hook's skill-structure check and CI remain the backstops.
        return 0

    # Validate a throwaway copy so the real file is untouched on failure.
    tmp_root = Path(tempfile.mkdtemp())
    try:
        skill_dir = tmp_root / file_path.parent.name
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(projected, encoding="utf-8")
        valid, message = validate_skill(skill_dir)
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)

    if valid:
        return 0

    print(f"SKILL.md validation failed for {file_path.parent.name}:", file=sys.stderr)
    print(f"  {message}", file=sys.stderr)
    print("\nThis blocks the write because the *resulting* file would be invalid.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
