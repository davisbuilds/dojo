#!/bin/sh
""":"
if command -v python >/dev/null 2>&1; then
    exec python "$0" "$@"
fi
exec python3 "$0" "$@"
":"""
"""
Generate skills.json — a machine-readable manifest of all skills in the repo.

Usage:
    python scripts/generate_skills_manifest.py [skills-directory] [output-file]

Defaults:
    skills-directory: skills/
    output-file:      skills.json

Walks skills/*/SKILL.md, extracts YAML frontmatter (name, description),
and writes a JSON manifest that any agent harness can consume.
"""

import json
import os
import re
import sys
import yaml
from pathlib import Path


def extract_frontmatter(skill_md_path):
    """Extract YAML frontmatter from a SKILL.md file."""
    content = skill_md_path.read_text()
    if not content.startswith('---'):
        return None

    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None

    try:
        frontmatter = yaml.safe_load(match.group(1))
        if not isinstance(frontmatter, dict):
            return None
        return frontmatter
    except yaml.YAMLError:
        return None


def generate_manifest(skills_dir, output_path):
    """Generate skills.json from all SKILL.md files."""
    skills_dir = Path(skills_dir)
    if not skills_dir.is_dir():
        print(f"Error: {skills_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    skills = []
    for skill_md in sorted(skills_dir.glob('*/SKILL.md')):
        frontmatter = extract_frontmatter(skill_md)
        if frontmatter is None:
            print(f"Warning: skipping {skill_md} (invalid frontmatter)", file=sys.stderr)
            continue

        name = frontmatter.get('name', '')
        description = frontmatter.get('description', '')
        if not name or not description:
            print(f"Warning: skipping {skill_md} (missing name or description)", file=sys.stderr)
            continue

        entry = {
            'name': name,
            'description': description,
            'path': str(skill_md.parent.relative_to(skills_dir.parent)),
        }

        # Include optional fields if present
        if 'license' in frontmatter:
            entry['license'] = frontmatter['license']
        if 'allowed-tools' in frontmatter:
            entry['allowed-tools'] = frontmatter['allowed-tools']

        skills.append(entry)

    manifest = {
        'version': 1,
        'skills': skills,
    }

    output_path = Path(output_path)
    output_path.write_text(json.dumps(manifest, indent=2) + '\n')
    print(f"Generated {output_path} with {len(skills)} skills")


if __name__ == '__main__':
    # Resolve repo root relative to this script
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent

    skills_dir = sys.argv[1] if len(sys.argv) > 1 else str(repo_root / 'skills')
    output_file = sys.argv[2] if len(sys.argv) > 2 else str(repo_root / 'skills.json')

    generate_manifest(skills_dir, output_file)
