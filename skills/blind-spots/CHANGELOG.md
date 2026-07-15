## 1.0.1

- Strengthen the routing fixture under the new ranking trigger-eval model:
  restore the sibling `avoid` assertions on positive cases (blind-spots must
  outrank write-plan, local-review, write-spec, etc.), which the old
  absolute-threshold model could not express. Flag one natural-paraphrase case
  as `known_hard`. Fixture-only; no change to the skill's runtime behavior.
