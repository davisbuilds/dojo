---
name: code-review-agents
description: "Specialized code review and quality assurance agents covering architecture, data integrity, security, performance, language-specific conventions, and deployment safety. Use when reviewing PRs, auditing code quality, checking migrations, or running an agent-native architecture audit. Triggers on 'review code', 'audit architecture', 'check data integrity', 'security review', 'heal skill'."
---

# Code Review Agents

A collection of specialized review agents, each focused on a specific quality dimension. Invoke individually via the Task tool or use the `/agent-native-audit` command to run a comprehensive scored review with parallel sub-agents.

## Commands

- `/agent-native-audit` — Comprehensive agent-native architecture review with scored principles (8 parallel sub-agents)
- `/heal-skill` — Fix incorrect SKILL.md files with wrong instructions or outdated API references

## Available Agents

### Architecture & Design

| Agent | Focus |
|-------|-------|
| `agent-native-reviewer` | Ensures features have agent action/context parity |
| `architecture-strategist` | Validates design patterns and component boundaries |
| `pattern-recognition-specialist` | Identifies design patterns, anti-patterns, naming issues |

### Language-Specific Reviewers

| Agent | Focus |
|-------|-------|
| `kieran-rails-reviewer` | Strict Rails conventions |
| `kieran-python-reviewer` | Pythonic patterns and type safety |
| `kieran-typescript-reviewer` | TypeScript type safety and best practices |
| `dhh-rails-reviewer` | Convention-over-configuration Rails review |
| `julik-frontend-races-reviewer` | JavaScript/Stimulus race condition detection |

### Data & Database

| Agent | Focus |
|-------|-------|
| `data-integrity-guardian` | Migrations, transaction boundaries, referential integrity |
| `data-migration-expert` | ID mapping validation, rollback safety |
| `schema-drift-detector` | Catches unrelated schema.rb changes in PRs |
| `deployment-verification-agent` | Go/No-Go checklists for risky deployments |

### Quality & Performance

| Agent | Focus |
|-------|-------|
| `code-simplicity-reviewer` | YAGNI enforcement, complexity removal |
| `performance-oracle` | Algorithm complexity, DB optimization, scalability |
| `security-sentinel` | OWASP compliance, vulnerability assessment |

## Usage

Invoke a specific agent via the Task tool:

```
Task(subagent_type: "review", prompt: "Review this PR for data integrity concerns")
```
