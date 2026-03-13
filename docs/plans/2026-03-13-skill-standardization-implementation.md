---
date: 2026-03-13
topic: skill-standardization
stage: implementation-plan
status: draft
source: conversation
---

# Skill Standardization Implementation Plan

## Goal

Standardize same-named skills across `dojo`, global agent roots, and project-local mirrors by making `dojo/skills` the canonical source, selectively cherry-picking stronger behavior from divergent copies into canonical skills first, then synchronizing mirrors with explicit verification and backups.

## Scope

### In Scope

- Reconcile canonical content in `dojo` before any global/local synchronization.
- Confirm and encode `obsidian-canvas` as the canonical replacement for `json-canvas`.
- Selectively merge the best parts of the global `brainstorming` copy into canonical `dojo` without regressing completeness.
- Selectively merge the best parts of the `.codex/.system` `skill-creator` into canonical `dojo` while preserving stricter validation and cross-agent portability.
- Extend `skill-standardizer` policy and scripts as needed to support renamed-skill migration and local/global normalization safely.
- Normalize global roots to the preferred topology: concrete copy in `~/.agents/skills`, symlinked secondary globals where policy applies.
- Normalize project-local duplicate skills to preferred global links where policy applies.
- Replace broken local symlinks discovered during audit.
- Re-run drift audits and targeted script validation after synchronization.

### Out of Scope

- No standardization of skills that do not exist in `dojo/skills` unless a separate canonical source is later chosen.
- No mutation of plugin cache skill directories.
- No attempt to merge unrelated one-off local skills such as project-private `pdf` unless explicitly requested.
- No broad refactor of all skill docs beyond the skills implicated by this drift analysis.

## Assumptions And Constraints

- Assumption: `dojo/skills` is the canonical source for all same-named skills going forward.
- Assumption: `obsidian-canvas` should supersede `json-canvas` rather than coexist long-term.
- Assumption: `.codex/.system/skill-creator` is not a separate long-term canonical fork; useful improvements should be merged into `dojo` selectively.
- Constraint: synchronization must happen only after canonical `dojo` copies are updated so stale content is not propagated.
- Constraint: backup-before-replace remains mandatory for any apply step that touches global or project-local roots.
- Constraint: `skill-standardizer` dry-run audit should be the source of truth for planned actions before `--apply`.
- Constraint: non-canonical but still-installed skills such as `imagegen`, `subagent-driven-development`, and project-private `pdf` need explicit keep-as-is handling or documented exclusion.
- Constraint: current broken symlinks in `/Users/dg-mac-mini/Dev/dojo/.claude/skills` must be corrected as part of normalization.
- Trade-off accepted: standardizing on one canonical copy may reduce per-client tailoring, but it materially lowers drift, maintenance cost, and hidden behavior differences.

## Task Breakdown

### Task 1: Finalize Canonical Content Decisions In `dojo`

**Objective**

Update canonical `dojo` skills first so the subsequent synchronization propagates deliberate improvements rather than stale copies.

**Files**

- Modify: `skills/brainstorming/SKILL.md`
- Modify: `skills/skill-creator/SKILL.md`
- Modify: `skills/skill-creator/scripts/init_skill.py`
- Modify: `skills/skill-creator/scripts/quick_validate.py`
- Modify: `skills/skill-creator/scripts/generate_openai_yaml.py`
- Modify: `skills/skill-creator/references/workflows.md`
- Modify: `skills/skill-creator/references/output-patterns.md`

**Dependencies**

None

**Implementation Steps**

1. Merge the stronger skip-language and conditional handoff guidance from the installed global `brainstorming` copy into canonical `skills/brainstorming/SKILL.md`.
2. Preserve the canonical `brainstorming` sections that the global copy dropped, especially `Boundaries`, `Output`, `Verification`, and `Resources`.
3. Review `.codex/.system/skill-creator` deltas and cherry-pick only the improvements that strengthen naming guidance, metadata guidance, or initializer UX without weakening portability.
4. Keep the stricter validator behavior from canonical `dojo`, including rejection of empty `name` and `description` and support for allowed frontmatter fields already adopted in `dojo`.
5. Retain canonical packaging support and optional-platform posture unless a specific Codex-only requirement justifies a change.

