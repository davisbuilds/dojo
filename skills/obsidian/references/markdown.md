# Notes (.md)

Obsidian-specific note syntax and its traps; CommonMark/GFM is assumed knowledge. Vault-fit guidance lives in `SKILL.md`.

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

## Checks

- Frontmatter parses as YAML; wikilinks in it are quoted; list properties are lists.
- Link targets exist: by file name in the vault, or `obsidian unresolved verbose` (which misses literal `[[##x]]`, above).
- Notes written on mobile often contain non-breaking spaces and curly quotes, which make exact-string replacements silently miss; re-read the changed region.
