# Format of `.agent.md` Files

> **Target audience**: framework contributors, custom agent authors
> **Prerequisites**: read [getting-started.md](getting-started.md)
> **Last updated**: 2026-03-17
> **Estimated reading time**: 10 min

This document describes the standard format of a `.agent.md` file in the renga framework.

---

## General Structure

A `.agent.md` file has two parts:

1. **YAML frontmatter**: structured metadata between `---`
2. **Markdown body**: the agent's detailed description

```markdown

---
name: my-agent
user-invocable: true
description: "Short description of the domain"
tools: ["execute", "read", "edit", "search", "web", "agent", "todo"]
model: ['Claude Opus 4.6 (copilot)']
---
# Agent: MyAgent

Markdown body of the agent...

```

---

## YAML Frontmatter

| Field | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `name` | `string` | **yes** | — | Unique kebab-case identifier. Must match the filename. |
| `user-invocable` | `boolean` | no | `true` | `true` = invocable by a human via `@name`. `false` = internal reference. |
| `description` | `string` | **yes** | — | Short description (10-200 chars.) of the domain. Used for the catalog and dispatch. |
| `tools` | `string[]` | **yes** | — | Allowed MCP tools. Short names or qualified patterns. |
| `agents` | `string[]` | no | — | Agents invocable via `runSubagent`. `["*"]` = all. Reserved for orchestrators. |
| `model` | `string[]` | no | central config | LLM model. Optional if the central config is defined (see below). |
| `plugin` | `boolean` | no | — | `true` = plugin agent (in `plugins/`). Required for plugins. |
| `filiere` | `string` | no | — | Associated track: `tech`, `produit`, `data`, `gouvernance`. Plugins only. |
| `overrides` | `string` | no | — | `name` of the core agent to override. Plugins only. |

### Common Values for `tools`

| Tool | Description |
| --- | --- |
| `execute` | Run terminal commands |
| `read` | Read files |
| `edit` | Modify files |
| `search` | Search the workspace |
| `web` / `web/fetch` | Web access |
| `agent` / `agent/runSubagent` | Invoke sub-agents |
| `todo` | Manage a task list |
| `io.github.chromedevtools/chrome-devtools-mcp/*` | Browser DevTools |
| `io.github.upstash/context7/*` | Context7 documentation |
| `playwright/*` | Automated browser tests |

### Naming Convention

- **Filename**: `<name>.agent.md` (example: `backend-dev.agent.md`)
- **`name` field**: kebab-case, lowercase letters and digits only
- **Core agent location**: `.github/agents/`
- **Plugin location**: `.github/agents/plugins/` (see [plugin-system.md](plugin-system.md))

---

## Markdown Body — Expected Sections

The markdown body follows a conventional structure. The sections in **bold** are strongly recommended.

### 1. Title and Header

```markdown

# Agent: AgentName

**Domain**: Description of the area of expertise
**Collaboration**: List of collaborating agents

```

### 2. **Identity & Stance**

Personality, experience level, and fundamental principles. Defines the "role" the agent embodies.

### 3. **Core Skills**

Bulleted list of the technical areas mastered.

### 4. Reference Stack

Table of the default technical choices (framework, ORM, tests, etc.). Configurable per project via `.github/instructions/project/`.

### 5. MCP Tools

Description of the expected usage of each MCP tool listed in the frontmatter.

### 6. Workflow / Response Format

Step-by-step reasoning process the agent must follow.

### 7. **Behavior Rules**

List of **Always** / **Never** / **If in doubt** / **Challenge** rules. These are the non-negotiable behavioral constraints.

### 8. **Checklist Before Delivery**

Checklist items (☐) the agent must complete before returning its output.

### 9. Handoff Contract

Defines what the agent passes to the next agent: fixed decisions, open questions, artifacts, and the expected next action.

---

## Non-Invocable Agents

Some `.agent.md` files are not active agents but **internal references**:

- `user-invocable: false`
- `tools: ["read"]` (read-only)
- Used as shared documentation (example: `consensus-protocol`, `execution-modes`)

---

## Minimal Template

```markdown

---
name: my-agent
user-invocable: true
description: "Short description of the agent's domain"
tools: ["execute", "read", "edit", "search", "web", "agent", "todo", "io.github.upstash/context7/*"]
model: ['Claude Opus 4.6 (copilot)']
---
# Agent: MyAgent

**Domain**: [Area of expertise]
**Collaboration**: [Collaborating agents]

---

## Identity & Stance

[Personality, experience, fundamental principles — 3 to 5 lines]

---

## Core Skills

- [Skill 1]
- [Skill 2]
- [Skill 3]

---

## MCP Tools

- **context7**: [expected usage]

---

## Workflow

1. **[Step 1]** — [description]
2. **[Step 2]** — [description]
3. **[Step 3]** — [description]

---

## Behavior Rules

- **Always** [positive rule]
- **Never** [negative rule]
- **If in doubt** → [fallback]
- **Challenge** [who] if [condition]
- **Always** reread your output against the checklist before delivery

---

## Checklist Before Delivery

- ☐ [Check 1]
- ☐ [Check 2]
- ☐ [Check 3]

---

## Handoff Contract

**Primary handoff to [recipient agents]**

- **Fixed decisions**: [validated constraints]
- **Open questions**: [unresolved points]
- **Artifacts to reuse**: [files, diagrams, tests]
- **Expected next action**: [what the recipient must do]

```

