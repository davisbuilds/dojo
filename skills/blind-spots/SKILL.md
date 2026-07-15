---
name: blind-spots
description: Find the gaps in a user's understanding of a code change — before it gets built, or after an agent has built it. Use when the user asks for a blind spot pass, asks to understand the scope and blast radius of a proposed change, or asks to be quizzed on a change an agent just made. Scope mode calibrates to the user's existing knowledge, then maps entry points, call paths, blast radius, and unknown unknowns into a mental model the user can steer with. Quiz mode reads the actual diff, briefs the user on the change, then asks a single question per turn about consequences the briefing left open, teaching with repository evidence after each answer so comprehension sticks. Triggers on "blind spot pass", "find my blind spots", "unknown unknowns", "help me understand this change", "quiz me on this change". Optional and conversational — never scores the user, never gates delivery.
skill-type: workflow
version: 1.0.1
triggers:
  - blind spot pass
  - find my blind spots
  - unknown unknowns
  - help me understand this change
  - quiz me on this change
---

# Blind Spots

An agent can take a change from idea to merge-ready without the human ever
building a mental model of it. This skill finds what the human does not know
about **one specific change** — before it gets built, or after an agent built it.

It teaches. It does not review, verify, plan, or approve.

## When To Use

Invoke when the user explicitly asks:

- **Scope mode** — before implementation. "Do a blind spot pass on this." "What
  am I not seeing here?" "What is this change going to touch?"
- **Quiz mode** — after implementation, usually before merge. "Quiz me on this
  change." "Make sure I actually understand what you just built."

The two modes are independent. Neither requires the other.

## Boundaries

- **Optional and non-gating.** Never volunteer a quiz. Never insert a teaching
  step into an implementation, review, or merge request the user did not ask for.
  Ordinary work does not acquire a ritual.
- **No score, no verdict.** No numeric score, no pass/fail, no merge approval, no
  claim that the implementation is correct. The user's answers are evidence about
  *their* mental model, never about the code.
- **One change, not the codebase.** If the requested subject is too broad to
  explain coherently, narrow the learning target with the user. Do not attempt a
  codebase survey.
- **Chat-only by default.** Write no file unless the user explicitly asks for a
  durable artifact.
- **Evidence or silence.** Never invent a system relationship, a call path, or a
  quiz answer. If the repository does not show it, say so.
