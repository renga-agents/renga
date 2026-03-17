# Plugin System — Custom Drop-in Agents

> **Target audience**: developers who want to extend the framework with custom agents
> **Prerequisites**: have read [agent-format.md](agent-format.md)
> **Last updated**: 2026-03-17
> **Estimated reading time**: 12 min
>
> **Status**: Adopted
> **Date**: 2026-03-16
> **Author**: SoftwareArchitect
> **ADR**: [ADR-006](adr/ADR-006-plugin-system.md)

---

## Table of Contents

- [Problem](#problem)
- [Decision](#decision)
- [Naming Convention](#naming-convention)
- [Plugin Format](#plugin-format)
- [Auto-Discovery](#auto-discovery)
- [Track Registration](#track-registration)
- [Core Agent Overrides](#core-agent-overrides)
- [Isolation](#isolation)
- [Lifecycle](#lifecycle)
- [Interaction with Complexity Profiles](#interaction-with-complexity-profiles)
- [Rejected Alternatives](#rejected-alternatives)
- [Consequences](#consequences)

---

## Problem

Adding a specialized agent (example: `graphql-expert`, `firebase-dev`, `unity-engineer`) currently requires:

1. Creating the `.agent.md` file in `.github/agents/` — mixing core and custom agents
2. Potentially modifying the orchestrator to reference it
3. Updating track profiles manually

**Forces in tension**:

| Force | Direction |
| --- | --- |
| Extensibility | Users want to add agents without touching the framework |
| Core stability | Core agents must not be impacted by plugins |
| Simplicity | The mechanism must be trivial (drop-in, no configuration) |
| Consistency | Plugins must follow the same format as core agents |
| Isolation | A faulty plugin must not break orchestration |

---

## Decision

Introduce a dedicated `.github/agents/plugins/` directory with an auto-discovery mechanism. Plugins use the same `.agent.md` format with additional frontmatter fields.

---

## Naming Convention

### Plugin Directories: `plugins/` vs `_plugins/`

The framework distinguishes **two plugin directories** with different roles:

| Directory | Owner | Content | Frontmatter `plugin` |
| --- | --- | --- | --- |
| `.github/agents/plugins/` | **User** | Custom agents created by the user for their project | `plugin: true` |
| `.github/agents/_plugins/` | **Framework** | Bundled packs distributed with the framework (example: `game-studio`) | `plugin: <pack-name>` |

**`plugins/`** — User directory:

- Contains the agents that **you** create for your project (example: `graphql-expert`, `billing-assistant`)
- **Not overwritten** during a framework update via Git Subtree
- Each agent declares `plugin: true` in its frontmatter
- Detected by auto-discovery just like core agents

**`_plugins/`** — Framework bundled packs:

- Contains thematic packs distributed with the framework (example: `_plugins/game-studio/` with 9 specialized video game agents)
- **Updated** automatically with the framework via Git Subtree
- Each agent declares `plugin: <pack-name>` in its frontmatter (example: `plugin: game-studio`)
- Can be enabled or disabled by pack via `.renga.yml`

> **Naming convention**: the `_` (underscore) prefix indicates a directory **managed by the framework**, like `_config/`, `_profiles/`, `_references/`. Directories **without an underscore** are managed by the user.

### Directory Structure

```text

.github/agents/plugins/
├── example-custom-agent.agent.md
├── graphql-expert.agent.md
├── firebase-dev.agent.md
├── unity-engineer/
│   ├── unity-engineer.agent.md
│   └── configs/
│       └── unity-conventions.md
└── stripe-integrator/
    ├── stripe-integrator.agent.md
    └── instructions/
        └── stripe-api-patterns.md

```

### Rules

- **Location**: `.github/agents/plugins/`
- **Single file**: `<name>.agent.md` directly in `plugins/`
- **Structured folder**: `plugins/<name>/<name>.agent.md` for plugins with supplementary files
- **Naming**: kebab-case, identical to the `name` field in the frontmatter
- **Extension**: `.agent.md` — identical to core agents

---

## Plugin Format

A plugin uses the standard `.agent.md` format with additional frontmatter fields.

### Frontmatter — Plugin-Specific Fields

| Field | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `plugin` | `boolean` | **yes** | — | Must be `true`. Marker that distinguishes a plugin from a core agent. |
| `filiere` | `string` | no | — | Associated track: `tech`, `product`, `data`, `governance`. Determines which track orchestrator can dispatch this plugin. |
| `overrides` | `string` | no | — | Name (`name`) of the core agent to override. The plugin replaces the core agent during dispatch. |

### Fields Inherited from the Standard Format

All fields from the standard `.agent.md` format apply: `name`, `user-invocable`, `description`, `tools`, `agents`, `model`.

See [agent-format.md](agent-format.md) for the complete reference.

### Minimal Example

```yaml

---
name: graphql-expert
plugin: true
user-invocable: true
description: "GraphQL expert — schemas, resolvers, federation, N+1 performance"
tools: ["execute", "read", "edit", "search", "web", "agent", "todo", "io.github.upstash/context7/*"]
filiere: tech
---
```

### Example with Override

```yaml

---
name: custom-backend-dev
plugin: true
user-invocable: true
description: "Elixir/Phoenix-specialized backend dev replacing the core backend-dev"
tools: ["execute", "read", "edit", "search", "web", "agent", "todo", "io.github.upstash/context7/*"]
filiere: tech
overrides: backend-dev
---
```

---

## Auto-Discovery

The orchestrator discovers plugins **automatically** without any configuration changes.

### Mechanism

1. When a task starts, the orchestrator recursively scans `.github/agents/plugins/`
2. Any `*.agent.md` file containing `plugin: true` in its frontmatter is registered as an available agent
3. Plugins are added to the agent catalog alongside the core agents
4. No orchestrator or track profile modification is required

### Name Resolution

```text

1. Scan .github/agents/*.agent.md             → core agents
2. Scan .github/agents/plugins/**/*.agent.md  → plugins
3. If a plugin declares overrides: <name>     → the plugin replaces core agent <name>
4. If there is a name conflict without override → validation error, the plugin is ignored

```

### Priority

| Situation | Behavior |
| --- | --- |
| Plugin with a unique `name` | Added to the catalog normally |
| Plugin with `overrides: agent-core` | Replaces the core agent for dispatch |
| Two plugins with the same `name` | **Error** — the first one found (alphabetical order) is loaded, warning emitted |
| Plugin with the same `name` as a core agent without `overrides` | **Error** — the plugin is ignored |

---

## Track Registration

Plugins can register in an orchestrator track via the `filiere` field.

### Available Tracks

| Value | Track orchestrator | Description |
| --- | --- | --- |
| `tech` | `orchestrator-tech` | Technical track — dev, architecture, infra, security |
| `product` | `orchestrator-product` | Product track — PM, UX, analytics |
| `data` | `orchestrator-data` | Data track — data engineering, ML, MLOps |
| `governance` | `orchestrator-governance` | Governance track — compliance, risk, audit |

### Behavior

- If `filiere` is declared, the corresponding track orchestrator can dispatch to this plugin
- If `filiere` is absent, the plugin is available for direct invocation (`@name`) but does not automatically appear in any track
- The main orchestrator can always dispatch to any plugin, regardless of track

---

## Core Agent Overrides

A plugin can replace a core agent by declaring `overrides: <agent-name>`.

### Override Rules

1. The `overrides` field contains the exact `name` of the core agent to replace
2. The plugin takes the place of the core agent in **all** dispatch mechanisms
3. The core agent remains present in `.github/agents/` — it is neither modified nor removed
4. Only one plugin can override a given core agent — conflict = error
5. The plugin inherits the track of the overridden core agent if `filiere` is not explicitly declared

### Use Cases

- Replace `backend-dev` with a Rust/Go/Elixir-specialized version
- Replace `database-engineer` with a specific expert (MongoDB, Cassandra)
- Adapt `frontend-dev` for an in-house framework

### Guardrail

A plugin **cannot** override:

- `orchestrator` — the main entry point is immutable
- `consensus-protocol` — the consensus protocol is structural
- `execution-modes` — execution modes are structural

---

## Isolation

Each plugin is sandboxed in its own file space.

### File Structure

```text

.github/agents/plugins/<plugin-name>/
├── <plugin-name>.agent.md    # Agent definition (required)
├── instructions/             # Plugin-specific instructions (optional)
│   └── *.md
├── configs/                  # Plugin configuration (optional)
│   └── *.yml
└── examples/                 # Code/pattern examples (optional)
    └── *.md

```

### Isolation Rules

| Rule | Description |
| --- | --- |
| Own read access | A plugin can read its files in `plugins/<plugin-name>/` |
| Core read access | A plugin can read core files (agents, profiles, references) read-only |
| Own write access | A plugin modifies only its own files |
| No cross-plugin access | A plugin does not read or modify another plugin's files |
| No core modification | A plugin never modifies core agents or framework configuration |

### Single-File Plugins

For simple plugins without supplementary files:

```text

.github/agents/plugins/graphql-expert.agent.md

```

A single file directly in `plugins/` is valid. Isolation applies to that one file only.

---

## Lifecycle

The plugin lifecycle is intentionally **trivial**:

### Add a Plugin

```bash

# Simple plugin
cp my-agent.agent.md .github/agents/plugins/

# Structured plugin
mkdir -p .github/agents/plugins/my-agent/
cp my-agent.agent.md .github/agents/plugins/my-agent/
cp -r instructions/ .github/agents/plugins/my-agent/

```

**Effect**: the plugin is immediately available at the next dispatch. No migration, no registration, no build.

### Remove a Plugin

```bash

# Simple plugin
rm .github/agents/plugins/my-agent.agent.md

# Structured plugin
rm -rf .github/agents/plugins/my-agent/

```

**Effect**: the plugin disappears immediately. If it was overriding a core agent, the core agent resumes its role.

### Update a Plugin

Modify the plugin's `.agent.md` file. Effect is immediate.

### No Built-In Versioning

Plugins follow the repository's versioning (git). There is no internal versioning system. A `CHANGELOG.md` in the plugin folder is recommended for complex plugins.

---

## Interaction with Complexity Profiles

Complexity profiles (Lite, Standard, Full) manage **core** agents. Plugins are added **on top**, regardless of the active profile.

### Filtering via `.renga.yml`

```yaml

# Plugins are included by default
plugins:
  enabled: true        # Enable/disable plugins globally (default: true)
  include:             # Whitelist (optional — if absent, all plugins are active)
    - graphql-expert
    - firebase-dev
  exclude:             # Blacklist (optional — applied after include)
    - experimental-agent

```

### Resolution Rules

1. If `plugins.enabled: false` → no plugin is loaded
2. If `plugins.include` is defined → only the listed plugins are loaded
3. If `plugins.exclude` is defined → the listed plugins are excluded
4. If nothing is configured → all plugins in `plugins/` are loaded (default behavior)

---

## Rejected Alternatives

### 1. Centralized Registry (`plugins.yml`)

A configuration file listing all installed plugins.

**Rejected**: adds a manual registration step and breaks the drop-in principle. Synchronization errors between the file and the directory.

**Would be better if**: there were a need for load-order control or inter-plugin dependencies.

### 2. Plugins in `.github/agents/` with `plugin-` Prefix

Plugins coexist with core agents, distinguished by a name prefix.

**Rejected**: pollutes the core directory, makes differentiation harder, and provides no file isolation.

**Would be better if**: VS Code tooling did not support navigation in subdirectories.

### 3. Plugins as Installable npm/pip Packages

Distribution through a package manager with installation hooks.

**Rejected**: oversized for markdown files. Installation complexity, runtime dependencies, adoption barrier.

**Would be better if**: plugins contained executable code or binary dependencies.

---

## Consequences

### Positive

- **Zero-config**: adding an agent = dropping a file
- **Isolation**: plugins do not break core agents
- **Compatibility**: same `.agent.md` format, zero learning curve
- **Reversibility**: removing a plugin = deleting a file, immediate restoration of the core behavior

### Negative

- **No inter-plugin dependencies**: one plugin cannot declare that it depends on another plugin
- **No versioning**: no built-in semantic versioning, relies on git
- **Discovery on every task**: directory scan on every dispatch (negligible cost for ~10-50 markdown files)

### Rollback Cost

**Reversible in minutes** — delete the `plugins/` directory and the added frontmatter fields. No impact on core agents.

---

## Architecture Diagram

```text

┌─────────────────────────────────────────────────────────┐
│                       User                              │
│                    @agent-name                          │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│                    Orchestrator                          │
│                                                          │
│  1. Scan .github/agents/*.agent.md         → Core agents │
│  2. Scan .github/agents/plugins/**/*.agent.md → Plugins  │
│  3. Apply overrides (plugin → core)                     │
│  4. Filter via .renga.yml                               │
│  5. Dispatch                                            │
└───────┬──────────────────────────────────┬───────────────┘
        │                                  │
        ▼                                  ▼
┌───────────────────┐         ┌────────────────────────────┐
│    Core Agents    │         │        Plugins             │
│                   │         │                            │
│  .github/agents/  │         │  .github/agents/plugins/   │
│  ├── backend-dev  │         │  ├── graphql-expert.agent  │
│  ├── frontend-dev │         │  ├── firebase-dev/         │
│  ├── qa-engineer  │         │  │   ├── firebase-dev.agent│
│  └── ...          │         │  │   └── instructions/     │
│                   │         │  └── unity-engineer/       │
│  (immutable to    │         │      ├── unity-engineer... │
│   plugins)        │         │      └── configs/          │
└───────────────────┘         └────────────────────────────┘

```

### Data Flow — Override

```text

                    Dispatch "backend-dev"
                           │
                           ▼
                 ┌─────────────────────┐
                 │   Override declared?│
                 └─────────┬───────────┘
                    yes    │    no
               ┌───────────┴──────────┐
               ▼                      ▼
  ┌───────────────────┐   ┌───────────────────┐
  │  Override plugin  │   │   Core agent      │
  │ (custom-backend)  │   │  (backend-dev)    │
  └───────────────────┘   └───────────────────┘

```

---

## Validation

The `scripts/validate_agents.py` script must be extended to:

1. Scan `plugins/` in addition to `.github/agents/`
2. Validate the `plugin: true` field in plugin frontmatter
3. Check that `overrides` references an existing core agent
4. Detect name conflicts (two plugins with the same `name`)
5. Check that `filiere` values are valid

---

## Implementation Checklist

- [x] Naming convention documented
- [x] Plugin format defined (frontmatter + body)
- [x] Auto-discovery described (recursive scan)
- [x] Track registration specified
- [x] Overrides documented with guardrails
- [x] Isolation defined (read/write)
- [x] Trivial lifecycle (drop-in / drop-out)
- [x] Interaction with complexity profiles clarified
- [x] Rejected alternatives justified
- [x] Architecture diagram provided