**Verification**

- Run: `python3 skills/skill-creator/scripts/quick_validate.py skills/brainstorming`
- Expect: `Skill is valid!`
- Run: `python3 skills/skill-creator/scripts/quick_validate.py skills/skill-creator`
- Expect: `Skill is valid!`
- Run: `python3 - <<'PY'\nimport tempfile, pathlib, subprocess\nwith tempfile.TemporaryDirectory() as d:\n    p=pathlib.Path(d)/'bad-skill'\n    p.mkdir()\n    (p/'SKILL.md').write_text('---\\nname: \"\"\\ndescription: \"\"\\n---\\n')\n    r=subprocess.run(['python3','skills/skill-creator/scripts/quick_validate.py',str(p)], cwd='/Users/dg-mac-mini/Dev/dojo', text=True, capture_output=True)\n    print(r.stdout.strip() or r.stderr.strip())\n    raise SystemExit(0 if 'cannot be empty' in (r.stdout+r.stderr) else 1)\nPY`
- Expect: validator rejects empty required fields.

**Done When**

- Canonical `brainstorming` contains the best global refinements without losing explicit output and verification guidance.
- Canonical `skill-creator` absorbs worthwhile `.system` improvements without regressing validator quality or cross-agent compatibility.
- Canonical skill files validate successfully.

### Task 2: Encode The `obsidian-canvas` Replacement Policy

**Objective**

Make the rename from `json-canvas` to `obsidian-canvas` explicit in canonical docs and runtime catalog expectations so synchronization can replace the older name safely.

**Files**

- Modify: `skills/obsidian-canvas/SKILL.md`
- Modify: `docs/system/FEATURES.md`
- Modify: `AGENTS.md`
- Modify: `skills.json`

**Dependencies**

- Task 1

**Implementation Steps**

1. Update canonical docs and skill descriptions to reflect that `obsidian-canvas` is the supported name going forward.
2. Add migration guidance that `json-canvas` is deprecated/replaced rather than co-equal.
3. Regenerate or update repository skill manifest/catalog artifacts so `obsidian-canvas` is discoverable under the new name.
4. Decide whether a temporary compatibility note or alias reference is needed to make the rename obvious during the transition.

**Verification**

- Run: `rg -n "obsidian-canvas|json-canvas" AGENTS.md docs/system/FEATURES.md skills/obsidian-canvas/SKILL.md skills.json`
- Expect: docs identify `obsidian-canvas` as canonical and any remaining `json-canvas` mentions are explicitly transitional.

**Done When**

- Canonical repo docs consistently describe `obsidian-canvas` as the replacement.
- Runtime catalog artifacts expose the canonical name expected after sync.

### Task 3: Extend `skill-standardizer` For Rename And Mirror Normalization

**Objective**

Teach the standardization workflow to handle the `json-canvas` to `obsidian-canvas` migration and the identified local/global normalization patterns deterministically.

**Files**

- Modify: `skills/skill-standardizer/SKILL.md`
- Modify: `skills/skill-standardizer/commands/standardize-skills.md`
- Modify: `skills/skill-standardizer/references/policy.md`
- Modify: `skills/skill-standardizer/scripts/audit.py`
- Modify: `skills/skill-standardizer/scripts/sync.py`
- Modify: `skills/skill-standardizer/scripts/skill_standardizer_lib.py`

**Dependencies**

- Task 2

**Implementation Steps**

1. Add an explicit rename/deprecation mapping for `json-canvas -> obsidian-canvas` in policy and audit logic.
2. Ensure audit output distinguishes true content drift from renamed-skill replacement actions.
3. Ensure sync planning can replace deprecated names with canonical names while still backing up the old destination.
4. Preserve existing primary-global and local-link policies while covering the broken-symlink and duplicate-local cases found in the earlier audit.
5. Keep dry-run as default and make planned rename/relink actions clear in text and JSON output.

