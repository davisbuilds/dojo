---
name: skill-creator
description: Create and improve agent skills with precise discovery, useful instructions, portable resources, and proportionate testing. Use when authoring SKILL.md, revising skill behavior, or preparing a skill release.
skill-type: workflow
license: Complete terms in LICENSE.txt
version: 3.0.0
---

# Skill Creator

A standalone authoring guide for portable agent skills. Add what the agent would
otherwise lack: a working capability, specialized knowledge, a preference, or a
safeguard for a consequential failure. Start from the actual harness, tools,
repository guidance, and settled user intent.

## Choose the useful change

Ground the target in the conversation, existing skill, and real usage. Identify
what the executor should accomplish, when this skill should be considered, and
which constraints or consumers matter. Reuse settled answers; ask only about
missing decisions that would change the work. Inspect the harness's existing
capabilities to avoid duplicating them. This guide does not require another
creator or its workflow.

A new skill is one option. Improve an existing tool or reference, narrow discovery,
move project-only facts to their owner, or retire redundant guidance when that
better solves the problem.

State the desired result and relevant constraints. Prescribe order or format
only for a real dependency, fragile operation, or consumer contract. Consulting
another skill supplies relevant guidance without inheriting its artifacts,
approvals, or entire workflow. Skill creation does not authorize installation,
publication, paid evaluations, or broader changes.

## Author the bundle

Keep selection cues in the description: what this capability does and when it
helps. Use specific task distinctions instead of trying to maximize invocation.
Keep the body focused on decisions and tools the executor needs; use references
for optional detail with clear pointers about when to read them. No required
heading order, example quota, file roster, or line-count target applies.

Use scripts for repeated mechanics or enforceable invariants, references for
conditional knowledge, and assets for material copied into the output. Bundle a
helper when real usage shows repeated reinvention; do not turn every reasoning
step into code. A short skill can be a single SKILL.md. Examples should clarify a
hard judgment or consumer contract, not teach the model routine competence.

Keep core instructions model-agnostic. State platform-specific assumptions where
they matter. Anchor runnable paths to the loaded skill directory, not the user's
working directory. Before removing a resource, check wrappers, scripts, tests,
and downstream consumers. Rewrite the owning guidance rather than preserving
obsolete requirements in a reference.

Validate against the actual destination's supported fields and loading model.
Do not remove valid harness-specific metadata merely to pass a different
validator. The bundled tools use Dojo's conventions:

- `name` matches the directory: lowercase letters, digits, single hyphens, up to
  64 characters. `description` is nonempty, at most 1024 characters, with no
  angle brackets. These are packaging limits, not measures of usefulness.
- Declare SemVer `version` without a leading `v`; catalog skills also declare
  `skill-type: workflow` or `reference`. The type describes purpose, not a
  mandatory document shape. Dojo's validator requires version metadata;
  that is a Dojo convention, not a universal harness requirement.
- In Dojo, bump the version and add a per-skill `CHANGELOG.md` entry for
  release-relevant edits. Use patch for clarification, minor for compatible
  additions, major for changed workflows/required outputs, removed resources,
  narrowed triggers, or incompatible scripts. Reconcile generated metadata and
  owning docs as well as the skill body.
- Preserve license/provenance when adapting third-party material. Inspect
  distribution declarations before introducing a second same-name installation.

## Tools when needed

Substitute the loaded directory for `<skill-dir>` and the target for
`<target-skill>`. Python 3 and PyYAML are needed for the authoring tools.

```bash
# Optional scaffold; direct authoring is equally valid.
python3 <skill-dir>/scripts/init_skill.py my-skill --path <parent-directory>

# Dojo-compatible metadata validation; this does not assess the prose.
python3 <skill-dir>/scripts/quick_validate.py <target-skill>

# Only when a distributable .skill archive is requested.
python3 <skill-dir>/scripts/package_skill.py <target-skill> <output-directory>
```

The initializer supports `--resources scripts,references,assets` and opt-in
`--examples`; create only resources that serve the task. Remove unused examples
and unfinished placeholders. The packager validates metadata and zips files;
it does not assess security, resource completeness, or task quality. Inspect the
bundle contents before distributing it, including local or sensitive files.

For optional Codex metadata, see `references/openai_yaml.md`.
`--with-openai-agent` creates it during initialization;
`scripts/generate_openai_yaml.py` can create it separately. That helper replaces
an existing file: edit existing metadata in place to preserve policy,
dependencies, icons, and curated interface fields. In a Dojo checkout, use the
repository adapter generator for generator-owned files. Change discovery policy
only when the user's intended exposure changes.

## Check the result

Run the relevant packaging and script checks; in Dojo follow the repository's
release and generated-artifact checks. `skill-evals` distinguishes those checks
from lexical routing and actual task outcomes. A missing recognized heading is
an authoring hint, not a demand to add one.

For substantive behavior changes, choose realistic tasks that distinguish the
intended improvement from the old behavior, including a relevant boundary or
near miss. Reuse suitable existing evidence; for execution details and comparison
pitfalls, consult `references/evaluation.md` when an actual trial is warranted.
Green structure checks or shorter instructions do not establish improvement.
A small correction does not require a benchmark.

When results expose friction, inspect both output and execution: was information
missing, a tool unreliable, discovery wrong, or an instruction sending the agent
through unnecessary work? Fix the responsible layer. Generalize from the failure
instead of adding the exact test answer or another universal rule. Repeat the
relevant case after repair and use fresh cases before making broader claims.
Stop when the requested capability has adequate evidence; do not manufacture
another revision merely to keep an improvement loop running.

Deliver the requested revision with relevant verification and unresolved limits.
Create an archive, report, or evaluation workspace only when it serves the task;
do not add them as ceremony for every edit.
