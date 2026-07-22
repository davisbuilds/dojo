# Operations

## Setup

### System Dependencies

The hooks require these tools (ship with most systems):

```bash
git jq python3 sed grep
```

### Python Dependencies

```bash
python -m pip install --require-hashes -r requirements.lock
```

Core installs are hash-pinned via `requirements.lock`. Update the lock whenever `requirements.txt` changes:

```bash
uv pip compile --generate-hashes requirements.txt -o requirements.lock
```

Core: `PyYAML==6.0.3`; test tooling: `pytest` (runs the `tests/` regression
suite). Optional per-skill extras are documented in `requirements.txt`.

Run the repo regression tests with:

```bash
python -m pytest tests/ -q
```

## Skill Management Commands

### Create a new skill

```bash
python skills/skill-creator/scripts/init_skill.py <skill-name> --path ./ \
  --resources scripts,references --examples
```

### Validate a skill

```bash
python skills/skill-creator/scripts/quick_validate.py <path/to/skill-folder>
```

### Validate a spec or plan

The pre-execution pipeline is `brainstorm (docs/design/) → spec (docs/specs/) →
plan (docs/plans/)`. Specs are mechanism-free contracts; plans are the execution
breakdown. Each layer has its own schema validator (also wired as on-write hooks):

```bash
# Contract schema — rejects plan-shaped content (files/steps/task breakdowns)
python3 skills/write-spec/scripts/validate_spec.py docs/specs/<file>-spec.md

# Execution schema — task breakdown, files, ordered steps, verification matrix
python3 skills/write-plan/scripts/validate_plan.py docs/plans/<file>-plan.md
```

Add `--strict-filename` to enforce the `-spec.md` / `-plan.md` suffix (the hooks do).
The plan validator also prints non-blocking grounding and test-discovery advisories
when explicit task metadata suggests an omission; these messages never change an
otherwise valid plan's exit status.

New artifacts declare `risk_profile: routine|high` and
`readiness: draft|ready`; legacy artifacts default to routine/draft. High-risk
specs add stable criteria/scenario IDs and critique closure. High-risk plans link
the spec through repository-relative `spec:` frontmatter and hard-fail on missing
ID coverage, task dependencies, modified files, conditional readiness sections,
or unresolved blocking findings. Semantic authority and recovery claims still
require adversarial review.

Every newly authored design summary, spec, or plan also declares `author:` with
the producing agent's most specific available model or harness identifier (for
example, `gpt-5.6-sol`); the literal `<agent>` template placeholder must be
resolved. Spec/plan validators enforce this for current-schema artifacts while
continuing to accept legacy documents without fabricated attribution.

### Package a skill for distribution

```bash
python skills/skill-creator/scripts/package_skill.py <path/to/skill-folder> [output-directory]
```

### Generate OpenAI metadata (optional)

```bash
python skills/skill-creator/scripts/generate_openai_yaml.py <path/to/skill-folder>
```

### Regenerate manifest

```bash
python scripts/generate_skills_manifest.py          # write
python scripts/generate_skills_manifest.py --check  # verify no drift (CI)
```

The top-level `skills.json` `version` is the manifest schema version. Each skill entry also includes the per-skill release `version` declared in SKILL.md frontmatter.

### Check skill release versions

Compares release-relevant skill changes against a git base. After the one-time unversioned baseline, changed skill contents require a strictly greater SemVer value and a matching `CHANGELOG.md` entry:

```bash
python3 skills/skill-evals/scripts/check_skill_versions.py --base origin/main
```

Use `DOJO_VERSION_CHECK_BASE=<ref>` to point the stop hook at a different comparison base when working from a non-main integration branch.

### Bump a skill version

Performs the two-file edit the version check requires: updates the `version` field in SKILL.md frontmatter and prepends a matching `## <version> - <date>` heading (and bullet) to `CHANGELOG.md`, creating it if absent:

```bash
python3 skills/skill-evals/scripts/bump_skill_version.py skills/<name> patch   # or minor / major
python3 skills/skill-evals/scripts/bump_skill_version.py skills/<name> minor -m "What changed."
python3 skills/skill-evals/scripts/bump_skill_version.py skills/<name> --set 2.0.0   # explicit version
python3 skills/skill-evals/scripts/bump_skill_version.py skills/<name> patch --dry-run
```

Bumping resets lower parts and drops any prerelease (`1.2.0-rc.1` patch → `1.2.1`). It refuses a non-increasing `--set` and refuses to duplicate an existing changelog heading. `-m/--message` supplies the entry bullet (a placeholder is written otherwise).

### Compose opt-in shared fragments

Expands `<!-- INCLUDE: name -->` directives from `skills/_fragments/` into SKILL.md (skills with no directive are untouched):

```bash
python scripts/gen_skill_docs.py          # write
python scripts/gen_skill_docs.py --check  # verify no drift (CI)
```

### Regenerate harness adapters

Creates the local `.claude/.agents/.agent` `skills/` symlinks and the colocated Codex `openai.yaml` sidecars from frontmatter. Run after cloning (symlinks are gitignored) and after editing skill descriptions:

```bash
python scripts/gen_harness_adapters.py                      # write symlinks, .claude/commands links, and sidecars
python scripts/gen_harness_adapters.py --check              # verify all locally
python scripts/gen_harness_adapters.py --check --skip-symlinks  # verify committed sidecars only (CI)
```

Hand-curated sidecars (no `AUTO-GENERATED` marker) are preserved; for those, author with `skills/skill-creator/scripts/generate_openai_yaml.py`.

