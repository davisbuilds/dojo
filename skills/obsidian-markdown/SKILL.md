---
name: obsidian-markdown
description: Create and edit Obsidian Flavored Markdown with wikilinks, embeds, callouts, properties, and other Obsidian-specific syntax. Use when working with .md files in Obsidian, or when the user mentions wikilinks, callouts, frontmatter, tags, embeds, or Obsidian notes.
skill-type: reference
version: 2.0.0
---

# Obsidian Flavored Markdown

Obsidian-specific syntax plus what it takes for a note to fit an existing vault. CommonMark/GFM is assumed knowledge. Vault files are plain Markdown, YAML, and JSON: read and edit them directly. When Obsidian is running with its CLI enabled, the CLI adds what only the app knows — resolved links, indexed tags and properties, applied setting defaults, link-updating renames.

Notes that parse fine can still drift from their vault — a new tag variant, an unfamiliar property key, the wrong link style — and that drift fragments tag search and Bases views.

## When To Use

- Creating or editing `.md` notes that live in an Obsidian vault
- Adding or changing frontmatter properties, tags, wikilinks, embeds, callouts, or block references
- Renaming or moving notes inside a vault

## Fit the Vault

A new or edited note should look like its neighbors. The sources, roughly in order of authority:

- **Vault guidance.** An `AGENTS.md`/`CLAUDE.md` at the vault root overrides this skill's examples, especially tag vocabulary and property conventions. Read it before adding tags or properties.
- **Vault settings** in `.obsidian/`, when the task touches them: `app.json` sets link style (`useMarkdownLinks: true` means Markdown links with URL-encoded paths instead of `[[Note Name]]`), link paths (`newLinkFormat`: shortest, relative, or absolute), and where attachments go (`attachmentFolderPath`); `daily-notes.json` and `templates.json` set those folders and formats.
- **Sibling notes** in the same folder: their frontmatter keys, key names, value vocabulary (`type`, `status`), and list style — or no frontmatter where they have none. Bases views filter on property values, so an invented key or value silently drops a note from a view.
- **Let the app resolve settings when it can.** With the Obsidian CLI, `obsidian daily:path` returns today's daily-note path with the app's folder and date-format defaults applied (`daily-notes.json` omits unchanged defaults, so reading it can mislead), `daily:append content=...` writes to it, and `property:set name=<key> value=<v> type=<text|list|number|checkbox|date|datetime>` writes a property with an explicit type instead of leaving the type to inference.
- **Existing tags.** Search frontmatter `tags:` and inline `#tags`, or ask the app with `obsidian tags counts sort=count`. Tags are case-insensitive (`#AI` and `#ai` are one tag), so reuse the established form rather than adding a casing, plural, or synonym variant, and skip tags that only restate the folder or a property. A new tag earns its place when nothing fits and it will apply to more than one note; mention new tags and property keys in the reply, since they change the vault's shared vocabulary.

## Properties

```yaml
---
type: book
author: "[[Ursula K. Le Guin]]"
related:
  - "[[Other Note]]"
published: 1969-03-01
rating: 4.5
read: true
tags:
  - fiction
aliases:
  - Left Hand
---
```

- Quote wikilinks in YAML (`"[[Note]]"`); unquoted `[[...]]` parses as a nested list. Use wikilinks, not Markdown links, for internal links in properties.
- `tags`, `aliases`, and `cssclasses` are lists. The singular `tag`/`alias`/`cssclass` keys are deprecated.
- Frontmatter tags take no `#`. Types are inferred per property name vault-wide (text, list, number, checkbox, date, datetime), so keep one type per key: a key that is a date in one note and free text in another breaks sorting and Bases filters.
- When editing, preserve existing key order and list style (`[a, b]` vs block list); don't reformat the whole block.

## Tags

Inline `#tag` or frontmatter `tags:`. Allowed: letters, numbers, `_`, `-`, `/` for nesting (`#area/health`); at least one non-numeric character; no spaces. If the vault keeps tags in frontmatter, don't also add inline tag lines.

