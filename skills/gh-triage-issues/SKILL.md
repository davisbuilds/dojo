---
name: gh-triage-issues
description: "Triage GitHub issues using the gh CLI. Analyzes new issues to apply labels, assess priority, detect duplicates, and optionally assign owners. Use when user asks to triage issues, label issues, check for duplicates, prioritize backlog, or process incoming issues. Triggers on phrases like 'triage issue #N', 'triage issues', 'label this issue', 'is this a duplicate', 'prioritize issue', 'process new issues in repo'."
---

# gh-triage-issues

Triage GitHub issues: label, prioritize, detect duplicates, and assign.

## Prerequisites

- `gh` CLI installed (`apt install gh` if missing)
- Authentication configured (`gh auth status` to verify)

## Workflow

### 1. Parse Input

Determine mode:

- **Single issue**: `owner/repo` + issue number
- **Batch triage**: `owner/repo` + filter (e.g., unlabeled issues)

### 2. Fetch Issue Details

```bash
bash scripts/fetch_issue.sh <owner/repo> <issue_number>
```

### 3. Get Available Labels

```bash
bash scripts/list_labels.sh <owner/repo>
```

Cache this per-repo; labels rarely change mid-session.

### 4. Check for Duplicates

Extract key terms from title/body, then search:

```bash
bash scripts/find_duplicates.sh <owner/repo> "<key terms>"
```

**If likely duplicate found:**

- Comment linking to original issue
- Add `duplicate` label
- Close issue (with user confirmation)
- Stop triage here

### 5. Classify Issue Type

Determine primary type from content:

| Type       | Indicators                                               |
| ---------- | -------------------------------------------------------- |
| `bug`      | "error", "crash", "doesn't work", "broken", stack traces |
| `feature`  | "add", "would be nice", "request", "enhancement"         |
| `docs`     | "documentation", "typo", "README", "unclear"             |
| `question` | "how do I", "is it possible", "?", support-style asks    |
| `security` | "vulnerability", "CVE", "exploit", "injection"           |
| `chore`    | "upgrade", "dependency", "refactor", "tech debt"         |

### 6. Assess Priority

Evaluate based on:

| Signal                           | Priority Impact                |
| -------------------------------- | ------------------------------ |
| Security issue                   | → Critical                     |
| Data loss potential              | → Critical                     |
| Blocks many users                | → High                         |
| Workaround exists                | → Lower                        |
| Edge case                        | → Lower                        |
| Reactions (👍 count)             | Higher count → Higher priority |
| Author is maintainer/contributor | May indicate importance        |

**Priority labels** (adapt to repo conventions):

- `priority: critical` — Security, data loss, wide breakage
- `priority: high` — Significant impact, no workaround
- `priority: medium` — Normal bugs/features
- `priority: low` — Minor issues, nice-to-haves

### 7. Add Area/Component Labels

If repo uses area labels (e.g., `area/api`, `area/ui`, `component/auth`), identify from:

- File paths mentioned
- Keywords in description
- Stack traces

### 8. Apply Labels

```bash
gh issue edit <issue_number> --repo <owner/repo> \
  --add-label "bug,priority: high,area/api"
```

### 9. Assign (Optional)

If repo has CODEOWNERS or known maintainers per area:

```bash
gh issue edit <issue_number> --repo <owner/repo> \
  --add-assignee "<username>"
```

Only assign if:

- Clear owner for the area
- User requested assignment
- Following repo's assignment conventions

### 10. Post Triage Comment (Optional)

For complex issues or when clarification needed:

```bash
gh issue comment <issue_number> --repo <owner/repo> --body "<comment>"
```

**Comment templates:**

_Needs more info:_

```markdown
Thanks for reporting! To help us investigate, could you provide:

- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, version, etc.)
```

_Duplicate detected:_

```markdown
This appears to be a duplicate of #<original>. Closing in favor of that issue.
Please add any additional context there. Reopen if this is actually distinct.
```

_Triaged successfully:_

```markdown
Triaged: labeled as `<labels>`, priority `<priority>`.
<optional: assigned to @user or "Added to backlog for future planning.">
```

### 11. Report Summary

Provide user with:

- Labels applied
- Priority assessment rationale
- Duplicates found (if any)
- Assignment (if made)
- Any questions/blockers

## Output Requirements

Include:
- labels applied and rationale
- priority decision and supporting signals
- duplicate outcome (found/not found, linked issue if found)
- assignment/comment actions taken

## Batch Triage Mode

To triage multiple issues:

```bash
# List unlabeled open issues
gh issue list --repo <owner/repo> --label "" --state open --limit 20
```

Then loop through each, applying the single-issue workflow.

For large backlogs, summarize findings:

```markdown
## Triage Summary

| Issue | Type | Priority | Labels Applied | Notes        |
| ----- | ---- | -------- | -------------- | ------------ |
| #42   | bug  | high     | bug, area/api  | —            |
| #43   | dup  | —        | duplicate      | Dup of #12   |
| #44   | feat | medium   | enhancement    | Needs design |
```

## Edge Cases

**Issue lacks detail**: Label `needs-info`, post comment requesting details, don't set priority yet.

**Security issue**: Label `security`, set critical priority, avoid discussing details publicly. Suggest private disclosure if repo supports it.

**Issue is actually a PR or discussion**: Redirect author to correct venue, close issue.

**Author is first-time contributor**: Be welcoming in tone; they may not know repo conventions.

**Contentious/heated issue**: Triage factually; don't engage in debates. Flag for maintainer attention if needed.

## Boundaries

- Do not close issues as duplicate without evidence and explicit user confirmation.
- Do not assign owners arbitrarily when ownership is unclear.
- Do not expose sensitive security details in public issue comments.

## Verification

Before reporting completion:
- confirm issue/repo identifiers match user request
- confirm labels and priority changes succeeded via CLI response
- confirm any comment/assignment/closure action actually executed

## Command Wrapper

If the harness supports command files, use `commands/triage-issue.md` as the canonical entrypoint for this skill.
