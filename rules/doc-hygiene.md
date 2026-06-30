# Doc & commit hygiene rules

Standing conventions for changes in this repo.

## Commits

- Commit completed work in coherent, self-contained chunks as you go.
- Use conventional-commit prefixes: `feat`, `fix`, `docs`, `refactor`, `test`,
  `chore`, `ci`.
- Branch off `main` for any non-trivial change; never commit directly to `main`.
- Push only when asked. History is preserved per-commit — squash is disabled
  (see `docs/project/GIT_HISTORY_POLICY.md`).

## Reference docs

- After a significant change, update the now-stale references under
  `docs/system/` (`ARCHITECTURE.md`, `FEATURES.md`, `OPERATIONS.md`,
  `ROADMAP.md`) and `README.md`. Skip trivial changes.
- Keep one canonical home per fact; link rather than duplicate.
- Generated artifacts (`skills.json`, `docs/catalog/`, harness sidecars,
  composed SKILL.md blocks) are never hand-edited — change the source and
  regenerate.

## Plans & specs

- Plans and specs carry a `status:` that follows a lifecycle:
  `draft → in-progress → complete` (terminal synonyms: `shipped`, `implemented`,
  `superseded`). Update it honestly as work progresses — downstream tooling keys
  off it.
- Completed pre-execution docs don't linger in `docs/design/`, `docs/specs/`, or
  `docs/plans/`. They move to a gitignored `docs/archive/<category>/` — kept
  locally, out of the tracked tree; preserve the emptied dir with `.gitkeep`.
- Don't hand-sweep one at a time: `ops/scripts/archive_plans.py` archives
  terminal-status docs past a settling buffer and reports anything missing
  lifecycle frontmatter. Setting `status:` correctly is what lets it run safely.

## Verification

- State outcomes faithfully: if tests fail, say so with output; if a step was
  skipped, say that. Claim "done" only after the relevant `--check`/tests pass.
