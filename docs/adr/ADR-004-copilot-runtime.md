# ADR-004: GitHub Copilot as the Primary Runtime

**Date**: 2026-03-16
**Status**: Accepted
**Decision makers**: Founding team

## Context

The framework needs an execution runtime for agents: an environment that interprets agent definitions, manages invocation, exposes tools such as terminal, filesystem, and browser, and supports multi-agent orchestration. Multiple LLM-enabled IDE platforms exist, but they differ in format and capabilities.

## Decision

Adopt **GitHub Copilot Agent mode** in VS Code as the primary runtime. Agents are defined natively as `.agent.md` files under `.github/agents/`, and multi-agent orchestration uses `runSubagent`.

A **transpilation** pipeline produces secondary formats:

- **Cursor**: `.mdc` files under `output/cursor/` via `scripts/port_to_cursor.py`
- **Claude Code**: `CLAUDE.md` under `output/claude-code/` via `scripts/port_to_claude_code.py`

The Copilot `.agent.md` format is the source of truth. Secondary formats are generated derivatives.

## Consequences

### Positive

- **Native format**: `.agent.md` uses the full Copilot feature set, including YAML frontmatter, MCP tools, `runSubagent`, and configurable models
- **Multi-agent orchestration**: Copilot is the only supported runtime here that natively allows orchestrated subagent invocation
- **Integrated ecosystem**: native access to terminal, filesystem, browser, and MCP inside VS Code
- **Existing portability pipeline**: transpilation scripts already exist and are tested

### Negative

- **Most value is lost outside Copilot**: multi-agent orchestration, lane-based dispatch, and quality control are not portable; `.mdc` and `CLAUDE.md` keep only agent-local instructions
- **Vendor dependency**: `.agent.md` is specific to GitHub Copilot and not standardized
- **Uneven coverage**: agent updates require retranspilation to keep secondary formats in sync

### Risks

- **Copilot format changes without backward compatibility**, mitigated by versioned transpilation scripts and JSON schema validation in `schemas/agent.schema.json`
- **GitHub deprecating Copilot Agent mode**, mitigated by maintaining secondary formats as fallback outputs

## Alternatives Considered

### Native multi-runtime support (write for every platform)

Maintain native definitions for Copilot, Cursor, and Claude Code at the same time. Rejected: triples maintenance cost, creates inevitable divergence, and removes the single source of truth.

### Custom CLI runtime

Build a command-line interpreter for agents. Rejected: large implementation cost, reinvents capabilities already available in IDEs, and lacks an existing ecosystem.

### Cursor as the primary runtime (`.mdc` format)

Use Cursor Rules (`.mdc`) as the main format. Rejected: less expressive format, no structured frontmatter, no `runSubagent`, and no native multi-agent orchestration. Dispatch would have to be rebuilt from scratch.
