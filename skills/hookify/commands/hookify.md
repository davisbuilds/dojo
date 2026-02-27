---
description: Create hooks to prevent unwanted behaviors from conversation analysis or explicit instructions
argument-hint: Optional specific behavior to address
allowed-tools: ["Read", "Write", "AskUserQuestion", "Task", "Grep"]
---

# Hookify - Create Hooks from Unwanted Behaviors

**FIRST: Load the writing-rules reference** from this skill's `references/writing-rules.md` to understand rule file format.

## Your Task

Create hookify rules to prevent problematic behaviors.

### Step 1: Gather Behavior Information

**If $ARGUMENTS is provided:** User has specific instructions. Check recent conversation for examples.

**If $ARGUMENTS is empty:** Analyze recent conversation (last 10-15 user messages) for:
1. Explicit "don't do X" requests
2. Corrections or reversions
3. Frustrated reactions
4. Repeated issues

### Step 2: Present Findings

Use AskUserQuestion with multiSelect to let user pick which behaviors to hookify and whether to warn or block.

### Step 3: Generate Rule Files

For each confirmed behavior, create a rule file in the project's config directory.

**Detect config dir:** Use the first that exists: `.claude/`, `.agents/`, `.hookify/`. Create `.hookify/` if none exist.

**File:** `{config_dir}/hookify.{rule-name}.local.md`

```markdown
---
name: {rule-name}
enabled: true
event: {bash|file|stop|prompt|all}
pattern: {regex pattern}
action: {warn|block}
---

{Message shown when rule triggers}
```

### Step 4: Confirm

Show what was created. Remind user rules are active immediately.
