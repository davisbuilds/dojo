#!/usr/bin/env bash
# Setup script for secure-code skill: install and validate semgrep CLI.
set -euo pipefail

echo "=== secure-code setup ==="

if command -v semgrep &>/dev/null; then
  echo "semgrep already installed: $(semgrep --version 2>&1 | head -1)"
  exit 0
fi

if ! command -v brew &>/dev/null; then
  echo "ERROR: brew is not available."
  echo "Install Homebrew first: https://brew.sh"
  echo "Then run: brew install semgrep"
  exit 1
fi

echo "Installing semgrep via brew..."
brew install semgrep

if command -v semgrep &>/dev/null; then
  echo "semgrep installed successfully: $(semgrep --version 2>&1 | head -1)"
else
  echo "ERROR: semgrep installation failed."
  exit 1
fi
