# Loop state: {{NAME}}

State lives on disk, not in context. The loop forgets everything between runs; this file and git history are how it remembers. Every iteration appends here.

## Goal

{{GOAL}}

## Oracle

`./verify.sh` (runs: `{{DONE_WHEN}}`) — exit 0 means done.

## Status

- [ ] Not started

## Log

<!-- Newest first. One entry per iteration: what was tried / what passed / what is still open. -->
<!-- Machine-readable per-iteration events also append to `.loop_log.jsonl` (one JSON object per line)
     so a human can diagnose how the loop died: runaway, stuck (same failure repeating), or silent death. -->
