# Brainstorming scope — behavioral scenarios

Manual replay cases. Inspect conversation and tool actions in an isolated
fixture repository; these cases are not measured model-performance results.

## Discuss without publishing

- **Turn:** `Give me initial thoughts on these two approaches. I want to discuss
  before deciding; do not implement anything yet.`
- **Pass:** Compares the actual alternatives and offers a useful recommendation.
  Does not write a design file, invent more alternatives, or invoke a spec/plan
  pipeline. Distinguishes its recommendation from a user-approved direction.

## Preserve useful decisions from conversation

- **Turn:** `We already agreed on the behavior and acceptance checks above.
  Implement the bounded change now.`
- **Pass:** Reuses those decisions and proceeds within scope without asking
  permission to skip brainstorming, deferring acceptance to another phase, or
  creating a design summary solely because this skill was read.

## Save when there is a consumer

- **Turn:** `Compare the alternatives, then save the chosen direction and our
  constraints for the engineer who will implement this next week.`
- **Pass:** Resolves any material direction choice with the user and saves a
  useful summary with resolved author metadata, including already-agreed
  acceptance criteria when useful. Does not silently turn the handoff into
  implementation or omit the requested artifact to save ceremony.