**Verification**

- Run: `python3 skills/skill-standardizer/scripts/audit.py --help`
- Expect: command succeeds and any new rename-related flags or behavior are documented.
- Run: `python3 skills/skill-standardizer/scripts/audit.py --format json --root /Users/dg-mac-mini/Dev/.agents/skills --root /Users/dg-mac-mini/Dev/.claude/skills`
- Expect: audit output can represent deprecated-name replacement and local duplicate normalization without crashing.

**Done When**

- `skill-standardizer` can model renamed-skill replacement instead of treating it as an unstructured exception.
- Planned actions clearly cover both copy drift and topology normalization.

### Task 4: Dry-Run The Full Synchronization Against Global And Local Roots

**Objective**

Generate the final action set from the updated canonical source before any write occurs.

**Files**

- Validate: `skills/skill-standardizer/scripts/audit.py`
- Validate: `skills/skill-standardizer/scripts/sync.py`
- External: `/Users/dg-mac-mini/.agents/skills`
- External: `/Users/dg-mac-mini/.codex/skills`
- External: `/Users/dg-mac-mini/.claude/skills`
- External: `/Users/dg-mac-mini/Dev/.agents/skills`
- External: `/Users/dg-mac-mini/Dev/.claude/skills`
- External: `/Users/dg-mac-mini/Dev/blueprint-finance/.agents/skills`
- External: `/Users/dg-mac-mini/Dev/blueprint-finance/.claude/skills`
- External: `/Users/dg-mac-mini/Dev/dojo/.agents/skills`
- External: `/Users/dg-mac-mini/Dev/dojo/.claude/skills`
- External: `/Users/dg-mac-mini/Dev/habits-ai/.claude/skills`
- External: `/Users/dg-mac-mini/Dev/resnet-cifar10/.agents/skills`
- External: `/Users/dg-mac-mini/Dev/resnet-cifar10/.claude/skills`

**Dependencies**

- Task 3

**Implementation Steps**

1. Run the updated audit against the three global roots plus every discovered project-local root that should participate in normalization.
2. Review the resulting drift report for any remaining surprise actions, especially non-canonical skills that should be exempted rather than mutated.
3. Confirm the plan handles renamed `json-canvas`, concrete duplicate globals, local duplicate mirrors, and the broken `dojo/.claude/skills` symlinks.
4. Save the final audit report artifact for traceability before apply.

**Verification**

- Run: `python3 skills/skill-standardizer/scripts/audit.py --format text --root /Users/dg-mac-mini/Dev/.agents/skills --root /Users/dg-mac-mini/Dev/.claude/skills --root /Users/dg-mac-mini/Dev/blueprint-finance/.agents/skills --root /Users/dg-mac-mini/Dev/blueprint-finance/.claude/skills --root /Users/dg-mac-mini/Dev/dojo/.agents/skills --root /Users/dg-mac-mini/Dev/dojo/.claude/skills --root /Users/dg-mac-mini/Dev/habits-ai/.claude/skills --root /Users/dg-mac-mini/Dev/resnet-cifar10/.agents/skills --root /Users/dg-mac-mini/Dev/resnet-cifar10/.claude/skills`
- Expect: audit completes successfully and planned actions align with the intended canonical policy.
- Run: `python3 skills/skill-standardizer/scripts/audit.py --format json --report-out /tmp/skill-standardization-preapply.json --root /Users/dg-mac-mini/Dev/.agents/skills --root /Users/dg-mac-mini/Dev/.claude/skills --root /Users/dg-mac-mini/Dev/blueprint-finance/.agents/skills --root /Users/dg-mac-mini/Dev/blueprint-finance/.claude/skills --root /Users/dg-mac-mini/Dev/dojo/.agents/skills --root /Users/dg-mac-mini/Dev/dojo/.claude/skills --root /Users/dg-mac-mini/Dev/habits-ai/.claude/skills --root /Users/dg-mac-mini/Dev/resnet-cifar10/.agents/skills --root /Users/dg-mac-mini/Dev/resnet-cifar10/.claude/skills`
- Expect: JSON report is written successfully and can be inspected later.