---

## Centralized LLM Model Configuration

The `model:` field in each agent's frontmatter is now **optional**. The default model is defined in the central config:

```text

.github/agents/_config/models.yml

```

### Resolution Behavior

1. If the agent has a `model:` in its frontmatter → **use that value** (override)
2. Otherwise → use `default.model` from `_config/models.yml`

### When Should You Override It in an Agent?

Rarely. Legitimate cases:

- An agent requiring a specific model (example: advanced reasoning for the orchestrator)
- A/B tests between models on a specific agent

For new agents, **do not** include `model:` in the frontmatter — the central config applies automatically.

---

## Shared Handoff Protocol

The "Handoff Contract" block follows a standard format defined in:

```text

.github/agents/_profiles/handoff-protocol.md

```

This profile defines:

- The required **structure** (Fixed Decisions, Open Questions, Artifacts, Next Action)
- The protocol **rules** (completeness, no renegotiation, traceability, symmetry)
- A **concrete example** of a handoff

Existing agents keep their handoff block inline. New agents can reference the profile:

```markdown

## Handoff Contract

> Handoff structure: see `_profiles/handoff-protocol.md`

**Primary handoff to `<recipients>`**

- **Fixed decisions**: [specific]
- **Open questions**: [specific]
- **Artifacts to reuse**: [specific]
- **Expected next action**: [specific]

```

---

## Complexity Profiles

The framework provides 3 predefined profiles to adapt the number of agents to the size of the project:

| Profile | Agents | Usage |
| --- | --- | --- |
| **Lite** | 8 | Solo project / prototype |
| **Standard** | 20 | Team of 2-5 developers |
| **Full** | 52 core agents | Enterprise, strong governance |

Full details: [`docs/complexity-profiles.md`](complexity-profiles.md)

---

## Plugins

Custom agents are added as **drop-in plugins** in `.github/agents/plugins/`. They use the same `.agent.md` format with the additional fields `plugin`, `filiere`, and `overrides`.

Full details: [`docs/plugin-system.md`](plugin-system.md)

---

## Skills

**Skills** are reusable knowledge blocks that an agent can load on demand. Unlike instructions (applied automatically based on the `applyTo` glob), a skill is invoked explicitly — either by the user or by the agent when it detects that the skill is relevant.

### Location

```text

.github/skills/<skill-name>/SKILL.md

```

Each skill is a folder containing at minimum a `SKILL.md` file. The folder may also include supporting resources (templates, examples, diagrams).

### `SKILL.md` File Format

Like agents, the `SKILL.md` file combines a **YAML frontmatter** and a **Markdown body**:

```yaml

---
name: task-decomposition
description: "Breaks down a complex task into atomic subtasks"
argument-hint: "Describe the task to break down"
user-invocable: true
---
# Skill: Task Decomposition

Skill content...

```

### Frontmatter Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | `string` | **yes** | Unique kebab-case identifier. Must match the folder name. |
| `description` | `string` | **yes** | Short description of the skill. Used for automatic discovery. |
| `argument-hint` | `string` | no | Guidance for the user about the expected argument when invoking the skill. |
| `user-invocable` | `boolean` | no | `true` = the user can invoke the skill directly. |
| `disable-model-invocation` | `boolean` | no | `true` = only the user can trigger the skill (no automatic invocation by the model). |

### Referencing a Skill from an Agent

An agent can declare the skills it uses through the `skills:` field in its frontmatter:

```yaml

---
name: orchestrator
skills:
  - task-decomposition
  - dag-patterns
  - handoff-protocol
---
```

Declared skills are presented to the model as available capabilities. The agent can then load them when the task justifies it.

### Progressive Loading

Loading a skill follows 3 steps to optimize token usage:

1. **Discovery** — the model sees the list of available skills (name + description)
2. **Instructions** — when a skill is relevant, the content of `SKILL.md` is loaded
3. **Resources** — if the skill contains supporting files, they are loaded on demand

### Framework Skills

The framework includes 5 ready-to-use skills:

| Skill | Description |
| --- | --- |
| `task-decomposition` | Breaks down a complex task into atomic subtasks with L0-L4 classification |
| `dag-patterns` | Builds a multi-agent DAG organized in waves |
| `auto-triggers` | Identifies automatic triggers for specialized agents |
| `worktree-lifecycle` | Manages the lifecycle of an isolated Git worktree |
| `handoff-protocol` | Standardizes handoffs between agents |

---

## Hooks

**Hooks** (GitHub Copilot Agent Hooks) are a **repository-level** feature, not an individual agent feature. They are therefore not declared in `.agent.md` frontmatter.

Hooks are defined in the `.github/hooks/` folder and apply globally to all agents in the workspace. They make it possible to run scripts automatically before or after certain Copilot actions (tool calls, session startup, etc.).

→ Full reference: [`docs/hooks.md`](hooks.md)

---

## Validation

The reference JSON schema is available in [`schemas/agent.schema.json`](../schemas/agent.schema.json).
