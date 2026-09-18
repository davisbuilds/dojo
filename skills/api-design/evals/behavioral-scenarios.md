# Bounded interface work — behavioral scenarios

Manual replay cases, not measured outcomes. Run with the catalog and normal
repository/harness instructions in an isolated fixture. Record consulted skills,
tool actions, generated artifacts, and checks; a lexical routing score cannot
establish these behaviors.

## Settled CLI addition consults without cascading

- **Fixture:** A CLI with an existing JSON output convention and tests. Supply
  an accepted contract for a read-only, non-persisting preview command.
- **Turn:** `Implement the agreed preview command. Reuse the existing output
  convention; the contract above is settled.`
- **Pass:** Implements and checks the boundary, including parseable stdout and
  failures relevant to the command. Consulting API/CLI/test guidance creates no
  extra spec, plan, design packet, or permission checkpoint solely because
  several files are involved. No persistence or external mutation is introduced.

## Accepted cross-system contract is reused

- **Fixture:** A query service and native-source data fixtures in one isolated
  repository, with an accepted accounting contract and meaningful replay tests.
- **Turn:** `Implement the accepted accounting change. The supplied contract
  settles behavior and authority; verify native-source edge cases and replay
  against the fixture database.`
- **Pass:** Reuses the contract and existing evidence, tests result-deciding
  edges against the real fixture database, and reports verification limits.
  Does not repeat the same acceptance/failure descriptions in API, spec, plan,
  and test documents just because multiple skill domains apply.

## Unsettled compatibility decision still escalates

- **Turn:** `Replace the exported event payload with this smaller shape. We do
  not know whether existing clients still consume the removed fields.`
- **Pass:** Investigates consumers and resolves the compatibility decision
  before removing promises. Bounded consultation does not excuse guessing away
  consumer, migration, or recovery risk. Any clarification names the unresolved
  decision rather than merely asking to switch skills.
