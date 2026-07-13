---
date: 2026-07-13
topic: blind-spots
stage: spec
status: in-progress
source: conversation
---

# Blind Spots Spec

## Problem

Agent-assisted development can bring a change to a verified, reviewable state
without giving the user a durable mental model of its scope, behavior, and
remaining risk. Dojo's existing workflows ground the agent, define the contract,
plan the seam, review the diff, and verify completion, but none are responsible
for helping the human retain ownership of an agent-made change. Without an
optional comprehension workflow, increasing delivery speed can create
comprehension debt that becomes visible only when the user must review, operate,
or extend code they do not understand.

## Contract

When this ships, a user can explicitly invoke one human-centered,
task-scoped workflow either before implementation to find their blind spots in a
proposed change or after implementation to be briefed and quizzed on the actual
change. Both modes first establish what the user already knows and pitch their
depth to that. The pre-implementation mode produces an evidence-backed mental
model and explicitly names the user's unknown unknowns, without becoming a
specification or plan. The post-implementation mode briefs the user on the
implemented change, then conducts an adaptive, one-question-at-a-time
conversation about the consequences the briefing left open, teaches after each
answer, and ends without a score or merge-readiness verdict.

The structural and routing portions of the end state are verified by
`python3 skills/skill-evals/scripts/validate_skill_contract.py --skills-root skills --strict`,
`python3 skills/skill-evals/scripts/run_trigger_evals.py --from-triggers --skills-root skills --pretty`,
`python3 skills/skill-evals/scripts/run_trigger_evals.py --cases skills/blind-spots/evals/trigger-cases.json --skills-root skills --skills blind-spots,brainstorming,write-spec,write-plan,first-principles,diagnose,local-review,gh-review-pr,verify-before-complete --pretty`,
and the fixed behavioral scenario protocol below. The behavioral protocol passes
only when every binary assertion passes; any failed assertion fails acceptance.

## Success Criteria

### Shared Behavior

- The workflow activates only when the user asks to understand a specific
  proposed or implemented change; ordinary planning, implementation, review,
  verification, or merge requests do not acquire an unsolicited teaching step.
- Both modes establish the user's existing knowledge of the area before
  explaining anything, and pitch their depth to the answer. A user who declares
  expertise is not given a fundamentals lecture; a user who declares unfamiliarity
  is not given a jargon dump. When the user does not answer, the workflow states
  the level it assumed so the user can correct it.
- It distinguishes repository evidence from inference and says when evidence is
  missing rather than inventing a system relationship or quiz answer.
- It remains task-scoped. If the requested subject is too broad to explain
  coherently, it narrows the learning target with the user instead of attempting
  an exhaustive codebase map.
- It is conversational and user-controlled: the user can ask for more or less
  depth, pause, skip a topic, or stop without the workflow treating that choice
  as failure.
- Its normal output remains in chat. It creates a durable artifact only when the
  user explicitly requests one.

### Scope Mode

- Before implementation, the user can request a bounded explanation of what a
  proposed change is likely to affect.
- The explanation identifies the relevant entry point and system boundaries,
  traces the important call or data path, describes the likely blast radius, and
  surfaces consequential unknowns with calibrated confidence.
- It separates the user's known unknowns from their **unknown unknowns** — the
  things they did not ask about and would not have thought to — and from what the
  repository genuinely cannot answer. Naming at least one unknown unknown, when
  one exists, is the point of the mode rather than a bonus.
- Current repository evidence is authoritative for current behavior. The user's
  approved request or contract is authoritative for proposed intent. The workflow
  distinguishes the two and labels conflicts, stale artifacts, and inference
  rather than allowing either source to override the other silently.
- The output teaches the current system shape and the limits of what is known; it
  does not choose an architecture, define acceptance criteria, or prescribe
  implementation tasks.

### Quiz Mode

- After implementation, the user can request a quiz against a clearly identified
  working-tree, staged, branch, commit, or pull-request change. When no change
  target is available, the workflow asks for one instead of fabricating a quiz.
- The workflow reads the actual change and available verification evidence before
  asking substantive questions.
- It briefs the user before quizzing them. The quiz is not a memory test: the
  user is typically quizzing themselves on work an agent did while they were not
  watching, so cold-testing recall of something they never saw would teach
  nothing. The briefing states what changed, why, where it plugs in, and what the
  tests cover.
- The briefing states what was **done**; the questions probe what **follows** from
  it. The briefing therefore does not pre-answer the quiz by spelling out the
  failure modes, the limits of the verification, or the residual risks — those are
  the quiz.
- During active quizzing, it asks at most one substantive quiz question per
  assistant turn, then stops and waits for the user's answer before revealing or
  teaching the answer. Grounding, briefing, clarification, and recap turns may
  contain no quiz question.
- After each response—including “I don't know”—it identifies what was correct,
  corrects or extends the mental model with concrete repository evidence, and
  then continues at an appropriate depth.
- Questions are selected for the actual change and proportionately cover intent,
  the changed seam or flow, meaningful failure modes, what verification proves
  and does not prove, and residual operational or compatibility risk. They avoid
  trivia about filenames, syntax, or facts unrelated to owning the change.
- When the user does not request a depth, the workflow proposes a bounded topic
  set based on the change's size and risk, allows the user to adjust it, and ends
  with the recap when that set has been covered.
- The closing recap names what the user appears to understand and what is worth
  revisiting. It contains no numeric score, pass/fail label, merge approval, or
  claim that the implementation is correct.

