# Interpreting and repairing findings

Preserve the distinction between an indicator and a demonstrated boundary failure.

| Observation | Investigate before recommending a change |
| --- | --- |
| Override or jailbreak language | Is it an active instruction, an attack fixture, a quoted example, or protective guidance? What would the receiving agent actually load? |
| Credential-like string | Real secret, synthetic fixture, or placeholder? Report the location without reproducing the value. A real exposure may need revocation beyond deleting the string. |
| Broad tool declaration | Is the capability needed for the task, what does this harness enforce, and can consequential operations be scoped by trusted code? |
| Config, hook, or memory edits | Is this the intended feature, already authorized, and limited to the right owner? Can the edit affect future or privileged execution? |
| Dynamic execution or shell use | Who controls the input, what constraints survive to execution, and which identity performs it? An argument list still permits option injection if untrusted options are accepted. |
| Network access | What leaves the process, who controls the destination, and are credentials forwarded? Ordinary downloads and exfiltration are different claims. |
| Binary, link, unreadable file, remote dependency | What remains uninspected, and does that gap affect the recommendation? Investigate provenance or isolation as appropriate; do not convert a skipped check into a clean result. |

Repair the demonstrated behavior while preserving authorized use. Removing a
keyword, fencing a paragraph, or splitting code across files is not evidence of
reduced authority. Where the intended behavior is itself ambiguous, state the
unresolved decision. Existing approval to implement a repair remains valid.

Use focused tests or controlled probes for material changes. For code-specific
investigation, consult the relevant `secure-code` guidance without inheriting a
second audit or mandatory report.
