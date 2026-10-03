# Skills and delegated authority

A skill is instructions and possibly executable resources distributed into an
agent's context. Loading it can influence decisions; it does not necessarily
change OS permissions. Its effective reach depends on the harness, executing
identity, installed tools, inherited credentials, and the user's delegated task.

Follow relevant paths rather than scoring file properties:

- **Instruction influence:** entry-point prose, examples, remote references,
  command wrappers, or tool output redirect the agent beyond the task or attempt
  to override trusted constraints. Markdown formatting does not confer trust.
- **Execution and supply chain:** helpers, package hooks, downloaded code, native
  binaries, and dependencies run with the invoking identity. A source-only skill
  can still fetch an executable; a binary is an inspection limitation, not proof
  of malice.
- **Data and effects:** scripts or induced tool calls read sensitive information,
  select recipients, mutate unrelated projects, or forward credentials. Intent,
  destination control, and user authorization distinguish useful capabilities
  from violations.
- **Persistence and later authority:** hooks, shared settings, memories, startup
  files, and writable service scripts can affect future sessions or more
  privileged processes. Check the downstream consumer, not just the write itself.

A safe-use recommendation is conditional on the inspected revision and environment.
Declared `allowed-tools` may be ignored, interpreted differently, or supplemented
by harness defaults. A reviewer agent sharing the same data and credentials is
not a new security boundary. Unknowns about execution permissions remain unknown
until the relevant interface/configuration or a safe controlled probe resolves them.

Static checks can locate suspicious syntax and inventory blind spots. They cannot
establish author intent, exhaustive dependency safety, effective containment, or
absence of a path assembled across multiple files, tools, and agents.
