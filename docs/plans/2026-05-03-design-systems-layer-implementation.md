---
date: 2026-05-03
topic: design-systems-layer
stage: implementation-plan
status: draft
source: conversation
---

# Design Systems Layer Implementation Plan

## Goal

Add a design-systems layer to dojo built around the Google Labs DESIGN.md format and the impeccable.style anti-pattern taxonomy. Ship two new skills (`design-md` for token formalization and `design-critique` for taste audit) plus a curated bundle of five Refero-style DESIGN.md exemplars and a structured slop catalog. Build from scratch without analyzing or modifying existing design-related skills; treat any overlap as a follow-up remediation pass.

## Scope

### In Scope

- Create a new `design-md` skill that wraps the Google `@google/design.md` CLI for `lint`, `diff`, and `export` operations and teaches the agent how to read, write, and reason about DESIGN.md files.
- Create a new `design-critique` skill that audits implemented UI against an impeccable-style anti-pattern catalog and returns ranked, category-scoped findings with named alternatives.
- Vendor five opinionated DESIGN.md exemplars sourced from Refero into a shared reference bundle that both skills can use as anchor examples.
- Encode the impeccable slop taxonomy as a single structured reference file consumed by `design-critique`.
- Wire both skills into the existing manifest, catalog, and acknowledgements paths.

### Out of Scope

- Comparison, deconfliction, or modification of any existing design-related skills (`frontend-design`, `web-design-guidelines`, `vercel-react-best-practices`, `theme-factory`). These will be reviewed in a separate remediation pass after the new skills are in use.
- The full impeccable.style six-category workflow taxonomy (Create / Evaluate / Refine / Simplify / Harden / System). Only the slop anti-pattern catalog is borrowed; the workflow framing is intentionally skipped.
- Strict `validate_skill_contract.py --strict` conformance for this first pass. Contract revisions are deferred to a follow-up.
- Playwright integration for live screenshot capture inside `design-critique`. The first pass operates on agent-supplied input (pasted markup, file paths, screenshots already at hand).
- Authoring a Refero-equivalent SaaS catalog. Exemplar set is fixed at five for v1.
- License negotiation or attribution beyond a one-line README acknowledgement and a frontmatter `metadata.upstream` pointer per vendored asset.

## Assumptions And Constraints

- The Google DESIGN.md format is at `version: alpha` and may churn; the skill must pin a CLI version and surface a "regenerate when spec moves" note.
- `npx @google/design.md` is reachable from user environments. The skill prefers `npx` invocation over installing a global binary.
- The impeccable slop catalog is publicly readable on `impeccable.style/slop`; we reproduce its anti-pattern taxonomy in our own words with attribution. We do not vendor their CLI or their workflow commands.
- The Refero exemplars are publicly viewable on `styles.refero.design`; the user has accepted the risk of vendoring without explicit license confirmation. If a takedown request lands later, we remove or replace the affected exemplars.
- Both skills are `workflow` type per dojo's skill-type taxonomy. The exemplars and slop catalog are reference assets nested under their consuming skill.
- Triggers must be sharp enough to fire reliably without colliding with each other. `design-md` triggers on token / format / lint / export language; `design-critique` triggers on review / audit / taste / "looks AI-generated" language.

## Open Decisions To Confirm Before Task 2

These are surfaced in "Open Questions for User" below; the plan proceeds with the recommended defaults if not overridden.

1. Which five Refero exemplars to vendor (recommended set in Task 2).
2. Whether `design-critique` accepts a screenshot input path in v1, or requires markup/CSS input only.
3. Whether the slop catalog lives under `design-critique/references/` only, or is duplicated under `design-md/references/` for shared access. Recommended: single home in `design-critique`, with `design-md` linking out.

## Task Breakdown

### Task 1: Scaffold The Two Skills

**Objective**

Create the directory structure, frontmatter, and section skeletons for both new skills so subsequent tasks have stable file paths to write into.

**Files**

- Create: `skills/design-md/SKILL.md`
- Create: `skills/design-md/references/` (directory)
- Create: `skills/design-md/scripts/` (directory)
- Create: `skills/design-critique/SKILL.md`
- Create: `skills/design-critique/references/` (directory)

**Dependencies**

None.

**Implementation Steps**

