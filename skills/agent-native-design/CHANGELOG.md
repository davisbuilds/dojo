# Changelog

## 3.0.0 - 2026-10-02

- Rename `agent-native-architecture` to `agent-native-design`. Update explicit
  invocations and installed copies to the new name; the old entrypoint and
  reference paths are removed rather than shipped as a second skill.
- Distinguish software agents can use, systems that delegate work, and products
  with agents as primary consumers. Apply relevant design lenses within the
  requested task instead of requiring an architecture plan and checklist.
- Replace the five overlapping references with three focused references on
  agent-facing interfaces, delegated work, and product/human agency.
- Remove universal UI parity, CRUD completeness, primitive-only tools, and
  prompt-only development mandates. Preserve meaningful composition and
  discovery while keeping enforceable invariants in the executing system.
- Add outcome evidence, honest measurement scope, recoverable execution,
  cross-agent authority/context boundaries, and control over ongoing work.
  Keep platform capabilities and product value as questions to establish.

## 2.0.0 - 2026-07-31

- **Restructure for progressive disclosure.** The skill owned 14 reference files
  (216 KB) and still expounded all five core principles and the full
  anti-pattern catalogue inline. `Core Principles` (135 lines) and
  `Anti-Patterns` (86 lines) move to `references/core-principles.md` and
  `references/anti-patterns.md`; SKILL.md keeps a one-line statement of each
  principle and a pointer.
- Merge the intake menu and the routing table, which enumerated the same 13
  topics twice, into a single Routing table.
- Strip 258 XML section tags (`<why_now>`, `<core_principles>`, ...) from
  SKILL.md and all 14 reference files. No other skill in the catalog uses them --
  they came in with the compound-engineering-plugin import -- and the markdown
  headings underneath already carry the structure. The restructure above had
  also left several unbalanced, so they were actively wrong as well as
  inconsistent.
- **Cut 11 of 14 reference files** (~4,800 lines). Kept `core-principles.md`,
  `anti-patterns.md`, `action-parity-discipline.md`, `mcp-tool-design.md`, and
  `refactoring-to-prompt-native.md` — the material that states a checkable
  practice. Dropped the iOS/mobile patterns, self-modification, shared-workspace
  theory, product implications, testing, system-prompt design, architecture
  patterns, context injection, files-as-interface, and domain-tool graduation:
  third-party material tied to one stack, never read once.
- Remove the skill's `README.md`, which duplicated the reference index a third
  time. `SKILL.md` is the entrypoint.
- 448 -> 203 lines and 256 KB -> 76 KB, below the 250-line
  progressive-disclosure threshold added to the contract in skill-evals 1.4.0.

MAJOR because content moved between files: anything that linked to a heading
inside SKILL.md for the principles or anti-patterns now needs the reference path.