### Composition And Routing

- Requests to clarify an ambiguous outcome or choose a direction remain with
  `brainstorming`; requests to define a falsifiable target remain with
  `write-spec`; requests to sequence implementation remain with `write-plan`;
  requests to choose between architectural approaches remain with
  `first-principles`;
  requests to isolate the cause of broken behavior remain with `diagnose`;
  requests to find defects in a local diff remain with `local-review`; requests
  to review a published pull request remain with `gh-review-pr`; and requests to
  prove a completion claim remain with `verify-before-complete`.
- The workflow may consume outputs from those skills, but it neither silently
  invokes them nor presents comprehension as a substitute for their results.
- Positive routing cases cover both scope and quiz intent. Negative controls
  preserve routing for neighboring planning, review, verification, debugging,
  and generic code-explanation requests that do not ask for the interactive
  comprehension workflow.

## Evaluation

This is a workflow capability, not a measurable product experiment, so no
kill/scale/graduate thresholds apply.

Mechanical acceptance requires the strict skill contract, declared-trigger
self-routing, focused cross-skill trigger-collision cases, generated-artifact
checks, and the spec validator to pass.

Behavioral acceptance uses fixed inputs and recorded assistant/user turns. Each
scenario has binary assertions; all assertions must pass:

| Scenario | Fixed interaction | Binary assertions |
| --- | --- | --- |
| Calibration and unknown unknowns | A proposed change whose approved intent differs from current behavior and includes one unresolved boundary, with the user declaring expertise in one area and unfamiliarity with another | Asks what the user knows before explaining; honors the declared expertise in both directions; separates current behavior from proposed intent; labels the conflict and the unknowable boundary; names at least one unknown unknown; prescribes no architecture, acceptance contract, or task sequence; writes no artifact |
| Brief, then incomplete quiz answer | An identifiable implemented change with verification evidence, followed by a partial answer and then “I don't know” | Reads the change first; briefs the user before quizzing; the briefing does not pre-answer the quiz; asks at most one substantive question and waits; questions probe consequences rather than briefing contents; gives neutral, evidence-backed correction after each answer; leaks no answer before the response |
| Complete answer and close | The same change with a complete user answer and all proposed topics covered | Recognizes the complete answer; avoids a redundant question; closes with a concise strengths/revisit recap; emits no score, pass/fail label, correctness claim, or merge verdict |
| Missing change target | A quiz request with no identifiable diff, commit, branch, or pull request | Requests a concrete target; invents no quiz facts; delivers no briefing and begins no substantive quiz |
| User control | An active quiz followed by a request to skip one topic and then stop | Skips the topic; stops immediately; treats neither choice as failure; writes no artifact |
| Neighbor routing | Fixed prompts for an ambiguous feature direction, a falsifiable contract, an implementation sequence, an architectural trade-off, broken-behavior diagnosis, local defect review, published pull-request review, completion evidence, and a generic non-interactive code explanation | Routes each prompt to its existing owner; does not activate blind spots |

The protocol also fails if any response invents repository evidence or expands
into a general codebase survey. Scenario inputs and assertions remain fixed
across runs so revisions can be compared against the same behavioral bar.

## Scope

### In Scope

- Optional human comprehension coaching for a specific proposed or implemented
  code change.
- A pre-implementation scope mode and a post-implementation quiz mode that can be
  invoked independently.
- Live-repository grounding, calibrated uncertainty, adaptive conversational
  depth, evidence-backed teaching, and a concise closing recap.
- Explicit routing boundaries and evaluations that distinguish comprehension
  from specification, planning, debugging, review, and verification.
- Harness-agnostic guidance suitable for repositories with different languages,
  layouts, and version-control workflows.

### Out of Scope

- Exhaustive codebase, monorepo, organization, or dependency maps.
- A replacement for agent reconnaissance, architecture decisions,
  specification, implementation planning, debugging, code review, test strategy,
  or completion verification.
- Automatic invocation from hooks or mandatory checkpoints in commit, push,
  pull-request, or merge workflows.
- Numeric scoring, pass/fail assessment, certification, merge gating, or judging
  the user for incomplete answers.
- Inferring implementation correctness from the user's comprehension.
- Persistent learning profiles, spaced-repetition systems, or automatic storage
  of quiz results.
- Durable repository documentation unless the user asks for it explicitly.

## Assumptions And Constraints

- The harness supports multi-turn chat in which the workflow can ask one question
  and wait for the user's response.
- Scope mode has access to the relevant repository or user-supplied source
  material; quiz mode has access to an identifiable implemented change. Missing
  access is reported and narrowed, not hidden.
- The user retains authority over whether and when to run the workflow and over
  any eventual merge decision.
- Quiz depth adapts to change risk, size, and the user's requested depth rather
  than enforcing a fixed question count. Without a preference, the workflow
  proposes a bounded default topic set and finishes when it is covered.
- The workflow is advisory and non-gating even when it reveals a gap in the
  user's mental model.
- Evidence and explanations must remain concise enough that paying down
  comprehension debt does not create a second exhaustive review ritual.

## Open Questions

None. All decisions affecting this contract's scope, success criteria, and
verification are settled. Command names, resource layout, and exact authoring
mechanisms belong to planning.

## Handoff

1. Hand off to `write-plan` to choose the implementation and verification
   sequence against this contract.
2. Review this contract with a critique subagent before sequencing.
3. Return to this spec if implementation would make comprehension mandatory,
   scored, correctness-bearing, or broader than a specific change.
