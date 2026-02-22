#!/usr/bin/env python3
"""
Skill Initializer - Creates a new skill from template.

Usage:
    init_skill.py <skill-name> --path <path> [--resources scripts,references,assets] [--examples]
    init_skill.py <skill-name> --path <path> [--with-openai-agent] [--interface key=value]

Examples:
    init_skill.py my-new-skill --path skills/public
    init_skill.py my-new-skill --path skills/public --resources scripts,references --examples
    init_skill.py my-skill --path skills/public --with-openai-agent
    init_skill.py my-skill --path skills/public --interface short_description="Short UI label"
"""

import argparse
import re
import sys
from pathlib import Path

MAX_SKILL_NAME_LENGTH = 64
ALLOWED_RESOURCES = {"scripts", "references", "assets"}

try:
    from generate_openai_yaml import write_openai_yaml
except Exception:
    write_openai_yaml = None

SKILL_TEMPLATE = """---
name: {skill_name}
description: "TODO: Complete and informative explanation of what the skill does and when to use it. Include specific scenarios, file types, or tasks that should trigger this skill."
---

# {skill_title}

## Overview

[TODO: 1-2 sentences explaining what this skill enables]

## Structuring This Skill

[TODO: Choose the structure that best fits this skill's purpose. Common patterns:

**1. Workflow-Based** (best for sequential processes)
- Works well when there are clear step-by-step procedures
- Example: DOCX skill with "Workflow Decision Tree" -> "Reading" -> "Creating" -> "Editing"
- Structure: ## Overview -> ## Workflow Decision Tree -> ## Step 1 -> ## Step 2...

**2. Task-Based** (best for tool collections)
- Works well when the skill offers different operations/capabilities
- Example: PDF skill with "Quick Start" -> "Merge PDFs" -> "Split PDFs" -> "Extract Text"
- Structure: ## Overview -> ## Quick Start -> ## Task Category 1 -> ## Task Category 2...

**3. Reference/Guidelines** (best for standards or specifications)
- Works well for brand guidelines, coding standards, or requirements
- Example: Brand styling with "Brand Guidelines" -> "Colors" -> "Typography" -> "Features"
- Structure: ## Overview -> ## Guidelines -> ## Specifications -> ## Usage...

**4. Capabilities-Based** (best for integrated systems)
- Works well when the skill provides multiple interrelated features
- Example: Product Management with "Core Capabilities" -> numbered capability list
- Structure: ## Overview -> ## Core Capabilities -> ### 1. Feature -> ### 2. Feature...

Patterns can be mixed and matched as needed. Most skills combine patterns (e.g., start with task-based, add workflow for complex operations).

Delete this entire "Structuring This Skill" section when done - it's just guidance.]

## [TODO: Replace with the first main section based on chosen structure]

[TODO: Add content here. See examples in existing skills:
- Code samples for technical skills
- Decision trees for complex workflows
- Concrete examples with realistic user requests
- References to scripts/templates/references as needed]

## Resources (optional)

Create only the resource directories this skill actually needs. Delete this section if no resources are required.

### scripts/
Executable code (Python/Bash/etc.) that can be run directly to perform specific operations.

### references/
Documentation and reference material intended to be loaded into context as needed.

### assets/
Files not intended to be loaded into context, but rather used within the output the agent produces.

### agents/ (optional, platform add-on)
Platform-specific metadata files. Only include if your target platform supports them.
For OpenAI/Codex-compatible metadata, see `references/openai_yaml.md`.

---

**Not every skill requires all resource or platform directories.**
"""

EXAMPLE_SCRIPT = '''#!/usr/bin/env python3
"""Example helper script for {skill_name}."""


def main():
    print("This is an example script for {skill_name}")


if __name__ == "__main__":
    main()
'''

EXAMPLE_REFERENCE = """# Reference Documentation for {skill_title}

This is a placeholder for detailed reference documentation.
Replace with actual reference content or delete if not needed.
"""

EXAMPLE_ASSET = """# Example Asset File

This placeholder represents where asset files would be stored.
Replace with actual assets or delete if not needed.
"""


def normalize_skill_name(skill_name):
    """Normalize a skill name to lowercase hyphen-case."""
    normalized = skill_name.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = normalized.strip("-")
    normalized = re.sub(r"-{2,}", "-", normalized)
    return normalized


def title_case_skill_name(skill_name):
    """Convert hyphenated skill name to Title Case for display."""
    return " ".join(word.capitalize() for word in skill_name.split("-"))


def parse_resources(raw_resources):
    if not raw_resources:
        return []
    resources = [item.strip() for item in raw_resources.split(",") if item.strip()]
    invalid = sorted({item for item in resources if item not in ALLOWED_RESOURCES})
    if invalid:
        allowed = ", ".join(sorted(ALLOWED_RESOURCES))
        print(f"[ERROR] Unknown resource type(s): {', '.join(invalid)}")
        print(f"   Allowed: {allowed}")
        sys.exit(1)
    deduped = []
    seen = set()
    for resource in resources:
        if resource not in seen:
            deduped.append(resource)
            seen.add(resource)
    return deduped


