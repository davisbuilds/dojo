# Skill Security Threat Model

## Attack Surfaces

### 1. Instruction Layer (SKILL.md, commands/, references/)

Markdown files loaded into the agent's context window. Attackers embed prompt injection, encoding tricks, or exfiltration instructions that execute when the agent processes the skill.

**Risk**: Direct influence over agent behavior. The agent trusts skill instructions as part of its operating context.

### 2. Code Layer (scripts/)

Executable code invoked by the agent via allowed tools. Malicious scripts can access the filesystem, network, environment variables, and other system resources.

**Risk**: Full system access within the agent's permission boundary. Code runs with the user's privileges.

### 3. Structural Layer (frontmatter, file layout, allowed-tools)

Metadata that determines what the agent is permitted to do when the skill is active. Overly broad tool permissions or suspicious file types expand the attack surface.

**Risk**: Grants capabilities the skill doesn't need, enabling lateral movement.

## Privilege Model

Activating a skill grants:

1. **Context injection** — SKILL.md body loaded into the conversation
2. **Tool access** — Tools listed in `allowed-tools` (frontmatter or command wrappers) become available
3. **Script execution** — Agent can run scripts/ via Bash tool calls
4. **Reference loading** — Agent can read references/ for additional context

A malicious skill exploits this trust chain: injection in instructions directs the agent to use granted tools to execute malicious scripts.

## Attack Taxonomy

### Prompt Injection
- **Role hijacking**: Override the agent's identity or safety constraints
- **Instruction override**: "Ignore previous instructions" variants
- **Goal manipulation**: Redirect the agent toward attacker objectives

### Tool Poisoning
- **Overly broad permissions**: `Bash(*)` grants unrestricted shell access
- **Implicit escalation**: Scripts that call tools not listed in allowed-tools
- **Dependency confusion**: Runtime `pip install` of attacker-controlled packages

### Data Exfiltration
- **Direct**: curl/wget/fetch to external URLs with local data
- **Indirect**: Agent instructed to include sensitive data in outputs
- **Staging**: Write data to world-readable locations for later retrieval

### Safety Bypass
- **Jailbreak patterns**: DAN mode, developer mode, unrestricted mode
- **Protection disabling**: Skip hooks, disable validation, --no-verify
- **Config tampering**: Modify .claude/settings, CLAUDE.md

### Supply Chain
- **Runtime installation**: pip/npm install at execution time
- **Binary inclusion**: Compiled files (.pyc, .so, .exe) in skill package
- **External fetch**: Download and execute code from URLs

## Trust Score Weight Rationale

| Layer | Weight | Rationale |
|-------|--------|-----------|
| Structural (L1) | 25% | Metadata issues are preconditions, not direct exploits |
| Instructions (L2) | 35% | Prompt injection directly compromises agent behavior |
| Code (L3) | 40% | Executable code has the highest blast radius |

When a skill has no scripts/, Layer 3's weight redistributes proportionally to Layers 1 and 2, since the code attack surface is absent.
