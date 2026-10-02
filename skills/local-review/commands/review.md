---
name: review
description: Review the requested local change for actionable, evidence-backed defects.
argument-hint: "[--mode working|staged|branch --base <ref> --head <ref> --max-diff-lines <n> --deep]"
allowed-tools: [Read, Bash(git:*), Bash(rg:*), Bash(bash skills/local-review/scripts/collect_review_context.sh:*)]
---

# Local Review Command

Use the parent `SKILL.md` for scope, finding criteria, optional specialist lenses,
and output. This wrapper does not replace a harness's native `/review` command.

Resolve the requested target; an empty argument list means working changes.
The bundled collector can supply initial context:

```bash
bash <skill-dir>/scripts/collect_review_context.sh $ARGUMENTS
```

With no arguments:

```bash
bash <skill-dir>/scripts/collect_review_context.sh --mode working
```

Read omitted diff sections and relevant unchanged consumers as needed. `--deep`
only raises the collector's output budget. Keep findings tied to the requested
change and reviewed revision, including focused error-handling or type reviews.

Return concise findings under the parent skill's priority convention, followed
only by material scope/evidence limits. No mandatory extra report sections.
Do not edit source or post to GitHub as a side effect of review.
