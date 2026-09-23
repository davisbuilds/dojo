# Publication Conventions

Repository guidance and established history take precedence. If none exists,
use a short descriptive task branch (for example, `fix/cart-null-pointer`) and
an imperative commit subject. Add rationale when the diff does not explain why.
Use issue-closing footers only when the change actually resolves the issue.

Stage the intended scope explicitly. Keep unrelated staged/unstaged work intact;
inspect an unexpectedly broad index instead of blindly committing it. Generated
assets and binaries may be intentional when the repository tracks them.

Review outgoing history as well as the final diff for private data and actual
credentials. A filename alone is not a reliable secret detector. If a credential
is found in history, a new removal commit does not erase it. Avoid publishing
that history; arrange appropriate credential revocation and history remediation
under the applicable authorization, without printing secret values.
