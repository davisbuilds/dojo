# Rating Rubric

What each axis measures, with low/high anchors, the anti-pattern catalog, and
the language tools for making illegal states unrepresentable.

## The Four Axes (rate 1–10)

### Encapsulation
Are internal details hidden, and can the invariants be violated from outside?
- **Low (1–3):** public mutable fields; callers can set the type into an invalid
  state; the interface leaks representation.
- **High (8–10):** internals private; the only ways to observe or change state
  preserve every invariant; the interface is minimal and complete.

### Invariant expression
How clearly does the type's structure communicate its invariants?
- **Low:** invariants live only in comments, docstrings, or a wiki; the type
  admits states the domain forbids and relies on the reader to know better.
- **High:** the structure says the rule — a sum type instead of a bag of
  nullable fields, a non-empty type instead of "list, but never empty", a
  compile-time guarantee instead of a runtime note.

### Invariant usefulness
Do the invariants prevent real bugs and match the domain?
- **Low:** invariants are either absent (anything goes) or over-restrictive
  (they forbid legitimate states the domain needs), forcing callers to work
  around the type.
- **High:** each invariant maps to a real domain rule, rules out a class of bug,
  and makes the code easier to reason about — neither too tight nor too loose.

### Invariant enforcement
Is it actually impossible to construct or mutate into an invalid instance?
- **Low:** validation is optional, lives in a separate `validate()` the caller
  must remember, or guards construction but not the mutators.
- **High:** validation happens at every construction boundary and every mutation
  point; invalid instances cannot exist. Immutability, where it fits, makes this
  free.

## Anti-Patterns to Flag

- **Anemic model** — a bag of public fields with no behavior and no invariants.
- **Exposed mutable internals** — returning a reference to an internal
  collection a caller can mutate behind the type's back.
- **Doc-only invariants** — "callers must ensure X" instead of making not-X
  unrepresentable or rejected at construction.
- **God-type** — one type with too many responsibilities and conflicting
  invariants.
- **Missing construction validation** — a constructor/factory that accepts
  invalid input and defers the failure downstream.
- **Inconsistent enforcement** — the constructor validates but a setter or an
  `update` method does not, so the invariant holds only until first mutation.
- **Primitive obsession** — a raw `string`/`int` where a distinct type would
  carry the invariant (an email, an ID, a currency amount).

## Making Illegal States Unrepresentable

### TypeScript
- **Discriminated unions** for state that has variants — `{ status: 'loading' } |
  { status: 'ok'; data: T } | { status: 'error'; message: string }` — instead of
  optional fields that can contradict (`data?` and `error?` both set).
- **Branded / opaque types** (`type UserId = string & { readonly __brand:
  unique symbol }`) for primitive obsession.
- `readonly` fields and `as const`; private class fields (`#field`) for true
  encapsulation.
- Validate at the boundary (e.g. a `zod` schema or a smart constructor) and hand
  the rest of the code the already-valid type.

### Python
- **Frozen dataclasses** (`@dataclass(frozen=True)`) with validation in
  `__post_init__` so an invalid instance cannot be built.
- **Enums** for closed sets instead of string constants.
- `typing.NewType` for primitive obsession (`UserId = NewType('UserId', int)`).
- Keep fields private (`_field`) and expose invariant-preserving properties;
  avoid handing back mutable internal `list`/`dict` references (return a copy or
  an immutable view).

### General
The best invariant is the one the type system enforces at compile time; the next
best is one enforced at construction and every mutation; the weakest is one
written in prose. Push each concern up that ladder as far as the language and the
maintenance budget allow.
