## 1.0.4 - 2026-08-12

- Repoint the behavioral-scenarios reference at the archived spec path; the contract moved out of the tracked tree.

# Changelog

## 1.0.3 - 2026-07-31

- Remove `gh-review-pr` from sibling text, the quiz-change command, and the
  trigger/behavioral fixtures, following its retirement on 2026-07-31. One
  trigger case (`negative-gh-review-pr`) existed only to route to it and is
  dropped; the remaining cases keep their assertions.

## 1.0.2 - 2026-07-31

- Trim the description from 882 to 477 chars. It described how scope and quiz mode work internally; that detail belongs in the body, not the always-loaded skills listing. All five trigger phrases are unchanged, so routing is unaffected.

## 1.0.1

- Strengthen the routing fixture under the new ranking trigger-eval model:
  restore the sibling `avoid` assertions on positive cases (blind-spots must
  outrank write-plan, local-review, write-spec, etc.), which the old
  absolute-threshold model could not express. Flag one natural-paraphrase case
  as `known_hard`. Fixture-only; no change to the skill's runtime behavior.
