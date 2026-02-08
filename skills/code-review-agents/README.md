# Code Review Agents

A collection of specialized code review and quality assurance agents from the compound-engineering plugin.

## Structure

```
code-review-agents/
├── commands/           # Slash commands for invoking reviews
│   ├── agent-native-audit.md
│   └── heal-skill.md
└── agents/
    └── review/         # Individual reviewer agents
        ├── agent-native-reviewer.md
        ├── architecture-strategist.md
        ├── code-simplicity-reviewer.md
        ├── data-integrity-guardian.md
        ├── data-migration-expert.md
        ├── deployment-verification-agent.md
        ├── dhh-rails-reviewer.md
        ├── julik-frontend-races-reviewer.md
        ├── kieran-rails-reviewer.md
        ├── kieran-python-reviewer.md
        ├── kieran-typescript-reviewer.md
        ├── pattern-recognition-specialist.md
        ├── performance-oracle.md
        ├── schema-drift-detector.md
        └── security-sentinel.md
```

## Commands

| Command | Description |
|---------|-------------|
| `agent-native-audit` | Comprehensive agent-native architecture review with scored principles (8 parallel sub-agents) |
| `heal-skill` | Fix incorrect SKILL.md files with wrong instructions or outdated API references |

## Review Agents

### Architecture & Design
| Agent | Focus |
|-------|-------|
| `agent-native-reviewer` | Ensures features are agent-native with action/context parity |
| `architecture-strategist` | Analyzes code from architectural perspective, validates design patterns |
| `pattern-recognition-specialist` | Identifies design patterns, anti-patterns, naming conventions |

### Language-Specific Reviewers
| Agent | Focus |
|-------|-------|
| `kieran-rails-reviewer` | High-bar Rails code review with strict conventions |
| `kieran-python-reviewer` | High-bar Python code review with Pythonic patterns |
| `kieran-typescript-reviewer` | High-bar TypeScript code review with type safety focus |
| `dhh-rails-reviewer` | Rails review from DHH's perspective - convention over configuration |
| `julik-frontend-races-reviewer` | JavaScript/Stimulus review focused on race conditions |

### Data & Database
| Agent | Focus |
|-------|-------|
| `data-integrity-guardian` | Database migrations, data models, transaction boundaries |
| `data-migration-expert` | Validates ID mappings, rollback safety, data transformations |
| `schema-drift-detector` | Catches unrelated schema.rb changes in PRs |
| `deployment-verification-agent` | Creates Go/No-Go checklists for risky data deployments |

### Quality & Performance
| Agent | Focus |
|-------|-------|
| `code-simplicity-reviewer` | YAGNI principle, removes unnecessary complexity |
| `performance-oracle` | Algorithmic complexity, database optimization, scalability |
| `security-sentinel` | OWASP compliance, vulnerability assessment, input validation |

## Usage

These agents are designed to be invoked via the Task tool in Claude Code:

```
Task(subagent_type: "review", prompt: "Review this PR for data integrity concerns")
```

Or via the compound-engineering plugin commands:

```
/compound-engineering:agent-native-audit
```

## Source

These agents are extracted from the compound-engineering plugin v2.30.0.
