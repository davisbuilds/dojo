# Pull Request Body Fallback

Read and follow the repository's template when present. Otherwise adapt this
small example to the final change; no heading or section quota is required.

```markdown
<Concrete problem and resulting behavior; include an example if it clarifies.>

Validation: <checks actually run and their result, or relevant CI evidence>

<Material limitation or reviewer decision, only if there is one.>
```

Keep the title and body about the final implementation. Distinguish completed
validation from proposed checks. Add an issue reference when relevant and use
closing syntax only when the issue is resolved. Pass the exact Markdown in a
file with `--body-file`; avoid shell interpolation of prose or backticks.