- Do not silently invoke sibling skills, and never present this as a substitute
  for their results. See [Sibling skills](#sibling-skills).

## Calibrate First

**Both modes open by finding out where the user actually stands.** An explanation
pitched at the wrong level is wasted: too basic and it insults, too advanced and
it lands on nothing.

Ask, in one short question, some version of: *what do you already know about this
area, and what are you unsure of?* Then take the answer at face value.

- Assume competence by default. A user who says they know the codebase does not
  need fundamentals re-explained — go straight to what is genuinely non-obvious.
- Blind spots are not ignorance. A strong engineer's unknowns are usually
  specific: a subsystem they have never touched, a library's internals, an
  invariant nobody wrote down. They are not gaps in general knowledge.
- If the user does not answer, infer from how they framed the request and state
  what you assumed, so they can correct it.

## Scope Mode

Goal: surface the user's unknowns about a proposed change, and leave them with a
mental model they can steer with.

### Workflow

1. **Calibrate.** Establish what the user already knows before explaining
   anything.
2. **Fix the target.** Confirm which change is being scoped. If the request is
   broader than one coherent change, propose a narrower learning target and get
   agreement.
3. **Gather evidence.** Locate the entry point and the boundaries the change sits
   between. Trace the call or data path that carries the behavior in question —
   not every path.
4. **Separate current from proposed.** Current repository evidence is
   authoritative for *how the system behaves today*. The user's approved request
   is authoritative for *what is intended*. Neither overrides the other silently.
   When they conflict, or an existing artifact looks stale, say so and name which
   source you trust for which claim.
5. **Map it, calibrated.** Cover the entry point and boundaries, the call or data
   path that matters, and the likely blast radius — what else reads, writes, or
   depends on this.
6. **Name the unknowns.** This is the point of the mode, not an afterthought.
   Separate them honestly:
   - **Known unknowns** — what the user already flagged as uncertain.
   - **Unknown unknowns** — what they did not ask about and would not think to:
     the invariant nobody wrote down, the caller nobody remembers, the failure
     mode this area is historically prone to, the thing that will look obvious in
     hindsight.
   - **Unknowable from here** — what the repository simply does not say. Name it
     as such rather than guessing.
7. **Stop at understanding.** Do not choose an architecture, define acceptance
   criteria, or prescribe implementation tasks. Route those to the sibling that
   owns them.

## Quiz Mode

Goal: the user ends up actually understanding a change that already exists.

The quiz is not a memory test. The user is usually quizzing themselves on work an
agent did while they were not watching closely — cold-testing recall of something
they never saw teaches nothing. So **brief first, then quiz on what the briefing
did not answer.**

### Workflow

1. **Resolve the change target.** Working tree, staged changes, a branch, a
   commit, or a pull request. If no target is identifiable, **ask for one**.
   Never quiz against a change you have not read.
2. **Read the change and its evidence.** The actual diff, plus whatever tests, CI
   results, or review exist. Know the answers before asking the questions.
3. **Calibrate.** One short question about what the user already knows here. This
   sets the briefing's depth and the quiz's difficulty.
4. **Brief the user.** A compact walkthrough of the change: what changed, why,
   where it plugs into the existing system, and what the tests cover. This is the
   shared ground the quiz stands on.

   The briefing states **what was done**. It must not pre-answer the questions,
   which probe **what follows from it**. Do not spell out the failure modes, the
   limits of the tests, or the residual risks in the briefing — those are the
   quiz.
5. **Propose a bounded topic set**, sized to the change's risk and surface area.
   Let the user adjust it. This is what makes the quiz end.
6. **Quiz, one question at a time.**
   - **At most one substantive question per turn.** Ask it, then **stop and
     wait.** Do not ask a second, hint at the answer, or answer it yourself in
     the same turn.
   - After each answer — including "I don't know", which is legitimate and
     cost-free — name what was right, then correct or extend the model with
     **concrete repository evidence** (file, line, symbol). Then continue at a
     depth that matches how the user is doing.
7. **Close with a recap** when the topic set is covered, or the moment the user
   asks to stop.

### What To Ask About

Ask about consequences, not contents — the briefing already gave them the
contents.

- **Intent** — why this approach, and what was rejected?
- **The seam** — why does it plug in *there*, and what breaks if it moved?
- **Failure modes** — bad input, dependency down, concurrent call, partial write.
- **What the tests do not prove** — usually more interesting than what they do.
- **Residual risk** — operational, compatibility, migration, rollback.

Never ask trivia: filenames, syntax, line numbers, or anything answerable without
understanding the change.

## Output Contract

Both modes deliver prose in chat and write no file, unless the user explicitly
asks for a durable artifact.

**Scope mode** leaves the user able to say where the change lands, what it can
break, and — the point of the mode — what they did not know they did not know.

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
- Depth matches what the user said they know — no fundamentals lecture to an
  expert, no jargon dump on a newcomer.
- Every substantive claim is traceable to the repository, marked as inference, or
  admitted as unknown.
- Scope mode names unknown unknowns the user did not ask about, and stops short
  of becoming a plan.
- The briefing precedes the questions, and the questions probe what the briefing
  left open rather than what it already said.
- Quiz turns hold the line: one question, then a wait; evidence-backed teaching
  after each answer.
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
- `write-plan` — sequencing the build. It maps the code to pick a seam; this maps
  the code to teach a human. Same territory, different reader.
- `first-principles` — choosing between architectural approaches
- `diagnose` — finding the cause of broken behavior
- `local-review` / `gh-review-pr` — finding defects in a diff or a pull request
- `verify-before-complete` — proving a completion claim with evidence

If the user wants any of those, say which skill owns it and why, in one sentence.
