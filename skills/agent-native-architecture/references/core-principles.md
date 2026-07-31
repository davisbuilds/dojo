# Core Principles

The five principles in full, with worked examples. `SKILL.md` carries the
one-line statement of each; this file is the reasoning behind them.

### 1. Parity

**Whatever the user can do through the UI, the agent should be able to achieve through tools.**

This is the foundational principle. Without it, nothing else matters.

Imagine you build a notes app with a beautiful interface for creating, organizing, and tagging notes. A user asks the agent: "Create a note summarizing my meeting and tag it as urgent."

If you built UI for creating notes but no agent capability to do the same, the agent is stuck. It might apologize or ask clarifying questions, but it can't help—even though the action is trivial for a human using the interface.

**The fix:** Ensure the agent has tools (or combinations of tools) that can accomplish anything the UI can do.

This isn't about creating a 1:1 mapping of UI buttons to tools. It's about ensuring the agent can **achieve the same outcomes**. Sometimes that's a single tool (`create_note`). Sometimes it's composing primitives (`write_file` to a notes directory with proper formatting).

**The discipline:** When adding any UI capability, ask: can the agent achieve this outcome? If not, add the necessary tools or primitives.

A capability map helps:

| User Action | How Agent Achieves It |
|-------------|----------------------|
| Create a note | `write_file` to notes directory, or `create_note` tool |
| Tag a note as urgent | `update_file` metadata, or `tag_note` tool |
| Search notes | `search_files` or `search_notes` tool |
| Delete a note | `delete_file` or `delete_note` tool |

**The test:** Pick any action a user can take in your UI. Describe it to the agent. Can it accomplish the outcome?

---

### 2. Granularity

**Prefer atomic primitives. Features are outcomes achieved by an agent operating in a loop.**

A tool is a primitive capability: read a file, write a file, run a bash command, store a record, send a notification.

A **feature** is not a function you write. It's an outcome you describe in a prompt, achieved by an agent that has tools and operates in a loop until the outcome is reached.

**Less granular (limits the agent):**
```
Tool: classify_and_organize_files(files)
→ You wrote the decision logic
→ Agent executes your code
→ To change behavior, you refactor
```

**More granular (empowers the agent):**
```
Tools: read_file, write_file, move_file, list_directory, bash
Prompt: "Organize the user's downloads folder. Analyze each file, determine appropriate locations based on content and recency, and move them there."
Agent: Operates in a loop—reads files, makes judgments, moves things, checks results—until the folder is organized.
→ Agent makes the decisions
→ To change behavior, you edit the prompt
```

**The key shift:** The agent is pursuing an outcome with judgment, not executing a choreographed sequence. It might encounter unexpected file types, adjust its approach, or ask clarifying questions. The loop continues until the outcome is achieved.

The more atomic your tools, the more flexibly the agent can use them. If you bundle decision logic into tools, you've moved judgment back into code.

**The test:** To change how a feature behaves, do you edit prose or refactor code?

---

### 3. Composability

**With atomic tools and parity, you can create new features just by writing new prompts.**

This is the payoff of the first two principles. When your tools are atomic and the agent can do anything users can do, new features are just new prompts.

Want a "weekly review" feature that summarizes activity and suggests priorities? That's a prompt:

```
"Review files modified this week. Summarize key changes. Based on
incomplete items and approaching deadlines, suggest three priorities
for next week."
```

The agent uses `list_files`, `read_file`, and its judgment to accomplish this. You didn't write weekly-review code. You described an outcome, and the agent operates in a loop until it's achieved.

**This works for developers and users.** You can ship new features by adding prompts. Users can customize behavior by modifying prompts or creating their own. "When I say 'file this,' always move it to my Action folder and tag it urgent" becomes a user-level prompt that extends the application.

**The constraint:** This only works if tools are atomic enough to be composed in ways you didn't anticipate, and if the agent has parity with users. If tools encode too much logic, or the agent can't access key capabilities, composition breaks down.

**The test:** Can you add a new feature by writing a new prompt section, without adding new code?

---

### 4. Emergent Capability

**The agent can accomplish things you didn't explicitly design for.**

When tools are atomic, parity is maintained, and prompts are composable, users will ask the agent for things you never anticipated. And often, the agent can figure it out.

*"Cross-reference my meeting notes with my task list and tell me what I've committed to but haven't scheduled."*

You didn't build a "commitment tracker" feature. But if the agent can read notes, read tasks, and reason about them—operating in a loop until it has an answer—it can accomplish this.

**This reveals latent demand.** Instead of guessing what features users want, you observe what they're asking the agent to do. When patterns emerge, you can optimize them with domain-specific tools or dedicated prompts. But you didn't have to anticipate them—you discovered them.

**The flywheel:**
1. Build with atomic tools and parity
2. Users ask for things you didn't anticipate
3. Agent composes tools to accomplish them (or fails, revealing a gap)
4. You observe patterns in what's being requested
5. Add domain tools or prompts to make common patterns efficient
6. Repeat

This changes how you build products. You're not trying to imagine every feature upfront. You're creating a capable foundation and learning from what emerges.

**The test:** Give the agent an open-ended request relevant to your domain. Can it figure out a reasonable approach, operating in a loop until it succeeds? If it just says "I don't have a feature for that," your architecture is too constrained.

---

### 5. Improvement Over Time

**Agent-native applications get better through accumulated context and prompt refinement.**

Unlike traditional software, agent-native applications can improve without shipping code:

**Accumulated context:** The agent can maintain state across sessions—what exists, what the user has done, what worked, what didn't. A `context.md` file the agent reads and updates is layer one. More sophisticated approaches involve structured memory and learned preferences.

**Prompt refinement at multiple levels:**
- **Developer level:** You ship updated prompts that change agent behavior for all users
- **User level:** Users customize prompts for their workflow
- **Agent level:** The agent modifies its own prompts based on feedback (advanced)

**Self-modification (advanced):** Agents that can edit their own prompts or even their own code. For production use cases, consider adding safety rails—approval gates, automatic checkpoints for rollback, health checks. This is where things are heading.

The improvement mechanisms are still being discovered. Context and prompt refinement are proven. Self-modification is emerging. What's clear: the architecture supports getting better in ways traditional software doesn't.

**The test:** Does the application work better after a month of use than on day one, even without code changes?