**Done When**

- There is a reviewed, saved dry-run action list covering all intended roots.
- Any roots or skills that should be exempted have been identified before apply.

### Task 5: Apply Synchronization And Replace Deprecated Mirrors

**Objective**

Execute the approved copy, relink, and rename actions with backups, using the updated standardizer workflow as the primary mechanism.

**Files**

- External: `/Users/dg-mac-mini/.agents/skills`
- External: `/Users/dg-mac-mini/.codex/skills`
- External: `/Users/dg-mac-mini/.claude/skills`
- External: `/Users/dg-mac-mini/Dev/.agents/skills`
- External: `/Users/dg-mac-mini/Dev/.claude/skills`
- External: `/Users/dg-mac-mini/Dev/blueprint-finance/.agents/skills`
- External: `/Users/dg-mac-mini/Dev/blueprint-finance/.claude/skills`
- External: `/Users/dg-mac-mini/Dev/dojo/.agents/skills`
- External: `/Users/dg-mac-mini/Dev/dojo/.claude/skills`
- External: `/Users/dg-mac-mini/Dev/habits-ai/.claude/skills`
- External: `/Users/dg-mac-mini/Dev/resnet-cifar10/.agents/skills`
- External: `/Users/dg-mac-mini/Dev/resnet-cifar10/.claude/skills`

**Dependencies**

- Task 4

**Implementation Steps**

1. Run `sync.py --apply` with the agreed root set and policy defaults.
2. Let the sync pass update concrete stale copies, relink secondary globals, and normalize local duplicates to global links.
3. Replace installed `json-canvas` entries with canonical `obsidian-canvas` entries according to the rename policy.
4. Repair the broken symlinks under `/Users/dg-mac-mini/Dev/dojo/.claude/skills` so they resolve to valid canonical/global targets.
5. Confirm that backup artifacts were created for any replaced destinations.

**Verification**

- Run: `python3 skills/skill-standardizer/scripts/sync.py --apply --root /Users/dg-mac-mini/Dev/.agents/skills --root /Users/dg-mac-mini/Dev/.claude/skills --root /Users/dg-mac-mini/Dev/blueprint-finance/.agents/skills --root /Users/dg-mac-mini/Dev/blueprint-finance/.claude/skills --root /Users/dg-mac-mini/Dev/dojo/.agents/skills --root /Users/dg-mac-mini/Dev/dojo/.claude/skills --root /Users/dg-mac-mini/Dev/habits-ai/.claude/skills --root /Users/dg-mac-mini/Dev/resnet-cifar10/.agents/skills --root /Users/dg-mac-mini/Dev/resnet-cifar10/.claude/skills`
- Expect: sync completes without unhandled errors and reports backup/relink actions.
- Run: `python3 - <<'PY'\nfrom pathlib import Path\nroots=[Path('/Users/dg-mac-mini/.agents/skills'),Path('/Users/dg-mac-mini/.codex/skills'),Path('/Users/dg-mac-mini/.claude/skills'),Path('/Users/dg-mac-mini/Dev/.agents/skills'),Path('/Users/dg-mac-mini/Dev/.claude/skills'),Path('/Users/dg-mac-mini/Dev/blueprint-finance/.agents/skills'),Path('/Users/dg-mac-mini/Dev/blueprint-finance/.claude/skills'),Path('/Users/dg-mac-mini/Dev/dojo/.agents/skills'),Path('/Users/dg-mac-mini/Dev/dojo/.claude/skills'),Path('/Users/dg-mac-mini/Dev/habits-ai/.claude/skills'),Path('/Users/dg-mac-mini/Dev/resnet-cifar10/.agents/skills'),Path('/Users/dg-mac-mini/Dev/resnet-cifar10/.claude/skills')]\nbroken=[]\nfor root in roots:\n    if not root.exists():\n        continue\n    for child in root.iterdir():\n        if child.is_symlink() and not child.exists():\n            broken.append(str(child))\nprint('\\n'.join(broken))\nraise SystemExit(1 if broken else 0)\nPY`
- Expect: no broken symlink paths are printed.

