---
name: write-plan
description: 'Sequence the build: turn a settled target (a `write-spec` contract, a ticket, or a clear request) into an execution plan — task breakdown, files, ordered steps, seam selection, and verification commands. Use when WHAT is already decided and you need HOW: the file-level, dependency-ordered steps to implement it. If the target is not yet falsifiable, route back to `write-spec`.'
skill-type: workflow
version: 2.4.0
---

# Write Plan

Turn a settled target into an execution plan a zero-context engineer can follow:
task breakdown, exact files, ordered steps, and verification commands. The plan is
held to a contract — its acceptance gate is the spec's end-state, not the steps it
happens to list.

## When To Use

Use this skill when:
- WHAT is already decided (a `write-spec` contract exists, or the request is clear)
  and you need HOW
- the work spans multiple files or phases and needs ordered, verifiable steps
- explicit verification gates are needed before coding

Skip this skill when:
- the target is not yet falsifiable → route back to `write-spec` first
- the change is a tiny mechanical edit
- requirements are still ambiguous → `brainstorming` first

## Input

Prefer to plan against a contract:
- If `docs/specs/YYYY-MM-DD-<topic>-spec.md` exists, plan against it and reuse its
  topic slug. `## Goal` restates/links that contract; every `Done When` traces to
  the contract's end-state.
- Before planning from a spec, confirm its open questions do not change scope,
  success criteria, or verification. Route such questions back to `write-spec`;
  a plan must not silently decide the contract.
- If no contract exists and the work is non-trivial or touches coupled code, route
  back to `write-spec` to pin the target first.
- For a small, clear, self-contained request, proceed directly.

## Start Behavior

Start with:
`I'm using the write-plan skill to sequence the build.`

If key context is missing, ask focused questions before writing:
- the target/contract and its acceptance criteria
- constraints and non-goals
- affected files or systems (if known)

<!-- INCLUDE: risk-profile-gate -->
<!-- AUTO-GENERATED from skills/_fragments/risk-profile-gate.md — do not edit -->
## Risk Profile Gate

Classify each new artifact before drafting:

- `routine` — the default; keep the normal template and validation path lean.
- `high` — use when credentials or privilege separation, remote/destructive
  effects, cross-system state agreement, retries/concurrency/queues, executable
  untrusted input, external policy decisions, or persisted-state migration can
  make a plausible-looking artifact unsafe or infeasible.

Record `risk_profile: routine|high` and `readiness: draft|ready` separately from
delivery `status`. Legacy artifacts without these fields remain routine/draft.
For `high`, load this skill's high-risk reference and addendum; do not add those
sections to routine work. Reclassify when repository evidence reveals a trigger.
<!-- /INCLUDE: risk-profile-gate -->

## Output Path

Save the plan to:
`docs/plans/YYYY-MM-DD-<topic>-plan.md`

## Output Contract

Every plan must include YAML frontmatter and the required sections below.

### Required Frontmatter

```yaml
---
date: YYYY-MM-DD
author: <agent>
topic: <kebab-case-topic>
stage: plan
status: draft
source: conversation
risk_profile: routine
readiness: draft
---
```

Replace `<agent>` with the producing agent's most specific available model or
harness identifier (for example, `author: gpt-5.6-sol`). Attribute the agent
that writes the plan, not the user or a later reviewer, and never leave the
placeholder unresolved. Legacy plans without `author` remain valid.

`status:` is born `draft` and follows the lifecycle `draft → in-progress →
complete` (terminal synonyms: `shipped`, `implemented`, `superseded`). Update it
honestly as the work lands so a reader — or any lifecycle tooling — can tell a
live plan from a finished one.

### Required Sections

1. `# <Title> Plan`
2. `## Goal` (restates/links the spec contract)
3. `## Scope`
4. `## Assumptions And Constraints`
5. `## Task Breakdown`
6. `## Risks And Mitigations`
7. `## Verification Matrix`
8. `## Handoff`

Add `## Map Before You Cut` (below) whenever a task touches existing or coupled
code — strongly recommended, and included in the template. Use
`assets/plan-template.md` as the default scaffold.

For `risk_profile: high`, also add a repository-relative `spec:` frontmatter
path, use `assets/high-risk-plan-addendum.md`, and follow
`references/high-risk-readiness.md`. The linked spec must be high-risk and every
contract ID must trace to a task and proof. Do not plan from a high-risk spec
until it has `readiness: ready`.

