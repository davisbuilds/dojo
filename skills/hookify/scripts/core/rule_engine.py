#!/usr/bin/env python3
"""Rule evaluation engine for hookify.

Harness-agnostic: outputs a generic result dict. The hook entry points
adapt the output to the calling harness's expected JSON schema.
"""

import re
import sys
from functools import lru_cache
from typing import List, Dict, Any, Optional

from core.config_loader import Rule, Condition


@lru_cache(maxsize=128)
def compile_regex(pattern: str) -> re.Pattern:
    return re.compile(pattern, re.IGNORECASE)


class RuleEngine:
    """Evaluates rules against hook input data."""

    def evaluate_rules(self, rules: List[Rule], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate all rules. Returns a harness-neutral result dict.

        Result keys:
          matched: bool
          action: "block" | "warn" | None
          messages: list[str]
          rule_names: list[str]
        """
        blocking = []
        warnings = []

        for rule in rules:
            if self._rule_matches(rule, input_data):
                entry = {"name": rule.name, "message": rule.message}
                if rule.action == 'block':
                    blocking.append(entry)
                else:
                    warnings.append(entry)

        if not blocking and not warnings:
            return {"matched": False, "action": None, "messages": [], "rule_names": []}

        combined = blocking or warnings
        return {
            "matched": True,
            "action": "block" if blocking else "warn",
            "messages": [e["message"] for e in combined],
            "rule_names": [e["name"] for e in combined],
        }

    def _rule_matches(self, rule: Rule, input_data: Dict[str, Any]) -> bool:
        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})

        if rule.tool_matcher and not self._matches_tool(rule.tool_matcher, tool_name):
            return False
        if not rule.conditions:
            return False

        return all(
            self._check_condition(c, tool_name, tool_input, input_data)
            for c in rule.conditions
        )

    def _matches_tool(self, matcher: str, tool_name: str) -> bool:
        if matcher == '*':
            return True
        return tool_name in matcher.split('|')

    def _check_condition(self, condition: Condition, tool_name: str,
                         tool_input: Dict[str, Any], input_data: Dict[str, Any] = None) -> bool:
        field_value = self._extract_field(condition.field, tool_name, tool_input, input_data)
        if field_value is None:
            return False

        op = condition.operator
        pat = condition.pattern

        if op == 'regex_match':
            return self._regex_match(pat, field_value)
        elif op == 'contains':
            return pat in field_value
        elif op == 'equals':
            return pat == field_value
        elif op == 'not_contains':
            return pat not in field_value
        elif op == 'starts_with':
            return field_value.startswith(pat)
        elif op == 'ends_with':
            return field_value.endswith(pat)
        return False

    def _extract_field(self, field: str, tool_name: str,
                       tool_input: Dict[str, Any], input_data: Dict[str, Any] = None) -> Optional[str]:
        # Direct tool_input fields
        if field in tool_input:
            value = tool_input[field]
            return str(value) if not isinstance(value, str) else value

        # Stop/prompt event fields
        if input_data:
            if field == 'reason':
                return input_data.get('reason', '')
            elif field == 'transcript':
                transcript_path = input_data.get('transcript_path')
                if transcript_path:
                    try:
                        with open(transcript_path, 'r') as f:
                            return f.read()
                    except Exception:
                        return ''
            elif field == 'user_prompt':
                return input_data.get('user_prompt', '')

        # Tool-specific field extraction
        if tool_name == 'Bash' and field == 'command':
            return tool_input.get('command', '')
        elif tool_name in ('Write', 'Edit', 'MultiEdit'):
            if field in ('content', 'new_text', 'new_string'):
                return tool_input.get('content') or tool_input.get('new_string', '')
            elif field in ('old_text', 'old_string'):
                return tool_input.get('old_string', '')
            elif field == 'file_path':
                return tool_input.get('file_path', '')

        return None

    def _regex_match(self, pattern: str, text: str) -> bool:
        try:
            return bool(compile_regex(pattern).search(text))
        except re.error as e:
            print(f"Invalid regex '{pattern}': {e}", file=sys.stderr)
            return False
