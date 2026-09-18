# Output Patterns

Use these patterns when skills need to produce consistent, high-quality output.

## Template Pattern

Provide templates for output format. Match the level of strictness to your needs.

**For a real consumer contract (such as a machine-readable CLI response):**

```markdown
## Output contract

The existing consumer expects JSON on stdout with these fields:
- `status`: `ok` or `error`
- `result`: the value on success, null on failure
- `error`: null on success, otherwise an object with `code` and `message`

Send diagnostics to stderr so the consumer can parse stdout. Preserve the
established exit-code mapping and test success and failure with that consumer.
```

Use the actual consumer's schema, not this example by default. A narrative
report does not need fixed headings merely because consistency is desirable.

**For flexible guidance (when adaptation is useful):**

```markdown
## Report structure

Here is a sensible default format, but use your best judgment:

# [Analysis Title]

## Executive summary
[Overview]

## Key findings
[Adapt sections based on what you discover]

## Recommendations
[Tailor to the specific context]

Adjust sections as needed for the specific analysis type.
```

## Examples Pattern

For skills where output quality depends on seeing examples, provide input/output pairs:

```markdown
## Commit message format

Generate commit messages following these examples:

**Example 1:**
Input: Added user authentication with JWT tokens
Output:
```
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware
```

**Example 2:**
Input: Fixed bug where dates displayed incorrectly in reports
Output:
```
fix(reports): correct date formatting in timezone conversion

Use UTC timestamps consistently across report generation
```

Follow this style: type(scope): brief description, then detailed explanation.
```

Examples help the agent understand the desired style and level of detail more clearly than descriptions alone.
