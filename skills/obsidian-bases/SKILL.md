---
name: obsidian-bases
description: Create and edit Obsidian Bases (.base files) with database-style views, filters, formulas, and summaries. Use when working with .base files, building table/card/dashboard views over a vault, or when the user mentions Bases, filters, or formulas in Obsidian.
---

# Obsidian Bases Skill

Obsidian Bases are YAML-based `.base` files that define dynamic views of notes in an Obsidian vault. A Base file can contain multiple views, global filters, formulas, property configurations, and custom summaries.

## Complete Schema

```yaml
# Global filters apply to ALL views in the base
filters:
  and: []    # All conditions must be true
  or: []     # Any condition can be true
  not: []    # Exclude matching items
  # Can also be a single filter string: 'status == "done"'

# Define formula properties (computed values)
formulas:
  formula_name: 'expression'

# Configure display names for properties
properties:
  property_name:
    displayName: "Display Name"
  formula.formula_name:
    displayName: "Formula Display Name"

# Define custom summary formulas
summaries:
  custom_summary_name: 'values.mean().round(3)'

# Define one or more views
views:
  - type: table | cards | list | map
    name: "View Name"
    limit: 10                    # Optional: limit results
    groupBy:                     # Optional: group results
      property: property_name
      direction: ASC | DESC
    filters:                     # View-specific filters (same syntax as global)
      and: []
    order:                       # Properties to display in order
      - file.name
      - property_name
      - formula.formula_name
    summaries:                   # Map properties to summary formulas
      property_name: Average
```

## Filter Syntax

```yaml
# Single filter
filters: 'status == "done"'

# AND / OR / NOT
filters:
  and:
    - 'status == "done"'
    - 'priority > 3'

# Nested filters
filters:
  or:
    - file.hasTag("tag")
    - and:
        - file.hasTag("book")
        - file.hasLink("Textbook")
    - not:
        - file.hasTag("archived")
```

### Filter Operators

| Operator | Description |
|----------|-------------|
| `==` | equals |
| `!=` | not equal |
| `>`, `<`, `>=`, `<=` | comparisons |
| `&&` | logical and |
| `\|\|` | logical or |
| `!` | logical not |

## Properties

Three types of properties:
1. **Note properties** - From frontmatter: `author` or `note.author`
2. **File properties** - File metadata: `file.name`, `file.mtime`, etc.
3. **Formula properties** - Computed values: `formula.my_formula`

### File Properties

| Property | Type | Description |
|----------|------|-------------|
| `file.name` | String | File name |
| `file.basename` | String | Name without extension |
| `file.path` | String | Full path |
| `file.folder` | String | Parent folder |
| `file.ext` | String | Extension |
| `file.size` | Number | Size in bytes |
| `file.ctime` | Date | Created time |
| `file.mtime` | Date | Modified time |
| `file.tags` | List | All tags |
| `file.links` | List | Internal links |
| `file.backlinks` | List | Files linking to this |
| `file.embeds` | List | Embeds in note |
| `file.properties` | Object | All frontmatter |

### The `this` Keyword

- In main content area: refers to the base file itself
- When embedded: refers to the embedding file
- In sidebar: refers to the active file in main content

## Formulas

```yaml
formulas:
  total: "price * quantity"
  status_icon: 'if(done, "✅", "⏳")'
  formatted_price: 'if(price, price.toFixed(2) + " dollars")'
  created: 'file.ctime.format("YYYY-MM-DD")'
  days_old: '(now() - file.ctime).days'
  days_until_due: 'if(due_date, (date(due_date) - today()).days, "")'
```

For the complete function catalog (global, string, number, list, date, duration, file, link, object, regex functions), see `references/functions.md`.

## Default Summary Formulas

| Name | Input | Description |
|------|-------|-------------|
| `Average`, `Min`, `Max`, `Sum`, `Range`, `Median`, `Stddev` | Number | Numeric aggregations |
| `Earliest`, `Latest`, `Range` | Date | Date aggregations |
| `Checked`, `Unchecked` | Boolean | Boolean counts |
| `Empty`, `Filled`, `Unique` | Any | General counts |

## Complete Example: Task Tracker

```yaml
filters:
  and:
    - file.hasTag("task")
    - 'file.ext == "md"'

formulas:
  days_until_due: 'if(due, (date(due) - today()).days, "")'
  is_overdue: 'if(due, date(due) < today() && status != "done", false)'
  priority_label: 'if(priority == 1, "🔴 High", if(priority == 2, "🟡 Medium", "🟢 Low"))'

properties:
  status:
    displayName: Status
  formula.days_until_due:
    displayName: "Days Until Due"
  formula.priority_label:
    displayName: Priority

views:
  - type: table
    name: "Active Tasks"
    filters:
      and:
        - 'status != "done"'
    order:
      - file.name
      - status
      - formula.priority_label
      - due
      - formula.days_until_due
    groupBy:
      property: status
      direction: ASC
    summaries:
      formula.days_until_due: Average

  - type: table
    name: "Completed"
    filters:
      and:
        - 'status == "done"'
    order:
      - file.name
      - completed_date
```

## Common Filter Patterns

```yaml
# By tag
filters:
  and:
    - file.hasTag("project")

# By folder
filters:
  and:
    - file.inFolder("Notes")

# By date range (last 7 days)
filters:
  and:
    - 'file.mtime > now() - "7d"'

# By property value
filters:
  and:
    - 'status == "active"'
    - 'priority >= 3'
```

## Embedding Bases

```markdown
![[MyBase.base]]
![[MyBase.base#View Name]]
```

## YAML Quoting Rules

- Use single quotes for formulas containing double quotes: `'if(done, "Yes", "No")'`
- Use double quotes for simple strings: `"My View Name"`

## When To Use

- Creating or editing `.base` files for Obsidian vaults
- Building table, cards, list, or map views over vault notes
- Writing filters, formulas, or summaries for Bases
- User mentions Obsidian Bases, database views, or `.base` file syntax

## Boundaries

- Not for editing standard Obsidian Markdown (use obsidian-markdown skill instead)
- Not for Dataview plugin queries; Bases uses its own YAML schema
- Skip when the user needs a community plugin that is not Bases (e.g., Kanban, Calendar)
- Do not generate Base files that reference plugins or properties the vault does not have

## Output

- A valid `.base` YAML file or YAML code block ready to paste into Obsidian
- Includes views, filters, formulas, properties, and summaries as needed
- Uses correct quoting rules (single quotes for expressions containing double quotes)

## Verification

- Output is valid YAML that Obsidian Bases can parse without errors
- All referenced properties, formulas, and summary names are internally consistent
- Filter expressions use only documented operators and functions
- Duration arithmetic accesses numeric fields (`.days`, `.hours`) before applying `.round()`

## References

- [Bases Syntax](https://help.obsidian.md/bases/syntax)
- [Functions](https://help.obsidian.md/bases/functions)
- [Views](https://help.obsidian.md/bases/views)
- [Formulas](https://help.obsidian.md/formulas)
