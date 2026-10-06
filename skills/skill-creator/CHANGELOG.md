## 3.0.0 - 2026-10-06

- Replace the generic tutorial with a standalone authoring guide combining portable tools, scoped design decisions, and optional behavioral comparison guidance.
- Distinguish destination requirements from Dojo release conventions.
- Remove unused workflow/output tutorial references and reduce initializer scaffolding to optional prompts.
- Clarify metadata-only validation, archive contents, and preservation of curated harness sidecars.

## 2.0.1 - 2026-10-02

- Align description guidance with the required body scope anchor instead of telling authors to omit it.

## 2.0.0 - 2026-09-18

- Design for capable agents and revisitable marginal value; scope authoring stages and packaging to the request, with consumer-driven output examples.

## 1.0.1

- Add the required `version: 1.0.0` field to `init_skill.py`'s `SKILL_TEMPLATE`.
  A freshly scaffolded skill previously failed contract validation on creation,
  which also deadlocked the pre-write validation hook: the invalid scaffold
  blocked the very edit that would have added the missing field.
