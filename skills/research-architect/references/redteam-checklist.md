# Stage-5 Red-Team Checklist

The mandate for the stage-5 critique subagent. Spawn a **fresh** subagent (no
drafting-stage context) and give it the assembled prompt plus this checklist
verbatim. Its job is adversarial simulation, not generic critique.

## The mandate (paste into the subagent prompt)

> Role-play a competent but lazy executor running this research prompt. You
> want to finish fast and look compliant. Report, in this order:
>
> 1. **Letter-vs-spirit gaps** — where you could satisfy the literal
>    requirement while missing its point. Quote the instruction; describe the
>    lazy-but-compliant output.
> 2. **Silent skips** — instructions you would quietly ignore because they are
>    expensive, vague, or unverifiable. Say why each is skippable in practice.
> 3. **Conflicts** — pairs of instructions that cannot both be followed, or
>    where following one weakens the other.
> 4. **Deletions (mandatory: at least three)** — instructions that are dead
>    weight: restatements of general good practice, requirements no verifier
>    could check from the report text, or duplicates of what another block
>    already enforces. Name them for deletion even if the prompt is good.
> 5. **Missing do-nots** — topic-specific failure modes a lazy executor would
>    hit that the do-not list does not cover. Propose each as a one-line
>    do-not item.
>
> Do not praise the prompt. Do not suggest additions except in item 5. Your
> output is consumed by a drafting session that will edit the prompt directly.

## Why the deletion mandate is non-negotiable

Iterated prompt-critique loops are additive by disposition: every round adds
hedges and constraints, and long prompts demonstrably drop instructions —
every instruction competes with every other. Requiring three deletions per
round is the structural counterweight. If the red-teamer genuinely cannot find
three, that is a finding worth recording in `postmortems.md` — it has not
happened yet.

## Processing the findings (drafting session)

- Fold items 1–3 into rewrites: make the requirement checkable or delete it.
- Apply item 4 deletions unless a deletion would remove the only enforcement
  of a stage-0/1 priority — in that case record why it stays.
- Add item-5 do-nots only if they are concrete errors for THIS topic; generic
  virtue goes nowhere.
- Re-run `scripts/lint_prompt.py` after edits. One round is usually enough; a
  second round only if round one surfaced a conflict (item 3).
