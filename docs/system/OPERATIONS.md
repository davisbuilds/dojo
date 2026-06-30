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
python scripts/generate_skills_manifest.py
```

### Compose opt-in shared fragments

Expands `<!-- INCLUDE: name -->` directives from `skills/_fragments/` into SKILL.md (skills with no directive are untouched):

```bash
python scripts/gen_skill_docs.py          # write
python scripts/gen_skill_docs.py --check  # verify no drift (CI)
```

### Regenerate harness adapters

Creates the local `.claude/.agents/.agent` `skills/` symlinks and the colocated Codex `openai.yaml` sidecars from frontmatter. Run after cloning (symlinks are gitignored) and after editing skill descriptions:

```bash
python scripts/gen_harness_adapters.py                      # write symlinks + sidecars
python scripts/gen_harness_adapters.py --check              # verify both locally
python scripts/gen_harness_adapters.py --check --skip-symlinks  # verify committed sidecars only (CI)
```

Hand-curated sidecars (no `AUTO-GENERATED` marker) are preserved; for those, author with `skills/skill-creator/scripts/generate_openai_yaml.py`.

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

### Behavioral trigger evals (opt-in, never in CI)

Asks a real local agent which skill it would pick for each declared trigger, then checks against the owner. Requires `DOJO_BEHAVIORAL_EVALS=1` and a local agent command (`DOJO_BEHAVIORAL_AGENT`, default `claude -p`; reads the prompt on stdin). Non-deterministic and may cost tokens, so it is gated off by default and not wired into CI:

```bash
DOJO_BEHAVIORAL_EVALS=1 python scripts/behavioral_evals.py
DOJO_BEHAVIORAL_EVALS=1 python scripts/behavioral_evals.py --json
```

### Run skill-standardizer regression tests

```bash
python3 skills/skill-standardizer/scripts/test_skill_standardizer.py
```

## Hook Configuration

Hooks are configured in `.claude/settings.json` and `.agents/settings.json`. No manual installation is needed — they activate automatically when opening the repo in a supported harness.

## CI

GitHub Actions enforces strict contract compliance, generated-artifact sync, and an AI-slop prose scan on the manifest-backed skill catalog via:

- `.github/workflows/skill-contract-pilot.yml`

```bash
python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict
python3 scripts/gen_skill_docs.py --check
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
- Stop hooks verify git state and skill structure; uncommitted changes and untracked files block, but unpushed commits never do (push timing is the operator's call).

See `docs/system/skill-contract-v1.md` for the contract checklist and `docs/system/SKILL-BEST-PRACTICES.md` for authoring guidance.

## Optional Skill Dependencies

| Skill | Extra Packages | Env Vars |
|-------|---------------|----------|
| `gemini-imagen` | `google-genai>=1.0.0`, `Pillow>=10.0.0` | `GEMINI_API_KEY` |
| `gpt-imagen` | `openai>=1.0.0`, `Pillow>=10.0.0` | `OPENAI_API_KEY` |
| `design-md` | `npx` on PATH; pulls `@google/design.md@0.1.1` on first invocation via `scripts/run_cli.sh` | — |
