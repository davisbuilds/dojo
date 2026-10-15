# Dojo

Reusable skills for developers working with coding agents. Add a focused capability
to Claude Code, Codex, or another harness that reads `SKILL.md`: review a change,
diagnose a bug, design an API, or carry task context into a fresh session.

Each skill bundles instructions and, where useful, tools or specialist references.
Dojo favors scoped guidance that leaves room for the agent's judgment. Start with
one skill for a task you already have; the catalog is a menu, not a required workflow.

## Try a code review

[`local-review`](skills/local-review/SKILL.md) is a small first task if you have a
Git repository with an uncommitted change. It asks the agent to trace affected
callers and contracts, then return actionable findings with evidence. Review is
read-only unless you separately request a fix or publication.

### Install

With Git and Python 3.11+ available, run:

```bash
git clone https://github.com/davisbuilds/dojo.git
cd dojo
python3 skills/skill-installer/scripts/install-skill-from-github.py \
  --agent codex --repo davisbuilds/dojo --path skills/local-review
```

For **Claude Code**, replace `--agent codex` with `--agent claude`. The installer
copies the complete skill from GitHub's `main` into `~/.codex/skills/local-review`
or `~/.claude/skills/local-review` by default, and prints the destination. It
honors `CODEX_HOME` / `CLAUDE_HOME` and refuses to overwrite an existing directory.
See [installation options and troubleshooting](docs/system/OPERATIONS.md#using-a-skill)
for other destinations, pinned revisions, and existing copies.

This path uses Python's standard library. Repository development dependencies,
hooks, adapters, and the `dojo` CLI are optional for using this skill.

### Use it on your change

Start a fresh agent session **in the repository you want reviewed**, then ask:

```text
Use local-review to review my uncommitted changes relative to HEAD.
Trace affected callers and contracts. Return actionable findings with file and
line references, and state any material verification limits. Do not edit files
or post comments.
```

Use the skill's name explicitly for the first attempt. Check the session's tool
activity or skill-loading indicator to confirm it read the installed
`local-review/SKILL.md`; the skill being present on disk alone does not establish
that it was used. This prompt uses the skill in an ordinary agent conversation;
a harness's native `/review` is a separate entrypoint.

A useful result explains **what triggers a defect, what breaks, and where**.
For example, one [authored review case](skills/local-review/evals/behavioral-scenarios.md)
renames a producer's field while an unchanged consumer still reads the old key.
The intended finding traces that mismatch beyond the diff. If there are no
supported findings, the agent should say so and state material limits. These
are expected behaviors, not a measured success story or proof that every review
will find every bug.

## Choose another task

| What you need | Start with |
| --- | --- |
| Find the cause of a failing behavior or slowdown | [diagnose](skills/diagnose/SKILL.md) |
| Design or review an API contract | [api-design](skills/api-design/SKILL.md) |
| Explore an idea whose requirements are still unclear | [brainstorming](skills/brainstorming/SKILL.md) |
| Preserve ongoing work for another session | [handoff](skills/handoff/SKILL.md) |

Replace `skills/local-review` in the install command with the skill you choose.
Read its `SKILL.md` for scope and dependencies. Some skills need external tools
or service access; [optional dependencies](docs/system/OPERATIONS.md#optional-skill-dependencies)
are separate from the basic installation.

Browse the [skill catalog](docs/system/FEATURES.md), or open the generated
[searchable catalog](docs/catalog/index.html) locally in a browser. The generated
[`skills.json`](skills.json) manifest supplies the inventory. Installing a skill
copies its bundle; it does not install the whole catalog or Dojo's repository hooks.

## Check installation and evidence

If the skill is missing, stale, or not being selected, start with
[consumer troubleshooting](docs/system/OPERATIONS.md#skill-troubleshooting).
For Codex, the optional `dojo inspect` command compares installed content and a
fresh harness catalog against this checkout. It reports incomplete evidence when
it cannot establish exposure; it does not prove that a running session loaded
the skill body.

Packaging checks establish structure and links. Routing probes, observed loading,
and useful task outcomes are separate evidence. For the review example, see the
[review basis and limits](skills/local-review/references/review-basis.md) and
[authored scenarios](skills/local-review/evals/behavioral-scenarios.md). For comparing
a skill with your agent's existing baseline, see the
[evaluation guidance](skills/skill-creator/references/evaluation.md).

## Work on Dojo

To change skills or use the development CLI, install
[uv](https://docs.astral.sh/uv/getting-started/installation/) and run from this checkout:

```bash
uv sync --locked
uv run --locked bin/dojo list review
uv run --locked bin/dojo check local-review
```

`list` searches canonical names and descriptions; `check` validates the selected
skill's packaging and Markdown links. Neither runs a code review. Use
[Operations](docs/system/OPERATIONS.md#setup) for hook prerequisites, adapters,
regression tests, full-catalog validation, and the optional `dojo` PATH setup.

Focused fixes, documentation improvements, and supported proposals are welcome.
Start with [Contributing](CONTRIBUTING.md) and [agent guidance](AGENTS.md).
Skill authors should read [best practices](docs/system/SKILL-BEST-PRACTICES.md)
and the [skill contract](docs/system/skill-contract-v1.md). Changes to skill
instructions use per-skill versions and changelogs; the root
[changelog](CHANGELOG.md) covers CLI/tooling releases.

## Documentation

- [Architecture](docs/system/ARCHITECTURE.md): skill structure, progressive loading, hooks, and generated adapters.
- [Operations](docs/system/OPERATIONS.md): installation, diagnostics, development, and distribution tooling.
- [Vision](docs/project/VISION.md): what belongs in Dojo and why.
- [Roadmap](docs/project/ROADMAP.md) and [Backlog](docs/project/BACKLOG.md): selected direction and unresolved work.
- [Git history policy](docs/project/GIT_HISTORY_POLICY.md): contribution and merge conventions.

## Acknowledgements

- [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)
- [superpowers](https://github.com/obra/superpowers)
- [agent-scripts](https://github.com/steipete/agent-scripts)
- [anthropics/skills](https://github.com/anthropics/skills)
- [compound-engineering-plugin](https://github.com/everyinc/compound-engineering-plugin) — source of the original agent-native-architecture skill (now rewritten as agent-native-design) and the retired compound-docs skill
- [Vercel skills](https://github.com/vercel/next.js) — React, Next.js, React Native best-practice rules and composition patterns, plus preview deployment debugging workflows
- [Kepano's Obsidian skills](https://github.com/kepano) — Obsidian Markdown, Bases, and JSON Canvas skill references
- [skills.sh](https://skills.sh) — community skill registry and discovery
- [Google Labs `@google/design.md`](https://github.com/google-labs-code/design.md) — DESIGN.md format and CLI wrapped by the `design-md` skill (Apache-2.0)
- [Refero](https://styles.refero.design) — source of the five DESIGN.md exemplars vendored under `skills/design-md/references/exemplars/`
- [impeccable.style](https://impeccable.style/slop) — slop anti-pattern taxonomy paraphrased into the `design-critique` slop catalog
- [mattpocock/skills](https://github.com/mattpocock/skills) — source of the `diagnose` (feedback-loop-first debugging) and `caveman` (ultra-compressed communication mode) skills (MIT)
