# Contributing

Bug reports, focused fixes, documentation improvements, and supported proposals
are welcome. Discuss substantial new skills, dependencies, integrations, or public
interface changes before investing in implementation. This is a solo-maintained
project; contributions do not imply a support or response-time commitment.

## Understanding And Scope

Agent-assisted work is welcome. Understand the purpose, important behavior, and
tradeoffs of the change you submit. Explain what you verified and any limitations.
A prompting diary or a manual rewrite of agent output is not required.

For skill design, start with [best practices](docs/system/SKILL-BEST-PRACTICES.md)
and the [vision](docs/project/VISION.md). Explain what the skill adds beyond the
agent's existing context and why any mandatory process is needed. Removing or
narrowing obsolete guidance is a useful contribution.

## Choosing And Discussing Work

The [Roadmap](docs/project/ROADMAP.md) describes selected direction; the
[Backlog](docs/project/BACKLOG.md) records unresolved candidates. Backlog tasks can
be assigned directly to agents. Use an issue for a persistent discussion, external
participation, investigation, or coordination across PRs; a focused change can go
straight to a PR. An issue or backlog entry alone is not a feature commitment.
When an issue owns the details, retain only a short backlog link if useful.

## Delivering A Change

Work on a focused branch from `main`. Keep commits coherent and use the
Conventional Commit prefixes in [doc and commit hygiene](rules/doc-hygiene.md).
The [Git policy](docs/project/GIT_HISTORY_POLICY.md) preserves per-commit history
with merge or rebase merges; squash merging is disabled.

Describe the problem and resulting behavior in the PR, with relevant verification
and unresolved limitations. Follow [skill authoring](rules/skill-authoring.md) and
run the relevant checks, including the strict skill contract:

```bash
python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict
```

[Operations](docs/system/OPERATIONS.md) owns setup, regression checks, generated
files, and release commands. Skills are versioned individually: record consumer
changes and compatibility implications in the affected skill's changelog and follow
its version-bump checks. There is no required duplicate catalog-wide changelog.

Update reference docs whose claims changed. Roadmap is not a completion log;
Git and PRs preserve routine delivery history.
