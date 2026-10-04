## 1.0.0 - 2026-10-03

- Preserve Canvas extension metadata, scope diagram-format guidance to Canvas, and honor authorized CLI setup.

- Consolidate `obsidian-markdown`, `obsidian-bases`, and `obsidian-canvas` into one skill: `SKILL.md` routes by task and carries vault fit, the CLI entry points, and verification; notes, Bases (with the function catalog), Canvas, and the Obsidian CLI live in `references/`.
- Add `references/cli.md` from the official CLI docs (1.12.7+ installer, registration) and Obsidian 1.13.7 behavior: availability and probing, targeting (`vault=` first, `path=` over `file=`, active-file default), output traps (exit status 0 on errors, silent `create` renames, empty output for missing folders), app-only commands, File Recovery history, and commands that need explicit intent.
