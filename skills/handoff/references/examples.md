# Handoff examples

Illustrative shapes, not required sections or claims about a real repository.

## Compact continuation through the harness

> Resume the CSV export fix. The user wants stable column ordering; they approved
> implementation and a draft PR, not merging or deployment. Parser changes are
> committed, but the empty-result regression is unfinished. Check the worktree
> and `AGENTS.md`, then continue in `tests/test_export.py`. The last parser-only
> test run passed; integration coverage is still outstanding. The accepted
> contract is `docs/specs/export-order.md`; do not reopen that settled decision.

This can go through an existing compaction or agent-transfer channel without
creating a second file. It preserves direction while naming the live state and
source the recipient must check.

## Executor handoff with work remaining

> Continue the export fix in `/work/reporting`, branch `fix/export-order`.
> The user authorized implementation and a draft PR; merging and deployment
> remain outside the requested scope. Preserve the existing CSV column order.
>
> Commit `abc1234` contains the parser fix. The worktree also has an unfinished
> change in `tests/test_export.py`; do not discard it or treat it as verified.
> `pytest tests/test_parser.py -q` passed at that commit before the test edit.
> Export integration tests have not run. The previous agent reported a full
> suite pass but supplied no log; that is not independent verification.
>
> Next: finish the empty-result regression in `tests/test_export.py`, run the
> affected checks, and open the draft PR. The accepted behavior is in
> `docs/specs/export-order.md`; source code remains the reference for implementation.

Save this kind of note when the next executor needs a durable artifact. Use a
repo-relative path when the recipient has a different checkout location, and
include active job identifiers or temporary-artifact locations only if needed.
