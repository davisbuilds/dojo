# Features

Product-surface reference for the Agent Skills Repository.

## Skills Catalog

Catalog snapshot by category. For canonical runtime inventory, use `skills.json`:

```bash
jq '.skills | length' skills.json
```

### GitHub Workflows

| Skill | Purpose |
|-------|---------|
| `gh-commit-push-pr` | Commit, push, and open a Pull Request |
| `gh-fix-issue` | Fix GitHub issues end-to-end from analysis through PR |
| `gh-review-pr` | Review Pull Requests with merge recommendations |
| `gh-triage-issues` | Label, prioritize, and de-duplicate GitHub issues |

### Code Review and Quality

| Skill | Purpose |
|-------|---------|
| `code-review-agents` | Multi-agent reviews: architecture, security, data, performance, deployment |
| `diagnose` | Disciplined six-phase debugging loop — build a deterministic pass/fail signal, reproduce, hypothesise, instrument, fix, regression-test |
| `local-review` | Findings-first local reviews on workspace diffs |

### Content Creation and Design

| Skill | Purpose |
|-------|---------|
| `algorithmic-art` | Generative art with p5.js and controlled randomness |
| `design-md` | Read, write, lint, diff, and export DESIGN.md files via the pinned `@google/design.md` CLI |
| `design-critique` | Audit UI against a 37-pattern slop catalog and return ranked, scoped findings |
| `frontend-design` | Distinctive, production-grade frontend interfaces |
| `gemini-imagen` | Image generation/editing via Gemini API |
| `gpt-imagen` | Image generation/editing via OpenAI Image API |
| `theme-factory` | Apply preset or generated theme systems |
| `web-design-guidelines` | Review UI against web interface guidelines |

The four design skills above compose into a pipeline: `design-md` (token spec) → `frontend-design` (build) → `design-critique` (taste / AI-slop review), with `web-design-guidelines` as a parallel rule-compliance pass (Vercel WIG, accessibility, UX). Each skill's body carries a `Sibling skills` footer that names the adjacent stages and hand-off cues.

### Development Workflows

| Skill | Purpose |
|-------|---------|
| `api-design` | Design and review robust API, event, interface, and machine-output contracts |
| `autonomous-engineering` | Full end-to-end feature workflows (`/lfg`, `/slfg`) |
| `loop-design` | Design verifiable autonomous loops on top of `/loop` and `/goal`; gate on an oracle, then scaffold a portable loop bundle (`/loop-design`) |
| `brainstorming` | Clarify WHAT to build and capture the chosen direction (`docs/design/`) |
| `write-spec` | Pin the falsifiable contract — WHAT must be true, mechanism-free; conditionally add high-risk authority/invariant scenarios and review closure (`docs/specs/`) |
| `write-plan` | Sequence the build — HOW: tasks, files, seam selection, and verification; conditionally add high-risk traceability, evidence, capability gates, and review closure (`docs/plans/`) |
| `blind-spots` | Find what you don't know about one change — blind spot pass before it's built, or a brief-then-quiz before you merge (never scored, never gating) |
| `create-cli` | CLI parameter and UX design |
| `agent-native-architecture` | Build agent-native apps with tool/action parity |
| `deep-research` | Web-backed research with conditional depth and explainable, URL-host-derived evidence filtering |
| `research-architect` | Engineer deep-research prompts, route execution, independently verify reports, synthesize multi-run results, and compound lessons via postmortems |
| `self-improve` | Capture learnings, compact them, and promote validated patterns into reusable artifacts |

### Disciplines

`reference`-typed skills that govern *how* the agent operates rather than what to build. They produce no discrete deliverable; they shape style, rigor, and reasoning across every other skill.

| Skill | Purpose |
|-------|---------|
| `caveman` | Sticky ultra-compressed output mode (~75% token cut) until the user says "stop caveman" |
| `first-principles` | Systems reasoning for high-stakes decisions — epistemic framework, decision matrix, principle tensions |
| `test-strategy` | Testing methodology: TDD, real dependencies over mocks, behavior-based tests, and conditional effective authority-boundary probes |
| `verify-before-complete` | Evidence-based completion gate; require verification before claiming done |

### Security

| Skill | Purpose |
|-------|---------|
| `repo-hardening` | Audit repos for supply-chain risk, generate repo-local security artifacts, and drive hardening work |
| `secure-code` | Static analysis security scanning and architectural trifecta detection via semgrep |
| `audit-skill` | Security-audit agent skills for prompt injection, overreach, secrets, and dangerous code patterns |

### Platform Integrations