def create_resource_dirs(skill_dir, skill_name, skill_title, resources, include_examples):
    for resource in resources:
        resource_dir = skill_dir / resource
        resource_dir.mkdir(exist_ok=True)
        if resource == "scripts":
            if include_examples:
                example_script = resource_dir / "example.py"
                example_script.write_text(EXAMPLE_SCRIPT.format(skill_name=skill_name), encoding="utf-8")
                example_script.chmod(0o755)
                print("[OK] Created scripts/example.py")
            else:
                print("[OK] Created scripts/")
        elif resource == "references":
            if include_examples:
                example_reference = resource_dir / "api_reference.md"
                example_reference.write_text(EXAMPLE_REFERENCE.format(skill_title=skill_title), encoding="utf-8")
                print("[OK] Created references/api_reference.md")
            else:
                print("[OK] Created references/")
        elif resource == "assets":
            if include_examples:
                example_asset = resource_dir / "example_asset.txt"
                example_asset.write_text(EXAMPLE_ASSET, encoding="utf-8")
                print("[OK] Created assets/example_asset.txt")
            else:
                print("[OK] Created assets/")


def maybe_create_openai_yaml(skill_dir, skill_name, raw_overrides):
    if write_openai_yaml is None:
        print("[ERROR] OpenAI metadata helper not available: scripts/generate_openai_yaml.py")
        return False
    result = write_openai_yaml(skill_dir, skill_name, raw_overrides)
    return bool(result)


def init_skill(skill_name, path, resources, include_examples, with_openai_agent, interface_overrides):
    """
    Initialize a new skill directory with template SKILL.md.

    Args:
        skill_name: Name of the skill
        path: Path where the skill directory should be created
        resources: Resource directories to create
        include_examples: Whether to create example files in resource directories
        with_openai_agent: Whether to create agents/openai.yaml
        interface_overrides: Optional key=value pairs for openai.yaml fields

    Returns:
        Path to created skill directory, or None if error
    """
    skill_dir = Path(path).resolve() / skill_name

    if skill_dir.exists():
        print(f"[ERROR] Skill directory already exists: {skill_dir}")
        return None

    try:
        skill_dir.mkdir(parents=True, exist_ok=False)
        print(f"[OK] Created skill directory: {skill_dir}")
    except Exception as exc:
        print(f"[ERROR] Error creating directory: {exc}")
        return None

    skill_title = title_case_skill_name(skill_name)
    skill_content = SKILL_TEMPLATE.format(skill_name=skill_name, skill_title=skill_title)

    skill_md_path = skill_dir / "SKILL.md"
    try:
        skill_md_path.write_text(skill_content, encoding="utf-8")
        print("[OK] Created SKILL.md")
    except Exception as exc:
        print(f"[ERROR] Error creating SKILL.md: {exc}")
        return None

    if resources:
        try:
            create_resource_dirs(skill_dir, skill_name, skill_title, resources, include_examples)
        except Exception as exc:
            print(f"[ERROR] Error creating resource directories: {exc}")
            return None

    should_create_openai_agent = with_openai_agent or bool(interface_overrides)
    if should_create_openai_agent:
        if not maybe_create_openai_yaml(skill_dir, skill_name, interface_overrides):
            return None

    print(f"\n[OK] Skill '{skill_name}' initialized successfully at {skill_dir}")
    print("\nNext steps:")
    print("1. Edit SKILL.md to complete the TODO items and update the description")
    if resources:
        if include_examples:
            print("2. Customize or delete the example files in selected resource directories")
        else:
            print("2. Add resources to scripts/, references/, and assets/ as needed")
    else:
        print("2. Create resource directories only if needed (scripts/, references/, assets/)")
    if should_create_openai_agent:
        print("3. Review agents/openai.yaml for platform-specific UI metadata")
        print("4. Run the validator when ready to check skill structure")
    else:
        print("3. Add optional platform metadata only if needed (for example agents/openai.yaml)")
        print("4. Run the validator when ready to check skill structure")

    return skill_dir


def main():
    parser = argparse.ArgumentParser(
        description="Create a new skill directory with a SKILL.md template.",
    )
    parser.add_argument("skill_name", help="Skill name (normalized to hyphen-case)")
    parser.add_argument("--path", required=True, help="Output directory for the skill")
    parser.add_argument(
        "--resources",
        default="",
        help="Comma-separated list: scripts,references,assets",
    )
    parser.add_argument(
        "--examples",
        action="store_true",
        help="Create example files inside the selected resource directories",
    )
    parser.add_argument(
        "--with-openai-agent",
        action="store_true",
        help="Create optional agents/openai.yaml metadata",
    )
    parser.add_argument(
        "--interface",
        action="append",
        default=[],
        help="OpenAI interface override in key=value format (repeatable)",
    )
    args = parser.parse_args()

    raw_skill_name = args.skill_name
    skill_name = normalize_skill_name(raw_skill_name)
    if not skill_name:
        print("[ERROR] Skill name must include at least one letter or digit.")
        sys.exit(1)
    if len(skill_name) > MAX_SKILL_NAME_LENGTH:
        print(
            f"[ERROR] Skill name '{skill_name}' is too long ({len(skill_name)} characters). "
            f"Maximum is {MAX_SKILL_NAME_LENGTH} characters."
        )
        sys.exit(1)
    if skill_name != raw_skill_name:
        print(f"Note: Normalized skill name from '{raw_skill_name}' to '{skill_name}'.")

    resources = parse_resources(args.resources)
    if args.examples and not resources:
        print("[ERROR] --examples requires --resources to be set.")
        sys.exit(1)

    print(f"Initializing skill: {skill_name}")
    print(f"   Location: {args.path}")
    if resources:
        print(f"   Resources: {', '.join(resources)}")
        if args.examples:
            print("   Examples: enabled")
    else:
        print("   Resources: none (create as needed)")
    if args.with_openai_agent or args.interface:
        print("   Optional platform metadata: OpenAI/Codex")
    print()

    result = init_skill(
        skill_name,
        args.path,
        resources,
        args.examples,
        args.with_openai_agent,
        args.interface,
    )

    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
