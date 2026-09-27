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

- Update the owning reference when a documented contract, boundary, procedure,
  or direction changes. Reconcile affected backlog entries as work lands; Roadmap
  records selected direction, not a running shipment log.
- Keep one canonical home per fact; link rather than duplicate.
- Generated artifacts (`skills.json`, `docs/catalog/`, harness sidecars,
  composed SKILL.md blocks) are never hand-edited — change the source and
  regenerate.

## Pre-execution artifacts

- Newly authored design summaries, specs, and plans carry `author:` with the
  producing agent's most specific available model or harness identifier. Do not
  attribute the user or a reviewer, and do not leave `<agent>` unresolved.
- Plans and specs carry a `status:` that follows a lifecycle:
  `draft → in-progress → complete` (terminal synonyms: `shipped`, `implemented`,
  `superseded`). Update it honestly as work progresses — downstream tooling keys
  off it.
- Completed pre-execution docs don't linger in `docs/design/`, `docs/specs/`, or
  `docs/plans/`. They move to a gitignored `docs/archive/<category>/` — kept
  locally, out of the tracked tree; preserve the emptied dir with `.gitkeep`.
- Archive in one reviewed batch: select only terminal-status docs past a
  settling buffer, report missing lifecycle frontmatter before moving anything,
  and preserve the emptied tracked directories with `.gitkeep`. Setting
  `status:` correctly is what makes that batch safe.

## Verification

- State outcomes faithfully: if tests fail, say so with output; if a step was
  skipped, say that. Claim "done" only after the relevant `--check`/tests pass.