## Map Before You Cut

Before prescribing steps for any task that touches existing or coupled code, trace
the ground first — do not pick a mechanism blind:

1. **Trace the data/call path** the change rides on (who calls what, what state
   flows where). Read the code; don't assume.
2. **Pick the thinnest seam** that satisfies the contract — the smallest cut that
   makes the end-state true. A cleaner realization than the contract author
   imagined is allowed, as long as `Done When` still equals the contract.
3. **Map the whole defect or property class.** Enumerate sibling sources,
   alternate CLI branches, upstream/downstream stages, error paths, and ported
   implementations that must preserve the same property. Give each a `Done When`
   or an explicit out-of-scope note; do not fix only the focal instance.
4. **Record `**Assumptions Verified**` for each existing-code task** — state the
   claim the step depends on, and the evidence appropriate to *that* claim. For
   in-repo mechanism, that is the exact file and symbol being cut plus the
   observed behavior at that line; a neighboring file may establish data shape,
   but label it `Research Context`. Create-only work needs no invented citation.

   **A citation is the right evidence only for a claim the repository can
   exhibit.** Requiring one everywhere invites citation-as-ritual: a correct line
   reference attached to a claim it does not support reads as verified and is
   not.

5. **Record `**Behavior Measured**` when a step depends on a tool the repo does
   not own** — a shell, multiplexer, sandbox policy, VCS, package manager, or
   vendor CLI. No line in the repository exhibits what that tool does, so the
   artifact is **a command and its observed output**, not a citation. These
   probes are almost always seconds long; the cost of skipping one is a plan step
   built on a plausible guess.

   **Both blocks record dated observations, not facts.** They are written when
   the plan is drafted and consumed days or weeks later, by which time the
   runtime, the vendor, or a sibling task may have moved. Write
   `verified YYYY-MM-DD` beside each entry and re-run the check at the start of
   the task that relies on it. Anything observed from a runtime — a
   version-dependent limit, an output shape, a tool's behavior — also names the
   build it was seen on, because a constant that holds for one release is not
   thereby a constant.
6. **Resolve the current before prescribing.** Grep/read questions that can be
   answered now, then write facts. Do not leave conditional discovery in a step
   (for example, "if X is already wired"). Put only irreducible future
   uncertainty in Risks And Mitigations, with a signal and mitigation.

See `references/seam-selection.md` for the worked checklist and a before/after.

## Task Design Rules

Each task must be independently verifiable and include:
- `### Task N: <name>`
- `**Objective**`
- `**Files**` with exact repository paths
- `**Dependencies**` (or `None`)
- `**Assumptions Verified**` when the task modifies existing code; state the claim
  and evidence appropriate to it — for in-repo mechanism, the exact target
  file/symbol, not a neighboring precedent
- `**Behavior Measured**` when a step depends on a tool the repo does not own;
  a command and its observed output, not a citation
- `**Implementation Steps**` as ordered steps
- `**Verification**` commands with expected signals
- `**Test Discovery Verified**` when the task creates or changes tests; name the
  runner/discovery evidence and the command that runs the literal new test
- `**Done When**` acceptance bullets that trace to the contract and pin a
  meaningful magnitude, floor, rate, or non-degeneracy bound when trivial output
  could otherwise pass

Granularity target:
- one meaningful unit of behavior per task
- usually 10-30 minutes of focused work
- avoid over-fragmented 2-minute steps unless risk demands it

## Verification Requirements

- Include at least one concrete, deterministic verification command per task.
- Include integration or end-to-end verification when applicable.
- Add negative-path verification for risky logic.
- Do not accept bare existence/sign/completion checks such as `> 0`, "not empty",
  or "completes." Pin the smallest meaningful magnitude and prove a non-degenerate
  run when empty or trivial output could pass.
- **Assert each `Done When` bullet against a case you believe is false; if it
  still passes, it is not a criterion** — a bullet that cannot fail describes your
  instrument, not the system. Watch three degenerate forms: an enumeration that
  lists cases instead of stating the invariant they stand for; an `only X does A`
  partition asserted while every case still takes one branch; and an assertion
  over a collection that can be empty (`every declared …`). The validator flags
  the last two as advisories; the enumeration form is yours to catch. See
  `references/seam-selection.md`.
