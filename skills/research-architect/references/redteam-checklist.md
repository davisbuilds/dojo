# Focused prompt critique

Use when a prompt has consequential ambiguity, competing goals, uncertain source
access, or a history of weak results. A separate reviewer can help, but the
critique may be inline and need not produce its own artifact.

Read the prompt as an executor who has no surrounding conversation:

- Could a polished answer satisfy its wording while missing the user's real
  question? Identify the concrete mismatch.
- Does a premise ask the executor to confirm an unverified statistic, forecast,
  or user belief? Distinguish a research lead from a fact to assume.
- Does the requested breadth leave room to investigate the central uncertainty?
  Identify a specific lower-priority question to defer if needed.
- Are required sources or attachments actually available on the chosen surface?
  If access is untested, retain the uncertainty instead of inventing a fallback
  that cannot answer the question.
- Do formatting or process demands serve an actual consumer? Remove or revise
  redundant and conflicting instructions without a deletion quota.
- Is there a useful output if the evidence is weak, the premise is wrong, or no
  action is justified?

Return only consequential improvements, with the failure each addresses. An
already focused prompt may need no changes. Do not iterate critiques to optimize
wording indefinitely; a real output is better evidence of whether it worked.
