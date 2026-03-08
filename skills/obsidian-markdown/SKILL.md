---
name: obsidian-markdown
description: Create and edit Obsidian Flavored Markdown with wikilinks, embeds, callouts, properties, and other Obsidian-specific syntax. Use when working with .md files in Obsidian, or when the user mentions wikilinks, callouts, frontmatter, tags, embeds, or Obsidian notes.
---

# Obsidian Flavored Markdown Skill

Obsidian extends CommonMark / GitHub Flavored Markdown with wikilinks, embeds, callouts, comments, and specialized properties. This skill covers only the Obsidian-specific extensions — standard Markdown syntax (headings, lists, bold/italic, code blocks, tables, footnotes, blockquotes, horizontal rules, HTML) is assumed knowledge.

## Internal Links (Wikilinks)

### Basic Links

```markdown
[[Note Name]]
[[Note Name|Display Text]]
```

### Link to Headings

```markdown
[[Note Name#Heading]]
[[Note Name#Heading|Custom Text]]
[[#Heading in same note]]
[[##Search all headings in vault]]
```

### Link to Blocks

```markdown
[[Note Name#^block-id]]
[[Note Name#^block-id|Custom Text]]
```

Define a block ID by adding `^block-id` at the end of a paragraph:
```markdown
This is a paragraph that can be linked to. ^my-block-id
```

For lists and quotes, add the block ID on a separate line:
```markdown
> This is a quote
> With multiple lines

^quote-id
```

### Search Links

```markdown
[[##heading]]     Search for headings containing "heading"
[[^^block]]       Search for blocks containing "block"
```

## Embeds

### Embed Notes

```markdown
![[Note Name]]
![[Note Name#Heading]]
![[Note Name#^block-id]]
```

### Embed Images

```markdown
![[image.png]]
![[image.png|640x480]]    Width x Height
![[image.png|300]]        Width only (maintains aspect ratio)
```

### External Images

```markdown
![Alt text](https://example.com/image.png)
![Alt text|300](https://example.com/image.png)
```

### Embed Audio / PDF

```markdown
![[audio.mp3]]
![[document.pdf]]
![[document.pdf#page=3]]
![[document.pdf#height=400]]
```

### Embed Search Results

````markdown
```query
tag:#project status:done
```
````

## Callouts

### Basic Callout

```markdown
> [!note]
> This is a note callout.

> [!info] Custom Title
> This callout has a custom title.

> [!tip] Title Only
```

### Foldable Callouts

```markdown
> [!faq]- Collapsed by default
> This content is hidden until expanded.

> [!faq]+ Expanded by default
> This content is visible but can be collapsed.
```

### Nested Callouts

```markdown
> [!question] Outer callout
> > [!note] Inner callout
> > Nested content
```

### Supported Callout Types

| Type | Aliases | Description |
|------|---------|-------------|
| `note` | - | Blue, pencil icon |
| `abstract` | `summary`, `tldr` | Teal, clipboard icon |
| `info` | - | Blue, info icon |
| `todo` | - | Blue, checkbox icon |
| `tip` | `hint`, `important` | Cyan, flame icon |
| `success` | `check`, `done` | Green, checkmark icon |
| `question` | `help`, `faq` | Yellow, question mark |
| `warning` | `caution`, `attention` | Orange, warning icon |
| `failure` | `fail`, `missing` | Red, X icon |
| `danger` | `error` | Red, zap icon |
| `bug` | - | Red, bug icon |
| `example` | - | Purple, list icon |
| `quote` | `cite` | Gray, quote icon |

### Custom Callouts (CSS)

```css
.callout[data-callout="custom-type"] {
  --callout-color: 255, 0, 0;
  --callout-icon: lucide-alert-circle;
}
```

## Highlight Syntax

```markdown
==Highlighted text==
```

## Comments

```markdown
This is visible %%but this is hidden%% text.

%%
This entire block is hidden.
It won't appear in reading view.
%%
```

## Properties (Frontmatter)

Properties use YAML frontmatter at the start of a note:

```yaml
---
title: My Note Title
date: 2024-01-15
tags:
  - project
  - important
aliases:
  - My Note
  - Alternative Name
cssclasses:
  - custom-class
status: in-progress
rating: 4.5
completed: false
due: 2024-02-01T14:30:00
---
```

### Property Types

| Type | Example |
|------|---------|
| Text | `title: My Title` |
| Number | `rating: 4.5` |
| Checkbox | `completed: true` |
| Date | `date: 2024-01-15` |
| Date & Time | `due: 2024-01-15T14:30:00` |
| List | `tags: [one, two]` or YAML list |
| Links | `related: "[[Other Note]]"` |

### Default Properties

- `tags` - Note tags
- `aliases` - Alternative names for the note
- `cssclasses` - CSS classes applied to the note

## Tags

```markdown
#tag
#nested/tag
#tag-with-dashes
#tag_with_underscores
```

Tags can contain: letters (any language), numbers (not as first character), underscores, hyphens, forward slashes (for nesting).

In frontmatter:
```yaml
tags:
  - tag1
  - nested/tag2
```

## Escaping Pipes in Tables

Escape pipes with backslash in wikilinks inside tables:
```markdown
| Column 1 | Column 2 |
|----------|----------|
| [[Link\|Display]] | ![[Image\|100]] |
```

## Usage

1. Use wikilinks (`[[...]]`) for internal note references instead of Markdown links
2. Use embeds (`![[...]]`) to inline content from other notes, images, or PDFs
3. Use callouts (`> [!type]`) for structured admonitions
4. Use YAML frontmatter for structured metadata (tags, aliases, dates)
5. Use `%%comments%%` for content hidden from reading view

## When To Use

- Creating or editing `.md` files intended for an Obsidian vault
- User mentions wikilinks, callouts, embeds, frontmatter properties, or Obsidian-specific syntax
- Building notes with block references or embedded search queries
- Adding or updating YAML frontmatter properties on Obsidian notes

## Boundaries

- Not for Obsidian Bases / `.base` files (use obsidian-bases skill instead)
- Not for plain/GitHub Flavored Markdown that will never live in Obsidian
- Skip when the task is purely about Obsidian plugin configuration (e.g., community plugin settings JSON)
- Do not generate Dataview or Templater syntax unless the user explicitly requests it

## Output

- Valid Obsidian Flavored Markdown ready to save as a `.md` file in a vault
- Frontmatter uses correct YAML types (text, number, list, date, checkbox)
- Wikilinks, embeds, callouts, and block IDs follow documented syntax

## Verification

- Frontmatter parses as valid YAML between `---` fences
- Internal links use `[[...]]` syntax with proper heading/block anchors
- Callout types are from the supported set (note, tip, warning, etc.) or clearly marked as custom
- No raw HTML is used where an Obsidian Markdown equivalent exists

## References

- [Basic formatting syntax](https://help.obsidian.md/syntax)
- [Advanced formatting syntax](https://help.obsidian.md/advanced-syntax)
- [Obsidian Flavored Markdown](https://help.obsidian.md/obsidian-flavored-markdown)
- [Internal links](https://help.obsidian.md/links)
- [Embed files](https://help.obsidian.md/embeds)
- [Callouts](https://help.obsidian.md/callouts)
- [Properties](https://help.obsidian.md/properties)
