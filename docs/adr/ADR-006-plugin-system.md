# ADR-006: Two-Layer Plugin System

**Date**: 2026-03-17
**Status**: Accepted
**Decision makers**: Founding team

## Context

The renga framework defines 52 core agents across four business lanes (see [ADR-003](ADR-003-4-filieres.md)). Two distinct extensibility needs emerged:

1. **User custom plugins**: a user wants to add a specialized agent such as `graphql-expert` or `firebase-dev` without modifying the core
2. **Bundled plugin packs**: the framework ships thematic agent packs such as `game-studio`; they are maintained by the team but are not part of the core set

**Forces in tension**:

| Force | Direction |
| --- | --- |
| Extensibility | Users want to add agents without modifying the framework |
| Core stability | Core agents must not be impacted by plugins |
| Simplicity | The mechanism should be drop-in and require no configuration |
| Consistency | Plugins should use the same `.agent.md` format as core agents |
| Isolation | A broken plugin must not break orchestration |
| Distribution | Bundled packs must remain distinct from user plugins |

## Decision

Introduce a **two-layer plugin system** with auto-discovery:

### Layer 1: Custom plugins (`plugins/`)

- Location: `.github/agents/plugins/`
- Frontmatter: `plugin: true` (boolean)
- Created by the user for their project
- Auto-discovered by the orchestrator at startup

### Layer 2: Bundled packs (`_plugins/`)

- Location: `.github/agents/_plugins/<pack-name>/`
- Frontmatter: `plugin: <pack-name>` (string, for example `plugin: game-studio`)
- Distributed with the framework and maintained by the team
- The `_` prefix excludes them from core scanning by convention
- Organized by thematic pack such as `game-studio/`

### `plugin` field in the schema

The `plugin` frontmatter field accepts two shapes:

- `plugin: true` for a user custom plugin
- `plugin: <pack-name>` for a bundled plugin pack, using a kebab-case pack identifier

### Auto-discovery

```

1. Scan .github/agents/*.agent.md              -> core agents
2. Scan .github/agents/plugins/**/*.agent.md   -> custom plugins (plugin: true)
3. Scan .github/agents/_plugins/**/*.agent.md  -> bundled packs (plugin: <pack>)
4. If a plugin declares overrides: <name>      -> replace the core agent at dispatch time
5. If there is a name conflict without override -> error, plugin is ignored

```

### Shared format

Both custom and bundled plugins use the same `.agent.md` format as core agents, with extra fields such as `plugin`, optional `filiere`, and optional `overrides`.

## Consequences

### Positive

- **Zero-config**: dropping a `.agent.md` file into `plugins/` is enough
- **Isolation**: plugins do not mutate core agents directly
- **Clear separation**: `plugins/` for user content vs `_plugins/` for bundled content
- **No inter-plugin dependencies**: each plugin stays autonomous
- **Safe overrides**: a plugin can replace a core agent via `overrides` without editing the original agent

### Negative

- **Two directories**: the `plugins/` vs `_plugins/` distinction adds a concept that must be documented
- **No dependency graph**: a plugin cannot declare a dependency on another plugin
- **Discovery overhead**: three directories are scanned instead of one, though the cost is negligible in practice

### Invariants

- The central orchestrator (`orchestrator`), the consensus protocol (`consensus-protocol`), and execution modes (`execution-modes`) cannot be overridden by a plugin
- A bundled plugin cannot override another bundled plugin from the same pack

## Alternatives Considered

### Single directory for all plugins

Put both custom and bundled plugins into `plugins/`. Rejected: mixes user files with framework-distributed files, complicates framework updates, and weakens `.gitignore` hygiene.

### Centralized registry

Use a `plugins.yml` file listing enabled plugins explicitly. Rejected: adds configuration, breaks the zero-config principle, and creates a merge contention point.

### Git submodules for packs

Distribute each pack as a Git submodule. Rejected: excessive Git complexity, onboarding friction, and version compatibility problems.

## References

- [Plugin System — full documentation](../plugin-system.md)
- [ADR-003 — Four-lane organization](ADR-003-4-filieres.md)
- [ADR-005 — Agent Markdown format](ADR-005-markdown-agent-format.md)