1. Run `python skills/skill-creator/scripts/init_skill.py design-md --path skills --resources scripts,references` to scaffold `design-md`.
2. Run the same command for `design-critique` with `--resources references`.
3. Replace the generated frontmatter with hand-written values: `name`, `description`, `skill-type: workflow`, and a `metadata.upstream` block pointing at the source repos and URLs.
4. Add placeholder section headers to both `SKILL.md` bodies (`When To Use`, `What It Does`, `How To Run`, `References`, `Out Of Scope`) so downstream tasks have clear insertion points.
5. Do not run strict contract validation; only run `quick_validate.py` to confirm frontmatter parses.

**Verification**

- Run: `python3 skills/skill-creator/scripts/quick_validate.py skills/design-md`
- Run: `python3 skills/skill-creator/scripts/quick_validate.py skills/design-critique`
- Expect: both skills pass quick validation with valid frontmatter and pass the stop hook's skill-structure check.

**Done When**

- Both skill directories exist with the expected resource subfolders.
- Both `SKILL.md` files have valid frontmatter and skeleton bodies.
- `skills.json` regenerates cleanly when the post-tool-use hook runs.

### Task 2: Vendor Five Refero DESIGN.md Exemplars

**Objective**

Curate a fixed set of five aesthetically distinct DESIGN.md files that act as anchor examples for `design-md` and as positive references for `design-critique`.

**Files**

- Create: `skills/design-md/references/exemplars/cursor.md`
- Create: `skills/design-md/references/exemplars/linear.md`
- Create: `skills/design-md/references/exemplars/stripe.md`
- Create: `skills/design-md/references/exemplars/vercel.md`
- Create: `skills/design-md/references/exemplars/figma.md`
- Create: `skills/design-md/references/exemplars/README.md`

**Dependencies**

- Task 1.

**Implementation Steps**

1. Pull each exemplar's DESIGN.md from Refero. Recommended set spans aesthetic poles: Cursor (warm ivory, technical-studio), Linear (dark, geometric, sharp), Stripe (clean, generous, blue accent), Vercel (minimal monochrome geometric), and Figma (colorful, playful, accessible). Substitute if any of the five is not actually available on Refero at fetch time and record the substitution in the exemplars `README.md`.
2. Save each as a verbatim copy with a short header comment: source URL, fetch date, attribution to Refero, and a one-line summary of why this exemplar earned a slot (which aesthetic pole it covers).
3. Author the exemplars `README.md` as a one-page index: each exemplar's name, dominant mood, color temperature, type personality, and notable token decisions. This index is what the agent reads first; the full exemplars are progressive disclosure.
4. Do not normalize, reformat, or "improve" the exemplars. Their value is in being faithful copies that surface real-world variation in how DESIGN.md gets used.

**Verification**

- Run: `ls skills/design-md/references/exemplars/`
- Expect: six files (five exemplars plus the `README.md`).
- Run: `head -20 skills/design-md/references/exemplars/cursor.md`
- Expect: header attribution comment, then verbatim DESIGN.md frontmatter.

**Done When**

- Five exemplars exist with attribution headers.
- The exemplars index documents which aesthetic pole each one anchors.
- The set spans warm and cool palettes, dark and light modes, dense and generous spacing, and at least one custom-typeface example.

### Task 3: Encode The Slop Catalog As A Structured Reference

**Objective**

Translate the impeccable.style slop page into a single structured reference file optimized for an audit pass, organized so `design-critique` can scope findings by category.

**Files**

- Create: `skills/design-critique/references/slop-catalog.md`

**Dependencies**

- Task 1.

**Implementation Steps**

1. Reproduce the slop taxonomy in our own words across these eight categories: visual details, typography, color and contrast, layout and space, motion, interaction, responsive, general quality.
2. For each pattern, write a single entry with these fields: `id` (short slug), `name`, `tells` (1–2 sentences describing what to look for), `why-it-fails` (the underlying mistake), `alternative` (the recommended replacement), and `severity` (low / medium / high based on how badly it dates the work or harms usability).
3. Add an explicit attribution paragraph at the top of the file naming impeccable.style as the source of the taxonomy and noting that descriptions are paraphrased.
4. Add a one-paragraph `How To Use` block at the top that tells the agent: read the catalog, scan the target UI for each pattern in order, return a finding only when you have a concrete observation, group findings by category, and rank by severity.
5. Do not import impeccable's CLI command names, workflow framing, or six-category maturity model. The catalog is a flat reference, not a workflow.

**Verification**

