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
    python scripts/generate_skills_manifest.py --check [skills-directory] [output-file]

Defaults:
    skills-directory: skills/
    output-file:      skills.json

Walks skills/*/SKILL.md, extracts YAML frontmatter (name, description, version),
and writes a JSON manifest that any agent harness can consume.
"""

import argparse
import json
import re
import sys
import yaml
from pathlib import Path

SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)


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


def build_manifest(skills_dir):
    """Build manifest data from all SKILL.md files."""
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
        version = normalized_version(frontmatter.get('version', ''))
        if not name or not description or version is None:
            print(f"Warning: skipping {skill_md} (missing name/description or invalid version)", file=sys.stderr)
            continue

        entry = {
            'name': name,
            'description': description,
            'path': str(skill_md.parent.relative_to(skills_dir.parent)),
            'version': version,
        }

        # Include optional fields if present
        if 'license' in frontmatter:
            entry['license'] = frontmatter['license']
        if 'allowed-tools' in frontmatter:
            entry['allowed-tools'] = frontmatter['allowed-tools']
        if 'triggers' in frontmatter:
            entry['triggers'] = frontmatter['triggers']

        skills.append(entry)

    return {
        'version': 1,
        'skills': skills,
    }


def normalized_version(version):
    if not isinstance(version, str):
        return None
    version = version.strip()
    if not version or version.startswith('v') or SEMVER_RE.match(version) is None:
        return None
    return version


def render_manifest(manifest):
    return json.dumps(manifest, indent=2) + '\n'


def generate_manifest(skills_dir, output_path):
    """Generate skills.json from all SKILL.md files."""
    manifest = build_manifest(skills_dir)
    output_path = Path(output_path)
    output_path.write_text(render_manifest(manifest))
    print(f"Generated {output_path} with {len(manifest['skills'])} skills")
    return manifest


def check_manifest(skills_dir, output_path):
    """Return 0 when output_path already matches generated manifest."""
    manifest = build_manifest(skills_dir)
    output_path = Path(output_path)
    expected = render_manifest(manifest)
    if not output_path.exists():
        print(f"Manifest is stale: {output_path} does not exist.", file=sys.stderr)
        return 1
    current = output_path.read_text(encoding='utf-8')
    if current == expected:
        print("Manifest is up to date.")
        return 0
    print(f"Manifest is stale (run scripts/generate_skills_manifest.py).", file=sys.stderr)
    return 1


if __name__ == '__main__':
    # Resolve repo root relative to this script
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('skills_dir', nargs='?', default=str(repo_root / 'skills'))
    parser.add_argument('output_file', nargs='?', default=str(repo_root / 'skills.json'))
    parser.add_argument('--check', action='store_true', help='Report stale manifest without writing')
    args = parser.parse_args()

    if args.check:
        sys.exit(check_manifest(args.skills_dir, args.output_file))
    generate_manifest(args.skills_dir, args.output_file)
