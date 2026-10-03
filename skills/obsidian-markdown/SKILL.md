---
name: obsidian-markdown
description: Create and edit Obsidian Flavored Markdown with wikilinks, embeds, callouts, properties, and other Obsidian-specific syntax. Use when working with .md files in Obsidian, or when the user mentions wikilinks, callouts, frontmatter, tags, embeds, or Obsidian notes.
skill-type: reference
version: 2.0.0
---

# Obsidian Flavored Markdown

Obsidian-specific syntax and vault conventions only; CommonMark/GFM is assumed knowledge. The common failures are not syntax errors but notes that drift from the vault they land in: invented tags, mismatched properties, wrong link style, broken links after a rename.

## When To Use

- Creating or editing `.md` notes that live in an Obsidian vault
- Adding or changing frontmatter properties, tags, wikilinks, embeds, callouts, or block references
- Renaming or moving notes inside a vault

## Fit the Vault First

Before writing into an existing vault:

1. **Read vault guidance.** An `AGENTS.md`/`CLAUDE.md` at the vault root overrides this skill's examples, especially tag vocabulary and property conventions.
2. **Read vault settings** in `.obsidian/` when the task touches them:
   - `app.json` — `useMarkdownLinks: true` means Markdown-style links with URL-encoded paths (spaces as `%20`) instead of `[[Note Name]]`; `newLinkFormat` (shortest/relative/absolute) sets link paths; `attachmentFolderPath` is where new images and PDFs go.
   - `daily-notes.json` — daily note `folder` and `format`; `templates.json` — template folder.
3. **Match sibling notes** in the same folder: same frontmatter keys, key names, value vocabulary (e.g. `type`, `status`), and list style — or no frontmatter where siblings have none. Bases views filter on property values, so an invented key or value silently drops a note from a view.
4. **Reuse tags.** List existing ones (`obsidian tags counts sort=count`, or search `tags:` and inline `#tags`). Tags are case-insensitive, so `#AI` and `#ai` are one tag; match the established form instead of adding a casing, plural, or synonym variant. Don't tag what a folder or property already records. Coin a new tag only when nothing fits and it will apply to more than one note, and say so.

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
- Inside tables, escape the pipe: `[[Note\|Display]]`, `![[image.png\|200]]`.

## Embeds

`![[Note]]`, `![[Note#Heading]]`, `![[Note#^block-id]]`, `![[image.png|300]]` (width) or `|640x480`, `![[doc.pdf#page=3]]`. External images: `![alt|300](https://...)`. A fenced `query` block embeds live search results.

## Callouts, Highlights, Comments

```markdown
> [!warning] Optional title
> Body.

> [!faq]- Collapsed by default (`+` = expanded but foldable)
```

Types (aliases): `note`, `abstract` (`summary`, `tldr`), `info`, `todo`, `tip` (`hint`, `important`), `success` (`check`, `done`), `question` (`help`, `faq`), `warning` (`caution`, `attention`), `failure` (`fail`, `missing`), `danger` (`error`), `bug`, `example`, `quote` (`cite`). Unknown types render as `note`. Callouts nest with `> >`.

`==highlight==`. `%%hidden comment%%`, or `%%` lines around a hidden block.

## Boundaries

- Not for `.base` files (`obsidian-bases`) or `.canvas` files (`obsidian-canvas`)
- Not for Markdown that will never live in Obsidian
- Do not write Dataview or Templater syntax unless the vault already uses that plugin or the user asks
- Skip plugin configuration JSON under `.obsidian/plugins/`

## Verification

- Frontmatter parses as YAML; wikilinks in it are quoted; list properties are lists.
- New tags and property keys already exist in the vault, or the reply names each new one.
- With the Obsidian CLI available (probe `obsidian version`; it needs the app running and CLI enabled in Settings → General → Advanced): `obsidian unresolved verbose` shows no new broken links; `obsidian properties file=<name>` and `obsidian tags file=<name>` show what Obsidian actually indexed. Without it, check link targets exist by file name.
- Edits matched the file exactly. Notes written on mobile often contain non-breaking spaces and curly quotes, so exact-string replacements can silently miss; re-read the changed region.

## References

- [Obsidian Flavored Markdown](https://help.obsidian.md/obsidian-flavored-markdown), [Properties](https://help.obsidian.md/properties), [Tags](https://help.obsidian.md/tags), [Callouts](https://help.obsidian.md/callouts), [Obsidian CLI](https://help.obsidian.md/cli)
- Adapted from [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) (MIT).

## Sibling skills

Three Obsidian-format references, distinguished by *file type*.

- `obsidian-bases` — `.base` files: database-style views, filters, formulas. Use when the file extension is `.base` or the user mentions Bases.
- `obsidian-canvas` — `.canvas` files: visual node/edge canvases. Use for `.canvas` files or whiteboard-style diagrams.
- This skill covers `.md` notes with Obsidian-Flavored extensions (wikilinks, callouts, embeds, properties).
