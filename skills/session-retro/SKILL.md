---
name: session-retro
description: 'Update existing project reference docs with non-obvious learnings from the current session. Route each learning to the single best existing target: AGENTS.md, CLAUDE.md, README.md, or canonical docs/system and docs/project references such as OPERATIONS.md, ARCHITECTURE.md, FEATURES.md, or ROADMAP.md. Use at session end, after solving tricky problems, or when new CLI commands/features were added. Triggers on "/retro", "update docs with learnings", "save what we learned", or proactively at session end.'
---

# Session Retro

Capture non-obvious learnings from this session in the project's existing reference docs. Prefer the single most canonical destination for each learning, and skip updates when the right doc does not already exist.

## What Qualifies

- Environment quirks or workarounds that cost time to discover
- Non-obvious API behavior, flag combinations, or config requirements
- Dependency gotchas (version conflicts, install flags, peer deps)
- Commands that exist but weren't documented
- New CLI commands or features built this session
- Build/test/deploy steps that differ from what you'd expect

## What Does NOT Qualify

- Anything already in the project's docs
- Obvious language/framework behavior
- One-off typos or syntax errors that were fixed
- Session-specific context (current task state, temp files)
- Anything the next agent would figure out in under 30 seconds

## Eligible Targets

Only update docs that already exist. Never create new reference docs during `/retro`.

- Root docs: `AGENTS.md`, `CLAUDE.md`, `README.md`
- Canonical system docs: `docs/system/OPERATIONS.md`, `docs/system/ARCHITECTURE.md`, `docs/system/FEATURES.md`
- Canonical project docs: `docs/project/ROADMAP.md`, `docs/project/VISION.md`
- Other project ref docs only when they are clearly canonical, already present, and a better fit than the files above

## Routing Guide

Choose exactly one primary destination per learning. Avoid duplicate updates across multiple docs unless the user explicitly asks for that.

- **Agent workflow / implementation gotcha / repo-specific shortcut** -> `AGENTS.md` or `CLAUDE.md` (prefer `AGENTS.md`)
- **Quickstart / primary commands / setup the next developer expects at repo entry** -> `README.md`
- **Runbooks / CI / cron / env vars / migrations / operational commands** -> `docs/system/OPERATIONS.md`
- **Service boundaries / invariants / data flow / required code patterns** -> `docs/system/ARCHITECTURE.md`
- **Shipped capability or catalog-style reference** -> `docs/system/FEATURES.md`
- **Actual project status or planned work that changed this session** -> `docs/project/ROADMAP.md`
- **Product direction or policy decisions** -> `docs/project/VISION.md` or the matching existing policy doc

If the best-fit doc is missing, fall back to the closest existing root doc only when the learning still belongs there. Otherwise skip it.

## Process

1. **Inventory existing ref docs** — check which eligible target files actually exist in the current project.

2. **Identify learnings** — from session context, list candidates. Apply the "would this save the next agent 5+ minutes?" filter. Discard the rest.

3. **Route each learning to one canonical doc** using the routing guide above. Prefer the most specific existing doc, not the most convenient one.

4. **Use the smallest safe edit.**
   - Prefer single-line append-only additions for root docs and gotcha-style notes.
   - Allow minimal in-place edits for stateful structured docs when append-only would create duplication or stale information.
   - Match the file's existing format exactly (table row, bullet, numbered item, short paragraph, code block entry).

5. **For gotchas in agent docs**, match numbering, bold-key style, and indentation exactly. The standard format is:

   ```
   N. **Bold Key**: One-line explanation with specific details.
   ```

   If no gotchas section exists, add `## Implementation Gotchas` before appending.

6. **For commands, features, roadmap items, or architecture tables**, update only the smallest relevant section. Do not reorganize unrelated content.

7. **Present the diff** — group the preview by file, show exactly what will change, and wait for approval before writing.

## Rules

- **Update only existing docs.** No new `docs/system/*` or `docs/project/*` files during `/retro`.
- **One learning, one home.** Do not copy the same learning into multiple docs.
- **Prefer append-only.** Use in-place edits only when a structured ref doc would become misleading or duplicative otherwise.
- **Keep edits narrow.** Touch the smallest relevant section and avoid rewrites or reorganization.
- **Never add comments like `// added by agent` or timestamps.** The git log is the audit trail.
- **Max 5 learnings per session.** If you have more, keep only the highest-signal ones.
- **Max 3 files per run** unless the user explicitly asks for broader documentation cleanup.
- **Be specific.** "Use `--legacy-peer-deps` with npm install" not "npm install may need flags."
- **Skip weak fits.** If no clearly correct existing doc exists, do not force the update.

## When To Use

- At the end of a coding session when non-obvious learnings were discovered
- After solving a tricky problem that cost significant debugging time
- When new CLI commands, features, architecture constraints, or operational procedures were added and the matching ref doc already exists
- When triggered by `/retro` or explicit request to capture learnings

## Output

- One to five narrow updates in the project's existing ref docs
- Each learning is routed to exactly one canonical file
- Each change follows the target doc's existing formatting conventions
- A grouped diff preview shown to the user before any file writes

## Verification

- Every learning passes the "would this save the next agent 5+ minutes?" filter
- Every target file exists before editing
- Every learning has a clear canonical home, with no unnecessary duplication
- Edits are append-only unless a minimal in-place structured update is clearly better
- The correct section is identified before editing, and untouched sections remain unchanged
