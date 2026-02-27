#!/usr/bin/env python3
"""UserPromptSubmit hook entry point. Harness-agnostic."""

import os, sys, json

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from core.config_loader import load_rules
from core.rule_engine import RuleEngine
from hooks.adapter import format_output


def main():
    try:
        input_data = json.load(sys.stdin)
        rules = load_rules(event='prompt')
        result = RuleEngine().evaluate_rules(rules, input_data)
        print(json.dumps(format_output(result, input_data)))
    except Exception as e:
        print(json.dumps({"systemMessage": f"Hookify error: {e}"}))
    finally:
        sys.exit(0)


if __name__ == '__main__':
    main()
