# Changelog

## 2.0.0 - 2026-07-31

- **Restructure for progressive disclosure.** The skill owned 14 reference files
  (216 KB) and still expounded all five core principles and the full
  anti-pattern catalogue inline. `Core Principles` (135 lines) and
  `Anti-Patterns` (86 lines) move to `references/core-principles.md` and
  `references/anti-patterns.md`; SKILL.md keeps a one-line statement of each
  principle and a pointer.
- Merge the intake menu and the routing table, which enumerated the same 13
  topics twice, into a single Routing table.
- 448 -> 240 lines, below the 250-line progressive-disclosure threshold added
  to the contract in skill-evals 1.4.0.

MAJOR because content moved between files: anything that linked to a heading
inside SKILL.md for the principles or anti-patterns now needs the reference path.
