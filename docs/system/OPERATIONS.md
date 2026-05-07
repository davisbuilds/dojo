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

Core: `PyYAML==6.0.3`. Optional per-skill extras are documented in `requirements.txt`.

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

### Run skill-standardizer regression tests

```bash
python3 skills/skill-standardizer/scripts/test_skill_standardizer.py
```

## Hook Configuration

Hooks are configured in `.claude/settings.json` and `.agents/settings.json`. No manual installation is needed — they activate automatically when opening the repo in a supported harness.

## CI

GitHub Actions enforces strict contract compliance on the full 48-skill catalog via:

- `.github/workflows/skill-contract-pilot.yml`

```bash
python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict
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
