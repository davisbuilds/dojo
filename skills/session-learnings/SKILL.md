---
name: session-learnings
description: Update project reference docs (AGENTS.md, CLAUDE.md) with non-obvious learnings from the current session. Use at session end, after solving tricky problems, or when new CLI commands/features were added. Triggers on "/learnings", "update docs with learnings", "save what we learned", or proactively at session end.
---

# Session Learnings

Append non-obvious learnings from this session to the project's reference docs. Every edit must be a single-line addition — no rewrites, no reorganization.

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

## Process

1. **Identify the project's ref doc** — find `AGENTS.md` or `CLAUDE.md` at the project root. Prefer `AGENTS.md` if both exist.

2. **Identify learnings** — from session context, list candidates. Apply the "would this save the next agent 5+ minutes?" filter. Discard the rest.

3. **Categorize each learning:**
   - **Gotcha** → append to `## Implementation Gotchas` section
   - **New CLI command/feature** → append to the commands/usage section
   - **New dependency or tool** → append to the relevant setup/dependencies section

4. **Append using the project's existing format.** Match numbering, bold-key style, and indentation exactly. For gotchas, the standard format is:

   ```
   N. **Bold Key**: One-line explanation with specific details.
   ```

   If no gotchas section exists, add `## Implementation Gotchas` before appending.

5. **For new CLI commands**, match the project's existing command documentation style (table, list, or code block). Add only the new entry.

6. **Present the diff** — show the user exactly what you'll add before writing. Wait for approval.

## Rules

- **One line per learning.** No multi-line explanations, no paragraphs, no sub-bullets.
- **Never rewrite existing content.** Append only.
- **Never add comments like `// added by agent` or timestamps.** The git log is the audit trail.
- **Max 5 learnings per session.** If you have more, keep only the highest-signal ones.
- **Be specific.** "Use `--legacy-peer-deps` with npm install" not "npm install may need flags."
