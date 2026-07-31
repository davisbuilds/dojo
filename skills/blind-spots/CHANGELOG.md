## 1.0.2 - 2026-07-31

- Trim the description from 882 to 477 chars. It described how scope and quiz mode work internally; that detail belongs in the body, not the always-loaded skills listing. All five trigger phrases are unchanged, so routing is unaffected.

## 1.0.1

- Strengthen the routing fixture under the new ranking trigger-eval model:
  restore the sibling `avoid` assertions on positive cases (blind-spots must
  outrank write-plan, local-review, write-spec, etc.), which the old
  absolute-threshold model could not express. Flag one natural-paraphrase case
  as `known_hard`. Fixture-only; no change to the skill's runtime behavior.
