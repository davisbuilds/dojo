#!/bin/sh
""":"
if command -v python >/dev/null 2>&1; then
    exec python "$0" "$@"
fi
exec python3 "$0" "$@"
":"""
"""Quick validation script for skills (minimal, portable)."""

import re
import sys
from pathlib import Path

import yaml

MAX_SKILL_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_COMPATIBILITY_LENGTH = 500
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9A-Za-z-][0-9A-Za-z-]*)(?:\.(?:0|[1-9A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
ALLOWED_PROPERTIES = {
    "name",
    "description",
    "skill-type",
    "version",
    "license",
    "allowed-tools",
    "metadata",
    "compatibility",
    "triggers",
}
ALLOWED_SKILL_TYPES = {"workflow", "reference"}


def _extract_frontmatter(content: str):
    if not content.startswith("---"):
        return None
    return re.match(r"^---\n(.*?)\n---", content, re.DOTALL)


def validate_skill(skill_path):
    """Basic validation of a skill folder."""
    skill_path = Path(skill_path)

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text(encoding="utf-8")
    match = _extract_frontmatter(content)
    if not match:
        return False, "Invalid or missing YAML frontmatter"

    frontmatter_text = match.group(1)
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as exc:
        return False, f"Invalid YAML in frontmatter: {exc}"

    if not isinstance(frontmatter, dict):
        return False, "Frontmatter must be a YAML dictionary"

    unexpected_keys = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected_keys:
        return (
            False,
            "Unexpected key(s) in SKILL.md frontmatter: "
            f"{', '.join(sorted(unexpected_keys))}. "
            f"Allowed properties are: {', '.join(sorted(ALLOWED_PROPERTIES))}",
        )

    if "name" not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if "description" not in frontmatter:
        return False, "Missing 'description' in frontmatter"
    if "version" not in frontmatter:
        return False, "Missing 'version' in frontmatter"

    name = frontmatter.get("name")
    if not isinstance(name, str):
        return False, f"Name must be a string, got {type(name).__name__}"
    name = name.strip()
    if not name:
        return False, "Name cannot be empty"
    if not re.match(r"^[a-z0-9-]+$", name):
        return (
            False,
            f"Name '{name}' should be hyphen-case (lowercase letters, digits, and hyphens only)",
        )
    if name.startswith("-") or name.endswith("-") or "--" in name:
        return False, f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
    if len(name) > MAX_SKILL_NAME_LENGTH:
        return (
            False,
            f"Name is too long ({len(name)} characters). "
            f"Maximum is {MAX_SKILL_NAME_LENGTH} characters.",
        )

    description = frontmatter.get("description")
    if not isinstance(description, str):
        return False, f"Description must be a string, got {type(description).__name__}"
    description = description.strip()
    if not description:
        return False, "Description cannot be empty"
    if "<" in description or ">" in description:
        return False, "Description cannot contain angle brackets (< or >)"
    if len(description) > MAX_DESCRIPTION_LENGTH:
        return (
            False,
            f"Description is too long ({len(description)} characters). Maximum is {MAX_DESCRIPTION_LENGTH} characters.",
        )

    version = frontmatter.get("version")
    if not isinstance(version, str):
        return False, f"Version must be a string, got {type(version).__name__}"
    version = version.strip()
    if not version:
        return False, "Version cannot be empty"
    if version.startswith("v"):
        return False, "Version must not use a leading 'v'"
    if not SEMVER_RE.match(version):
        return False, f"Version '{version}' must be valid SemVer, for example 1.0.0"

    skill_type = frontmatter.get("skill-type")
    if skill_type is not None:
        if not isinstance(skill_type, str):
            return False, f"skill-type must be a string, got {type(skill_type).__name__}"
        if skill_type not in ALLOWED_SKILL_TYPES:
            return (
                False,
                f"skill-type must be one of: {', '.join(sorted(ALLOWED_SKILL_TYPES))}. "
                f"Got: {skill_type}",
            )

    triggers = frontmatter.get("triggers")
    if triggers is not None:
        if not isinstance(triggers, list) or not triggers:
            return False, "triggers must be a non-empty list of strings"
        for item in triggers:
            if not isinstance(item, str) or not item.strip():
                return False, "triggers must contain only non-empty strings"

    compatibility = frontmatter.get("compatibility")
    if compatibility is not None:
        if not isinstance(compatibility, str):
            return False, f"Compatibility must be a string, got {type(compatibility).__name__}"
        if len(compatibility) > MAX_COMPATIBILITY_LENGTH:
            return (
                False,
                f"Compatibility is too long ({len(compatibility)} characters). Maximum is {MAX_COMPATIBILITY_LENGTH} characters.",
            )

    return True, "Skill is valid!"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: quick_validate.py <skill_directory>")
        sys.exit(1)

    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)
