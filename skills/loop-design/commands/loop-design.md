---
name: loop-design
description: Design a reusable, verifiable autonomous loop and scaffold the files a harness runs (on top of /loop, /goal, automations).
argument-hint: "[task description] | --blueprint <path.json> [--out-dir <dir>]"
allowed-tools: [Read, Write, Edit, Bash(python3 skills/loop-design/scripts/scaffold_loop.py:*), Bash(git:*)]
---

# Loop Design Command

Turn a task into a verifiable, portable autonomous loop — or decide it should not be one.

## Behavior

1. **Run the go/no-go gate.** Ask the four questions from `skills/loop-design/SKILL.md`:
   - Is there an oracle (a command that exits 0 when done)?
   - Is the maker graded by something other than itself?
   - Are credentials scoped and spend capped?
   - Will the diffs actually be read?
   If gate 1 fails, report why this is not loop-shaped and stop. Do not scaffold.
2. **Draft the blueprint** using the schema in `references/blueprint-spec.md` (`name`, `goal`, `done_when`, `constraints`, `cadence`, `harness`, `checker`, `sandbox`). Use `test-strategy` to design the oracle if one does not exist yet.
3. **Scaffold the bundle:**
   ```bash
   python3 skills/loop-design/scripts/scaffold_loop.py --blueprint <blueprint.json> --out-dir .loops/<name>
   ```
   (or pass `--name --goal --done-when --harness` directly).
4. **Bind to the harness** using the generated `BINDINGS.md` and `references/harness-bindings.md`. Place the checker in `.claude/agents/` or `.codex/agents/`.
5. **Require an attended dry-run** of one iteration before anything runs unattended.

## Rules

- Never scaffold a loop without a `done_when` oracle — the script enforces this; do not work around it.
- Never name an artifact or command `/loop` or `/goal` (collides with harness primitives).
- Keep `LOOP.md` harness-neutral (no slash commands inside it) so it is portable.
- Do not commit or push unless the user explicitly asks.

## Output

Report, in order:
1. The go/no-go verdict (and the reason if no-go).
2. The bundle path and the files written.
3. The exact harness wiring line to run next.
4. The reminder to dry-run one iteration attended before walking away.
