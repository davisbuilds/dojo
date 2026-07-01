---
date: 2026-07-01
topic: skill-semver
stage: spec
status: complete
source: conversation
---

# Skill Semver Spec

## Problem

Dojo skills are already treated as reusable, distributable capabilities, but the catalog does not expose per-skill release identity. Users and automation can tell that a skill exists, but not which release they have installed, whether a local copy is stale, or whether an edit represents a shipped change. The top-level manifest schema version is not enough because it describes the catalog format, not individual skill behavior.

## Contract

When this ships, every cataloged skill declares an explicit SemVer release, the generated skill inventory exposes that release per skill, and changed skill contents cannot pass release checks unless the skill version advances with a matching changelog entry. The end state is verified by `python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict`, `python3 skills/skill-evals/scripts/check_skill_versions.py --base origin/main`, `python3 scripts/generate_skills_manifest.py && python3 scripts/gen_catalog.py --check`, and `python3 skills/write-spec/scripts/validate_spec.py docs/specs/2026-07-01-skill-semver-spec.md`.

## Success Criteria

- Every cataloged skill has a `version` value in its frontmatter.
- Existing cataloged skills are baselined at `1.0.0`.
- Skill versions follow SemVer 2.0.0 syntax without a leading `v`.
- The generated manifest distinguishes the manifest schema version from each skill's release version.
- The browsable catalog exposes skill release versions.
- A release-relevant edit to a skill requires a strictly greater skill version than the selected git base.
- A changed skill with a bumped version requires a changelog entry for the new version.
- The initial baseline migration can pass without requiring historical changelog reconstruction for all prior unversioned states.

## Evaluation

This is a mechanical system feature, not a product experiment. It graduates when the strict skill contract, version-change check, manifest generation check, catalog check, and spec validation all pass from a clean working tree state.

## Scope

In scope:

- Per-skill SemVer metadata.
- Baseline release assignment for the current catalog.
- Generated inventory and catalog visibility for skill versions.
- Deterministic validation of version syntax and required bump behavior.
- Changelog presence for changed skill releases.
- Documentation that explains when to use major, minor, and patch bumps.

Out of scope:

- A remote skill registry.
- Dependency resolution between skills.
- Version range solving.
- Automatic classification of whether a change should be major, minor, or patch.
- Reconstructing historical releases before the baseline migration.

## Assumptions And Constraints

- `SKILL.md` frontmatter remains the source of truth.
- The manifest schema version and per-skill release versions remain separate concepts.
- Release enforcement should be deterministic and suitable for local hooks and CI.
- Enforcement may compare against a configurable git base because local branches and CI jobs have different base refs.
- Intermediate edits should not be blocked solely because they are temporarily unreleased; release validation belongs at explicit check points.

## Open Questions

- Should changelog entries use a strict date format immediately, or only require a heading containing the release version for now?
- Should hand-authored harness sidecars ever expose version metadata, or should version visibility stay in the manifest and catalog?

## Handoff

1. Hand off to implementation to satisfy this contract directly.
2. Hand off to `write-plan` if sequencing becomes unclear during implementation.
3. Revisit this spec if version enforcement needs to classify change magnitude instead of only requiring a strict increase.
