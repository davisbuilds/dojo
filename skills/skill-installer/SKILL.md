---
name: skill-installer
description: Install skills into Codex or Claude Code skills directories from a curated list or a GitHub repo path. Use when a user asks to list installable skills, install a curated skill, or install a skill from another repo (including private repos).
skill-type: workflow
compatibility: "Requires Python 3.11+ (standard library only), network access to GitHub, and git for the fallback path."
metadata:
  short-description: Install curated skills from openai/skills or other repos
version: 2.0.0
---

# Skill Installer

Helps install skills. By default these are from https://github.com/openai/skills/tree/main/skills/.curated, but users can also provide other locations. Experimental skills live in https://github.com/openai/skills/tree/main/skills/.experimental and can be installed the same way.

Use the helper scripts based on the task:
- List skills when the user asks what is available, or if the user uses this skill without specifying what to do. Default listing is `.curated`, but you can pass `--path skills/.experimental` when they ask about experimental skills.
- Install from the curated list when the user provides a skill name.
- Install from another repo when the user provides a GitHub repo/path (including private repos).

Choose the target with `--agent codex` (default) or `--agent claude`, matching the harness the user wants the skill in. Ask when that is unclear.

## Communication

When listing skills, output approximately as follows, depending on the context of the user's request. If they ask about experimental skills, list from `.experimental` instead of `.curated` and label the source accordingly:
"""
Skills from {repo}:
1. skill-1
2. skill-2 (already installed)
3. ...
Which ones would you like installed?
"""

After installing a skill, report where it landed and tell the user to start a new session if their agent does not list it yet.

## Scripts

All of these scripts use network, so when running in a sandbox, request escalation when running them. Substitute the loaded skill directory for `<skill-dir>`.

- `python3 <skill-dir>/scripts/list-skills.py` (prints skills list with installed annotations)
- `python3 <skill-dir>/scripts/list-skills.py --format json`
- `python3 <skill-dir>/scripts/list-skills.py --agent claude` (annotations from the Claude Code skills home)
- Example (experimental list): `python3 <skill-dir>/scripts/list-skills.py --path skills/.experimental`
- `python3 <skill-dir>/scripts/install-skill-from-github.py --repo <owner>/<repo> --path <path/to/skill> [<path/to/skill> ...]`
- `python3 <skill-dir>/scripts/install-skill-from-github.py --agent claude --repo <owner>/<repo> --path <path/to/skill>`
- `python3 <skill-dir>/scripts/install-skill-from-github.py --url https://github.com/<owner>/<repo>/tree/<ref>/<path>`
- Example (experimental skill): `python3 <skill-dir>/scripts/install-skill-from-github.py --repo openai/skills --path skills/.experimental/<skill-name>`

## Behavior and Options

- Defaults to direct download for public GitHub repos.
- If download fails with auth/permission errors, falls back to git sparse checkout.
- Aborts if the destination skill directory already exists. Compare an existing copy and preserve local edits before the user decides to replace it.
- Rejects skill paths that leave the repo, symlinks along the skill path, and symlinks inside the skill that point outside it.
- Installs into `<home>/skills/<skill-name>`: `--agent codex` uses `$CODEX_HOME` (default `~/.codex`), `--agent claude` uses `$CLAUDE_HOME` (default `~/.claude`). `--dest <path>` overrides the skills directory for both scripts.
- Multiple `--path` values install multiple skills in one run, each named from the path basename unless `--name` is supplied.
- Options: `--ref <ref>` (default `main`), `--agent codex|claude`, `--dest <path>`, `--method auto|download|git`.

## Notes

- Curated listing is fetched from `https://github.com/openai/skills/tree/main/skills/.curated` via the GitHub API. If it is unavailable, explain the error and exit.
- Private GitHub repos can be accessed via existing git credentials or optional `GITHUB_TOKEN`/`GH_TOKEN` for download.
- Git fallback tries HTTPS first, then SSH.
- Codex preinstalls the skills at https://github.com/openai/skills/tree/main/skills/.system, so no need to help Codex users install those. If they ask, just explain this. If they insist, you can download and overwrite. Claude Code does not ship them.
- An installed skill is a snapshot of the source ref, not a subscription to updates.

## Sibling skills

- `find-skills` — upstream. Use to discover what's available before installing.
- `audit-skill` — security gate. Run it on a third-party or untrusted skill before installing.
- `skill-standardizer` — downstream. After installing across multiple homes, use it to consolidate copies and avoid duplicate catalog entries.
