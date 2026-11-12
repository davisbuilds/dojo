#!/bin/bash

# PostToolUse hook: validate docs/specs/*-spec.md after write/edit against the
# write-spec schema with strict filename validation.
# Exit codes: 0 = pass / not applicable, 2 = validation failed.

exec bash "$(dirname -- "${BASH_SOURCE[0]}")/post-tool-use-validate-doc.sh" spec
