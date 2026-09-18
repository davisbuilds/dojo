# Contributing

This repository preserves full per-commit history on `main` (squash merging is disabled). Keep your PR commits tidy so what lands reads cleanly.

## Workflow

1. Sync local `main`.
2. Create a feature branch from `main`.
3. Make focused changes and commit normally.
4. Push branch and open a pull request.
5. Merge with **Create a merge commit** (default) or **Rebase and merge** after quality checks pass; squash is disabled.
6. Let GitHub auto-delete the merged remote branch.
7. Prune merged local branches periodically.

## Branch Naming

Use descriptive prefixes:

- `feat/<name>`
- `fix/<name>`
- `chore/<name>`
- `docs/<name>`

## Conventions

Standing always-follow conventions live in [`rules/`](rules/) — see [`rules/skill-authoring.md`](rules/skill-authoring.md) and [`rules/doc-hygiene.md`](rules/doc-hygiene.md).

For skill design, start with [best practices](docs/system/SKILL-BEST-PRACTICES.md)
and the [vision](docs/project/VISION.md). Explain what the skill adds beyond the
agent's existing context and why any mandatory process is needed. Removing or
narrowing obsolete guidance is a useful contribution; a new skill or artifact
is not the default measure of progress.

## Commit Guidance

- Keep commits logical and atomic while working on the branch.
- Use clear, imperative commit messages.
- It is fine to have multiple commits in one PR, but they all land on `main` (no squash) — reword or rebase locally so each reads cleanly before merging.

## Pull Request Expectations

- Keep PR scope tight (one objective per PR).
- Include a short summary and test evidence.
- Run the relevant checks and the strict skill contract before merge:
  `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict`.
  See [Operations](docs/system/OPERATIONS.md) for regression tests, generated-file
  checks, release metadata, and the full CI workflow. Hooks provide earlier feedback.

## Local Branch Cleanup

Run periodically:

```bash
git fetch --prune
git branch --merged main | grep -v ' main$' | xargs -n 1 git branch -d
```

## Documentation Hygiene

- Do not hardcode volatile counts in docs.
- Prefer executable source-of-truth references such as `skills.json` and the
  validation commands in `docs/system/OPERATIONS.md`.

## Related Docs

- Git history and branch hygiene config: `docs/project/GIT_HISTORY_POLICY.md`
- Agent implementation guidance: `AGENTS.md`
- Project onboarding: `README.md`
