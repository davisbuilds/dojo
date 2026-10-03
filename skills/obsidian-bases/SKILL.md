---
name: obsidian-bases
description: Create and edit Obsidian Bases (.base files) with database-style views, filters, formulas, and summaries. Use when working with .base files, building table/card/dashboard views over a vault, or when the user mentions Bases, filters, or formulas in Obsidian.
skill-type: reference
version: 2.0.0
---

# Obsidian Bases

A `.base` file is YAML defining filters, formulas, property display config, and one or more views over vault files. The same YAML can be embedded in a note as a ```` ```base ```` code block. Bases is a core plugin; Dataview syntax does not apply.

## When To Use

- Creating or editing `.base` files or `base` code blocks
- Writing Bases filters, formulas, or summaries
- Debugging a base that shows the wrong rows, empty columns, or `Error:` cells

## Schema

```yaml
filters:                 # global; ANDed with each view's filters
  and:
    - file.inFolder("Library")
    - 'type == "book"'
formulas:
  age_days: '(now() - file.ctime).days.round()'
  label: 'if(rating >= 4, "★ " + file.name, file.name)'
properties:              # display config only; not used by filters or formulas
  formula.age_days:
    displayName: "Age (days)"
summaries:               # custom summary formulas; `values` is the column's list
  mean2: 'values.mean().round(2)'
views:
  - type: table          # table | cards | list | map, plus plugin/newer types
    name: "By author"
    filters: 'status != "abandoned"'
    groupBy:
      property: author
      direction: ASC
    order: [file.name, author, formula.age_days]
    summaries:
      formula.age_days: Average
    limit: 50
```

## What Usually Goes Wrong

- **No filter means the whole vault.** There is no `from`; an unfiltered base includes every file, attachments included. Scope with `file.inFolder()`, `file.hasTag()`, a property test, and `file.ext == "md"` when only notes should appear.
- **Filter on the vault's real values.** Property names and values must match the frontmatter exactly (`type == "book"` misses notes typed `Book` or `books`), and tags are tested with `file.hasTag("x")`, not `tags == "x"`.
- **Property namespaces.** Bare names are note properties (`author` = `note.author`); `file.*` is file metadata; formulas are referenced as `formula.name`. Display names never work in expressions.
- **Quoting.** Expressions are YAML strings: wrap in single quotes when they contain double-quoted literals (`'status == "done"'`). Text literals need their own quotes.
- **Date math.** `today()`/`now()` plus or minus a duration string works (`file.mtime > now() - "7d"`; units `y M w d h m s`). Subtracting two dates gives a Duration, which supports neither `.round()` nor division into days; read a numeric field first: `(date(due) - today()).days.round()`. Scale durations explicitly with the duration on the left: `duration("1d") * 2`.
- **Links.** Wikilinks in frontmatter are Link objects: compare with `author == this` or `list.contains(link("Name"))`, not string equality.
- **`this`** is the base file when opened directly, the embedding note when embedded, and the active note when shown in a sidebar.
- **Expensive or stale fields.** `file.backlinks` and `file.properties` are slow and don't refresh as the vault changes; prefer `file.links` from the other side, or named properties.
- **View types.** Copy a `type` string from a view created in the UI rather than guessing one; newer types (such as Kanban) require newer Obsidian versions.

Default summary names: `Average`, `Min`, `Max`, `Sum`, `Range`, `Median`, `Stddev` (numbers); `Earliest`, `Latest`, `Range` (dates); `Checked`, `Unchecked` (booleans); `Empty`, `Filled`, `Unique` (any).

Full function catalog by type (global, string, number, date, duration fields, list, link, file, object, regex): `references/functions.md`.

## Embedding

`![[Books.base]]` or `![[Books.base#View name]]` in a note.

## Boundaries

- Not for `.md` note syntax (`obsidian-markdown`) or `.canvas` files (`obsidian-canvas`)
- Not for Dataview or other query plugins; Bases has its own expression language

## Verification

- The file parses as YAML, and every `formula.x` in `order`, `properties`, and `summaries` is defined.
- Useful when the Obsidian CLI is available (`obsidian version` succeeds): `obsidian base:query path=<file.base> view="<name>" format=json` runs the real evaluator. Formula errors come back as `Error: ...` cell values rather than a failed command, so a clean exit alone doesn't mean the base works.
- Without the CLI, spot-check filters by reading the frontmatter of a note that should match and one that shouldn't.

## References

- [Bases syntax](https://help.obsidian.md/bases/syntax), [Functions](https://help.obsidian.md/bases/functions), [Views](https://help.obsidian.md/bases/views)
- Date-subtraction behavior above was verified against Obsidian 1.13.7; the official syntax page still describes it as returning milliseconds.
- Adapted from [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) (MIT).

## Sibling skills

Three Obsidian-format references, distinguished by *file type*.

- `obsidian-markdown` — `.md` notes with Obsidian extensions (wikilinks, callouts, properties). Use for note authoring; this skill is for the database-view layer over those notes.
- `obsidian-canvas` — `.canvas` visual canvases. Orthogonal.
