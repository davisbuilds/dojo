#!/usr/bin/env python3
"""Configuration loader for hookify rules.

Loads and parses hookify.*.local.md files from the project's config directory.
Harness-agnostic: searches .claude/, .agents/, .codex/, and .hookify/ directories.
"""

import os
import sys
import glob
import re
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class Condition:
    """A single condition for matching."""
    field: str
    operator: str
    pattern: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Condition':
        return cls(
            field=data.get('field', ''),
            operator=data.get('operator', 'regex_match'),
            pattern=data.get('pattern', '')
        )


@dataclass
class Rule:
    """A hookify rule."""
    name: str
    enabled: bool
    event: str
    pattern: Optional[str] = None
    conditions: List[Condition] = field(default_factory=list)
    action: str = "warn"
    tool_matcher: Optional[str] = None
    message: str = ""

    @classmethod
    def from_dict(cls, frontmatter: Dict[str, Any], message: str) -> 'Rule':
        conditions = []

        if 'conditions' in frontmatter:
            cond_list = frontmatter['conditions']
            if isinstance(cond_list, list):
                conditions = [Condition.from_dict(c) for c in cond_list]

        simple_pattern = frontmatter.get('pattern')
        if simple_pattern and not conditions:
            event = frontmatter.get('event', 'all')
            if event == 'bash':
                fld = 'command'
            elif event == 'file':
                fld = 'new_text'
            else:
                fld = 'content'

            conditions = [Condition(field=fld, operator='regex_match', pattern=simple_pattern)]

        return cls(
            name=frontmatter.get('name', 'unnamed'),
            enabled=frontmatter.get('enabled', True),
            event=frontmatter.get('event', 'all'),
            pattern=simple_pattern,
            conditions=conditions,
            action=frontmatter.get('action', 'warn'),
            tool_matcher=frontmatter.get('tool_matcher'),
            message=message.strip()
        )


def extract_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
    """Extract YAML frontmatter and message body from markdown."""
    if not content.startswith('---'):
        return {}, content

    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content

    frontmatter_text = parts[1]
    message = parts[2].strip()

    frontmatter = {}
    lines = frontmatter_text.split('\n')

    current_key = None
    current_list = []
    current_dict = {}
    in_list = False
    in_dict_item = False

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue

        indent = len(line) - len(line.lstrip())

        if indent == 0 and ':' in line and not line.strip().startswith('-'):
            if in_list and current_key:
                if in_dict_item and current_dict:
                    current_list.append(current_dict)
                    current_dict = {}
                frontmatter[current_key] = current_list
                in_list = False
                in_dict_item = False
                current_list = []

            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            if not value:
                current_key = key
                in_list = True
                current_list = []
            else:
                value = value.strip('"').strip("'")
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                frontmatter[key] = value

        elif stripped.startswith('-') and in_list:
            if in_dict_item and current_dict:
                current_list.append(current_dict)
                current_dict = {}

            item_text = stripped[1:].strip()

            if ':' in item_text and ',' in item_text:
                item_dict = {}
                for part in item_text.split(','):
                    if ':' in part:
                        k, v = part.split(':', 1)
                        item_dict[k.strip()] = v.strip().strip('"').strip("'")
                current_list.append(item_dict)
                in_dict_item = False
            elif ':' in item_text:
                in_dict_item = True
                k, v = item_text.split(':', 1)
                current_dict = {k.strip(): v.strip().strip('"').strip("'")}
            else:
                current_list.append(item_text.strip('"').strip("'"))
                in_dict_item = False

        elif indent > 2 and in_dict_item and ':' in line:
            k, v = stripped.split(':', 1)
            current_dict[k.strip()] = v.strip().strip('"').strip("'")

    if in_list and current_key:
        if in_dict_item and current_dict:
            current_list.append(current_dict)
        frontmatter[current_key] = current_list

    return frontmatter, message


# Directories to search for rule files, in priority order.
# Harness-agnostic: works with Claude Code, Agents SDK, Codex, or standalone.
RULE_DIRS = ['.claude', '.agents', '.codex', '.hookify']


def load_rules(event: Optional[str] = None) -> List[Rule]:
    """Load all hookify rules from known config directories.

    Searches .claude/, .agents/, .codex/, and .hookify/ for hookify.*.local.md files.
    Deduplicates by rule name (first match wins).
    """
    rules = []
    seen_names = set()

    for dir_name in RULE_DIRS:
        pattern = os.path.join(dir_name, 'hookify.*.local.md')
        for file_path in glob.glob(pattern):
            try:
                rule = load_rule_file(file_path)
                if not rule or not rule.enabled:
                    continue
                if rule.name in seen_names:
                    continue
                if event and rule.event != 'all' and rule.event != event:
                    continue
                seen_names.add(rule.name)
                rules.append(rule)
            except Exception as e:
                print(f"Warning: Failed to load {file_path}: {e}", file=sys.stderr)
                continue

    return rules


def load_rule_file(file_path: str) -> Optional[Rule]:
    """Load a single rule file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        frontmatter, message = extract_frontmatter(content)
        if not frontmatter:
            return None
        return Rule.from_dict(frontmatter, message)
    except Exception as e:
        print(f"Error: Cannot load {file_path}: {e}", file=sys.stderr)
        return None
