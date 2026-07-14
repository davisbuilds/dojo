## 1.1.0

- Rewrite the trigger scorer: TF-IDF cosine over stemmed tokens with
  hyphenated-compound splitting, replacing token-overlap plus a hand-maintained
  stopword list. IDF now down-weights corpus-wide vocabulary automatically.
- Make ranking the default `--cases` assertion model (the top-scoring skill must
  be an expected trigger; each `avoid` must score below it). Add `--threshold`
  for the previous absolute-score model. `--from-triggers` is unchanged in
  contract.
- Support multi-skill `trigger` lists (route to any), empty-`trigger`
  match-nothing cases with a floor, and a `known_hard` case flag reported
  separately from real failures.
- Expanded collision fixture rises from 46/58 to 58/58 under ranking with no
  fixture assertions weakened.
