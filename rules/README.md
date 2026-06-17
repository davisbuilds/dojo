# rules/

Standing conventions for working in this repo — the always-follow guidance that
is **not** an on-trigger skill. Keeping it here (rather than as skills) avoids
trigger-collision pressure and gives one canonical home for "how we author and
ship," referenced from `AGENTS.md` and `CONTRIBUTING.md`.

## Files

- `skill-authoring.md` — the contract-shaped checklist every SKILL.md must satisfy.
- `doc-hygiene.md` — commit, branch, and reference-doc conventions.

## Composing rules into skills

These files double as composable fragments. A SKILL.md can pull one in with a
namespaced include and the composer (`scripts/gen_skill_docs.py`) expands it
into a managed `AUTO-GENERATED` block:

```markdown
<!-- INCLUDE: rules/skill-authoring -->
```

Edit the rule file, then run `python scripts/gen_skill_docs.py` — every skill
that includes it is regenerated. Bare names (no `rules/` prefix) still resolve
to `skills/_fragments/`.