- When a task depends on a tool the repository does not own, record
  `**Behavior Measured**` — the command and its observed output — not an in-repo
  citation. A correct citation attached to a false claim about external behavior
  still reads as verified; the validator advises when a step invokes a known
  external binary without this marker.
- When tests change, prove their discovery before claiming readiness: confirm the
  repository runner includes the new test path, then name a command that runs the
  literal test file (or exact test selector).
- **A capability gate must prove fidelity, not just mechanism.** When an early
  task establishes that some measurement or integration is possible at all,
  passing it shows the mechanism works — not that it observes the thing that
  matters. Require a **paired observation**: the tool's answer beside the same
  quantity taken from the surface a user actually touches, with the gate failing
  on disagreement. Name the entry point the evidence came from; a tool with
  several has no obligation to make them agree, and precision is not fidelity.
- Do not claim plan readiness until verification coverage is explicit.
- For high-risk plans, do not set `readiness: ready` or announce completion until
  deterministic validation passes, adversarial critique findings are revised,
  and a closure critique confirms no blocking finding remains.

If available, apply the mindset from `verify-before-complete` when checking final
plan quality.

## Plan Validation

After writing a plan, run:

```bash
python3 <skill-dir>/scripts/validate_plan.py docs/plans/<filename>.md
```

The validator resolves `spec:` and `Modify:` paths against the target plan's Git
root. Use `--repo-root <path>` for relocated artifacts; outside Git, the default
fallback is the caller's current directory.

Fix all reported issues before handoff.

The validator's routine grounding and test-discovery messages are advisories,
not schema failures. Obvious weak acceptance phrases also remain advisory. For
high-risk plans, conditional structure, linked-spec ID coverage, task references,
modified-file existence, and readiness closure are hard failures. No validator
can determine whether prose claims or commands are true; ground the task and use
semantic critique rather than treating the checker as a substitute for reading
the code.

## Handoff

End with:
`Plan complete and saved to docs/plans/<filename>.md.`

Use that completion line immediately for routine plans after validation. For
high-risk plans, keep `readiness: draft` through deterministic validation,
adversarial critique, revision, and closure critique; use the completion line
only after `readiness: ready` validates.

For high-risk plans, run the required critic described in
`references/high-risk-readiness.md` before handoff. Use a critique subagent when
the harness supports and authorizes one; otherwise run the same critique inline.
For routine plans, critique remains optional and is offered explicitly below.

Then offer:
1. Execute in this session, task by task.
2. **Review the plan with a critique subagent.** If the harness supports subagents
   (e.g. a Task/agent tool), launch one seeded with the plan's path, the spec
   contract, **and** the originating context, instructed to critique the *plan* —
   is the chosen seam the thinnest that satisfies the contract? do existing-code
   tasks cite their exact target file/symbol? are steps prescriptive because they
   are verified, not guesses? are risks irreducible rather than skipped lookups?
   are changed tests actually discovered? — and to propose improvements. Apply or
   discuss before executing. If subagents are unavailable, run the same critique
   inline via `verify-before-complete`.
3. Open a separate execution session, or refine the plan first.

## Command Wrapper

If command files are supported, use `commands/workflows/plan.md` as the canonical
`/workflows:plan` wrapper.

## Resources

- `references/seam-selection.md` — grounded seam selection and test discovery.
- `references/high-risk-readiness.md` — conditional traceability, authority,
  evidence, consumer-closure, stop-gate, and critique protocol.
- `assets/high-risk-plan-addendum.md` — conditional scaffold for high-risk plans;
  do not copy it into routine plans.

## Sibling skills

Pre-execution pipeline: **brainstorm → spec → plan**
(`docs/design/` → `docs/specs/` → `docs/plans/`).

- `write-spec` — upstream. Owns the falsifiable contract (the WHAT). Plan against
  it; route back if the target isn't yet falsifiable.
- `brainstorming` — further upstream. Clarifies WHAT + chosen direction when the
  request is ambiguous.
- `deep-research` — parallel. Use when steps need grounded references (library
  behavior, API contracts, current docs).
- `first-principles` — upstream for plans that hinge on a non-obvious
  architectural decision.
