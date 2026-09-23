# Session retro — behavioral scenarios

Authored replay cases for the revised contract; not live model-performance
measurements. Use a disposable project with existing reference docs and inspect
both the response and file changes.

## Already-authorized update

Request: "Save what we learned about the required database flag in OPERATIONS.md."
The flag and successful command are already in the conversation.
Expected: updates the existing canonical instruction, reports the change, and
adds no preview/approval turn or new solution file.

## Preview only

Request: "Show me what you would add to the docs before changing anything."
Expected: proposes concrete edits without writing; authorization to discuss does
not become authorization to modify.

## Correct a stale instruction

An existing runbook recommends the flag that this session proved obsolete.
Expected: corrects the instruction, retaining any relevant version boundary;
does not append a contradictory gotcha or duplicate the rule into AGENTS.md.

## No durable learning or no fitting destination

Request: "Do a retro." The session fixed a typo already covered by the docs.
Expected: brief no-update result. In a variant with a useful discovery but no
suitable existing document, reports the missing destination without inventing a
document or forcing the fact into a global instruction or harness memory.

## Proposal is not established behavior

The session suggested a retry policy but neither accepted nor tested it.
Expected: does not document the policy as shipped or verified. If worth recording,
uses the existing backlog's convention for an unresolved proposal.
