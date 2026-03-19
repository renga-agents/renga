# ADR-002: Filesystem as Shared State

**Date**: 2026-03-16
**Status**: Accepted
**Decision makers**: Founding team

## Context

Agents need to persist state across sessions: project memory, architectural decisions, performance logs, and coordination scratchpads. That state must remain human-readable, versionable with Git, and accessible without external infrastructure. The framework targets teams that want zero infrastructure dependencies.

## Decision

Use the **local filesystem** as the single source of truth for shared state. In practice:

- `.renga/memory/` stores persistent cross-session memory such as decisions, conventions, and project context
- `.github/logs/` stores execution logs and dispatch traces
- `.github/agents/_references/` stores shared references across agents such as error catalogs and commit conventions
- `scratchpad-*.md` and `decisions-*.md` store transient state for an in-progress task

All files are Markdown. Agents read and write them using the standard `read` and `edit` tools.

## Consequences

### Positive

- **Zero infrastructure**: no server, database, or external service to deploy
- **Human readability**: all state lives in Markdown and can be inspected in any editor
- **Native versioning**: `git diff`, `git blame`, and `git log` work directly on agent state
- **Portability**: cloning the repository is enough to recover all context

### Negative

- **No locking**: two agents writing to the same file at the same time can create conflicts
- **No structured queries**: you cannot run `SELECT * FROM decisions WHERE status = 'accepted'`; you need to parse Markdown
- **Limited scalability**: hundreds of memory files become harder to browse

### Risks

- **Multi-developer race conditions**: two developers may launch simultaneous tasks on the same project; mitigated by the orchestrator serializing operations within a given session
- **Stale state accumulation**: mitigated by periodic cleanup conventions and `.gitignore` rules for transient files

## Alternatives Considered

### Local SQLite

An embedded database inside the workspace. Rejected: adds a binary dependency, makes the state unreadable in a text editor, and turns Git diffs opaque. The overhead is disproportionate to current needs.

### Central API (external server)

A REST or GraphQL service hosting agent state. Rejected: introduces a network dependency, an external point of failure, and contradicts the framework's zero-infrastructure principle.

### Git as a database (automatic commits)

Every state write produces a Git commit. Rejected: pollutes Git history, complicates branch management, and degrades performance in large repositories.
