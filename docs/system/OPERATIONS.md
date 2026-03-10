# Operations

## Setup

### System Dependencies

The hooks require these tools (ship with most systems):

```bash
git jq python3 sed grep
```

### Python Dependencies

```bash
pip install -r requirements.txt
```

Core: `PyYAML>=6.0`. Optional per-skill extras are documented in `requirements.txt`.

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

## Hook Configuration

Hooks are configured in `.claude/settings.json` and `.agents/settings.json`. No manual installation is needed — they activate automatically when opening the repo in a supported harness.

## CI

GitHub Actions enforces strict contract compliance on the full 45-skill catalog via:

- `.github/workflows/skill-contract-pilot.yml`

```bash
python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict
```

Hooks enforce quality at edit-time and session-stop:

- Pre-tool-use hook blocks pushes to protected branches unless the command includes `DOJO_ALLOW_PROTECTED_PUSH=1`.
- Pre-tool-use hook validates SKILL.md on every write.
- Stop hooks verify git state and skill structure; protected branches may keep local unpushed commits.

See `docs/system/skill-contract-v1.md` for the contract checklist and `docs/system/SKILL-BEST-PRACTICES.md` for authoring guidance.

## Optional Skill Dependencies

| Skill | Extra Packages | Env Vars |
|-------|---------------|----------|
| `gemini-imagen` | `google-genai>=1.0.0`, `Pillow>=10.0.0` | `GEMINI_API_KEY` |
| `gpt-imagen` | `openai>=1.0.0`, `Pillow>=10.0.0` | `OPENAI_API_KEY` |
