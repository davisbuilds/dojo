# Compound Docs

Capture solved problems as categorized documentation with YAML frontmatter for fast lookup. This skill provides a 7-step workflow for documenting solutions that compound team knowledge.

## Purpose

When you solve a non-trivial problem, document it so future developers (and agents) can find it quickly. The structured YAML frontmatter enables filtering by:

- Problem type (build errors, test failures, runtime errors, etc.)
- Component (models, controllers, services, etc.)
- Root cause (missing includes, config errors, logic bugs, etc.)
- Severity (critical, high, medium, low)

## Files

| File | Description |
|------|-------------|
| `SKILL.md` | Main skill instructions with 7-step workflow |
| `schema.yaml` | Complete YAML frontmatter schema |
| `assets/resolution-template.md` | Template for troubleshooting docs |
| `assets/critical-pattern-template.md` | Template for critical patterns |
| `references/yaml-schema.md` | Reference for frontmatter fields |

## 7-Step Workflow

1. **Read Problem Context** - Gather conversation history and constraints
2. **Classify & Prepare** - Determine problem type, severity, category
3. **Apply Template** - Generate documentation from template
4. **Validate Frontmatter** - Check against schema.yaml
5. **Locate Target File** - Determine file path based on category
6. **Write File** - Create the documentation file
7. **Link in Patterns** - Add to critical-patterns.md if significant

## Category Mapping

Based on `problem_type`, documentation is filed in:

- `build_error` → `docs/solutions/build-errors/`
- `test_failure` → `docs/solutions/test-failures/`
- `runtime_error` → `docs/solutions/runtime-errors/`
- `performance_issue` → `docs/solutions/performance-issues/`
- `database_issue` → `docs/solutions/database-issues/`
- And more...

## Source

Extracted from the compound-engineering plugin (v2.30.0) for reference and adaptation.
