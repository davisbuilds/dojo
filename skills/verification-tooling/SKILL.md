---
name: verification-tooling
description: Build and maintain repeatable repository verification tooling. Use when a project lacks a usable verification environment, important consumer paths cannot be exercised, setup or fixtures have drifted, or verification scripts and runbooks need repair or an audit.
skill-type: workflow
license: MIT; see LICENSE.txt
version: 1.0.0
---

# Verification Tooling

Leave a verification path that another agent can discover, run, and maintain:
representative state, a usable target, real interaction, observable outcomes,
and cleanup that preserves the evidence. Improve the project's existing tools
and references before adding another runner or document.

## Scope

Create, repair, or maintain the machinery needed to verify the behavior in scope.
Ordinary test execution needs the repo's commands; choosing assertions belongs
to `test-strategy`, and assessing completion evidence to `verify-before-complete`.
Consult those skills only for an unresolved decision; their workflows and
deliverables do not become requirements of this one.

An audit can end with findings. Follow existing authorization for edits, external
services, credentials, and effects. Prefer disposable instances and data; do not
reset a user's environment, provision paid services, or deploy merely to make
verification possible. Report any prerequisite that cannot be satisfied within
the task's authority.

## Establish the consumer path

Read the repo's guidance and existing setup, tests, scripts, and operations docs.
Identify the interface the consumer actually uses: a UI, command, API, library,
worker, or combination. Trace the entry point through the relevant effects;
choose a bounded behavior that exposes the current gap. Preserve working tooling
and meaningful checks, including intentionally manual steps.

Locate the build/runtime, dependencies, representative data, authentication, and
platform needed to exercise that path. A stand-in is useful only for the
semantics it preserves; name what still requires the intended environment.
Resolve source-visible prerequisites yourself and ask only for missing decisions
or access. A broken baseline is a finding to classify, not a reason to invent
instructions that have never worked.

## Make the path executable

Use existing entry points where practical. Add helpers for repeated or fragile
mechanics, with discoverable invocations, actionable failures, and meaningful
exit status. Keep the following properties together in the owning repo:

- **Setup and state.** Reach a representative starting state from documented
  prerequisites, including build/install steps, migrations, fixtures, and test
  identities. Isolate mutable data, ports, profiles, and resources; where an
  instance cannot be shared safely, give it one driver. Do not depend on residue
  from the author's session or silently replace an unavailable dependency.
- **Readiness and identity.** Establish that this is the intended build and
  instance, that the run owns what it may later stop, and that required behavior
  is usable. A process answering or a database accepting connections does not
  establish completed initialization or valid authentication. Provide a cheap
  diagnostic check; after a surprising failure, re-establish readiness or reset
  owned state before continuing.
- **Interaction and observation.** Drive the consumer interface with stable
  handles. Check the action, resulting state, and consequential side effects;
  internal setters or test-only shortcuts cannot prove the path they bypass.
  Use controlled substitutes where necessary and state the remaining boundary.
  Verify the effective effects of a dry-run/test mode before relying on its name.
- **Evidence and cleanup.** Name where bounded, relevant evidence is retained
  and associate it with the exercised path and build/configuration. Avoid
  credentials or sensitive fixture data. Stop only resources the run owns and
  remove its scratch state on failures as well as success. Store evidence outside
  disposable state so teardown does not erase the result.

Make important behaviors discoverable from existing repo guidance. A compact
map should connect each covered behavior to its entry point, prerequisites,
command or interaction, and observable expected outcome. Include necessary
negative or recovery cases and known limits; link tests and source rather than
copying their mechanics. Grow coverage with the task instead of requiring a
complete feature census. Use `references/verification-map.md` if an example
would help. A project-local skill is optional; an existing testing reference and
runnable scripts may already provide the right interface.

## Prove and maintain the machinery

Execute new or changed instructions from the documented starting conditions:
prepare, establish readiness, drive the affected path, inspect results, and
clean up. Confirm retained evidence remains readable afterward and owned
resources are gone. Clean up failed attempts too. Use an applicable known
positive or failure control when a check could pass without reaching the target.
Writing instructions or passing lint alone does not establish this capability.

For maintenance, inspect the affected consumer paths and recent changes to
builds, startup, data, auth, selectors, or contracts. Distinguish:

- **Tooling or documentation drift:** repair stale setup, commands, fixtures,
  checks, or maps within scope, then exercise the repaired path.
- **Product defect:** preserve the intended expectation and report the observed
  failure. Repair product code only when the task authorizes it; do not weaken
  the check or rewrite the map to make a regression pass.
- **Unavailable prerequisite:** record the attempted path and missing condition;
  that behavior remains unverified. An unreachable feature is not a passing one.

Reuse evidence when its code, environment, and configuration still apply. Broaden
coverage when changed inputs or failures justify it; whole-project audits and
scheduled maintenance need an actual task, not an automatic cadence.

## Handoff

Point to the runnable entry points and their owning reference. State what was
exercised, where its evidence is, and what remains unverified. Distinguish working
machinery for the sampled paths from complete product coverage. Keep dated run
results separate from maintained instructions; a separate report or prescribed
file layout is needed only when it has a consumer.

## Resources

- `references/verification-map.md` — optional example of a compact behavior map.
- `evals/behavioral-scenarios.md` — authoring replay cases, not measured outcomes.
- `evals/trigger-cases.json` — lexical discovery checks, not harness invocation proof.
