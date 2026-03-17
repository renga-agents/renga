# ADR-007: Integrating Agent Skills

**Date**: 2026-03-17
**Status**: Accepted
**Decision makers**: Founding team

## Context

The renga framework relies on two behavioral configuration mechanisms:

- **Agents** in `.agent.md` files, which define a complete role with identity, tools, and rules
- **Instructions** in `.instructions.md` files, which apply conventions by technology through `applyTo` globs

What was missing was an intermediate mechanism: **reusable knowledge blocks** that an agent can load on demand, without carrying them permanently in its context. Several issues motivated this need:

1. **Duplication**: workflows such as the handoff protocol and task decomposition were duplicated across multiple agents
2. **Token consumption**: embedding all knowledge directly in the system prompt wastes context budget when it is irrelevant to the current task
3. **Cross-agent sharing**: some knowledge, such as DAG patterns or automatic triggers, is useful to several agents across different lanes without being broad enough to justify a global instruction

## Decision

Adopt the open **GitHub Copilot Agent Skills** standard for reusable knowledge blocks loaded progressively.

### Structure

Skills are stored in `.github/skills/<name>/SKILL.md`, with each file combining YAML frontmatter and a Markdown body:

```yaml

---
name: task-decomposition
description: "Breaks down a complex task into atomic subtasks"
argument-hint: "Describe the task to decompose"
user-invocable: true
---
```

### Referencing

Agents declare their skills through the `skills:` frontmatter field:

```yaml

---
name: orchestrator
skills:
  - task-decomposition
  - dag-patterns
  - handoff-protocol
---
```

### Progressive loading

Loading follows three steps to reduce token usage:

1. **Discovery**: the model sees only the list of available skills with name and description
2. **Instructions**: when a skill becomes relevant, the `SKILL.md` content is loaded
3. **Resources**: additional files in the skill folder are loaded on demand

## Consequences

### Positive

- **Portability**: `SKILL.md` is an open standard aligned with the GitHub Copilot ecosystem
- **Token efficiency**: progressive loading avoids filling the context with irrelevant knowledge
- **Reusability**: the same skill can be referenced by multiple agents without duplication
- **Extensibility**: users can create their own skills under `.github/skills/` without modifying the framework

### Negative

- **Discoverability**: skills are invisible until referenced by an agent or invoked by the user
- **Platform dependency**: progressive loading depends on native GitHub Copilot support

### Extracted skills

Five skills were extracted from duplicated knowledge previously embedded in agents:

| Skill | Origin |
| --- | --- |
| `task-decomposition` | L0-L4 decomposition logic from the orchestrator |
| `dag-patterns` | Multi-agent DAG construction in waves |
| `auto-triggers` | Automatic triggering of specialized agents |
| `worktree-lifecycle` | Lifecycle of isolated Git worktrees |
| `handoff-protocol` | Structured inter-agent handoff protocol |

## Alternatives Considered

### Put everything in instructions (`.instructions.md`)

Instructions apply automatically via `applyTo` globs. Rejected: skills must load on demand, not all the time. Large content under `applyTo: "**/*"` would waste context.

### Shared profiles (`_profiles/`)

The framework already used `_profiles/` to share content between agents. Rejected as the only solution: profiles do not support progressive loading or direct user invocation. Skills provide a richer mechanism.

### Inline inclusion in every agent

Copy the content directly into each relevant agent body. Rejected: duplication is unavoidable, maintenance is costly, and versions drift over time.