## Links and Block References

```markdown
[[Note Name|Display]]   [[Note Name#Heading]]   [[#Heading in this note]]
[[Note Name#^block-id]]

A linkable paragraph. ^block-id
```

- Block IDs: letters, numbers, and dashes only. For a list, quote, or table, put `^block-id` on its own line after the block, separated by a blank line.
- Shortest-form wikilinks (`[[Name]]`) resolve by unique file name, so they survive a folder move but break on rename; path-form links break on either. Rename or move with `obsidian rename`/`obsidian move` (which honor the vault's "Automatically update internal links" setting), or update inbound links yourself.
- `[[##heading]]` and `[[^^block]]` are editor search triggers that autocomplete turns into a real link. Written literally into a file, `[[^^x]]` is an unresolved link and `[[##x]]` silently becomes a link to a missing heading in the same note, which `obsidian unresolved` does not report.
- Inside tables, escape the pipe: `[[Note\|Display]]`, `![[image.png\|200]]`.

## Embeds and Callouts

Embeds are wikilinks with `!`; sizes and pages go after the target: `![[image.png|300]]` (width) or `|640x480`, `![[doc.pdf#page=3]]` (also `#height=400`), external `![alt|300](https://...)`. A fenced `query` block embeds live search results.

Callouts: `> [!type] Optional title`; add `-` after the type to collapse by default or `+` to start expanded but foldable; nest with `> >`. Types (aliases): `note`, `abstract` (`summary`, `tldr`), `info`, `todo`, `tip` (`hint`, `important`), `success` (`check`, `done`), `question` (`help`, `faq`), `warning` (`caution`, `attention`), `failure` (`fail`, `missing`), `danger` (`error`), `bug`, `example`, `quote` (`cite`). Unknown types render as `note`; a custom type needs a CSS snippet in `.obsidian/snippets/` targeting `.callout[data-callout="name"]` (set `--callout-color: r, g, b` and `--callout-icon: lucide-<icon>`), and the snippet does nothing until enabled (Appearance settings or `obsidian snippet:enable name=<file>`).

`==highlight==`; `%%hidden comment%%`, or `%%` lines around a hidden block.

## Boundaries

- Not for `.base` files (`obsidian-bases`) or `.canvas` files (`obsidian-canvas`)
- Not for Markdown that will never live in Obsidian
- Do not write Dataview or Templater syntax unless the vault already uses that plugin or the user asks
- Skip plugin configuration JSON under `.obsidian/plugins/`

## Verification

- Frontmatter parses as YAML; wikilinks in it are quoted; list properties are lists.
- Tags and property keys either already exist in the vault or are named in the reply as new.
- Link targets exist: by file name in the vault, or with `obsidian unresolved verbose` when the CLI responds (`obsidian version`; it needs the app running and the CLI enabled under Settings → General → Advanced). `obsidian properties file=<name>` and `obsidian tags file=<name>` show what Obsidian actually indexed when that matters.
- Edits landed where intended. Notes written on mobile often contain non-breaking spaces and curly quotes, which make exact-string replacements silently miss.

## References

- [Obsidian Flavored Markdown](https://help.obsidian.md/obsidian-flavored-markdown), [Properties](https://help.obsidian.md/properties), [Tags](https://help.obsidian.md/tags), [Callouts](https://help.obsidian.md/callouts), [Obsidian CLI](https://help.obsidian.md/cli)
- Adapted from [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) (MIT).

## Sibling skills

Three Obsidian-format references, distinguished by *file type*.

- `obsidian-bases` — `.base` files: database-style views, filters, formulas. Use when the file extension is `.base` or the user mentions Bases.
- `obsidian-canvas` — `.canvas` files: visual node/edge canvases. Use for `.canvas` files or whiteboard-style diagrams.
- This skill covers `.md` notes with Obsidian-Flavored extensions (wikilinks, callouts, embeds, properties).
