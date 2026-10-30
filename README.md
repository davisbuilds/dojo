<p align="center">
  <img src="docs/assets/dojo-header.svg" width="880" alt="Dojo — reusable skills for coding agents. A dojo entrance framed by code brackets." />
</p>

# Dojo

Reusable skills for developers working with coding agents. Add a focused capability
to Claude Code, Codex, or another harness that reads `SKILL.md`.

Each skill bundles instructions and, where useful, tools or specialist references.
Dojo favors scoped guidance that leaves room for the agent's judgment. Start with
one skill for a task you already have; the catalog is a menu, not a required workflow.

## Start with your agent

Open your coding agent in the project you want to work on and paste this:

```text
Help me get started with Dojo: https://github.com/davisbuilds/dojo

Read its README and consumer installation instructions. Use my current task to
suggest a useful starting skill; if the task is unclear, ask what I want to do.
Install the complete skill bundle for this agent using the documented installer,
preserving any existing customizations. Set up only what the selected skill needs.
Check whether this harness can discover it, tell me if I need a fresh session,
and show me how to invoke it on my task.

Do not set up Dojo's contributor tooling or repository hooks unless I ask to
work on Dojo itself.
```

Your agent handles skill selection, installation, and setup checks. You don't
need to clone Dojo or run its development commands yourself. If you already know
which skill you want, name it in the request. Prefer the terminal? Use
[manual installation](#manual-installation).

## Some starting points

| What you need | Start with |
| --- | --- |
| Find and reconcile drift between installed skill copies | [skill-standardizer](skills/skill-standardizer/SKILL.md) — audit and sync scripts with recovery records |
| Make a CLI work for people, scripts, and agents | [create-cli](skills/create-cli/SKILL.md) — interface conventions and a specialist reference |
| Write tests that catch the intended regression | [test-strategy](skills/test-strategy/SKILL.md) — testing preferences, dependency fidelity, and checks for misleading passes |

Browse the [full catalog](docs/system/FEATURES.md), or open the
[searchable catalog](docs/catalog/index.html) locally in a browser. Read the
chosen skill's `SKILL.md` for scope and dependencies.

## Use it in your project

After setup, follow any restart instructions and ask your agent to use the chosen
skill **in the project you want to work on**, with the task's scope and context.
These examples show tasks and results to inspect; they are not measured gains
over your agent's existing abilities. Adapt names and paths to your project.

### Reconcile drifted skill copies

Suppose you maintain `test-strategy` in a repository and have installed copies
in multiple agent homes:

```text
Use skill-standardizer to audit only test-strategy across this repository and
my agent skill directories. Show the resolved source and target paths, content
differences, and proposed copy or link changes. Preserve local customizations;
if the authoritative copy is unclear, leave that decision open. Do not apply yet.
```

**Inspect:** the scoped audit and dry-run actions identify which copies differ
and where each replacement would come from. Once you have chosen the source and
changes to apply, ask the agent to sync that selection and re-audit the same scope.
The result includes recovery records and retained unique prior contents; recovery
is manual. A clean audit establishes alignment under the selected policy, not
that a harness has loaded the updated skill.

### Make a command usable in automation

Suppose your CLI's `export` command prints progress alongside its JSON output,
breaking a downstream parser:

```text
Use create-cli to fix export's output contract for our existing JSON consumer.
Keep the established command syntax. Send diagnostics to stderr, keep stdout
parseable, and make missing required input fail clearly without prompting when
stdin is not a terminal. Implement the change and check success and failure paths.
```

**Inspect:** captured stdout, stderr, and exit status from the actual command.
The consumer can parse successful output, diagnostics stay on stderr, and missing
input produces a useful error and nonzero exit without waiting for a prompt.
The skill supplies conventions and reference material; your agent uses the
project's implementation and tooling.

### Check that a regression test catches the bug

Suppose a fix restores keyboard focus after a dialog closes:

```text
Use test-strategy to add regression coverage for this dialog focus fix using
the project's existing browser tests. Check that closing the dialog returns
focus to its opener. Demonstrate failure on the original behavior and success
with the fix. Use an isolated copy for the pre-fix run, preserve my working
changes, and exercise real browser focus handling.
```

**Inspect:** the test reaches the close interaction and fails on the original
focus assertion, then passes with the fix. A missing dependency or failure to
open the dialog does not establish regression coverage. The browser exercises
real focus behavior; use lower-level tests for contracts they can faithfully cover.

Name the skill explicitly for the first attempt. Ask your agent to confirm it
read the installed `SKILL.md` if you're unsure whether it used the skill.
If the skill is missing or stale, point your agent to
[consumer troubleshooting](docs/system/OPERATIONS.md#skill-troubleshooting).

Installation, discovery, actual use, and useful outcomes are separate checks. See
[evaluation guidance](skills/skill-creator/references/evaluation.md) for comparing
a skill against your agent's ordinary baseline.

## Manual installation

With Git and Python 3.11+ available, clone Dojo and run its installer. This example
installs `skill-standardizer`; replace that name with any skill from the table above:

```bash
git clone https://github.com/davisbuilds/dojo.git
cd dojo
python3 skills/skill-installer/scripts/install-skill-from-github.py \
  --agent codex --repo davisbuilds/dojo --path skills/skill-standardizer
```

For **Claude Code**, replace `--agent codex` with `--agent claude`. The installer
copies the complete skill from GitHub's `main` into `~/.codex/skills/skill-standardizer`
or `~/.claude/skills/skill-standardizer` by default, and prints the destination.
It honors `CODEX_HOME` / `CLAUDE_HOME` and refuses to overwrite an existing directory.
The installed bundle is a snapshot; pulling this checkout does not update it.
See [installation options](docs/system/OPERATIONS.md#using-a-skill) for pinned
revisions, other destinations, updates, and removal.

This installer uses Python's standard library. Repository development dependencies,
hooks, adapters, and the `dojo` CLI are optional for using these skills. Some skills
need additional tools or service access; configure those only when needed.

## Work on Dojo

To change skills or use the development CLI, install
[uv](https://docs.astral.sh/uv/getting-started/installation/) 0.9.17 or later (the 7-day `exclude-newer` release quarantine needs it) and run
from this checkout:

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

Credits for adopted and adapted material live here so skill instructions stay
focused on the task. Required license and notice files travel with each affected
skill when installed separately. Technical citations and source/version records
remain beside the guidance or fixtures they help verify and maintain.

- [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)
- [superpowers](https://github.com/obra/superpowers)
- [agent-scripts](https://github.com/steipete/agent-scripts)
- [anthropics/skills](https://github.com/anthropics/skills)
- [compound-engineering-plugin](https://github.com/everyinc/compound-engineering-plugin) — source of the original agent-native-architecture skill (now rewritten as agent-native-design) and the retired compound-docs skill
- Vercel skill contributions — retired React/Next.js references and deployment workflows remain available in Git history; see the [retirement decision](docs/project/DECISIONS.md#vercel-skills-and-shipping-profile-retirement).
- [Kepano's Obsidian skills](https://github.com/kepano/obsidian-skills) — MIT-licensed Markdown, Bases, and JSON Canvas references, consolidated into `obsidian`
- [skills.sh](https://skills.sh) — community skill registry and discovery
- [Google Labs `@google/design.md`](https://github.com/google-labs-code/design.md) — DESIGN.md format and CLI wrapped by the `design-md` skill (Apache-2.0)
- [Refero](https://styles.refero.design) — source of the five DESIGN.md exemplars vendored under `skills/design-md/references/exemplars/`
- [impeccable.style](https://impeccable.style/slop) — slop anti-pattern taxonomy paraphrased into the `design-critique` slop catalog
- [mattpocock/skills](https://github.com/mattpocock/skills) — source of the `diagnose` (feedback-loop-first debugging) and `caveman` (ultra-compressed communication mode) skills (MIT)
- [Emil Kowalski's skills](https://github.com/emilkowalski/skills/tree/2d228630ba1446365f614a108cb8252f1feda202/skills) — MIT-licensed content-edge remedies from `break-ui` and motion craft guidance from `animate` and `review-animations` adapted into `frontend-design`. Dojo keeps case selection and motion choices contextual, reuses existing tooling, and omits prescribed report formats and approval pauses. Browser API details are linked from the references.
- [Command Line Interface Guidelines](https://clig.dev/) by Aanand Prasad, Ben Firshman, Carl Tashian, Eva Parish, and contributors; design by Mark Hurrell — the `create-cli` reference adapts this [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) guide for human, script, and agent consumers. Agent discovery, bounded evidence, and asynchronous lifecycle guidance are Dojo additions.
- [Microsoft Playwright CLI](https://github.com/microsoft/playwright-cli) — Apache-2.0 material adapted for the `playwright` skill, with a wrapper and local reference guides; see its bundled notice.
