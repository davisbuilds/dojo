---
name: change-comprehension
description: Help a human understand a specific code change — optional, conversational, never gating. Use when the user asks to understand the scope of a proposed change before it is implemented, or asks to be quizzed on an implemented change before merging it. Scope mode explains entry points, call paths, blast radius, and unknowns without becoming a spec or a plan. Quiz mode reads the actual diff, asks a single question per turn, waits for the answer, then teaches with repository evidence. Triggers on "help me understand this change", "understand the scope of this change", "quiz me on this change", "test my comprehension of this change", "change comprehension". Never scores the user, judges correctness, or gates delivery.
skill-type: workflow
version: 1.0.0
triggers:
  - help me understand this change
  - understand the scope of this change
  - quiz me on this change
  - test my comprehension of this change
  - change comprehension
---

# Change Comprehension

Agent-assisted development can reach a merge-ready diff without the human ever
building a mental model of it. This skill pays down that comprehension debt for
**one specific change**, on request, in conversation.

It teaches. It does not review, verify, plan, or approve.

## When To Use

Invoke when the user explicitly asks to understand a change:

- **Scope mode** — before implementation. "What is this change going to touch?"
  "Help me understand the scope before you build it."
- **Quiz mode** — after implementation, usually before merge. "Quiz me on this
  change." "Test my comprehension of what you just built."

The two modes are independent. Neither requires the other.

## Boundaries

- **Optional and non-gating.** Never volunteer a quiz. Never insert a
  comprehension step into an implementation, review, or merge request the user
  did not ask for. Ordinary work does not acquire a teaching ritual.
- **No score, no verdict.** No numeric score, no pass/fail, no merge approval,
  no claim that the implementation is correct. The user's answers are evidence
  about *their* mental model, never about the code.
- **One change, not the codebase.** If the requested subject is too broad to
  explain coherently, narrow the learning target with the user. Do not attempt a
  codebase survey.
- **Chat-only by default.** Write no file unless the user explicitly asks for a
  durable artifact.
- **Evidence or silence.** Never invent a system relationship, a call path, or a
  quiz answer. If the repository does not show it, say so.
