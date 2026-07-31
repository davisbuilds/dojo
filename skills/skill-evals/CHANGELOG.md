# Changelog

## 1.4.1 - 2026-07-31

- Prune retired skills from `assets/trigger-collision-cases-expanded.json`.
  Four cases existed only to route to a now-retired skill and are removed;
  six `avoid` entries naming retired competitors are pruned.

## 1.4.0 - 2026-07-31

- `resource_map_present` recognizes `rules/` as a fifth resource directory.
  Five skills already shipped one, so their contents had been sitting outside
  validation entirely.
- `context_budget` gains a 250-line warn tier, conditional on the skill
  bundling `references/`. Length alone is not the defect; keeping detail inline
  when the skill already owns somewhere to put it is. Warn only -- no skill
  fails on it today.

## 1.3.0 - 2026-07-24

- Exempt append-only run memory (references/postmortems.md, references/executor-profiles.md) from the release-relevance check: a skill accumulates these as it is used, not as it is changed, so appending a lesson no longer forces a SemVer bump on an unchanged workflow.

## 1.2.1 - 2026-07-15

- Read the SKILL.md version via YAML (matching check_skill_versions) so quoted scalars and inline comments bump correctly; preserve quotes and inline comments on write.

## 1.2.0 - 2026-07-15

- Add bump_skill_version.py: bump a skill's SemVer and prepend a CHANGELOG heading in one command (major/minor/patch or --set), dogfooding the release-version contract.

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
- Score the skill vector on name + description only (declared triggers excluded),
  so `--from-triggers` stays a real check rather than matching a phrase against
  its own copy in the vector.
- Require a ranking winner to clear a small score floor, so a positive case with
  a single selected skill or an all-zero field cannot pass vacuously.
