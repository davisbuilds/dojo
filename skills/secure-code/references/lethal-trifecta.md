# Agent authority boundaries

The [lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
is a threat-model prompt: an agent can access private data, consume adversarial
content, and communicate externally. It is not a static signature or a claim
that ordinary request handling is prompt injection.

Follow an actual delegation path. For example: a fetched document supplies
instructions, the model treats them as authority, and a tool call sends a private
record to an attacker-controlled destination. These steps may span repositories,
services, turns, or agents. Conversely, an application can mention all three
capabilities without making that path available to an attacker.

Useful questions, selected for the system:

- Which content can the adversary influence, and can it become instructions or
  tool arguments? Consider retrieved files, tool results, memory, and handoffs.
- What data and actions can the *executing identity* reach? Check filesystem and
  process credentials, shared stores, writable service scripts, network routes,
  and downstream services; a model's declared tool list may understate authority.
- Which destinations, recipients, tenants, and objects are bound by trusted code?
  Are authorization and approvals attached to the exact action and inputs, or
  can the agent change them afterward?
- Can a low-trust result trigger a more privileged agent or workflow? Does that
  receiver independently enforce scope and provenance?
- What observation would distinguish a real denial from an unavailable tool,
  broken probe, empty result, or a different runtime than production?

Prefer controls that actually constrain the path: scoped identities, constrained
tool interfaces, destination restrictions, enforceable data boundaries, and human
approval for consequential actions where appropriate. Prompt instructions and
reviewer agents may help interpretation; they are not deterministic authorization
boundaries. Splitting functions or adding a second agent with the same credentials
does not by itself reduce authority.

Probe with synthetic data and controlled destinations when authorized. Report the
boundary tested and remaining uncertainty; do not require real exfiltration to
substantiate a credible path. Improving observability can aid investigation but
does not itself prevent the action.
