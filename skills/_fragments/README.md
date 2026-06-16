# Shared SKILL.md fragments

Reusable snippets composed into `SKILL.md` files by `scripts/gen_skill_docs.py`.
This directory is **not** a skill (underscore-prefixed; ignored by the manifest,
contract validator, and structure hook).

## How it works

A skill opts in by adding a directive anywhere in its `SKILL.md` body:

```markdown
<!-- INCLUDE: verification-footer -->
```

Run `python3 scripts/gen_skill_docs.py` to expand it into a managed block:

```markdown
<!-- INCLUDE: verification-footer -->
<!-- AUTO-GENERATED from skills/_fragments/verification-footer.md — do not edit -->
...fragment body...
<!-- /INCLUDE: verification-footer -->
```

Generation is idempotent. Edit the fragment file (e.g. `verification-footer.md`)
and the generated block in every opted-in skill, never the block itself.

- Add a fragment: create `skills/_fragments/<name>.md`.
- Use it: add `<!-- INCLUDE: <name> -->` to a skill, then regenerate.
- Check sync: `python3 scripts/gen_skill_docs.py --check`.

Opt-in only: skills without an `INCLUDE` directive are never modified.