| Skill | Purpose |
|-------|---------|
| `vercel-deploy` | Deploy to Vercel |
| `vercel-preview-logs` | Debug Vercel preview deployments |
| `vercel-react-best-practices` | React/Next.js performance optimization |
| `nextjs-app-router` | Next.js App Router patterns, data fetching, and debugging |
| `vercel-react-native-skills` | React Native and Expo best practices |
| `vercel-composition-patterns` | Scalable React composition patterns |

### UI Automation

| Skill | Purpose |
|-------|---------|
| `playwright` | Browser automation from the terminal — navigation, form filling, screenshots, data extraction |
| `screenshot` | Capture screenshots across platforms (full screen, app/window, region) |

### Knowledge and Documentation

| Skill | Purpose |
|-------|---------|
| `obsidian-markdown` | Obsidian Flavored Markdown with wikilinks and callouts |
| `obsidian-bases` | Obsidian Bases with views, filters, and formulas |
| `obsidian-canvas` | Obsidian Canvas files for visual canvases |
| `markdown-converter` | Convert file formats to Markdown |
| `fetchmd` | Convert webpages or local HTML into clean Markdown for AI workflows |
| `handoff` | Session summaries for context handoff |
| `compound-docs` | Capture solved problems as documentation |
| `session-retro` | Route non-obvious session learnings into existing project reference docs |

### Meta / Skill Management

| Skill | Purpose |
|-------|---------|
| `skill-creator` | Initialize, validate, and package new skills |
| `skill-evals` | Validate SKILL contract compliance and run trigger-eval scaffolds |
| `skill-installer` | Install skills from curated lists or GitHub repos |
| `skill-standardizer` | Detect drift and unify skill copies, with optional single-skill targeting |
| `find-skills` | Discover installable skills |
| `hookify` | Create and manage markdown-defined guard-rail hooks |
| `template` | Starter scaffold for new skills |

## Hook-Enforced Quality Gates

- SKILL.md frontmatter validated on every write/edit (pre-tool-use).
- New or updated skills should declare `skill-type` so contract validation applies the right structure for workflow vs reference skills.
- Every skill declares a SemVer `version`; release-relevant skill edits require a version bump and changelog entry against the selected git base.
- Pushes to protected branches are blocked unless the command includes an explicit `DOJO_ALLOW_PROTECTED_PUSH=1` override.
- `skills.json` manifest regenerated after every SKILL.md change (post-tool-use).
- Newly authored design summaries, specs, and plans identify the producing agent
  in `author:` frontmatter; current-schema spec/plan validation rejects missing
  or unresolved attribution while accepting legacy artifacts.
- `docs/specs/*-spec.md` and `docs/plans/*-plan.md` validated after every
  write/edit (post-tool-use).
- Uncommitted changes and untracked files blocked at session stop. Unpushed commits no longer block — push timing is the operator's call.
- Skill directory structure and skill release-version bumps validated at session stop.

## Command Wrappers

Slash-style entrypoints for harnesses that support command files. `scripts/gen_harness_adapters.py` links each skill's `commands/<rel>.md` into `.claude/commands/<rel>.md` (local-only, gitignored), so Claude Code resolves them as real slash commands — nested files like `commands/workflows/brainstorm.md` become `/workflows:brainstorm`. Run the generator after a clone to populate them:

- `/review` — local code review
- `/review-pr` — GitHub PR review
- `/fix-issue` — GitHub issue resolution
- `/triage-issue` — GitHub issue triage
- `/commit-push-pr` — commit, push, PR flow
- `/workflows:brainstorm` — brainstorming session (WHAT — chosen direction)
- `/workflows:spec` — write the falsifiable contract (WHAT must be true)
- `/workflows:plan` — sequence the build (HOW — task breakdown, files, steps)
- `/understand-change` — blind spot pass on a proposed change: scope, blast radius, and unknown unknowns
- `/quiz-change` — get briefed on an implemented change, then quizzed on it one question at a time
- `/standardize-skills` — skill standardization
- `/deep-research` — route depth and filter evidence in one command
- `/repo-audit` — generate repo-local audit artifacts and summarize hardening gaps
- `/repo-harden` — implement the highest-value hardening fixes and refresh the audit packet
- `/self-improve` — capture, compact, propose, and extract self-improvement artifacts
- `/retro` — capture session learnings into existing project reference docs, including matching root, `docs/system`, or `docs/project` files

## Skill Packaging

Skills can be packaged into `.skill` files (zip format) for distribution:

```bash
python skills/skill-creator/scripts/package_skill.py <skill-name> ./dist
```

Pre-packaged skills are available in `docs/downloads/`.
