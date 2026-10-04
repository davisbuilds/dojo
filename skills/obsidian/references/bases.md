# Bases (.base)

A `.base` file is YAML defining filters, formulas, property display config, and one or more views over vault files. The same YAML can be embedded in a note as a ```` ```base ```` code block. Bases is a core plugin; Dataview syntax does not apply.

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
- **Property namespaces.** Bare names are note properties (`author` = `note.author`); `file.*` is file metadata (fields table in `functions.md`); formulas are referenced as `formula.name`. Display names never work in expressions. For a note, `file.name` compares equal to the name without `.md`.
- **Quoting.** Expressions are YAML strings: wrap in single quotes when they contain double-quoted literals (`'status == "done"'`). Text literals need their own quotes.
- **Date math.** `today()`/`now()` plus or minus a duration string works (`file.mtime > now() - "7d"`; units `y M w d h m s`). Subtracting two dates gives a Duration, which supports neither `.round()` nor division into days; read a numeric field first: `(date(due) - today()).days.round()`. Scale durations explicitly with the duration on the left: `duration("1d") * 2`.
- **Links.** Wikilinks in frontmatter are Link objects: compare with `author == this` or `list.contains(link("Name"))`, not string equality.
- **`this`** is the base file when opened directly, the embedding note when embedded, and the active note when shown in a sidebar.
- **Expensive or stale fields.** `file.backlinks` and `file.properties` are slow and don't refresh as the vault changes; prefer `file.links` from the other side, or named properties.
- **View types.** Copy a `type` string from a view created in the UI rather than guessing one; newer types (such as Kanban) require newer Obsidian versions.

Default summary names: `Average`, `Min`, `Max`, `Sum`, `Range`, `Median`, `Stddev` (numbers); `Earliest`, `Latest`, `Range` (dates); `Checked`, `Unchecked` (booleans); `Empty`, `Filled`, `Unique` (any).

Full function catalog by type (global, string, number, date, duration fields, list, link, file fields and functions, object, regex): `functions.md`.

## Embedding

`![[Books.base]]` or `![[Books.base#View name]]` in a note.

## Checks

- The file parses as YAML, and every `formula.x` in `order`, `properties`, and `summaries` is defined.
- Only the app evaluates a base. With the CLI: `obsidian base:query path=<file.base> view="<name>" format=json` (or `format=paths` for just the row set). Formula errors come back as `Error: ...` cell values, not a failed command, so search the output for them. Without the CLI, spot-check filters against a note that should match and one that shouldn't, and say the base wasn't evaluated.
- Date-subtraction behavior above was verified against Obsidian 1.13.7; the official syntax page still describes it as returning milliseconds.