- Do not silently invoke sibling skills, and never present comprehension as a
  substitute for their results. See [Sibling skills](#sibling-skills).

## Shared Grounding Rules

Both modes obey these before saying anything substantive.

1. **Read before you speak.** Ground in the actual repository and the actual
   change. Reuse an existing spec, plan, or review if one exists; do not
   regenerate it.
2. **Label your sources.** Three kinds of statement, always distinguishable:
   - *Evidence* — "`auth.py:88` calls `refresh_token` before the retry."
   - *Inference* — "so a stale token would surface here, not at the caller."
   - *Unknown* — "I can't tell from the repo whether the queue retries this."
3. **Calibrate.** State confidence when it is below high, and say what would
   raise it.
4. **Stay proportionate.** Comprehension debt is paid down with a conversation,
   not a second exhaustive review. Be concise enough that the user reads it.

## Scope Mode

Goal: a task-bounded mental model of what a proposed change is likely to affect.

### Workflow

1. **Fix the target.** Confirm which change is being scoped. If the request is
   broader than one coherent change, propose a narrower learning target and get
   agreement before continuing.
2. **Gather evidence.** Locate the entry point and the boundaries the change sits
   between. Trace the important call or data path — the one that carries the
   behavior in question, not every path.
3. **Separate current from proposed.** Current repository evidence is
   authoritative for *how the system behaves today*. The user's approved request
   or contract is authoritative for *what is intended*. Neither overrides the
   other silently. When they conflict, or when an existing artifact looks stale,
   say so explicitly and name which source you trust for which claim.
4. **Explain.** Cover, in whatever order the change makes natural:
   - the entry point and the system boundaries involved
   - the call or data path that matters
   - the likely blast radius — what else reads, writes, or depends on this
   - the consequential unknowns, with calibrated confidence
5. **Stop at understanding.** Do not choose an architecture, define acceptance
   criteria, or prescribe implementation tasks. If the user wants those, route
   them to the sibling that owns them.

## Quiz Mode

Goal: the user discovers what they do and do not understand about a change that
already exists, and leaves understanding more.

### Workflow

1. **Resolve the change target.** Working tree, staged changes, a branch, a
   commit, or a pull request. If no target is identifiable, **ask for one**.
   Never fabricate a quiz against a change you have not read.
2. **Read the change and its evidence.** The actual diff, plus whatever
   verification exists — tests, CI, a review. Know the answers before asking the
   questions.
3. **Propose a bounded topic set.** Unless the user asked for a specific depth,
   propose a small set of topics sized to the change's risk and surface area, and
   let the user adjust it. This is what makes the quiz end.
4. **Quiz, one question at a time.**
   - **At most one substantive question per turn.** Ask it, then **stop and
     wait.** Do not ask a second question, hint at the answer, or answer it
     yourself in the same turn.
   - Grounding, clarifying, and recap turns may contain no question at all.
   - After each answer — including "I don't know", which is a legitimate and
     cost-free response — name what was right, then correct or extend the model
     with **concrete repository evidence** (file, line, symbol). Then continue at
     a depth that matches how the user is doing.
5. **Close with a recap** when the topic set is covered, or the moment the user
   asks to stop.

### What To Ask About

Choose questions the change actually justifies, spread across:

- **Intent** — what problem does this change solve, and why this way?
- **The seam** — where does it plug into the existing system, and why there?
- **Data and control flow** — what moves through the changed path?
- **Failure modes** — what happens when the input is bad, the dependency is
  down, or the call races?
- **What verification proves** — and, more importantly, what it does *not*.
- **Residual risk** — operational, compatibility, migration, rollback.

Never ask trivia: filenames, syntax, line numbers, or anything the user could
answer without understanding the change.

## Output Contract

Both modes deliver prose in chat and write no file, unless the user explicitly
asks for a durable artifact.

**Scope mode** leaves the user able to say where the change lands, what it can
break, and what nobody knows yet.

**Quiz mode** ends with a recap naming what the user appears to understand well
and what is worth revisiting. Nothing else: no score, no pass/fail label, no
correctness claim about the code, no merge verdict.

## User Control

The user runs this, not you. At any point they may ask for more or less depth,
skip a topic, pause, or stop. Honor it immediately and treat none of it as
failure — a user who stops has not "failed the quiz", because there is no quiz to
fail.

## Verification

The workflow is working when:

- It activated because the user asked, not because you offered.
- Every substantive claim is traceable to the repository, marked as inference, or
  admitted as unknown.
- Scope output teaches the system's shape without turning into a plan.
- Quiz turns hold the line: one question, then a wait; evidence-backed teaching
  after each answer; no answer leaked early.
- The session ends with a recap and no score, verdict, or file.

## Resources

- `commands/understand-change.md` — `/understand-change`, the scope-mode wrapper
- `commands/quiz-change.md` — `/quiz-change`, the quiz-mode wrapper
- `evals/trigger-cases.json` — routing fixture for this skill and its siblings
- `evals/behavioral-scenarios.md` — frozen conversational scenarios and the
  binary assertions that define acceptance

## Sibling skills

This skill sits beside the change lifecycle, not inside it. It consumes the
outputs of these skills and hands work back to them; it replaces none of them.

- `brainstorming` — deciding *what* to build when the direction is unclear
- `write-spec` — pinning the falsifiable contract
- `write-plan` — sequencing the implementation
- `first-principles` — choosing between architectural approaches
- `diagnose` — finding the cause of broken behavior
- `local-review` / `gh-review-pr` — finding defects in a diff or a pull request
- `verify-before-complete` — proving a completion claim with evidence

If the user wants any of those, say which skill owns it and why, in one sentence.
