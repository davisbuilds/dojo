---
name: gh-review-pr
description: "Review GitHub pull requests using the gh CLI. Analyzes code changes, checks CI status, and posts a review comment with findings and a merge recommendation. Use when user asks to review a PR, check a pull request, or evaluate code changes. Triggers on phrases like 'review PR #N', 'check this pull request', 'review github.com/.../pull/N', 'should we merge PR #N', 'evaluate this PR'."
---

# gh-review-pr

Review GitHub PRs and post analysis with merge recommendations.

## Prerequisites

- `gh` CLI installed (`apt install gh` if missing)
- Authentication configured (`gh auth status` to verify)

## Workflow

### 1. Parse Input

Extract from user request:

- **repo**: `owner/repo` format
- **pr_number**: numeric PR ID

### 2. Fetch PR Details

```bash
bash scripts/fetch_pr.sh <owner/repo> <pr_number>
```

Returns: title, description, diff, CI status, existing reviews, comments, and file list.

### 3. Pre-Review Checks

Before deep analysis, check blockers:

| Condition             | Action                                                |
| --------------------- | ----------------------------------------------------- |
| Draft PR              | Note it's a draft; ask user if they still want review |
| Failing CI            | Flag failing checks prominently in review             |
| Merge conflicts       | Note conflicts must be resolved before merge          |
| Already merged/closed | Inform user; skip review                              |

### 4. Analyze the Diff

Review each changed file for:

**Code Quality**

- Logic errors or bugs
- Edge cases not handled
- Error handling gaps
- Performance concerns

**Security**

- Hardcoded secrets or credentials
- SQL injection, XSS, or other vulnerabilities
- Unsafe deserialization
- Improper input validation

**Style & Maintainability**

- Consistency with codebase conventions
- Code clarity and readability
- Appropriate comments/documentation
- Test coverage (new code should have tests)

**Architecture**

- Breaking changes to APIs
- Backwards compatibility
- Dependency changes

### 5. Formulate Recommendation

Based on analysis, determine one of:

| Recommendation      | Criteria                                           |
| ------------------- | -------------------------------------------------- |
| **APPROVE**         | No blocking issues; minor nits at most             |
| **REQUEST_CHANGES** | Has bugs, security issues, or significant problems |
| **COMMENT**         | Questions or suggestions but not blocking          |

### 6. Post Review Comment

```bash
gh pr review <pr_number> --repo <owner/repo> \
  --body "<review_body>" \
  --approve|--request-changes|--comment
```

**Review body structure:**

```markdown
## Summary

<1-2 sentence overview of the PR's purpose>

## Analysis

### What This PR Does

<brief description of changes>

### Findings

<categorized list of observations>

#### Issues (if any)

- 🔴 **Critical**: <description>
- 🟡 **Concern**: <description>

#### Suggestions (if any)

- 💡 <improvement idea>

#### Positive Notes

- ✅ <what's done well>

## CI Status

<pass/fail summary>

## Recommendation

**<APPROVE | REQUEST CHANGES | COMMENT>**

<rationale for recommendation>
```

### 7. Report to User

Summarize:

- Key findings
- Recommendation given
- Link to the review comment
- Any follow-up actions needed

## Review Depth Guidelines

**Quick review** (small PRs, <50 lines):

- Scan diff directly
- Focus on obvious issues
- Faster turnaround

**Deep review** (large PRs, critical code):

- Clone repo and explore context
- Trace code paths
- Check related tests
- Consider broader implications

Ask user which depth they prefer if unclear.

## Edge Cases

**PR touches sensitive files** (auth, payments, infra): Flag for extra scrutiny.

**PR from external contributor**: Check CLA status; be welcoming in tone.

**PR has many commits**: Consider suggesting squash before merge.

**Stale PR with conflicts**: Recommend rebasing before review proceeds.

## Command Wrapper

If the harness supports command files, use `commands/review-pr.md` as the canonical entrypoint for this skill.