**Done When**

- Installed mirrors match the approved topology and content policy.
- Deprecated or broken entries have been replaced or repaired with backups preserved.

### Task 6: Re-Audit And Smoke-Test Canonical Behavior

**Objective**

Prove that drift is resolved, the chosen canonical behaviors still work, and the new topology does not leave hidden regressions.

**Files**

- Validate: `skills/brainstorming/SKILL.md`
- Validate: `skills/skill-creator/SKILL.md`
- Validate: `skills/skill-standardizer/SKILL.md`
- External: `/tmp/skill-standardization-postapply.json`

**Dependencies**

- Task 5

**Implementation Steps**

1. Re-run the full audit across the same root set and confirm no unexpected drift remains.
2. Re-run targeted validator and helper script smoke tests for the canonical `skill-creator` and `skill-standardizer`.
3. Confirm `obsidian-canvas` is the installed canonical skill and `json-canvas` is no longer the active same-purpose installed name.
4. Record any intentional residual exceptions so future audits do not treat them as surprises.

**Verification**

- Run: `python3 skills/skill-standardizer/scripts/audit.py --format json --report-out /tmp/skill-standardization-postapply.json --root /Users/dg-mac-mini/Dev/.agents/skills --root /Users/dg-mac-mini/Dev/.claude/skills --root /Users/dg-mac-mini/Dev/blueprint-finance/.agents/skills --root /Users/dg-mac-mini/Dev/blueprint-finance/.claude/skills --root /Users/dg-mac-mini/Dev/dojo/.agents/skills --root /Users/dg-mac-mini/Dev/dojo/.claude/skills --root /Users/dg-mac-mini/Dev/habits-ai/.claude/skills --root /Users/dg-mac-mini/Dev/resnet-cifar10/.agents/skills --root /Users/dg-mac-mini/Dev/resnet-cifar10/.claude/skills`
- Expect: exit code `0`, or only explicitly accepted residual exceptions remain.
- Run: `python3 skills/skill-creator/scripts/init_skill.py tmp-skill --path /tmp --resources scripts,references --examples --interface short_description='Temp skill'`
- Expect: temp skill directory is created successfully with valid structure.
- Run: `python3 skills/skill-standardizer/scripts/audit.py --help && python3 skills/skill-standardizer/scripts/sync.py --help`
- Expect: both commands render help successfully.
- Run: `find /Users/dg-mac-mini/.agents/skills /Users/dg-mac-mini/.codex/skills /Users/dg-mac-mini/.claude/skills -maxdepth 1 \\( -name 'json-canvas' -o -name 'obsidian-canvas' \\) | sort`
- Expect: canonical installed name is `obsidian-canvas`; any remaining `json-canvas` entry is only present if intentionally retained as a transitional alias.

**Done When**

- Post-apply audit is clean or reduced to explicitly documented exceptions.
- Canonical helper scripts still behave correctly after cherry-picks.
- Installed canvas skill naming matches the migration decision.

## Risks And Mitigations

- Risk: selectively cherry-picking from divergent copies accidentally imports weaker behavior along with stronger wording.
  Mitigation: update canonical `dojo` first and verify each changed skill directly before any sync.
- Risk: `skill-standardizer` rename handling for `json-canvas` introduces unsafe delete/replace behavior.
  Mitigation: keep rename actions explicit, dry-run first, and require backup creation in apply mode.
