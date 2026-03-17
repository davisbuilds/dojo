# Storage Layout

`self-improve` uses a dedicated, portable store rooted at `.self-improve/`.

## Default Layout

```text
.self-improve/
├── inbox/        # Raw structured learning records
├── summaries/    # Compact markdown summaries
├── proposals/    # Reviewable promotion proposals
└── candidates/   # Optional extracted skill drafts
```

The scripts accept `--store /path/to/workspace` and create `.self-improve/` underneath that path. If the provided path already ends with `.self-improve`, it is used directly.

## Reading Discipline

1. Read `summaries/latest.md` first.
2. Open raw inbox records only when the summary points to a record that matters.
3. Generate a promotion proposal before editing any durable memory or skill artifacts.

## Record Shape

Raw inbox records are JSON objects with:

- `record_id`
- `created_at`
- `kind`
- `summary`
- `evidence`
- `tags`
- `source`
- `context`
- `status`

The canonical example lives in `assets/learning-entry-template.json`.
