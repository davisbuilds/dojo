#!/bin/sh
# Optional evidence command. Exit status alone does not determine loop completion.
# Runs once; timeout/cancellation belong to the runtime. Review before execution.
set -eu
cd -- {{CHECK_CWD}}
exec sh -c {{CHECK_COMMAND}}
