#!/usr/bin/env python3
"""Harness adapter for hookify hook output.

Converts the harness-neutral result dict from RuleEngine into the JSON
schema expected by the calling harness.

Supported harnesses:
  - claude: Claude Code / Agents SDK (.claude, .agents settings.json hooks)
  - generic: Plain JSON with matched/action/messages (fallback)

Detection: checks HOOKIFY_HARNESS env var first, then auto-detects from
the stdin JSON structure.
"""

import os
from typing import Dict, Any


def detect_harness(input_data: Dict[str, Any]) -> str:
    """Detect which harness is calling based on env or input shape."""
    env = os.environ.get('HOOKIFY_HARNESS', '').lower()
    if env in ('claude', 'agents'):
        return 'claude'
    if env:
        return env

    # Auto-detect: Claude Code passes hook_event_name
    if 'hook_event_name' in input_data:
        return 'claude'

    return 'generic'


def format_output(result: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert engine result to harness-specific output JSON."""
    if not result.get('matched'):
        return {}

    harness = detect_harness(input_data)

    if harness == 'claude':
        return _format_claude(result, input_data)
    return _format_generic(result)


def _format_claude(result: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format for Claude Code / Agents SDK."""
    hook_event = input_data.get('hook_event_name', '')
    names = result.get('rule_names', [])
    messages = result.get('messages', [])
    combined = "\n\n".join(
        f"**[{n}]**\n{m}" for n, m in zip(names, messages)
    )

    if result['action'] == 'block':
        if hook_event == 'Stop':
            return {"decision": "block", "reason": combined, "systemMessage": combined}
        elif hook_event in ('PreToolUse', 'PostToolUse'):
            return {
                "hookSpecificOutput": {
                    "hookEventName": hook_event,
                    "permissionDecision": "deny"
                },
                "systemMessage": combined
            }
        return {"systemMessage": combined}

    # warn
    return {"systemMessage": combined}


def _format_generic(result: Dict[str, Any]) -> Dict[str, Any]:
    """Format for generic / unknown harnesses."""
    return {
        "matched": True,
        "action": result['action'],
        "rule_names": result['rule_names'],
        "messages": result['messages'],
    }
