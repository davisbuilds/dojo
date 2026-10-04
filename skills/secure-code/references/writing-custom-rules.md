# Custom rules that earn their maintenance

Add a rule when a recurring, checkable project property benefits from automation.
Keep project-specific rules and fixtures in the owning repository. Do not edit
installed global skills during an ordinary investigation.

Use [Semgrep's rule syntax](https://semgrep.dev/docs/writing-rules/rule-syntax)
and [rule testing](https://semgrep.dev/docs/writing-rules/testing-rules) for the
installed engine version. Test the real query: positive cases must match, benign
lookalikes must not, and known scope limitations should be explicit. In Semgrep,
`patterns` means conjunction; use `pattern-either` for alternatives such as
`eval(...)` and `exec(...)`.

Rule messages should name the observed property and what still needs checking.
Do not assert dataflow, attacker control, or exploitability that the rule does
not establish. Use taint/dataflow support where appropriate, and state engine or
language limitations. A `fix` field is executable replacement text, not a place
for prose remediation advice; omit it unless the transformation is safe and tested.

Keep a reproducible local rule file/version and meaningful positive/negative
fixtures. Registry names can resolve differently later. Passing a rule's tests
shows its behavior on those cases, not comprehensive security coverage.
