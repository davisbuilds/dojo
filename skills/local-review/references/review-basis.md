# Review Basis and Native Harness Behavior

The target is precise, useful defect detection. Prompt similarity, structural
validation, and a clean review do not establish parity with any hosted reviewer.

## Public Codex source inspected

Inspected 2026-10-02 at upstream commit
`0462dcc062b822bb8fff16cc31ce6eeab69823b9` (2026-09-29):

- [Review rubric](https://github.com/openai/codex/blob/0462dcc062b822bb8fff16cc31ce6eeab69823b9/codex-rs/prompts/templates/review/rubric.md):
  actionable introduced defects, demonstrated affected paths, proportionate
  rigor, concise comments, priority labels, and small diff anchors.
- [Review task](https://github.com/openai/codex/blob/0462dcc062b822bb8fff16cc31ce6eeab69823b9/codex-rs/core/src/tasks/review.rs):
  a one-shot reviewer conversation with the dedicated rubric as base instructions,
  no initial parent history, no approval requests, and collaboration disabled;
  returned JSON is parsed into review findings for the parent.
- [Review context](https://github.com/openai/codex/blob/0462dcc062b822bb8fff16cc31ce6eeab69823b9/codex-rs/core/src/session/review.rs):
  selects configured `review_model` or the parent's model, resolves compatible
  reasoning settings, and disables web search for the review.
- [Sample review-agent skill](https://github.com/openai/codex/blob/0462dcc062b822bb8fff16cc31ce6eeab69823b9/codex-rs/skills/src/assets/samples/review-agent/SKILL.md):
  portable defect-first guidance with concise prose findings.

These are versioned source observations, not verification of a running harness,
its current configuration, or the GitHub-hosted Codex review service. The sample
skill and the native review task are distinct surfaces. Approval policy alone
is not a read-only filesystem guarantee; inspect the actual permission profile.

## What Dojo carries forward

Keep the threshold for a worthwhile finding, investigation of affected consumers,
and comment clarity. Add explicit checks for parallel contracts and optional
failure/type lenses. Preserve scoped project instructions and safe probes.

Do not require Codex's JSON schema when no consumer parses it, numerical
confidence, or a blanket correctness verdict. An inline reviewer cannot discard
its implementation history by being told to think independently. When the user
requests an available native review, use that interface; otherwise apply this
portable guidance within the authorized review. Do not pretend that consulting
a skill invoked the native reviewer, or require two overlapping passes by default.

## Assessing quality later

Use held-out changes with known outcomes and plausible clean controls. Give the
reviewer the target and applicable instructions without seeding expected defects.
Compare accepted findings, missed material defects, false positives, actionable
locations, and cost under comparable model/harness conditions. Check findings
against source and outcomes rather than treating a cloud comment as ground truth.
The accompanying replay scenarios document intended behavior; they are not a
completed comparison or proof that this skill matches hosted review quality.
