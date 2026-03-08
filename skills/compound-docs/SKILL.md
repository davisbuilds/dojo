---
name: compound-docs
description: Capture solved problems as categorized documentation with YAML frontmatter for fast lookup. Use when a solution is confirmed and should be preserved for future retrieval.
allowed-tools:
  - Read # Parse conversation context
  - Write # Create resolution docs
  - Bash # Create directories
  - Grep # Search existing docs
---

## When To Use

- A non-trivial problem has been confirmed solved and the solution should be preserved
- User says "that worked", "it's fixed", or similar confirmation phrases
- User runs `/doc-fix` to manually trigger documentation capture
- Solution involved multiple investigation attempts or a non-obvious root cause

## Boundaries

- Not for documenting simple typos, obvious syntax errors, or trivial one-line fixes
- Not for writing project READMEs, API docs, or user-facing documentation
- Do not auto-promote patterns to Required Reading without explicit user approval
- Skip when the conversation lacks enough context to populate required YAML fields

## Output

- Single markdown file at `docs/solutions/[category]/[filename].md` with validated YAML frontmatter
- Cross-references added to related existing docs when similar issues are found
- Decision menu presented to user for follow-up actions

## Workflow

### 1. Detect Confirmation

Auto-invoke after phrases like "that worked", "it's fixed", "working now", "problem solved". Or manual via `/doc-fix`.

Skip documentation for simple typos, obvious syntax errors, and trivial fixes.

### 2. Gather Context

Extract from conversation history:

- **Module name**: Which module or component had the problem
- **Symptom**: Observable error/behavior (exact error messages)
- **Investigation attempts**: What didn't work and why
- **Root cause**: Technical explanation of actual problem
- **Solution**: What fixed it (code/config changes)
- **Prevention**: How to avoid in future
- **Environment**: Version, stage, OS, file/line references

If critical context is missing (module name, exact error, or resolution steps), ask user and wait before proceeding.

### 3. Check Existing Docs

Search `docs/solutions/` for similar issues by error message keywords and symptom category. If a similar issue is found, ask the user whether to create a new doc with cross-reference, update the existing doc, or skip. If no similar issue, proceed directly.

### 4. Generate Filename

Format: `[sanitized-symptom]-[module]-[YYYYMMDD].md`

Rules: lowercase, hyphens for spaces, no special characters, under 80 chars.

### 5. Validate YAML

Validate frontmatter against the schema defined in `references/yaml-schema.md`. All required fields must be present and enum values must match exactly. Block until validation passes.

### 6. Create Documentation

Map `problem_type` to category directory per `references/yaml-schema.md`. Create the directory if needed (`mkdir -p`). Populate `assets/resolution-template.md` with gathered context and validated YAML.

### 7. Cross-Reference & Follow-Up

If similar issues were found in step 3, add cross-references to both docs.

If this represents a common pattern (3+ similar issues), note it for potential pattern extraction.

Present the decision menu:

```
File created: docs/solutions/[category]/[filename].md

What's next?
1. Continue workflow (recommended)
2. Add to Required Reading - Promote to critical patterns
3. Link related issues - Connect to similar problems
4. Add to existing skill - Add to a learning skill
5. Create new skill - Extract into new learning skill
6. View documentation
7. Other
```

**Option 2 (Required Reading):** Extract pattern, format as wrong/correct with code examples, add to `docs/solutions/patterns/critical-patterns.md`. Never auto-promote — user must explicitly choose this option.

**Option 5 (New skill):** Run `python3 ../skill-creator/scripts/init_skill.py [skill-name]` and seed with this solution as first example.

## Quality Checklist

Good documentation includes:
- Exact error messages (copy-paste from output)
- Specific file:line references
- Failed attempts documented (helps avoid wrong paths)
- Technical explanation (not just "what" but "why")
- Code examples (before/after if applicable)
- Prevention guidance
- Cross-references to related issues

## Error Handling

- **Missing context:** Ask user, wait for response
- **YAML validation failure:** Show specific errors, block until valid
- **Similar issue ambiguity:** Present matches, let user choose action

## Verification

- YAML frontmatter validates against schema (all required fields, correct enum values)
- File created at `docs/solutions/[category]/[filename].md`
- Code examples included in solution section
- Cross-references added if related issues found
- User presented with decision menu
