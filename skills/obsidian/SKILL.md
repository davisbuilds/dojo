---
name: obsidian
description: Work in an Obsidian vault — notes with wikilinks, properties, tags, callouts, and embeds; Bases (.base); Canvas (.canvas); and the Obsidian CLI for answers only the running app has. Use when creating, editing, or checking vault files, or when the user mentions Obsidian, wikilinks, Bases, canvases, or the obsidian CLI.
skill-type: reference
version: 1.0.0
---

# Obsidian

A vault is a folder of plain files — Markdown notes, YAML `.base` files, JSON `.canvas` files — that agents read and edit directly. Two things are easy to miss: a file can be valid and still not fit its vault, and some answers exist only inside the running app.

## When To Use

- Creating or editing notes, `.base`, or `.canvas` files in an Obsidian vault
- Changing frontmatter properties, tags, links, or note names
- Questions that depend on Obsidian itself: resolved links, the tag index, Bases results, daily-note paths

## Route by Task

| Task | Read |
|---|---|
| Note syntax: properties, tags, links, block IDs, embeds, callouts | `references/markdown.md` |
| `.base` files or `base` code blocks | `references/bases.md`, function catalog in `references/functions.md` |
| `.canvas` files | `references/canvas.md` |
| Anything answered by the running app | `references/cli.md` |

## Fit the Vault

A new or edited file should look like its neighbors. Sources, roughly in order of authority:

- **Vault guidance.** An `AGENTS.md`/`CLAUDE.md` at the vault root overrides this skill's examples, especially tag vocabulary and property conventions. Read it before adding tags or properties.
- **Vault settings** in `.obsidian/`, when the task touches them: `app.json` sets link style (`useMarkdownLinks: true` means Markdown links with URL-encoded paths instead of `[[Note Name]]`), link paths (`newLinkFormat`), and the attachment folder (`attachmentFolderPath`). Settings files omit values left at their defaults, so the app (`obsidian daily:path`, for example) can be more reliable than reading them.
- **Sibling notes** in the same folder: frontmatter keys, key names, value vocabulary (`type`, `status`), and list style — or no frontmatter where they have none. Bases filter on property values, so an invented key or value silently drops a note from a view.
- **Existing tags.** Search frontmatter `tags:` and inline `#tags`, or `obsidian tags counts sort=count`. Tags are case-insensitive (`#AI` is `#ai`), so reuse the established form rather than adding a casing, plural, or synonym variant, and skip tags that only restate the folder or a property. A new tag earns its place when nothing fits and it will apply to more than one note; mention new tags and property keys in the reply, since they change the vault's shared vocabulary.

## The App, When It's Running

The Obsidian CLI (`obsidian` / `obsidian-cli`) reaches the running app: resolved links, the tag and property index, Bases evaluation, link-updating renames, File Recovery history. Probe with `obsidian version`; it needs a 1.12+ installer and the CLI enabled in Settings → General → Advanced, and launches the app if it isn't running. Two traps before the first command: it exits 0 even when it fails (errors arrive as text on stdout), and most commands act on whichever note is open in the app unless `path=` is given. Details in `references/cli.md`.

## Boundaries

- Not for Markdown that will never live in Obsidian, or for plugin configuration JSON under `.obsidian/plugins/`
- Not for Dataview or Templater syntax unless the vault already uses that plugin or the user asks
- Not for Mermaid or other diagram-as-code formats; canvases are JSON Canvas files
- Deleting, running `eval`, or changing plugins, themes, or sync through the CLI needs explicit user intent

## Verification

- Files parse (YAML frontmatter, `.base` YAML, `.canvas` JSON) and pass the checks at the end of the matching reference.
- Tags and property keys already exist in the vault, or the reply names each new one.
- Results that only the app can confirm — a base's rows, link resolution after a rename — are checked through the CLI when it responds. When it doesn't, the reply says what wasn't checked in-app.

## References

- [Obsidian Help](https://help.obsidian.md/): [Obsidian Flavored Markdown](https://help.obsidian.md/obsidian-flavored-markdown), [Properties](https://help.obsidian.md/properties), [Bases syntax](https://help.obsidian.md/bases/syntax), [CLI](https://help.obsidian.md/cli); [JSON Canvas 1.0](https://jsoncanvas.org/spec/1.0/)
- Consolidates the former `obsidian-markdown`, `obsidian-bases`, and `obsidian-canvas` skills. Adapted from [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) (MIT).
