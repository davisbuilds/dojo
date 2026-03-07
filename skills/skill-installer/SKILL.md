---
name: skill-installer
description: Install skills into Codex or Claude Code skills directories from a curated list or a GitHub repo path. Use when a user asks to list installable skills, install a curated skill, or install a skill from another repo (including private repos).
compatibility: "Requires python3, requests package. Requires network access for GitHub API."
metadata:
  short-description: Install curated skills from openai/skills or other repos
---

# Skill Installer

Helps install skills. By default these are from https://github.com/openai/skills/tree/main/skills/.curated, but users can also provide other locations. Experimental skills live in https://github.com/openai/skills/tree/main/skills/.experimental and can be installed the same way.

Use the helper scripts based on the task:
- List skills when the user asks what is available, or if the user uses this skill without specifying what to do. Default listing is `.curated`, but you can pass `--path skills/.experimental` when they ask about experimental skills.
- Install from the curated list when the user provides a skill name.
- Install from another repo when the user provides a GitHub repo/path (including private repos).

Install skills with the helper scripts.

## Communication

When listing skills, output approximately as follows, depending on the context of the user's request. If they ask about experimental skills, list from `.experimental` instead of `.curated` and label the source accordingly:
"""
Skills from {repo}:
1. skill-1
2. skill-2 (already installed)
3. ...
Which ones would you like installed?
"""

After installing a skill, tell the user: "Restart your agent to pick up new skills."

## Scripts

All of these scripts use network, so when running in the sandbox, request escalation when running them.

- `scripts/list-skills.py` (prints skills list with installed annotations)
- `scripts/list-skills.py --format json`
- `scripts/list-skills.py --agent claude` (installed annotations from `~/.claude/skills`)
- Example (experimental list): `scripts/list-skills.py --path skills/.experimental`
- `scripts/install-skill-from-github.py --repo <owner>/<repo> --path <path/to/skill> [<path/to/skill> ...]`
- `scripts/install-skill-from-github.py --agent claude --repo <owner>/<repo> --path <path/to/skill>`
- `scripts/install-skill-from-github.py --url https://github.com/<owner>/<repo>/tree/<ref>/<path>`
- Example (experimental skill): `scripts/install-skill-from-github.py --repo openai/skills --path skills/.experimental/<skill-name>`

## Behavior and Options

- Defaults to direct download for public GitHub repos.
- If download fails with auth/permission errors, falls back to git sparse checkout.
- Aborts if the destination skill directory already exists.
- Installs into selected agent home: `--agent codex` uses `$CODEX_HOME/skills` (default `~/.codex/skills`), `--agent claude` uses `$CLAUDE_HOME/skills` (default `~/.claude/skills`).
- Multiple `--path` values install multiple skills in one run, each named from the path basename unless `--name` is supplied.
- Options: `--ref <ref>` (default `main`), `--agent codex|claude`, `--dest <path>`, `--method auto|download|git`.

## When To Use

- User asks to list available or installable skills (curated or experimental)
- User requests installation of a skill by name from the curated/experimental catalog
- User provides a GitHub repo path or URL to install a skill from an external source
- User asks what skills are already installed

## Boundaries

- Not for creating or authoring new skills (use skill-creator instead)
- Not for validating or packaging existing skills
- Skip when the user asks about `.system` preinstalled skills (explain they are already present)
- Do not overwrite an existing skill directory unless the user explicitly insists

## Output

- A formatted list of available skills with installed/not-installed annotations
- Skill files installed into the correct agent skills directory (`~/.codex/skills` or `~/.claude/skills`)
- Post-install message telling the user to restart their agent

## Verification

- `scripts/list-skills.py` exits cleanly and lists skills with correct annotations
- Installed skill directory contains a valid `SKILL.md` with required frontmatter
- No existing skill directories were overwritten without explicit user confirmation
- Network errors are reported clearly rather than silently swallowed

## Notes

- Curated listing is fetched from `https://github.com/openai/skills/tree/main/skills/.curated` via the GitHub API. If it is unavailable, explain the error and exit.
- Private GitHub repos can be accessed via existing git credentials or optional `GITHUB_TOKEN`/`GH_TOKEN` for download.
- Git fallback tries HTTPS first, then SSH.
- The skills at https://github.com/openai/skills/tree/main/skills/.system are preinstalled, so no need to help users install those. If they ask, just explain this. If they insist, you can download and overwrite.
- Installed annotations come from the selected agent home (`$CODEX_HOME/skills` or `$CLAUDE_HOME/skills`) unless `--dest` is provided.