The same generator links each skill's `commands/*.md` into `.claude/commands/` (local-only, gitignored) so Claude Code exposes them as slash commands. It refuses when two skills' commands map to the same name (rename one), prunes symlinks whose source was removed, and never touches a hand-authored file in `.claude/commands/`. Commands are governed by the symlink phase, so `--skip-symlinks` (CI) ignores them.

### Regenerate the skill catalog

Builds a self-contained, searchable `docs/catalog/index.html` from `skills.json` (open it directly in a browser):

```bash
python scripts/gen_catalog.py          # write
python scripts/gen_catalog.py --check  # verify no drift (CI)
```

### Scan for AI-slop prose

Deterministic, high-precision linter for AI-slop tells in skill prose + core docs (complements the visual `design-critique` skill):

```bash
python scripts/slop_scan.py          # scan default set; exit 1 on hits (CI)
python scripts/slop_scan.py --list   # show the patterns
python scripts/slop_scan.py PATH...  # scan specific files
```

### Skill health report

Read-only aggregation of contract status + declared-trigger routing across the catalog (reporting, not a gate):

```bash
python scripts/skills_health.py         # human-readable
python scripts/skills_health.py --json  # machine-readable
```

The default run is network-free and unchanged. Opt-in runtime flags enrich the
report with per-skill trigger health from a running AgentMonitor instance
(the sibling local observability console) via `GET /api/v2/analytics/skills/health` —
invocation counts, never-fired status, and an experimental misfire rate:

```bash
python scripts/skills_health.py --runtime                 # fetch localhost:3141 (default endpoint)
python scripts/skills_health.py --agentmonitor-url URL    # custom endpoint (implies --runtime)
python scripts/skills_health.py --health-json FILE        # offline: read a saved health payload
python scripts/skills_health.py --findings --runtime      # paste-ready BACKLOG blocks for never-fired skills
```

Any runtime flag activates the runtime path; the default endpoint is
`http://127.0.0.1:3141/api/v2/analytics/skills/health`. The runtime section
ranks by the trustworthy signals — never-fired first, then a rarely-fired band,
then invocation volume ascending — while misfire is shown labeled experimental
and never drives rank. If AgentMonitor is unreachable or returns an unexpected
shape, the tool exits non-zero with a diagnostic and prints no partial report.
`--findings` only proposes maintainer-reviewable blocks; it writes nothing and
never invokes `skill-evals`.

### Behavioral trigger evals (opt-in, never in CI)

Asks a real local agent which skill it would pick for each declared trigger, then checks against the owner. Requires `DOJO_BEHAVIORAL_EVALS=1` and a local agent command (`DOJO_BEHAVIORAL_AGENT`, default `claude -p`; reads the prompt on stdin). Non-deterministic and may cost tokens, so it is gated off by default and not wired into CI:

```bash
DOJO_BEHAVIORAL_EVALS=1 python scripts/behavioral_evals.py
DOJO_BEHAVIORAL_EVALS=1 python scripts/behavioral_evals.py --json
```

### Run skill-standardizer regression tests

This suite ships beside the skill rather than in `tests/`, so `pytest tests/` does
not collect it. CI runs it as its own step; invoke it directly to run it locally:

```bash
python3 skills/skill-standardizer/scripts/test_skill_standardizer.py
```

## Hook Configuration

Hooks are configured in `.claude/settings.json` and `.agents/settings.json`. No manual installation is needed — they activate automatically when opening the repo in a supported harness.

The SessionStart drift notice (`session-start-skill-drift.sh`) keeps per-checkout
debounce state in `.skill-standardizer/drift-state.json` (gitignored). To force
the next session to re-report current drift, delete that file.

## CI

GitHub Actions enforces strict contract compliance, generated-artifact sync, and an AI-slop prose scan on the manifest-backed skill catalog via:

- `.github/workflows/skill-contract-pilot.yml`

```bash
python -m pytest tests/ -q
python3 skills/skill-standardizer/scripts/test_skill_standardizer.py
python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict
python3 skills/skill-evals/scripts/check_skill_versions.py --base origin/main
python3 scripts/gen_skill_docs.py --check
python3 scripts/generate_skills_manifest.py --check
python3 scripts/gen_harness_adapters.py --check --skip-symlinks
python3 scripts/gen_catalog.py --check
python3 scripts/slop_scan.py
```

The strict validator is type-aware:

- `workflow` skills must define execution flow and output expectations.
- `reference` skills are evaluated on scope, boundaries, verification, and resource navigation without being forced into workflow-only sections.

Hooks enforce quality at edit-time and session-stop:

- Pre-tool-use hook blocks pushes to protected branches unless the command includes `DOJO_ALLOW_PROTECTED_PUSH=1`.
- Pre-tool-use hook validates SKILL.md on every write.
- Stop hooks verify git state, skill structure, and required skill version bumps; uncommitted changes and untracked files block, but unpushed commits never do (push timing is the operator's call).

See `docs/system/skill-contract-v1.md` for the contract checklist and `docs/system/SKILL-BEST-PRACTICES.md` for authoring guidance.

## Optional Skill Dependencies

| Skill | Extra Packages | Env Vars |
|-------|---------------|----------|
| `gemini-imagen` | `google-genai>=1.0.0`, `Pillow>=10.0.0` | `GEMINI_API_KEY` |
| `gpt-imagen` | `openai>=1.0.0`, `Pillow>=10.0.0` | `OPENAI_API_KEY` |
| `design-md` | `npx` on PATH; pulls `@google/design.md@0.1.1` on first invocation via `scripts/run_cli.sh` | — |