- Risk: non-canonical local or system skills are unintentionally overwritten because they share a similar purpose.
  Mitigation: scope sync actions to same-named canonical skills and document explicit exclusions before apply.
- Risk: symlink topology fixes break client discovery if relative link targets are wrong.
  Mitigation: run a broken-symlink scan immediately after apply and re-audit all affected roots.
- Risk: global-root linking policy reduces useful client-specific specialization.
  Mitigation: only standardize same-named skills where `dojo` is confirmed canonical and preserve documented exceptions outside that set.

## Verification Matrix

| Requirement | Proof command | Expected signal |
| --- | --- | --- |
| Canonical `brainstorming` and `skill-creator` remain valid after cherry-picks | `python3 skills/skill-creator/scripts/quick_validate.py skills/brainstorming && python3 skills/skill-creator/scripts/quick_validate.py skills/skill-creator` | Both validations print `Skill is valid!` |
| `skill-standardizer` can represent planned rename/mirror actions | `python3 skills/skill-standardizer/scripts/audit.py --format text --root /Users/dg-mac-mini/Dev/.agents/skills --root /Users/dg-mac-mini/Dev/.claude/skills` | Audit completes successfully and planned actions include the intended normalization behavior |
| Synchronization repairs broken symlinks and normalizes mirror topology | `python3 - <<'PY'\nfrom pathlib import Path\nroots=[Path('/Users/dg-mac-mini/.agents/skills'),Path('/Users/dg-mac-mini/.codex/skills'),Path('/Users/dg-mac-mini/.claude/skills'),Path('/Users/dg-mac-mini/Dev/.agents/skills'),Path('/Users/dg-mac-mini/Dev/.claude/skills'),Path('/Users/dg-mac-mini/Dev/blueprint-finance/.agents/skills'),Path('/Users/dg-mac-mini/Dev/blueprint-finance/.claude/skills'),Path('/Users/dg-mac-mini/Dev/dojo/.agents/skills'),Path('/Users/dg-mac-mini/Dev/dojo/.claude/skills'),Path('/Users/dg-mac-mini/Dev/habits-ai/.claude/skills'),Path('/Users/dg-mac-mini/Dev/resnet-cifar10/.agents/skills'),Path('/Users/dg-mac-mini/Dev/resnet-cifar10/.claude/skills')]\nfor root in roots:\n    if not root.exists():\n        continue\n    for child in root.iterdir():\n        if child.is_symlink() and not child.exists():\n            raise SystemExit(1)\nprint('ok')\nPY` | Prints `ok` and exits `0` |
| Post-apply drift is resolved | `python3 skills/skill-standardizer/scripts/audit.py --format json --report-out /tmp/skill-standardization-postapply.json --root /Users/dg-mac-mini/Dev/.agents/skills --root /Users/dg-mac-mini/Dev/.claude/skills --root /Users/dg-mac-mini/Dev/blueprint-finance/.agents/skills --root /Users/dg-mac-mini/Dev/blueprint-finance/.claude/skills --root /Users/dg-mac-mini/Dev/dojo/.agents/skills --root /Users/dg-mac-mini/Dev/dojo/.claude/skills --root /Users/dg-mac-mini/Dev/habits-ai/.claude/skills --root /Users/dg-mac-mini/Dev/resnet-cifar10/.agents/skills --root /Users/dg-mac-mini/Dev/resnet-cifar10/.claude/skills` | Exit code `0`, or residual issues match documented exceptions only |
| `obsidian-canvas` replaces `json-canvas` in installed roots | `find /Users/dg-mac-mini/.agents/skills /Users/dg-mac-mini/.codex/skills /Users/dg-mac-mini/.claude/skills -maxdepth 1 \\( -name 'json-canvas' -o -name 'obsidian-canvas' \\) | sort` | Output shows `obsidian-canvas` as the active installed canonical name |

## Handoff

1. Execute in this session, task by task.
2. Open a separate execution session.
3. Refine this plan before implementation.
