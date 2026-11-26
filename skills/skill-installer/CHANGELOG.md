# Changelog

## 2.0.1 - 2026-11-23

- Clarify why the Git fallback needs a clean checkout on retry.

## 2.0.0 - 2026-11-20

- Rebase on OpenAI's current bundled copy: the `skill-installer` shipped with
  Codex CLI 0.163.0 (system-skills marker `3eadc798bef12c4a`), observed on
  2026-11-20. Upstream SHA-256 of the files Dojo modifies:
  - `SKILL.md`: `d68b77e5bbb34dedab89d134da52855f140fc4b4299b80104f534e3b9e98f8ee`
  - `scripts/install-skill-from-github.py`: `38f311b75664bb063808f982c600271ebc4b560830f491705190f88a94e3e781`
  - `scripts/list-skills.py`: `9d6dfb2abf3afeee7f027a89fb1626b918a973da18f4eb6c25681286301beb41`

  `scripts/github_utils.py`, `agents/openai.yaml`, `assets/`, and `LICENSE.txt`
  are byte-identical to upstream.
- Breaking: adopt upstream's install validation, which rejects a skill path that
  leaves the repo, symlinks along the skill path, and symlinks inside a skill
  that point outside it or at a non-file.
- Keep Dojo's harness-agnostic additions: `--agent codex|claude` for both
  scripts, `CLAUDE_HOME` resolution, and a neutral post-install message.
- Add `--dest` to `list-skills.py` so annotations can read any skills directory.
- Retry the SSH git fallback in a clean directory, so a failed HTTPS attempt no
  longer masks the real error with "destination path already exists".
- Correct the compatibility note (standard library only, not `requests`), anchor
  script commands to `<skill-dir>`, and drop the generic contract sections.

## 1.0.0 - 2026-11-20

- Vendored from OpenAI's `skill-installer` with `--agent codex|claude` support.
