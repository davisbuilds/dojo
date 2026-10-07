---
name: loop-design
description: Design bounded agent tasks, recurring monitoring, or iterative experiments using the available runtime.
argument-hint: "[task description] | --blueprint <path.json> [--out-dir <new-dir>]"
---

# Loop Design Command

Apply the loaded `loop-design` skill to the requested work. Distinguish a bounded
task, a recurring monitor, and an experiment; reuse settled intent and runtime
capabilities. Specify relevant evidence, stopping rules, authority, and recovery
without requiring a new runner or a fixed set of files.

When a portable brief serves an executor, consult `references/blueprint-spec.md`
and optionally scaffold it:

```bash
python3 <skill-dir>/scripts/scaffold_loop.py --blueprint <blueprint.json> --out-dir .loops/<name>
```

Resolve `<skill-dir>` from the installed skill. Scaffolding executes no commands
and configures no runtime. For existing loops, preserve current state and follow
the schema migration guidance instead of overwriting their bundles.

Return the design or requested files, actual runtime wiring when established,
and any unresolved execution or evidence gap. Respect the user's launch and
publication scope; ordinary project commit policy still applies.
