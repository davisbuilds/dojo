# Seam Selection — Map Before You Cut

A plan fails when it prescribes a heavy mechanism up front instead of finding the
thinnest cut that makes the contract's end-state true. This is the discipline that
prevents it: **trace the ground, pick the seam, verify, then prescribe.**

## The Checklist

For any task touching existing or coupled code:

1. **Trace the data/call path.** Start from the entry point named in the contract
   and follow it: who calls this, what state flows in and out, where the observable
   behavior is actually produced. Read the code — do not infer from names.
2. **Locate the seam.** The seam is the smallest place a change makes the
   contract's end-state true. Prefer the cut that touches the fewest call sites,
   preserves existing invariants, and is provable with a deterministic check.
3. **Compare against the obvious-but-heavy option.** The first mechanism that comes
   to mind (a new subsystem, a broad refactor, a new dependency) is usually not the
   thinnest seam. Justify why the chosen seam is smaller and still sufficient.
4. **Record `Assumptions Verified`.** Per existing-code task, write down what you
   confirmed in the exact file and symbol being cut: `file:line`, the observed
   behavior, the invariant you are relying on. These are facts you checked, not
   hopes. A different file can provide `Research Context` about a shape or prior
   art, but it does not prove the target seam exists.
5. **Resolve what is knowable now.** If a grep/read can answer a question, answer
   it before writing the step. Conditional discovery ("if the fetch already
   exists") is a plan that still needs mapping. Reserve Risks And Mitigations for
   irreducible future uncertainty, with an observable signal and mitigation.
6. **Then prescribe steps.** Because the steps are grounded in (1)–(5), they are
   prescriptive — not hypotheses to be discovered during execution. The acceptance
   gate is the contract's end-state (`Done When`), so a cleaner realization than
   first imagined is allowed as long as it still satisfies the contract.

## Verify-First, Then Prescribe

A grounded step reads like: "In `auth/session.py:142`, `refresh()` already
re-reads the token store, so route the new expiry check through it (verified: it
is the single call site for renewal)."

An ungrounded step reads like: "Add a new token-refresh manager that wraps the
session layer." — a mechanism chosen before tracing the path. If you cannot yet
name the seam from the code, the task is not ready to prescribe; trace first.

## Exact Target Evidence

For a task that modifies `parser.py`, an importer that happens to describe the
desired fields is not sufficient `Assumptions Verified`. Read `parser.py` and
cite the symbol or branch that the task changes. Keep the importer citation only
as `Research Context` if it still helps explain the data shape.

Create-only tasks are different: there is no target file to verify yet. Do not
invent a citation. Verify the direct owner or consumer when one exists, and label
any cross-file precedent as research context.

## Verify Test Discovery

When a task adds or changes tests, confirm two distinct facts before prescribing:

1. The runner's configuration discovers the proposed test path.
2. A literal command runs that test file or exact selector.

The full suite is still the regression gate; neither fact follows automatically
from the other.

## Worked Example (anonymized)

A trace-quality reframe was planned as: *"build a scoring subsystem that ingests
traces and emits a quality grade."* That is a mechanism, picked before mapping.

Mapping the path showed the traces already flowed through a single normalization
function before storage. The thinnest seam was a derived field computed at that
existing choke point — no new subsystem, one call site, provable with a single
query. Same end-state; a fraction of the blast radius.

The failure mode the checklist prevents: **prescribing the heavy mechanism up
front instead of stating the end-state and letting the seam be chosen.**