- Run: `wc -l skills/design-critique/references/slop-catalog.md`
- Expect: roughly 250–400 lines (30 patterns × ~10 lines each plus headers).
- Read the file and confirm every pattern has all five fields populated.

**Done When**

- All ~30 patterns from the impeccable slop page are represented with the five-field schema.
- Attribution is unambiguous.
- The agent can scan the file linearly and produce findings without consulting an external source.

### Task 4: Author The `design-md` Skill Body

**Objective**

Write the operational instructions for `design-md` so the agent can confidently lint an existing DESIGN.md, diff two versions, export to Tailwind or DTCG, or write a fresh DESIGN.md grounded in the exemplars.

**Files**

- Modify: `skills/design-md/SKILL.md`
- Create: `skills/design-md/references/format-primer.md`
- Create: `skills/design-md/scripts/run_cli.sh`

**Dependencies**

- Task 1, Task 2.

**Implementation Steps**

1. Write a `format-primer.md` reference (~150 lines) that summarizes the DESIGN.md schema: required frontmatter keys, the token sections (colors, typography, spacing, components, do/don't), and the contrast-ratio expectations the linter enforces. Pin to the CLI version we test against and note that the format is alpha.
2. Author `run_cli.sh` as a thin wrapper that invokes `npx @google/design.md@<pinned-version> "$@"` so the skill has a single deterministic call site. The wrapper passes through arguments and exits with the CLI's exit code.
3. In `SKILL.md`, write four operation playbooks: `lint` (run the CLI, surface findings, suggest fixes), `diff` (compare two DESIGN.md files, summarize material vs cosmetic changes), `export` (run with `--format tailwind|dtcg|css-vars` and integrate output into the target project), and `author` (write a fresh DESIGN.md by sampling the closest exemplar, then customizing tokens).
4. Add a `When To Use` section with sharp triggers: "user mentions DESIGN.md", "design tokens", "extract design system from", "lint design tokens", "export tokens to Tailwind".
5. Add a `When Not To Use` section that points at adjacent territory (generating UI from scratch, accessibility audits, taste critique) without naming specific other skills.
6. Note the alpha-spec risk and the regeneration playbook in a short `Maintenance` section at the end.

**Verification**

- Run: `bash skills/design-md/scripts/run_cli.sh --help`
- Expect: the `@google/design.md` CLI help text or a clear failure if `npx` is not on PATH.
- Run: `python3 skills/skill-creator/scripts/quick_validate.py skills/design-md`
- Expect: pass.

**Done When**

- `SKILL.md` documents all four operations with clear inputs, outputs, and example invocations.
- `format-primer.md` is self-sufficient as an in-context reference for the schema.
- `run_cli.sh` is the only path through which the CLI is invoked from the skill.

### Task 5: Author The `design-critique` Skill Body

**Objective**

Write the operational instructions for `design-critique` so the agent can take a piece of UI (markup, CSS, or a screenshot path) and return ranked, scoped findings using the slop catalog.

**Files**

- Modify: `skills/design-critique/SKILL.md`
- Create: `skills/design-critique/references/finding-template.md`

**Dependencies**

- Task 1, Task 3.

**Implementation Steps**

1. In `SKILL.md`, write the audit playbook: take the input, walk the slop catalog category by category, record only concrete findings (each tied to a specific element or selector when possible), group findings by category, rank by severity, and produce a summary of the top three highest-leverage fixes.
2. Author `finding-template.md` as a short reference defining the structured shape of a single finding: `pattern-id`, `where` (file:line or DOM selector), `evidence` (the offending snippet or coordinates), `severity`, `recommended-fix` (concrete, actionable, often pointing at the catalog's named alternative).
3. Add a `When To Use` section with sharp triggers: "review my UI", "audit this design", "does this look AI-generated", "check for design slop", "critique the visuals".
4. Add a `When Not To Use` section that explicitly excludes accessibility/WCAG audits and creative UI generation.
5. Add an `Inputs` section describing accepted forms: pasted HTML/JSX, file paths to component files, file paths to local screenshots, or a URL the agent can fetch via existing tools. Document the fallback when only a textual description is available (still possible, lower confidence).
6. Add a brief `Output Shape` section showing what a complete critique response looks like: grouped findings, severity-ranked, with a top-three summary and a one-line overall taste verdict.

**Verification**

- Run: `python3 skills/skill-creator/scripts/quick_validate.py skills/design-critique`
- Expect: pass.
- Manually trace a sample input (an existing component file from any active project) through the playbook on paper and confirm the output shape is producible without ambiguity.

**Done When**

- `SKILL.md` makes the audit reproducible by a fresh agent reading only the skill body and the slop catalog.
- `finding-template.md` is concrete enough that two agents would produce structurally identical findings for the same input.
- Triggers in `When To Use` are scenario-rich, not generic.

### Task 6: Integrate The Skills Into Catalog And Docs

**Objective**

Make both skills discoverable through the standard dojo discovery surfaces without touching any existing design-skill content.

**Files**

- Modify: `skills.json` (auto-regenerated by the post-tool-use hook)
- Modify: `docs/system/FEATURES.md`
- Modify: `README.md` (acknowledgements section)

**Dependencies**

- Task 4, Task 5.

**Implementation Steps**

1. Confirm the post-tool-use hook regenerated `skills.json` with both new skills present and correctly described.
2. Add both skills to `docs/system/FEATURES.md` in whichever section design-related skills currently live. Do not edit other entries.
3. Append acknowledgements to `README.md` for: Google Labs (`@google/design.md` format and CLI, Apache-2.0), Refero (DESIGN.md exemplars, web-published), and impeccable.style (slop taxonomy, web-published, paraphrased). Match the existing acknowledgement style.
4. Do not add a routing table or deconflict descriptions against existing design skills; that work is reserved for the follow-up remediation pass.

**Verification**

- Run: `jq '.skills[] | select(.name == "design-md" or .name == "design-critique") | {name, description}' skills.json`
- Expect: both entries present with the descriptions written in Tasks 4 and 5.
- Run: `grep -c "design-md\|design-critique" docs/system/FEATURES.md`
- Expect: at least two matches.

**Done When**

- `skills.json` lists both skills.
- `FEATURES.md` mentions both skills.
- `README.md` acknowledges all three upstream sources.

### Task 7: Smoke Test On A Real Project

**Objective**

Validate that both skills produce useful output on a real codebase before declaring v1 complete.

**Files**

- No code changes. Optionally create: `docs/learnings/2026-05-03-design-systems-layer-smoke-test.md` to record findings.

**Dependencies**

- Task 6.

**Implementation Steps**

1. Pick one active project from the parent `Dev/` workspace with a meaningful UI surface (`habits-ai-website`, `compendium`, `qotd`, or `davisbuilds-site`).
2. Run `design-md` in `lint` mode if the project already has a DESIGN.md, or in `author` mode to generate one from observed CSS/Tailwind tokens.
3. Run `design-critique` against one representative page or component from the same project.
4. Capture the run as a brief learning doc: what worked, what was awkward, what surfaced as a contract gap to fix in the deferred remediation pass.

**Verification**

- The learning doc exists and names at least one improvement to fold into the remediation pass.
- The smoke-test project remains unmodified (the audit is read-only; any fix-applies are explicitly user-driven).

**Done When**

- One real-project run is documented for each skill.
- Friction points are written down rather than fixed in this plan.

## Deferred Follow-Up Work

These items are deliberately out of scope for this plan but should be queued for a follow-up:

1. Compare `design-md` and `design-critique` against `frontend-design`, `web-design-guidelines`, `vercel-react-best-practices`, and `theme-factory`. Decide whether to add a routing table to `FEATURES.md`, tighten descriptions, or merge/retire any skills.
2. Run `validate_skill_contract.py --strict` against both new skills and resolve gaps.
3. Decide whether `design-critique` should grow optional Playwright integration for live screenshot capture.
4. Decide whether to grow the exemplar set beyond five, and whether to track a refresh cadence as Refero adds notable styles.
5. Watch for `@google/design.md` spec churn; bump the pinned CLI version and regenerate the format primer when material changes land.

## Open Questions For User

1. Confirm or override the recommended five exemplars: Cursor, Linear, Stripe, Vercel, Figma. Are there higher-signal alternatives in the Refero catalog you want included?
2. For `design-critique` v1, confirm: accept a screenshot path as input but do not auto-capture? Or stay text-input-only and add screenshot input in the remediation pass?
3. Confirm the smoke-test target in Task 7. Default recommendation is `habits-ai-website` since it has the most visible UI surface and a cohesive brand to critique against.
4. Confirm we should publish `design-critique` findings as agent output only, with no auto-applied fixes, in v1.
