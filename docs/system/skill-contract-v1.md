# SKILL Contract

Revised: 2026-10-06. Scope: `skills/*/SKILL.md` in Dojo.
The historical filename is retained so existing references keep resolving.

The validator enforces packaging metadata and optionally reports authoring hints.
It cannot certify advice, safety, discovery in a harness, or useful task outcomes.
`skills/skill-evals/scripts/validate_skill_contract.py` implements this contract.

## Packaging gates

`frontmatter_valid` is required in both default and strict modes. It uses
`skill-creator/scripts/quick_validate.py`: parseable YAML mapping, supported
fields and types, nonempty legal name and description, valid SemVer `version`,
and valid optional `skill-type`, `triggers`, and compatibility metadata. Names
are hyphen-case up to 64 characters; descriptions are at most 1024 characters
without angle brackets. See the validator for the complete schema.

`--strict` also requires:

- `name_matches_directory`: frontmatter name exactly matches the directory name.
- `skill_type_declared`: explicit `workflow` or `reference` classification.

Default mode warns on these two catalog-specific requirements. Untyped skills
fall back to workflow hints. An invalid declared type still fails metadata
validation in either mode. Workflow means task-oriented guidance; reference
means primarily navigational/informational guidance. Neither requires a fixed
sequence, heading order, report, or extra artifact.

## Authoring hints, never gates

Use `--authoring-hints` to opt into the prose/length detectors. They are off by
default to avoid recurring false alarms; their existing check keys remain in JSON
as `na` when not requested. With hints enabled, missing anchors warn in both modes;
recognized anchors only show that a heuristic matched.

| Check | What the detector recognizes |
| --- | --- |
| `description_trigger_ready` | Conventional trigger phrases, such as “Use when” |
| `scope_anchor_present` | Familiar scope headings |
| `boundaries_anchor_present` | Familiar headings or boundary phrases |
| `execution_anchor_present` | Familiar workflow/usage headings or a numbered step |
| `output_anchor_present` | Familiar output headings |
| `verification_anchor_present` | Familiar verification headings |
| `resource_map_present` | Resource headings or directory-path mentions when resources exist |
| `context_budget` | Whole-file line count, including frontmatter; warns above 500 |

Execution and output hints are not applicable to reference skills when no anchor
is recognized. `triggers_valid` reports optional declared phrases; malformed
phrases also fail the metadata gate.

These are review prompts, not a document schema. An unrecognized section may
already express the right substance; a recognized empty heading may express
nothing. Do not add headings or keywords just to silence hints. Review relevant
scope, boundaries, outcomes, verification, and resource reachability directly.
The resource heuristic does not validate files or links. Use repository link
checks and relevant script tests for those properties.

Line count is not token use or proof of waste. The presence of `references/`
does not make a shorter body defective, and length does not become a failure in
strict mode. Move or remove content based on relevance and when it is needed.

## Skill releases

Each catalog skill declares its release `version`, separate from the manifest
schema version. Use SemVer without a leading `v`.

- Patch: clarification, typo fixes, non-behavioral examples or documentation.
- Minor: compatible capabilities, optional commands/references, expanded triggers.
- Major: changed workflow contracts or required outputs, removed resources,
  narrowed triggers, or incompatible script behavior.

Release-relevant changes increase the version and add a corresponding
`CHANGELOG.md` heading. `check_skill_versions.py` enforces that against a Git
base; it is a separate gate. The first unversioned baseline is supported.

## Optional `triggers`

A nonempty list of nonempty literal phrases declares routing intent:

```yaml
triggers:
  - review this pr
  - check my diff
```

`run_trigger_evals.py --from-triggers` checks self-routing and lexical collisions.
A declared phrase passing does not establish actual harness invocation. Author
natural phrases and inspect failure causes; do not optimize only for the scorer.

## Generated artifacts

Frontmatter and declared includes own generated content:

- `scripts/gen_skill_docs.py` expands opt-in shared fragments. Skills without a
  template/include declaration are untouched.
- `scripts/gen_harness_adapters.py` generates marked Codex sidecars and selected
  project links/commands. It preserves unmarked, curated sidecars. Use the
  generator for files it owns; retain policy/dependencies in curated files.
- Manifest/catalog generators derive inventory and documentation from canonicals.

Generation checks establish consistency, not effectiveness. See
[ARCHITECTURE.md](ARCHITECTURE.md) for ownership and pipeline details.

## Results

- `pass`: packaging gates passed and no hints were raised.
- `warn`: gates passed, but one or more advisory checks need interpretation.
- `fail`: a required packaging gate failed.

The CLI exits nonzero on required failures or invocation errors, including an
empty selection. Warnings alone exit zero, including under `--strict`.
`--json` exposes per-check status, requiredness, and whether hints were enabled. `--markdown <path>` optionally
saves the same assessment with the current UTC date; no saved report is required.
A passing result must not be presented as behavioral evidence.
