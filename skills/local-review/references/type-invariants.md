# Type and Invariant Review Lens

Start with a domain rule and the code that relies on it. A type can be a plain
record without being defective. Prefer the smallest enforceable contract that
fits the language, consumers, and maintenance cost.

- What states does a changed type permit, and which do consumers assume cannot
  occur? Trace a reachable construction or transition to the broken assumption.
- Check alternate factories, deserialization, persisted legacy values, setters,
  update helpers, and aliases to mutable collections. Constructor validation
  alone does not establish an invariant after every write.
- Check whether stricter validation rejects legitimate data or breaks existing
  wire/storage consumers. Stronger types are not automatically compatible types.
- Distinguish compile-time promises from runtime enforcement. TypeScript casts,
  brands and readonly modifiers do not validate external input. Python NewType
  supplies static distinctions, not runtime validation; frozen records do not
  automatically freeze nested mutable objects. Private naming is not a security
  boundary. Judge these limits against actual callers, not hostile reflection
  that the project never promised to resist.
- Consider unions, boundary parsing, controlled mutation, or defensive copies
  when they eliminate a demonstrated failure at reasonable cost. Avoid demanding
  branded primitives, class methods, deep immutability, or a new abstraction for
  every data structure.

For example, an update helper that bypasses an established positive-quantity
check can permit a negative inventory allocation. A public mutable field is not
itself a finding unless a reachable write violates a required invariant.

Report concrete illegal states, their entry path, and consumer impact. Use the
main skill's finding threshold; no four-axis score or per-type report is needed.
